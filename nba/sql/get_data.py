import pandas as pd
import datetime as dt
import requests
from bs4 import BeautifulSoup, Tag
import plotly.graph_objects as go
import re


# 20 requests per minute maximum
# change /shot-chart/YYYYMMDD0TEAM.html to get games on different days
def request_soup_for_game(year: str, month: str, day: str, team: str):
    url = f'https://www.basketball-reference.com/boxscores/shot-chart/{year}{month}{day}0{team}.html'
    page = requests.get(url=url)
    soup = BeautifulSoup(page.content, "html.parser")
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
    location = re.findall(
        r'(?=\d{4})(\w+\s\w+,.+,\s.+)(?=\nLogos)', game_meta)[0][4:].split(',')
    arena = location[0].strip()
    city = location[1].strip()
    state = location[2].strip()

    df['arena'] = arena
    df['city'] = city
    df['state'] = state

    return df


soup = request_soup_for_game('2023', '05', '02', 'GSW')
shot_area = get_shot_area(soup)
game_meta = get_game_meta(soup)
df = create_df(shot_area, game_meta)
get_customdata(df)
