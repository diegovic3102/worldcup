import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL


load_dotenv()


def build_database_url():
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return database_url

    return URL.create(
        "postgresql+psycopg",
        username=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD") or None,
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=int(os.getenv("PGPORT", "5432")),
        database=os.getenv("PGDATABASE", "sucesores-worldcup"),
    )


class Config:
    SQLALCHEMY_DATABASE_URI = build_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
