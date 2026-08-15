from pathlib import Path

import duckdb
import pandas as pd


DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "lh_nautical.duckdb"
)


def get_connection():
    return duckdb.connect(
        str(DB_PATH),
        read_only=True
    )


def query(sql: str) -> pd.DataFrame:
    con = get_connection()

    try:
        return con.execute(sql).df()
    finally:
        con.close()