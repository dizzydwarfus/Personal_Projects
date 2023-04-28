from typing import List, Tuple, Dict
from dataclasses import dataclass, field


def default_headers() -> Dict[str, str]:
    return {'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'stats.nba.com',
            'Origin': 'https://www.nba.com',
            'Referer': 'https://www.nba.com/',
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': "Windows",
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36', }


def player_shots_columns() -> List[str]:
    index = [
        ("", 'PLAYER_ID'),
        ("", 'PLAYER_NAME'),
        ("", 'TEAM_ID'),
        ("", 'TEAM_ABBREVIATION'),
        ("", 'AGE'),
        ("", 'NICKNAME'),
        ('Less Than 5 ft.',    'FGM'),
        ('Less Than 5 ft.',    'FGA'),
        ('Less Than 5 ft.', 'FG_PCT'),
        ('5-9 ft.',    'FGM'),
        ('5-9 ft.',    'FGA'),
        ('5-9 ft.', 'FG_PCT'),
        ('10-14 ft.',    'FGM'),
        ('10-14 ft.',    'FGA'),
        ('10-14 ft.', 'FG_PCT'),
        ('15-19 ft.',    'FGM'),
        ('15-19 ft.',    'FGA'),
        ('15-19 ft.', 'FG_PCT'),
        ('20-24 ft.',    'FGM'),
        ('20-24 ft.',    'FGA'),
        ('20-24 ft.', 'FG_PCT'),
        ('25-29 ft.',    'FGM'),
        ('25-29 ft.',    'FGA'),
        ('25-29 ft.', 'FG_PCT'),
        ('30-34 ft.',    'FGM'),
        ('30-34 ft.',    'FGA'),
        ('30-34 ft.', 'FG_PCT'),
        ('35-39 ft.',    'FGM'),
        ('35-39 ft.',    'FGA'),
        ('35-39 ft.', 'FG_PCT'),
        ('40+ ft.',    'FGM'),
        ('40+ ft.',    'FGA'),
        ('40+ ft.', 'FG_PCT'),
        ("", "Year"),
    ]
    return index


@dataclass
class NBA:
    headers: Dict[str, str] = field(default_factory=default_headers)
    url: str = "https://stats.nba.com/stats/"
    player_shot_locations_columns: List[str] = field(
        default_factory=player_shots_columns)
