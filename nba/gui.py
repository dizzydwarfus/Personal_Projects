# Next Step: Build a UI using ttkbootstrap to have entry/dropdown for all parameters and automatically show in table (mimic website but have option to store into SQL database)
import datetime as dt

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.validation import add_regex_validation

url = "https://stats.nba.com/stats/"

headers = {
    'Accept': '*/*',
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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
}


class App(ttk.Window):
    def __init__(self):
        super().__init__()

        self.title('NBA Stats')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=4)

# Separate components into frames

# Component 1 - Parameters Input


class ParamsInput(ttk.Frame):
    def __init__(self, master_window):
        super().__init__(master_window)
        self.grid(row=0, column=0, sticky=W)
        self.endpoint = ttk.StringVar(value="leaguedashplayershotlocations?")
        self.college = ttk.StringVar(value="")
        self.conference = ttk.StringVar(value="")
        self.country = ttk.StringVar(value="")
        self.DateFrom = ttk.StringVar(value="")
        self.DateTo = ttk.StringVar(value="")
        self.distance_range = ttk.StringVar(value="")
        self.division = ttk.StringVar(value="")
        self.draft_pick = ttk.StringVar(value="")
        self.draft_year = ttk.StringVar(value="")
        self.game_scope = ttk.StringVar(value="")
        self.game_segment = ttk.StringVar(value="")
        self.height = ttk.StringVar(value="")
        self.last_n_games = ttk.StringVar(value="0")
        self.league_ID = ttk.StringVar(value="00")
        self.location = ttk.StringVar(value="")
        self.measure_type = ttk.StringVar(value="Base")
        self.month = ttk.StringVar(value="0")
        self.opponent_team_ID = ttk.StringVar(value="0")
        self.outcome = ttk.StringVar(value="")
        self.po_round = ttk.StringVar(value="")
        self.pace_adjust = ttk.StringVar(value="")
        self.per_mode = ttk.StringVar(value="")
        self.period = ttk.StringVar(value="0")
        self.player_experience = ttk.StringVar(value="")
        self.player_position = ttk.StringVar(value="")
        self.plus_minus = ttk.StringVar(value="N")
        self.rank = ttk.StringVar(value="N")
        self.season = ttk.StringVar(value=f"{dt.date.today().year}")
        self.season_segment = ttk.StringVar(value="")
        self.season_type = ttk.StringVar(value="Regular Season")
        self.stat_category = ttk.StringVar(value="")
        self.shot_clock_range = ttk.StringVar(value="")
        self.starter_bench = ttk.StringVar(value="")
        self.team_ID = ttk.StringVar(value="0")
        self.vs_conference = ttk.StringVar(value="")
        self.vs_division = ttk.StringVar(value="")
        self.weight = ttk.StringVar(value="")
        self.ahead_behind = ttk.StringVar(value="")
        self.active_flag = ttk.StringVar(value="")
        self.clutch_time = ttk.StringVar(value="")
        self.point_diff = ttk.StringVar(value="")

        self.data = []
        self.colors = master_window.style.colors

        instruction_text = "Please enter parameters to query from www.nba.com/stats: "
        instruction = ttk.Label(self, text=instruction_text, width=60)
        instruction.pack(fill=X, pady=10)

        self.create_form_entry('Endpoint', self.endpoint)
        self.create_form_entry('College', self.college)
        self.create_form_entry('Conference', self.conference)
        self.create_form_entry('Country', self.country)
        self.create_form_entry('DateFrom', self.DateFrom)
        self.create_form_entry('DateTo', self.DateTo)
        self.create_form_entry('DistanceRange', self.distance_range)
        self.create_form_entry('Division', self.division)
        self.create_form_entry('DraftPick', self.draft_pick)
        self.create_form_entry('DraftYear', self.draft_year)
        self.create_form_entry('GameScope', self.game_scope)
        self.create_form_entry('GameSegment', self.game_segment)
        self.create_form_entry('Height', self.height)
        self.create_form_entry('LastNGames', self.last_n_games)
        self.create_form_entry('LeagueID', self.league_ID)
        self.create_form_entry('Location', self.location)
        self.create_form_entry('MeasureType', self.measure_type)
        self.create_form_entry('Month', self.month)
        self.create_form_entry('OpponentTeamID', self.opponent_team_ID)
        self.create_form_entry('Outcome', self.outcome)
        self.create_form_entry('PORound', self.po_round)
        self.create_form_entry('PaceAdjust', self.pace_adjust)
        self.create_form_entry('PerMode', self.per_mode)
        self.create_form_entry('Period', self.period)
        self.create_form_entry('PlayerExperience', self.player_experience)
        self.create_form_entry('PlayerPosition', self.player_position)
        self.create_form_entry('PlusMinus', self.plus_minus)
        self.create_form_entry('Rank', self.rank)
        self.create_form_entry('Season', self.season)
        self.create_form_entry('SeasonSegment', self.season_segment)
        self.create_form_entry('SeasonType', self.season_type)
        self.create_form_entry('StatCategory', self.stat_category)
        self.create_form_entry('ShotClockRange', self.shot_clock_range)
        self.create_form_entry('StarterBench', self.starter_bench)
        self.create_form_entry('TeamID', self.team_ID)
        self.create_form_entry('VsConference', self.vs_conference)
        self.create_form_entry('VsDivision', self.vs_division)
        self.create_form_entry('Weight', self.weight)
        self.create_form_entry('AheadBehind', self.ahead_behind)
        self.create_form_entry('ActiveFlag', self.active_flag)
        self.create_form_entry('ClutchTime', self.clutch_time)
        self.create_form_entry('PointDiff', self.point_diff)

        self.create_menu(self.endpoint, ['/leaguedashplayerstats?', '/playerestimatedmetrics?',
                         '/leaguedashplayerclutch?', '/leagueleaders?', '/playergamelogs?', '/leaguedashplayershotlocations?'])

    def create_form_entry(self, label, variable):
        form_field_container = ttk.Frame(self)
        form_field_container.pack(fill=X, expand=YES, pady=5)

        form_field_label = ttk.Label(
            master=form_field_container, text=label, width=15)
        form_field_label.pack(side=LEFT, padx=12)

        form_input = ttk.Entry(
            master=form_field_container, textvariable=variable)
        form_input.pack(side=LEFT, padx=5, fill=X, expand=YES)

        add_regex_validation(form_input, r'^[a-zA-Z0-9_]*$')

        return form_input

    def create_menu(self, variable, options):
        menu_field_container = ttk.Frame(self)
        menu_field_container.pack(fill=X, expand=YES, pady=5)

        menu = ttk.Menubutton(master=menu_field_container,
                              textvariable=variable)
        menu.pack(side=LEFT, padx=12)

        menu_input = ttk.Menu(menu)
        for x in options:
            menu_input.add_radiobutton(label=x, variable=variable)

        menu['menu'] = menu_input
        return menu_input


# Component 2 - TableView Frame

class TableFrame(ttk.Frame):
    def __init__(self, master_window):
        super().__init__(master_window)
        self.pack(fill=BOTH, expand=YES)

        options = {'padx': 5, 'pady': 5}


if __name__ == "__main__":
    app = App()
    frame = ParamsInput(app)
    app.mainloop()
