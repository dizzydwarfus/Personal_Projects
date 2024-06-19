import sqlalchemy
from sqlalchemy import text
from functools import partial
import pandas as pd
from core.utils.sql_connector import DB
import re
import hashlib

nba = DB(db_name='NBA')
tempdb = DB(db_name='tempdb')

DATA_FOLDER = r'D:\lianz\Desktop\Python\personal_projects\nba_airflow\data'

DISABLE_FK_CONSTRAINTS = text(
    "EXEC sp_MSforeachtable @command1='ALTER TABLE ? NOCHECK CONSTRAINT ALL'")
ENABLE_FK_CONSTRAINTS = text(
    "EXEC sp_MSforeachtable @command1='ALTER TABLE ? WITH CHECK CHECK CONSTRAINT ALL'")
SET_IDENTITY_INSERT_ON = text("SET IDENTITY_INSERT {} ON")
SET_IDENTITY_INSERT_OFF = text("SET IDENTITY_INSERT {} OFF")


player_shotLocations = pd.read_csv(
    f"{DATA_FOLDER}\\player_shotLocations.csv", skipinitialspace=True, index_col=0)
games_played = pd.read_csv(
    f"{DATA_FOLDER}\\games_played.csv", parse_dates=['DateTime'])
players = pd.read_csv(f'{DATA_FOLDER}\\players.csv', parse_dates=['BirthDate'], names=[
                      'PlayerName', 'FromYear', 'ToYear', 'PositionID', 'Height', 'Weight', 'BirthDate', 'College'], header=0)
play_by_play = pd.read_parquet(f"{DATA_FOLDER}\\play_by_play.parquet")
positions = pd.read_csv(f'{DATA_FOLDER}\\position.csv')
teams = pd.read_csv(f'{DATA_FOLDER}\\team.csv', names=[
                    'TeamName', 'TeamShort'], header=0)


def insert_data(df, table_name, db, set_identity_insert=False):
    with db.engine.connect() as connection:
        connection.execute(DISABLE_FK_CONSTRAINTS)  # disable FK constraints
        if set_identity_insert:
            # set identity insert to on
            connection.execute(SET_IDENTITY_INSERT_ON, table_name)

        df.to_sql(table_name, con=db.engine, if_exists='append',
                  index=False)  # Use the engine here

        if set_identity_insert:
            # set identity insert to off
            connection.execute(SET_IDENTITY_INSERT_OFF, table_name)
        connection.execute(ENABLE_FK_CONSTRAINTS)  # enable FK constraints


def read_sql(db, table_name, columns=None):
    with db.engine.connect() as connection:
        result = connection.execute(
            text('SELECT {} FROM {}'), [', '.join(columns), table_name]).fetchall()
        if columns == '*':
            df = pd.DataFrame(result)
        else:
            df = pd.DataFrame(result, columns=columns)

        return df


if __name__ == '__main__':
    func = input('Enter function name: [insert_data, read_sql]')
    if func == 'insert_data':
        table_name = input('Enter table name: ')
        df_name = input('Enter file name: *.csv or *.parquet')
        if re.search(r'\.csv', df_name):
            df = pd.read_csv(f'{DATA_FOLDER}\{df_name}')
        elif re.search(r'\.parquet', df_name):
            df = pd.read_parquet(f'{DATA_FOLDER}\{df_name}')
        print(df)
        # insert_data(df, table_name, nba)
    elif func == 'read_sql':
        table_name = input('Enter table name: ')
        columns = input('Enter columns: format must be: [col1, col2, col3]')
        print(columns)
        print(read_sql(nba, table_name, columns))
