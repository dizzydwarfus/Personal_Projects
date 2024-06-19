import pandas as pd
import datetime as dt
import requests
from pprint import pprint
from bs4 import BeautifulSoup, Tag
import numpy as np
import time
import plotly.graph_objects as go
import re
import os
from dotenv import dotenv_values
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='nba_scraping.log', filemode='a', encoding='utf-8', datefmt='%Y-%m-%d %H:%M:%S')

secrets = dotenv_values(
    r'C:\Users\lianz\Python\personal_projects\nba-airflow\.env')

team_abbs = {
    "Atlanta Hawks": 'ATL',
    "Brooklyn Nets": 'BKN',
    "Boston Celtics": 'BOS',
    "Charlotte Hornets": 'CHH',
    "Chicago Bulls": 'CHI',
    "Cleveland Cavaliers": 'CLE',
    "Dallas Mavericks": 'DAL',
    "Denver Nuggets": 'DEN',
    "Detroit Pistons": 'DET',
    "Golden State Warriors": 'GSW',
    "Houston Rockets": 'HOU',
    "Indiana Pacers": 'IND',
    "Los Angeles Clippers": 'LAC',
    "Los Angeles Lakers": 'LAL',
    "Memphis Grizzlies": 'MEM',
    "Miami Heat": 'MIA',
    "Milwaukee Bucks": 'MIL',
    "Minnesota Timberwolves": 'MIN',
    "New Orleans Pelicans": 'NOP',
    "New York Knicks": 'NYK',
    "Oklahoma City Thunder": 'OKC',
    "Orlando Magic": 'ORL',
    "Philadelphia 76ers": 'PHI',
    "Phoenix Suns": 'PHX',
    "Portland Trail Blazers": 'POR',
    "Sacramento Kings": 'SAC',
    "San Antonio Spurs": 'SAS',
    "Toronto Raptors": 'TOR',
    "Utah Jazz": 'UTA',
    "Washington Wizards": 'WAS',
    'Seattle SuperSonics': 'SEA',
    'Vancouver Grizzlies': 'VAN',
    'New Jersey Nets': 'NJN',
    'New Orleans Hornets': 'NOH',
    'Charlotte Bobcats': 'CAB',
    'New Orleans/Oklahoma City Hornets': 'NCH',
}

# 20 requests per minute maximum
# change /shot-chart/YYYYMMDD0TEAM.html to get games on different days


def request_soup_for_game(year: str, month: str, day: str, team: str):
    url = f'https://www.basketball-reference.com/boxscores/shot-chart/{year}{month}{day}0{team}.html'
    page = requests.get(url=url)
    soup = BeautifulSoup(page.content, "html.parser")
    if soup.find('h1').text == 'Page Not Found (404 error)':
        return False
    else:
        return soup


def get_shot_area(soup):
    shot_area = soup.find_all("div", class_="shot-area")
    return shot_area


def get_game_meta(soup):
    game_meta = soup.find_all("div", class_='scorebox_meta')[0].text
    return game_meta


def get_customdata(df: pd.DataFrame) -> list:
    customdata = []
    for row in df.itertuples(index=False):
        customdata.append(tuple(row))
    return customdata


def create_df(shot_area, game_meta):
    df = dict(player_name=[], time_left=[], team_name=[], score_status=[],
              x_shot_pos=[], y_shot_pos=[], quarter=[], shot_status=[], full_text=[])
    for elem in shot_area:
        for content in elem.contents:
            if isinstance(content, Tag) and not re.search(r'alt="nbahalfcourt"', str(content)):
                shot_pos = re.findall(
                    r'\d+(?=px)', str(content.attrs.get('style')))
                tooltip = content.attrs.get('tip')
                status = content.attrs.get('class')
                df['x_shot_pos'].append(int(shot_pos[1]))
                df['y_shot_pos'].append(470 - int(shot_pos[0]))
                df['quarter'].append(tooltip.split(',')[0])
                df['time_left'].append(re.findall(
                    r'(?!\s)(\d+:\d+.\d)(?= remaining)', tooltip)[0])
                df['shot_status'].append(status[-1])
                df['player_name'].append(re.findall(
                    r"(?=<br>)(.*)((?= missed)|(?= made))", tooltip)[0][0][4:])
                df['team_name'].append(re.findall(
                    r"(?=ft<br>)(.*)((?= tied)|(?= now trails)|(?= trails)|(?= leads))", tooltip)[0][0][6:].replace('now', ''))
                df['score_status'].append(re.findall(
                    r"(?=ft<br>).*", tooltip)[0][6:])
                df['full_text'].append(tooltip)

    df = pd.DataFrame.from_dict(df,).astype({'quarter': 'category',
                                            'shot_status': 'category', })
    df['datetime'] = dt.datetime.strptime(re.findall(
        r'\d+:\d+ \w+, \w+ \d+, \d+', game_meta)[0], "%I:%M %p, %B %d, %Y")
    # location = re.findall(
    #     r'(?=\d{4})(\w+\s\w+,.+,\s.+)(?=\nLogos)', game_meta)[0][4:].split(',')
    # # arena = location[0].strip()
    # city = location[1].strip()
    # state = location[2].strip()

    # df['arena'] = arena
    # df['city'] = city
    # df['state'] = state

    return df


# Schedule Scraping
def get_schedule_html(year: str, month: str,):
    games = requests.get(
        f"https://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html#schedule")
    soup = BeautifulSoup(games.content, "html.parser")
    if soup.find('h1').text == 'Page Not Found (404 error)':
        return False
    else:
        return soup


def get_schedule_table(soup,):
    df = pd.read_html(str(soup.find_all('table')))[
        0].drop(['Unnamed: 6',], axis=1)
    return df


def process_schedule(df: pd.DataFrame):
    df = df.loc[df['Date'] != 'Playoffs'].copy()
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Start (ET)'] + 'm')
    df['DateStr'] = [dt.datetime.strftime(
        i, "%Y%m%d%H%M") for i in df['DateTime']]
    df = df.drop(['Date', 'Start (ET)', 'Notes'], axis=1)
    df.rename(columns={'Visitor/Neutral': 'Visitor', 'PTS': 'Visitor PTS', 'Home/Neutral': 'Home',
              'PTS.1': 'Home PTS', 'Unnamed: 7': 'OT', 'Attend.': 'Attendance'}, inplace=True)
    df['Visitor_short'] = [team_abbs[name] for name in df['Visitor']]
    df['Home_short'] = [team_abbs[name] for name in df['Home']]
    df['game_id'] = df['DateStr'] + df['Visitor_short'] + df['Home_short']
    df.set_index('DateTime', inplace=True)
    df['year'] = df.index.year
    df['month'] = df.index.month
    return df


def get_players_html(letter: str):
    players = requests.get(
        f"https://www.basketball-reference.com/players/{letter}/")
    soup = BeautifulSoup(players.content, "html.parser")
    if soup.find('h1').text == 'Page Not Found (404 error)':
        return False
    else:
        return soup


MONTHS = ['october', 'november', 'december', 'january', 'february',
          'march', 'april', 'may', 'june', 'july', 'august', 'september']
YEARS = [str(i) for i in range(2001, dt.date.today().year + 1)]

# Get schedule data
df_list = []
request_count = 0
start = time.time()
for year in YEARS:
    for month in MONTHS[:]:
        lag = np.random.randint(4, 6)
        logging.info(f'Cycle lag time: {lag}')
        time.sleep(lag)
        logging.info(f'Processing {month}-{year} request!')
        try:
            soup = get_schedule_html(year, month)
        except Exception as e:
            logging.error(
                f'Could not process {month}-{year} request!', exc_info=True)
            continue
        if not soup:
            continue
        request_count += 1
        try:
            df = get_schedule_table(soup)
            df = process_schedule(df)
            df_list.append(df)
            logging.info(f'Finished {month} request!\n')
        except:
            logging.error(
                f'Error while processing {month}-{year}\n', exc_info=True)
            continue
end = time.time()
logging.info(f'Total time taken: {round(end-start)}s')
logging.info(f'Total requests count: {request_count}')
logging.info(
    f'Average Requests per Second: {round((end-start)/request_count)}')
full_df = pd.concat(df_list, axis=0)

if os.path.isfile(r'C:\Users\lianz\Python\personal_projects\nba-airflow\data\games_played.csv'):
    read_df = pd.read_csv(
        r'C:\Users\lianz\Python\personal_projects\nba-airflow\data\games_played.csv', index_col=0)
    final_df = pd.concat([read_df, full_df], axis=0).reset_index(
    ).drop_duplicates(subset='game_id')
    final_df.to_csv(
        r'C:\Users\lianz\Python\personal_projects\nba-airflow\data\games_played.csv')
else:
    full_df.to_csv(
        r'C:\Users\lianz\Python\personal_projects\nba-airflow\data\games_played.csv')

df_final = pd.read_csv(r'C:\Users\lianz\Python\personal_projects\nba-airflow\data\games_played.csv',
                       index_col=0, parse_dates=['DateTime'], dtype={'DateStr': 'str'}).sort_values('DateTime')

# Get shot data using game schedule data
df_list = []
failed_games = []
total_lag_time = 0
start_time = time.time()
game_ids_to_scrape = df_final.iloc[:, -3]

logging.warning(
    '\n\n\n-------------------------------------Start of Scraping Shot Locations!-------------------------------------\n\n\n')
for i, x in enumerate(game_ids_to_scrape):
    lag = np.random.randint(4, 6)
    total_lag_time += lag
    logging.info(f'Cycle lag time: {lag}')
    time.sleep(lag)
    team = df_final.loc[df_final['game_id'] == x, 'Home_short'][0]
    date = df_final.loc[df_final['game_id'] == x,].index[0]
    year = '{:04d}'.format(date.year)
    month = '{:02d}'.format(date.month)
    day = '{:02d}'.format(date.day)
    logging.info(f'Processing {x} request!')
    try:
        test_soup = request_soup_for_game(
            year=year, month=month, day=day, team=team)
        logging.info(f'Successfully processed {x} request!')
    except Exception as e:
        logging.error(f'Request failed for {x}', exc_info=True)
        failed_games.append(x)
    try:
        shot_area = get_shot_area(test_soup)
        game_meta = get_game_meta(test_soup)
        df = create_df(shot_area, game_meta)
        df['game_id'] = x
        df_list.append(df)
        logging.info(f'Successfully processed {x} shots!\n')

    except Exception as e:
        logging.error(
            f'Could not get and process shots for {x}\n', exc_info=True)
        failed_games.append(x)

logging.info(
    f'Total lag time: {total_lag_time} seconds | {round(total_lag_time / 60, 2)} minutes | {round(total_lag_time / 3600, 2)} hours')
logging.info(
    f'Failed games: {len(failed_games)} games out of {len(game_ids_to_scrape)} games')
logging.info(
    f'Time elapsed: {time.time() - start_time} seconds | {round((time.time() - start_time) / 60, 2)} minutes | {round((time.time() - start_time) / 3600, 2)} hours')
logging.info(
    f'Averaged {round((time.time() - start_time) / len(game_ids_to_scrape), 2)} seconds per game')

logging.warning(
    '-------------------------------------End of Scraping Shot Locations!-------------------------------------')

pbp_all = pd.concat(df_list, axis=0)

if os.path.exists(r'C:\Users\lianz\Python\personal_projects\nba-airflow\data\play_by_play.parquet'):
    pbp_df = pd.read_parquet(
        r'C:\Users\lianz\Python\personal_projects\nba-airflow\data\play_by_play.parquet')
    pbp_df = pd.concat([pbp_df, pbp_all])
    pbp_df.to_parquet(
        r'C:\Users\lianz\Python\personal_projects\nba-airflow\data\play_by_play.parquet')
else:
    pbp_all.to_parquet(
        r'C:\Users\lianz\Python\personal_projects\nba-airflow\data\play_by_play.parquet')

# Scrape NBA players data
all_letters = [chr(i) for i in range(ord('a'), ord('z') + 1)]
failed_letters = []
players_df = pd.DataFrame()
total_lag_time = 0

logging.warning(
    '\n\n\n-------------------------------------Start of Scraping Player Info!-------------------------------------\n\n\n')

start_time = time.time()

for i in all_letters:
    logging.info(f'Scraping letter {i}')

    try:
        loop_players_df = pd.read_html(
            str(get_players_html(i).find_all('table', id='players')[0]))[0]
        logging.info(f'Scraped letter {i} | {len(players_df)} players')

    except Exception as e:
        logging.error(f'Failed to scrape letter {i}: {e}\n')
        failed_letters.append(i)

    players_df = pd.concat([players_df, loop_players_df], axis=0)
    logging.info(f'Concatenated letter {i} | {len(players_df)} players')

    lag = np.random.randint(4, 6)
    total_lag_time += lag

    logging.info(f'Cycle lag time: {lag}')
    logging.info(
        f'Total lag time after {all_letters.index(i)+1} cycles: {total_lag_time}\n')

    time.sleep(lag)
players_df = players_df.set_index('Player').reset_index()
players_df.to_csv(
    r'C:\Users\lianz\Python\personal_projects\nba-airflow\data\players.csv', index=False)

logging.info(
    f'Total lag time: {total_lag_time} seconds | {round(total_lag_time / 60, 2)} minutes | {round(total_lag_time / 3600, 2)} hours')
logging.info(
    f'Failed letters: {len(failed_letters)} out of {len(all_letters)} letters')
logging.info(
    f'Time elapsed: {time.time() - start_time} seconds | {round((time.time() - start_time) / 60, 2)} minutes | {round((time.time() - start_time) / 3600, 2)} hours')
logging.info(
    f'Averaged {round((time.time() - start_time) / len(all_letters), 2)} seconds per letter')
logging.warning(
    '\n\n\n-------------------------------------End of Scraping Player Info!-------------------------------------\n\n\n')

# TODO: use airflow to schedule daily requests
# TODO: schedule daily updates to SQL Server
