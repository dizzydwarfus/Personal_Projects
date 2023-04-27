# Next Step: Build a UI using ttkbootstrap to have entry/dropdown for all parameters and automatically show in table (mimic website but have option to store into SQL database)
import datetime as dt
import sys
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.validation import add_regex_validation
from nba_api import NBA

nba_info = NBA()
print(nba_info.player_shot_locations_columns)


class App(ttk.Window):
    def __init__(self, themename):
        super().__init__(themename=themename)

        self.title('NBA Stats')
        self.colors = self.style.colors
        self.theme_list = self.style.theme_names()
        self.create_switch(row=24, column=0, padx=10, pady=10, sticky=NSEW)
        self.create_menu(row=25, col=0)

    def create_switch(self, **kwargs):
        def toggle_mode():
            if mode_switch.instate(["selected"]):
                self.style.theme_use("superhero")
            else:
                self.style.theme_use("solar")
        mode_switch = ttk.Checkbutton(
            self, text='Mode', style='Roundtoggle.Toolbutton', command=toggle_mode)
        mode_switch.grid(**kwargs)

    def create_radio_buttons(self, **kwargs):
        btns_frame = ttk.Frame(self)
        btns_frame.grid(**kwargs)

        def my_upd():
            self.style.theme_use(my_str.get())

        my_str = ttk.StringVar(value=self.style.theme_use())

        for values in self.theme_list:
            b = ttk.Radiobutton(btns_frame, text=values, value=values,
                                variable=my_str, command=lambda: my_upd())
            b.pack(side=LEFT, padx=5, pady=5)

    def create_menu(self, row, col):
        def my_upd():
            self.style.theme_use(my_str.get())

        my_str = ttk.StringVar(value=self.style.theme_use())

        menu_field_container = ttk.Frame(self)
        menu_field_container.grid(sticky=EW, pady=5, row=row, column=col)

        menu_label = ttk.Label(master=menu_field_container,
                               text='Select a theme: ', )
        menu_label.pack(side=LEFT, padx=12, pady=10)

        menu = ttk.Menubutton(master=menu_field_container,
                              textvariable=my_str)
        menu.pack(side=LEFT, padx=12, pady=10)

        menu_input = ttk.Menu(menu)
        for x in self.theme_list:
            menu_input.add_radiobutton(
                label=x, variable=my_str, value=x, command=lambda: my_upd())

        menu['menu'] = menu_input
        return menu_input


# Separate components into frames

# Component 1 - Parameters Input


class ParamsInput(ttk.Frame):
    def __init__(self, master_window):
        super().__init__(master_window)
        self.grid(row=0, column=0, sticky=EW)
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
        instruction.grid(sticky=EW, pady=10, row=0, column=0)

        self.create_form_entry('Endpoint', self.endpoint, 1, 0)
        self.create_form_entry('College', self.college, 2, 0)
        self.create_form_entry('Conference', self.conference, 3, 0)
        self.create_form_entry('Country', self.country, 4, 0)
        self.create_form_entry('DateFrom', self.DateFrom, 5, 0)
        self.create_form_entry('DateTo', self.DateTo, 6, 0)
        self.create_form_entry('DistanceRange', self.distance_range, 7, 0)
        self.create_form_entry('Division', self.division, 8, 0)
        self.create_form_entry('DraftPick', self.draft_pick, 9, 0)
        self.create_form_entry('DraftYear', self.draft_year, 10, 0)
        self.create_form_entry('GameScope', self.game_scope, 11, 0)
        self.create_form_entry('GameSegment', self.game_segment, 12, 0)
        self.create_form_entry('Height', self.height, 13, 0)
        self.create_form_entry('LastNGames', self.last_n_games, 14, 0)
        self.create_form_entry('LeagueID', self.league_ID, 15, 0)
        self.create_form_entry('Location', self.location, 16, 0)
        self.create_form_entry('MeasureType', self.measure_type, 17, 0)
        self.create_form_entry('Month', self.month, 18, 0)
        self.create_form_entry('OpponentTeamID', self.opponent_team_ID, 1, 1)
        self.create_form_entry('Outcome', self.outcome, 2, 1)
        self.create_form_entry('PORound', self.po_round, 3, 1)
        self.create_form_entry('PaceAdjust', self.pace_adjust, 4, 1)
        self.create_form_entry('PerMode', self.per_mode, 5, 1)
        self.create_form_entry('Period', self.period, 6, 1)
        self.create_form_entry(
            'PlayerExperience', self.player_experience, 7, 1)
        self.create_form_entry('PlayerPosition', self.player_position, 8, 1)
        self.create_form_entry('PlusMinus', self.plus_minus, 9, 1)
        self.create_form_entry('Rank', self.rank, 10, 1)
        self.create_form_entry('Season', self.season, 11, 1)
        self.create_form_entry('SeasonSegment', self.season_segment, 12, 1)
        self.create_form_entry('SeasonType', self.season_type, 13, 1)
        self.create_form_entry('StatCategory', self.stat_category, 14, 1)
        self.create_form_entry('ShotClockRange', self.shot_clock_range, 15, 1)
        self.create_form_entry('StarterBench', self.starter_bench, 16, 1)
        self.create_form_entry('TeamID', self.team_ID, 17, 1)
        self.create_form_entry('VsConference', self.vs_conference, 18, 1)
        self.create_form_entry('VsDivision', self.vs_division, 19, 1)
        self.create_form_entry('Weight', self.weight, 19, 0)
        self.create_form_entry('AheadBehind', self.ahead_behind, 20, 1)
        self.create_form_entry('ActiveFlag', self.active_flag, 20, 0)
        self.create_form_entry('ClutchTime', self.clutch_time, 21, 1)
        self.create_form_entry('PointDiff', self.point_diff, 21, 0)

        self.create_menu(self.endpoint, ['/leaguedashplayerstats?', '/playerestimatedmetrics?',
                         '/leaguedashplayerclutch?', '/leagueleaders?', '/playergamelogs?', '/leaguedashplayershotlocations?'], 22, 0)

        self.create_separator(row=23, column=0, columnspan=2,
                              padx=5, pady=10, sticky=NSEW)

    def create_form_entry(self, label: str, variable, row: int, col: int):
        form_field_container = ttk.Frame(self)
        form_field_container.grid(sticky=NSEW, pady=5, row=row, column=col)

        form_field_label = ttk.Label(
            master=form_field_container, text=label, width=15)
        form_field_label.pack(side=LEFT, padx=12)

        form_input = ttk.Entry(
            master=form_field_container, textvariable=variable)
        form_input.pack(side=LEFT, padx=5, fill=X, expand=YES)

        add_regex_validation(form_input, r'^[a-zA-Z0-9_?\s]*$')

        return form_input

    def create_menu(self, variable, options, row, col):
        menu_field_container = ttk.Frame(self)
        menu_field_container.grid(sticky=EW, pady=5, row=row, column=col)

        menu = ttk.Menubutton(master=menu_field_container,
                              textvariable=variable)
        menu.pack(side=LEFT, padx=12)

        menu_input = ttk.Menu(menu)
        for x in options:
            menu_input.add_radiobutton(label=x, variable=variable)

        menu['menu'] = menu_input
        return menu_input

    def create_separator(self, **kwargs):
        separator = ttk.Separator(self)
        separator.grid(**kwargs)


# Component 2 - TableView Frame


coldata = [
    {"text": "LicenseNumber", "stretch": False},
    "CompanyName",
    {"text": "UserCount", "stretch": False},
]

rowdata = [
    ('A123', 'IzzyCo', 12),
    ('A136', 'Kimdee Inc.', 45),
    ('A158', 'Farmadding Co.', 36),
]


class TableFrame(ttk.Frame):
    def __init__(self, master_window):
        super().__init__(master_window)

        self.grid(row=0, column=1, sticky=NSEW)

        options = {'padx': 5, 'pady': 5}

        table = Tableview(master=self, coldata=coldata, rowdata=rowdata, paginated=True,
                          searchable=True, bootstyle=PRIMARY,)
        table.pack(fill=BOTH, expand=YES, padx=10, pady=10)


if __name__ == "__main__":
    app = App(themename='solar')
    frame = ParamsInput(app)
    table = TableFrame(app)
    app.mainloop()
