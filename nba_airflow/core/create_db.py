import hashlib
from sqlalchemy.ext.hybrid import hybrid_property
import os
from dataclasses import dataclass
from sqlalchemy import create_engine, text, Column, Integer, String, ForeignKey, DateTime, Table, MetaData
from sqlalchemy.orm import relationship, declarative_base
from sql_connector import DB

Base = declarative_base()


class Team(Base):
    __tablename__ = 'Team'
    TeamID = Column(Integer, primary_key=True, autoincrement=True)
    TeamName = Column(String, nullable=False)
    TeamShort = Column(String, nullable=False)

    # Relationships
    home_games = relationship(
        'GamesPlayed', backref='home_team', foreign_keys='GamesPlayed.HomeTeamID')
    visitor_games = relationship(
        'GamesPlayed', backref='visitor_team', foreign_keys='GamesPlayed.VisitorTeamID')
    shots = relationship('ShotsTaken', backref='team')


class Arena(Base):
    __tablename__ = 'Arena'
    ArenaID = Column(Integer, primary_key=True, autoincrement=True)
    ArenaName = Column(String, nullable=False)
    Capacity = Column(Integer)
    BuiltYear = Column(Integer)

    # Relationships
    games = relationship('GamesPlayed', backref='arena')


class Player(Base):
    __tablename__ = 'Player'
    PlayerID = Column(Integer, primary_key=True, autoincrement=True)
    PlayerName = Column(String, nullable=False)
    FromYear = Column(Integer)
    ToYear = Column(Integer)
    PositionID = Column(Integer, ForeignKey('Position.PositionID'))
    Height = Column(String)
    Weight = Column(Integer)
    BirthDate = Column(DateTime)
    College = Column(String)

    # Relationships
    shots = relationship('ShotsTaken', backref='player')


class Position(Base):
    __tablename__ = 'Position'
    PositionID = Column(Integer, primary_key=True, autoincrement=True)
    PositionName = Column(String, )
    Description = Column(String)

    # Relationships
    players = relationship('Player', backref='position')


class GamesPlayed(Base):
    __tablename__ = 'GamesPlayed'
    GameID = Column(String(30), primary_key=True)
    DateTime = Column(DateTime)
    VisitorTeamID = Column(Integer, ForeignKey('Team.TeamID'))
    HomeTeamID = Column(Integer, ForeignKey('Team.TeamID'))
    VisitorPTS = Column(Integer)
    HomePTS = Column(Integer)
    OT = Column(String(10))
    Attendance = Column(Integer)
    ArenaID = Column(Integer, ForeignKey('Arena.ArenaID'))

    # Relationships
    shots = relationship('ShotsTaken', backref='game')


class ShotsTaken(Base):
    __tablename__ = 'ShotsTaken'
    ShotID = Column(Integer, primary_key=True, autoincrement=True)
    PlayerID = Column(Integer, ForeignKey('Player.PlayerID'))
    TimeLeft = Column(String)
    TeamID = Column(Integer, ForeignKey('Team.TeamID'))
    ScoreStatus = Column(String(4))
    X_Shot_Pos = Column(Integer)
    Y_Shot_Pos = Column(Integer)
    Quarter = Column(String)
    ShotStatus = Column(String)
    FullText = Column(String)
    GameDate = Column(DateTime)
    GameID = Column(String(30), ForeignKey('GamesPlayed.GameID'))

    @hybrid_property
    def ShotsHashID(self):
        # Concatenate the relevant fields to form a unique string
        unique_string = f"{self.ShotID}{self.PlayerID}{self.TimeLeft}{self.TeamID}{self.ScoreStatus}{self.X_Shot_Pos}{self.Y_Shot_Pos}{self.Quarter}{self.ShotStatus}{self.FullText}{self.GameDate}{self.GameID}"

        # Compute the SHA1 hash of the unique string
        return hashlib.sha1(unique_string.encode()).hexdigest()


if __name__ == "__main__":
    db = DB(db_name="NBA")
    if db.test_connection():
        Base.metadata.drop_all(db.engine)
        Base.metadata.create_all(db.engine)
        print("Tables created successfully!")
    else:
        print("Failed to connect to the database.")
