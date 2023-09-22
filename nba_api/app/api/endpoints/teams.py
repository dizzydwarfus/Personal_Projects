from fastapi import APIRouter, Depends, HTTPException
from ...database.sql_connector import DB
from ...database.db import get_db
from sqlalchemy import text

router = APIRouter()
