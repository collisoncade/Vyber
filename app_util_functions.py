from flask_server import get_week_by_date, get_season_by_date, app, get_db
from time import sleep
from datetime import timedelta, date, time, datetime
from typing import List
import sqlite3

class APP_UTIL_FUNCTIONS:
    db_file:str = None
    user_ids: List[int] = None
    sorted_weekly_records = None
    sorted_season_records = None
    
    def __init__(self) -> None:
        self.db_file = 'master.db'
        self.user_ids = self._get_user_ids()
        self.sorted_weekly_records = self._sort_weekly_records()
        self.sorted_season_records = self._sort_season_records()

    def _init_db_creds(self) -> None:
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(255) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
            ''')
        conn.commit()
        conn.close()

    def _init_db_season(self) -> None:
        conn = sqlite3.connect('master.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS Seasons (
                season_id INTEGER PRIMARY KEY AUTOINCREMENT,
                season_name VARCHAR(255) UNIQUE
            )
            ''')

        c.execute('SELECT COUNT(*) FROM Seasons')
        size = c.fetchone()[0]
        if size == 0:
            c.execute('INSERT OR IGNORE INTO Seasons (season_name) VALUES (?)', ("Season 23",))
            c.execute('INSERT OR IGNORE INTO Seasons (season_name) VALUES (?)', ("Pre-Season 24",))
            c.execute('INSERT OR IGNORE INTO Seasons (season_name) VALUES (?)', ("Season 24",))

        conn.commit()
        conn.close()

    def _init_db_weekly_records(self) -> None:
        conn = sqlite3.connect('master.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS WeeklyRecords (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                week_number TEXT,
                season_id INTEGER,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                is_reconciled BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES Users(user_id),
                FOREIGN KEY (season_id) REFERENCES Seasons(season_id)
            )
            ''')
        conn.commit()
        conn.close()

    def _init_db_season_records(self) -> None:
        conn = sqlite3.connect('master.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS SeasonRecords (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                season_id INTEGER,
                wins INTEGER,
                losses INTEGER,
                win_percent TEXT,
                is_reconciled BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES Users(user_id)
                FOREIGN KEY (season_id) REFERENCES Season(season_id)
            )
            ''')
        conn.commit()
        conn.close()

    def _init_db_nfl_schedule(self) -> None:
        conn = sqlite3.connect('master.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS NFLSchedule (
                game_id          INTEGER PRIMARY KEY AUTOINCREMENT,
                game_weekday     TEXT,
                game_year        INTEGER,
                game_month       INTEGER,
                game_day         INTEGER,
                game_hour        INTEGER,
                game_minute      INTEGER,
                away_team        TEXT,
                home_team        TEXT,
                season_id        INTEGER,
                week_number      TEXT,
                FOREIGN KEY (season_id) REFERENCES Seasons(season_id)                    
            )
            ''')
        conn.commit()
        conn.close()

    def _init_db_results(self) -> None:
        conn = sqlite3.connect('master.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS Results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                season_id INTEGER,
                week_number TEXT,
                game_id INTEGER,
                result TEXT,
                FOREIGN KEY (season_id) REFERENCES Seasons(season_id)
                FOREIGN KEY (game_id) REFERENCES NFLSchedule(game_id)
            )
            ''')
        conn.commit()
        conn.close()

    def _init_db_picks(self) -> None:
        conn = sqlite3.connect('master.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS Picks (
                pick_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                season_id INTEGER,
                week_number TEXT,
                game_id INTEGER,
                user_choice TEXT,
                FOREIGN KEY (user_id) REFERENCES Users(user_id)
                FOREIGN KEY (game_id) REFERENCES NFLSchedule(game_id)
            )
            ''')
        conn.commit()
        conn.close()

    def _init_db_leagues(self) -> None:
        conn = sqlite3.connect('master.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS Leagues (
                league_id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_name VARCHAR(255) NOT NULL UNIQUE
            )
            ''')
        conn.commit()
        conn.close()

    def _get_user_ids(self) -> List[int]:
        conn = sqlite3.connect('master.db')
        c = conn.cursor()
        c.execute("SELECT user_id FROM Users")
        user_ids = [user_id[0] for user_id in c.fetchall()]
        conn.close()
        return user_ids

    def _reconcile_prev_week(self) -> None:
        today = date.today()
        one_week_ago = today - timedelta(weeks=1)
        prev_week_number = get_week_by_date(one_week_ago)
        with app.app_context():
            db = get_db()
            c = db.cursor()
            c.execute("SELECT * FROM WeeklyRecords WHERE week_number = ?", (prev_week_number,))
            reconciled = c.fetchone()[6]

            c.execute("SELECT result FROM Results WHERE week_number = ?", (prev_week_number,))
            results = c.fetchall()

            c.execute("SELECT * FROM NFLSchedule WHERE week_number = ?", (prev_week_number,))
            games = c.fetchall()

            if not bool(reconciled) and len(results) == len(games):
                c.execute("UPDATE WeeklyRecords SET is_reconciled = 1 WHERE week_number = ?", (prev_week_number,))
                db.commit()

        print("\t[x] Dispatch: func<_reconcile_prev_week>")

    def _update_week_records(self) -> None:
        week_number = get_week_by_date()
        today = date.today()
        games_data = {}

        for user_id in self.user_ids:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute('''
                SELECT * FROM WeeklyRecords WHERE week_number = ? AND user_id = ?
            ''', (week_number, user_id))
            exists = c.fetchone()
            conn.close()
        
            if not exists:
                conn = sqlite3.connect(self.db_file)
                c = conn.cursor()
                c.execute('''
                    INSERT INTO WeeklyRecords (user_id, week_number, season_id, wins, losses, is_reconciled)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, week_number, get_season_by_date(), 0, 0, 0))
                conn.commit()
                conn.close()

        with app.app_context():
            db = get_db()
            c = db.cursor()
            c.execute('''
                SELECT * FROM NFLSchedule WHERE week_number = ?
            ''', (week_number,))
            games = c.fetchall()

        for game in games:
            game_date = date(game[2], game[3], game[4])
            now = datetime.now().time()
            game_time = time(game[5], game[6])
            window_status = now <= game_time
            if today == game_date:
                window_status = now <= game_time

            games_data[game[0]] = [game, None, window_status, None, None]

        with app.app_context():
            db = get_db()
            c = db.cursor()
            c.execute('''
                SELECT game_id, result FROM Results WHERE week_number = ?
            ''', (week_number,))
            results = c.fetchall()

        for user_id in self.user_ids:
            with app.app_context():
                db = get_db()
                c = db.cursor()
                c.execute('''
                    SELECT game_id, user_choice FROM Picks WHERE week_number = ? AND user_id = ?
                ''', (week_number, user_id))
                picks = c.fetchall()

                for pick in picks:
                    game_id = pick[0]
                    user_choice = pick[1]
                    if user_choice:
                        game = games_data.get(game_id)
                        game[1] = user_choice
                        games_data[game_id] = game

            week_wins = 0
            week_losses = 0
            for result in results:
                game_id = result[0]
                winner = result[1]

                game = games_data.get(game_id)
                game[3] = winner
                games_data[game_id] = game
            
                with app.app_context():
                    db = get_db()
                    c = db.cursor()
                    
                    c.execute('''
                        SELECT game_year, game_month, game_day, game_hour, game_minute
                        FROM NFLSchedule
                        WHERE game_id = ?
                    ''', (game_id,))
                    info = c.fetchone()

                    game_start = date(info[0], info[1], info[2])
                    now = datetime.now().time()
                    game_time = time(info[3], info[4])
                    late = today > game_start or (today == game_start and now >= game_time)

                    c.execute('''
                        SELECT user_choice FROM Picks
                        WHERE user_id = ? AND week_number = ? AND game_id = ?
                    ''', (user_id, week_number, game_id))
                    try:
                        pick = c.fetchone()[0]
                    except TypeError as TE:
                        pick = None

                    week_wins += int(pick == winner)
                    week_losses += int((late and not pick) or pick != winner)
                    
                    c.execute('''
                        UPDATE WeeklyRecords
                        SET wins = ?, losses = ?
                        WHERE week_number = ? AND user_id = ?
                    ''',(week_wins, week_losses, week_number, user_id))
                    db.commit()

        print("\t[x] Dispatch: func<_update_week_records>")

    def _update_season_records(self) -> None:
        season_id: int = get_season_by_date()
        with app.app_context():
            db = get_db()
            c = db.cursor()

            for user_id in self.user_ids:
                c.execute('''
                    SELECT * FROM SeasonRecords WHERE user_id = ? AND season_id = ?
                ''', (user_id, season_id))
                season_record = c.fetchone()

                if not season_record:
                    c.execute('''
                        INSERT INTO SeasonRecords (user_id, season_id, wins, losses, win_percent, is_reconciled)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (user_id, season_id, 0, 0, "0%", 0))
                    db.commit()

        for user_id in self.user_ids:
            with app.app_context():
                c.execute('''
                    SELECT SUM(wins), SUM(losses) FROM WeeklyRecords 
                    WHERE user_id = ? AND season_id = ? AND is_reconciled = 1
                ''', (user_id, season_id))
                season_record = c.fetchone()

                season_wins = season_record[0] if season_record[0] else 0
                season_losses = season_record[1] if season_record[1] else 0

                if season_wins + season_losses > 0:
                    win_percent = f"{(season_wins / (season_wins + season_losses)) * 100:.2f}%"
                else:
                    win_percent = "0%"

                c.execute('''
                    UPDATE SeasonRecords SET wins = ?, losses = ?, win_percent = ?
                    WHERE user_id = ? AND season_id = ?
                ''', (season_wins, season_losses, win_percent, user_id, season_id))
                db.commit()
        
        print("\t[x] Dispatch: func<_update_season_records>")

    def _sort_weekly_records(self) -> None:
        with app.app_context():
            db = get_db()
            c = db.cursor()
            c.execute("SELECT * FROM WeeklyRecords Records WHERE week_number = ?", (get_week_by_date(),))
            weekly_records = c.fetchall()

            if weekly_records[0] and weekly_records[0][4] + weekly_records[0][5] > 0:
                try:
                    weekly_records.sort(key=lambda x: (x[4] / (x[4] + x[5])), reverse=True)
                except ZeroDivisionError as E:
                    pass

        print("\t[x] Dispatch: func<_sort_weekly_records>")
        return weekly_records

    def _sort_season_records(self) -> None:
        with app.app_context():
            db = get_db()
            c = db.cursor()
            c.execute("SELECT * FROM SeasonRecords WHERE season_id = ?", (get_season_by_date(),))
            season_records = c.fetchall()

            season_records.sort(key=lambda x: float(x[5][len(x[5]) - 2]))

        print("\t[x] Dispatch: func<_sort_weekly_records>")

if __name__ == "__main__":
    app_util_functions = APP_UTIL_FUNCTIONS()

    print("[ Running ] - Flask Application Utilities")

    while True:
        print("\t", datetime.now().time())
        app_util_functions._reconcile_prev_week()
        app_util_functions._update_week_records()
        app_util_functions._update_season_records()
        app_util_functions._sort_weekly_records()
        app_util_functions._sort_season_records()
        sleep(60 * 60)