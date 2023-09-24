from pydantic import BaseModel
from datetime import datetime
from typing import Union, List


class PlayerBase(BaseModel):
    PlayerID: Union[int, None]
    PlayerName: Union[str, None]
    FromYear: Union[int, None] = None
    ToYear: Union[int, None] = None
    # PositionID: Union[int, None] = None
    Height: Union[str, None] = None
    Weight: Union[int, None] = None
    BirthDate: Union[datetime, None] = None
    College: Union[str, None] = None
    PositionName: Union[str, None] = None


class PlayersResponse(BaseModel):
    players: List[PlayerBase]


class ShotsTakenBase(BaseModel):
    # ShotID: Union[int, None] = None
    # PlayerID: Union[int, None] = None
    TimeLeft: Union[str, None]
    # TeamID: Union[int, None] = None
    TeamName: Union[str, None]
    ScoreStatus: Union[str, None]
    X_Shot_Pos: Union[int, None]
    Y_Shot_Pos: Union[int, None]
    Quarter: Union[str, None]
    ShotStatus: Union[str, None]
    FullText: Union[str, None]
    GameDate: Union[datetime, None]
    # GameID: Union[str, None] = None
    # ShotsHashID: Union[str, None] = None
    PlayerName: Union[str, None]
    PositionName: Union[str, None] = None
    Height: Union[str, None] = None
    Weight: Union[int, None] = None
    BirthDate: Union[datetime, None] = None
    College: Union[str, None] = None
    ArenaName: Union[str, None] = None
    Attendance: Union[int, None] = None
    VisitorPTS: Union[int, None] = None
    HomePTS: Union[int, None] = None
    # HomeTeamID: Union[int, None] = None
    # VisitorTeamID: Union[int, None] = None
    HomeTeamName: Union[str, None] = None
    VisitorTeamName: Union[str, None] = None


class ShotsResponse(BaseModel):
    shots: List[ShotsTakenBase]


class PositionBase(BaseModel):
    PositionID: int
    PositionName: str
    Description: str


class PositionsResponse(BaseModel):
    positions: List[PositionBase]


class TeamBase(BaseModel):
    TeamID: int
    TeamName: str
    TeamShort: str


class Arena(BaseModel):
    ArenaID: int
    ArenaName: str
    Capacity: int
    BuiltYear: int


class GamesPlayed(BaseModel):
    GameID: str
    DateTime: datetime
    HomeTeamID: int
    VisitorTeamID: int
    HomePTS: int
    VisitorPTS: int
    OT: str
    Attendance: int
    ArenaID: int
