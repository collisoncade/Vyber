from flask_server import db_show, get_season_by_date, get_week_by_date, get_user_id
from datetime import datetime, date, time
from time import sleep
import sqlite3, json, os

__JSON_PATH = 'static/schedule_reference.json'

def __pick_inject(user_id:int, season_id:int, week_number:str, game_id:int, user_choice:str):
    conn = sqlite3.connect('master.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO Picks (user_id, season_id, week_number, game_id, user_choice)
        VALUES (?, ?, ?, ?, ?)
        ''',(user_id, season_id, week_number, game_id, user_choice))
    conn.commit()
    conn.close()

def __schedule_inject(game_weekday, game_year, game_month, game_day, game_hour, game_minute, away_team, home_team, season_id, week_number):
    conn = sqlite3.connect('master.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO NFLSchedule (game_weekday, game_year, game_month, game_day, game_hour, game_minute, away_team, home_team, season_id, week_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (game_weekday, game_year, game_month, game_day, game_hour, game_minute, away_team, home_team, season_id, week_number))
    conn.commit()
    conn.close()
    
def __update(new_game_weekday, new_game_year, new_game_month, new_game_day, new_game_hour, new_game_minute, new_away_team, new_home_team, new_season_id, game_id):
    conn = sqlite3.connect('master.db')
    c = conn.cursor()
    c.execute('''
        UPDATE NFLSchedule 
        SET game_weekday = ?, game_year = ?, game_month = ?, game_day = ?, game_hour = ?, game_minute = ?, away_team = ?, home_team = ?, season_id = ?
        WHERE game_id = ?
    ''', (new_game_weekday, new_game_year, new_game_month, new_game_day, new_game_hour, new_game_minute, new_away_team, new_home_team, new_season_id, game_id))
    conn.commit()
    conn.close()

def __schedule_inject_by_week(week):
    with open(__JSON_PATH, 'r') as file:
        data = json.load(file)
        games = data[week]
        for game in games:
            __schedule_inject(
                game_weekday     = game['game_weekday'],
                game_year        = game['game_year'],
                game_month       = game['game_month'],
                game_day         = game['game_day'],
                game_hour        = game['game_hour'],
                game_minute      = game['game_minute'],
                away_team        = game['away_team'], 
                home_team        = game['home_team'],
                season_id        = game['season_id'],
                week_number      = week
            )

def __schedule_delete_by_game_id(start, stop):
    conn = sqlite3.connect('master.db')
    c = conn.cursor()
    for i in range(start, stop):
        c.execute('''
            DELETE FROM NFLSchedule WHERE game_id = ?
        ''', (i,))
        conn.commit()
    conn.close()

def __pick_delete_by_id(pick_id):
    conn = sqlite3.connect('master.db')
    c = conn.cursor()
    c.execute('''
        DELETE FROM Picks WHERE pick_id = ?
    ''', (pick_id,))
    conn.commit()
    conn.close()

def __inject_result(winner:str, season_id:int, week_number:str, game_id:int):
    conn = sqlite3.connect('master.db')
    c = conn.cursor()

    c.execute('''
        INSERT OR IGNORE INTO Results (season_id, week_number, game_id, result)
        VALUES (?, ?, ?, ?)
    ''', (season_id, week_number, game_id, winner))
    conn.commit()

def main():
    ...
    p = input('main is empty? Y/n\n=> ')
    assert(p == 'Y')

    # __schedule_delete_by_game_id(0,17)

    # __pick_delete_by_id(4)

    # __pick_inject(2, 2, "Test Week", 50, "WAS")

    # __inject_result(winner="ARI", season_id=3, week_number='2', game_id=97)
    # __inject_result(winner="KC", season_id=3, week_number='2', game_id=98)
    # __inject_result(winner="WAS", season_id=3, week_number='3', game_id=117)

    # __schedule_inject_by_week("4")

    # conn = sqlite3.connect('master.db')
    # c = conn.cursor()

    # c.execute('''ALTER TABLE Users ADD league_id INTEGER''')

    # c.execute("DELETE FROM Results WHERE result_id = 132")

    # c.execute('''
    #     UPDATE Picks
    #     SET user_choice = 'NYJ'
    #     WHERE week_number = "3" AND user_id = 13 AND game_id = 102
    # ''')

    # c.execute('''
    #     INSERT INTO SeasonRecords (user_id, season_id, wins, losses, win_percent, is_reconciled)
    #     VALUES (?, ?, ?, ?, ?, ?)
    # ''', (2, 2, 0, 0, 'N/A', 0))

    # c.execute('''
    #     UPDATE Users SET league_id = 1 WHERE user_id IN (12, 13, 14, 15, 16 ,17, 18);
    # ''')

    # c.execute("UPDATE Results SET result = ? WHERE result_id = ?", ("CLE", 123))

    # c.execute('DROP TABLE SeasonRecords')
    # conn.commit()

    # conn.commit()
    # conn.close()


if __name__ == "__main__":

    main()
    os.system('clear')
    db_show('Users')
    # db_show('Seasons')
    db_show('WeeklyRecords')
    # db_show('SeasonRecords')
    # db_show('NFLSchedule')
    # db_show('Picks')
    db_show('Leagues')
    db_show('Results')
