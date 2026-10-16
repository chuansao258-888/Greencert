from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")


class Config:
    APP_ORIGIN = os.getenv("APP_ORIGIN", "http://127.0.0.1:5000").rstrip("/")
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
    RPC_URL = os.getenv("RPC_URL", "")
    CHAIN_ID = int(os.getenv("CHAIN_ID", "11155111"))
    DATABASE_PATH = Path(os.getenv("DATABASE_PATH", ROOT_DIR / "instance" / "greencert.db"))
    UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", ROOT_DIR / "instance" / "uploads"))
    DEPLOYMENT_FILE = Path(os.getenv("DEPLOYMENT_FILE", ROOT_DIR / "deployment.json"))
    COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
