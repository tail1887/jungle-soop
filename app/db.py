from __future__ import annotations

from urllib.parse import urlparse

from flask import Flask
from pymongo import MongoClient
from pymongo.database import Database


def _extract_db_name_from_uri(uri: str) -> str:
    parsed = urlparse(uri)
    name = parsed.path.lstrip("/")
    return name or "jungle_soop"


def init_mongo(app: Flask) -> None:
    uri = app.config["MONGO_URI"]
    app.config.setdefault("MONGO_DB_NAME", _extract_db_name_from_uri(uri))

    # Keep client creation lightweight; actual I/O happens on first operation.
    client = MongoClient(uri, serverSelectionTimeoutMS=2000, connectTimeoutMS=2000)
    app.extensions["mongo_client"] = client


def get_mongo_client(app: Flask) -> MongoClient:
    return app.extensions["mongo_client"]


def get_database(app: Flask) -> Database:
    client = get_mongo_client(app)
    db_name = app.config["MONGO_DB_NAME"]
    return client[db_name]
