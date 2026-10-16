from pathlib import Path

from backend.db import initialise_database
from config import Config


if __name__ == "__main__":
    database_path = Path(Config.DATABASE_PATH)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    Path(Config.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    initialise_database(database_path)
    print(f"Initialised {database_path}")
