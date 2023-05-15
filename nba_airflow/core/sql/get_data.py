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
        print(f'Cycle lag time: {lag}')
        time.sleep(lag)
        print(f'Processing {month}-{year} request!')
        try:
            soup = get_schedule_html(year, month)
        except Exception as e:
            print(f'Could not process {month}-{year} request! {e}')
            continue
        if not soup:
            continue
        request_count += 1
        try:
            df = get_schedule_table(soup)
            df = process_schedule(df)
            df_list.append(df)
            print(f'Finished {month} request!')
        except:
            print(f'Error while processing {month}-{year}')
            continue
end = time.time()
print(f'Total time taken: {round(end-start)}s')
print(f'Total requests count: {request_count}')
print(f'Average Requests per Second: {round((end-start)/request_count)}')
full_df = pd.concat(df_list, axis=0)

if os.path.isfile('data/games_played.csv'):
    read_df = pd.read_csv('data/games_played.csv', index_col=0)
    final_df = pd.concat([read_df, full_df], axis=0).reset_index(
    ).drop_duplicates(subset='game_id')
    final_df.to_csv('data/games_played.csv')
else:
    full_df.to_csv('data/games_played.csv')

df_final = pd.read_csv('data/games_played.csv', index_col=0, parse_dates=[
                       'DateTime'], dtype={'DateStr': 'str'}).sort_values('DateTime')

# Get shot data using game schedule data
df_list = []
for i, x in enumerate(df_final['game_id']):
    lag = np.random.randint(4, 6)
    print(f'Cycle lag time: {lag}')
    time.sleep(lag)
    team = df_final.loc[df_final['game_id'] == x, 'Home_short'][0]
    date = df_final.loc[df_final['game_id'] == x,].index[0]
    year = '{:04d}'.format(date.year)
    month = '{:02d}'.format(date.month)
    day = '{:02d}'.format(date.day)
    print(f'Processing {x} request!')
    try:
        test_soup = request_soup_for_game(
            year=year, month=month, day=day, team=team)
        print(f'Successfully processed {x} request!')
    except Exception as e:
        print(f'Request failed: {e}')
    try:
        shot_area = get_shot_area(test_soup)
        game_meta = get_game_meta(test_soup)
        df = create_df(shot_area, game_meta)
        df['game_id'] = x
        df_list.append(df)
        print(f'Successfully processed {x} shots!')

    except Exception as e:
        print(f'Could not get and process shots for {x}: {e}')
pbp_all = pd.concat(df_list, axis=0)

pbp_all.to_parquet('data\play_by_play.parquet')


# TODO: use airflow to schedule daily requests
# TODO: schedule daily updates to SQL Server
