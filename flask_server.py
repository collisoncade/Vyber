from flask import Flask, request, g, render_template, jsonify, session, redirect
from datetime import datetime, date, time
from time import sleep
from threading import Thread
from typing import List
import json
import os
import sqlite3
import hashlib
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = '147'

__DB_FILE = os.path.join(app.root_path, 'master.db')
__JSON_FILE = os.path.join(app.static_folder, 'schedule_reference.json')

@app.route('/')
def route_to_home_page():
    return render_template("home.html")

@app.route('/check-email', methods=['POST'])
def check_email():
    data = request.get_json()
    email = data.get('email')

    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute('SELECT email FROM Users WHERE email = ?', (email,))
        user = c.fetchone()

    if user:
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})

@app.route('/check-username', methods=['POST'])
def check_username():
    data = request.get_json()
    username = data.get('username')

    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute('SELECT username FROM Users WHERE username = ?', (username,))
        user = c.fetchone()

    if user:
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})
    
@app.route('/check-password', methods=['POST'])
def check_password():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute('SELECT * FROM Users WHERE username = ?', (username,))
        user = c.fetchone()

    if user and user[3] == hashlib.sha256(password.encode()).hexdigest():
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})

@app.route('/create-account', methods=['GET'])
def route_to_create_account_page():
    return render_template("create_account.html")

@app.route('/create-account', methods=['POST'])
def register_user():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data recieved'}), 400
    
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return jsonify({'error': 'Missing required fields'}), 400
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute(
            'INSERT INTO Users (username, email, password) VALUES (?, ?, ?)',
            (username, email, hashed_password))
        db.commit()

    user_id = get_user_id(username)
    week_number = get_week_by_date()
    season_id = get_season_by_date()

    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute(
            'INSERT INTO WeeklyRecords (user_id, week_number, season_id, wins, losses, is_reconciled) VALUES (?, ?, ?, ?, ?, ?)',
            (user_id, week_number, season_id, 0, 0, 0))
        db.commit()

    with app.app_context():
        c.execute(
            'INSERT INTO SeasonRecords (user_id, season_id, wins, losses, win_percent, is_reconciled) VALUES (?, ?, ?, ?, ?, ?)',
            (user_id, season_id, 0, 0, "0%", 0)
        )
        db.commit()

    return jsonify({'message': 'User registered successfuly'}), 200

@app.route('/login', methods=['GET'])
def route_to_login_page():
    return render_template("login.html")

@app.route('/log-user-in', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute('SELECT * FROM Users WHERE username = ?', (username,))
        user = c.fetchone()

    if user and user[3] == hashlib.sha256(password.encode()).hexdigest():
        token = jwt.encode({'username': username}, app.config['SECRET_KEY'], algorithm='HS256')
        session['username'] = username
        session['email'] = user[2]
        return jsonify({'token': token, 'user_id': get_user_id(username)})
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/verify-user')
def verify_user():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'error': 'Token is missing'}), 401

    if not token.startswith('Bearer '):
        return jsonify({'error': 'Token is invalid'}), 401

    try:
        token = token.split()[1]
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        username = data['username']

        with app.app_context():
            db = get_db()
            c = db.cursor()
            c.execute('SELECT * FROM Users WHERE username = ?', (username,))
            user = c.fetchone()

        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        g.user_id = get_user_id(session.get('username'))

        return redirect('/profile')

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except IndexError:
        return jsonify({'error': 'Token is malformed'}), 401

@app.route('/profile')
def route_to_profile_page():
    user = session.get('username')
    return render_template('profile.html', user=user)

@app.route('/make-picks', methods=["GET"])
def route_to_make_picks_page():
    username = session.get('username')
    try:
        user_id = get_user_id(username)
    except Exception as E:
        return redirect('/login')

    week = get_week_by_date()
    if not week:
        return jsonify({'error': 'Current week was not found.'}), 404
    
    season = get_season_by_date()
    if not season:
        return jsonify({'error': 'Current season was not found.'}), 404

    data = {}    
    games_data = {}
    data['user_data'] = {'username': username}
    data['week'] = week
    data['games_data'] = {}

    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute('''
            SELECT * FROM NFLSchedule WHERE week_number = ?
        ''', (week,))
        games = c.fetchall()

    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute('''
            SELECT game_id, user_choice FROM Picks WHERE week_number = ? AND user_id = ?
        ''', (week, user_id))
        picks = c.fetchall()

    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute('''
            SELECT game_id, result FROM Results WHERE week_number = ?
        ''', (week, ))
        results = c.fetchall()

    for i in range(len(games)):
        game = games[i]
        today = date.today()
        game_date = date(game[2], game[3], game[4])
        now = datetime.now().time()
        game_time = time(game[5], game[6])
        window_status = today <= game_date
        if today == game_date:
            window_status = now <= game_time

        games_data[game[0]] = [game, None, window_status, None, None]

    for pick in picks:
        pick_game_id = pick[0]
        user_choice = pick[1]
        if user_choice:
            game = games_data.get(pick_game_id)
            game[1] = user_choice
            games_data[pick_game_id] = game

    for result in results:
        result_game_id = result[0]
        winner = result[1]
        if winner:
            game = games_data.get(result_game_id)
            game[3] = winner
            games_data[result_game_id] = game

            with app.app_context():
                db = get_db()
                c = db.cursor()
                c.execute('''
                    SELECT user_choice FROM Picks
                    WHERE user_id = ? AND week_number = ? AND game_id = ?
                ''', (user_id, week, result_game_id))
                try:
                    pick = c.fetchone()[0]
                except TypeError as TE:
                    pick = None

    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute('''
            SELECT SUM(wins), SUM(losses) FROM WeeklyRecords
            WHERE user_id = ? AND week_number = ?
        ''',(user_id, week))
        week_record = c.fetchone()

    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute('''
            SELECT wins, losses FROM SeasonRecords WHERE user_id = ? AND season_id = ?
        ''',(user_id, season))
        season_record = c.fetchone()

    # Sort season records to get user season rank    
    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute("SELECT * FROM SeasonRecords WHERE season_id = ?", (get_season_by_date(),))
        season_records = c.fetchall()

        season_records.sort(key=lambda x: float(x[5][len(x[5]) - 2]))
    
    for srI in range(len(season_records)):
        curr_sr = season_records[srI]
        if curr_sr[1] == user_id:
            user_season_rank = srI

    # Sort weekly records to get user week rank
    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute("SELECT * FROM WeeklyRecords Records WHERE week_number = ?", (get_week_by_date(),))
        weekly_records = c.fetchall()

        if weekly_records[0] and weekly_records[0][4] + weekly_records[0][5] > 0:
            try:
                weekly_records.sort(key=lambda x: (x[4] / (x[4] + x[5])), reverse=True)
                for wrI in range(len(weekly_records)):
                    curr_wr = weekly_records[wrI]
                    if curr_wr[1] == user_id:
                        user_week_rank = wrI
            except ZeroDivisionError:
                user_week_rank = user_season_rank
        else:
            user_week_rank = user_season_rank

    user_data = data['user_data']
    user_data['week_wins'] = week_record[0]
    user_data['week_losses'] = week_record[1]
    user_data['season_wins'] = season_record[0]
    user_data['season_losses'] = season_record[1]
    user_data['season_rank'] = user_season_rank
    user_data['week_rank'] = user_week_rank
    data['games_data'] = games_data

    return render_template('make_picks.html', username=session.get('username'), data=data)

@app.route('/make-pick', methods=["POST"])
def make_pick():
    data = request.get_json()
    game_id = data.get('game_id')
    new_user_choice = data.get('pick')
    username = data.get('username')

    season_id = get_season_by_date()
    week = get_week_by_date()
    user_id = get_user_id(username)
    pick = get_pick(user_id, game_id)

    with app.app_context():
        db = get_db()
        c = db.cursor()
        if pick:
            c.execute('''
                UPDATE Picks SET user_choice = ? WHERE game_id = ? AND user_id = ?         
            ''', (new_user_choice, game_id, user_id))
            db.commit()
        else:
            c.execute('''
                INSERT INTO Picks (user_id, season_id, week_number, game_id, user_choice)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, season_id, week, game_id, new_user_choice))
            db.commit()
        return jsonify({'status': True})

@app.route('/league')
def route_to_league_page():
    data = {}
    data['usernames'] = {}
    data['username'] = session.get('username')
    data['week'] = get_week_by_date()
    
    with app.app_context():
        db = get_db()
        c = db.cursor()
        week_number = get_week_by_date()
        c.execute('''
            SELECT * FROM WeeklyRecords WHERE week_number = ?
        ''', (week_number,))
        week_results = c.fetchall()
        try:
            week_results.sort(key=lambda x: x[4]/(x[4] + x[5]), reverse=True)
        except ZeroDivisionError:
            pass
        data['week_results'] = week_results

        c.execute('''
            SELECT * FROM NFLSchedule WHERE week_number = ? 
        ''', (week_number,))
        games = c.fetchall()
        data['games'] = games

        for week_result in week_results:
            user_id = week_result[1]
            data['usernames'][user_id] = get_username(user_id)
            
            curr_picks = []
            for game in games:
                game_id = game[0]
                c.execute('''
                    SELECT user_choice FROM Picks WHERE game_id = ? AND user_id = ?
                ''', (game_id, user_id))
                pick = c.fetchone()
                if not pick:
                    pick = 'N/A'
                else:
                    pick = pick[0]
                curr_picks.append(pick)
            data[user_id] = curr_picks

    return render_template('league.html', data=data)

@app.route('/schedule')
def route_to_schedule_page():
    return render_template('schedule.html', username=session.get('username'))
    
@app.route('/static/<path:filename>')
def get_credentials(filename):
    return render_template("static", filename)

def get_season_by_date() -> int:
    with open(__JSON_FILE, 'r') as file:
        data = json.load(file)
        season_date_ranges = data.get('season_date_ranges', {})
        for season_id, season_dates in season_date_ranges.items():
            start_date = date(
                season_dates['start_year'],
                season_dates['start_month'],
                season_dates['start_day']
            )
            end_date = date(
                season_dates['end_year'],
                season_dates['end_month'],
                season_dates['end_day']
            )
            today = date.today()
            if today >= start_date and today <= end_date:
                return season_id

def get_week_by_date(explicit_date:date=None) -> str:
    '''@param explicit_date: Explicit date object'''
    with open(__JSON_FILE, 'r') as file:
        data = json.load(file)
        week_date_ranges = data.get('week_date_ranges', {})
        today = date.today()

        if explicit_date:
            today = explicit_date
        
        for week, week_dates in week_date_ranges.items():
            start_date = date(
                week_dates['start_year'],
                week_dates['start_month'],
                week_dates['start_day']
            )
            end_date = date(
                week_dates['end_year'],
                week_dates['end_month'],
                week_dates['end_day']
            )
            if today >= start_date and today <= end_date:
                return week

def get_db():
    if 'db' not in g:
        return sqlite3.connect(__DB_FILE)
    return

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def get_user_id(username):
    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute('SELECT user_id FROM Users WHERE username = ?', (username,))
        user_id = c.fetchone()

    return user_id[0] # returns tuple without indexing to first element

def get_username(user_id):
    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute("SELECT username FROM Users WHERE user_id = ?", (user_id,))
    return c.fetchone()[0]

def get_pick(user_id, game_id):
    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute('''
            SELECT * FROM Picks WHERE user_id = ? AND game_id = ?
        ''', (user_id, game_id))
        pick = c.fetchone()
    return pick    

def db_show(info=None):
    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute('SELECT * FROM {}'.format(info))
        rows = c.fetchall()
        print('[ {} ]'.format(info))
        for i in range(len(rows)):
            print('\t',rows[i])
        print('\n')

if __name__ == "__main__":
    app.run(debug=True)