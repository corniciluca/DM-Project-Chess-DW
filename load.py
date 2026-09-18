import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import argparse

def get_conn(args):
    return psycopg2.connect(
        host=args.host,
        port=args.port,
        database=args.db,
        user=args.user,
        password=args.password,
    )


def load_table(cur, table, df, conflict_cols=None):
    if df.empty:
        return
    cols = list(df.columns)
    sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES %s"
    
    rows = [tuple(x) for x in df.astype(object).where(pd.notna(df), None).to_numpy()]
    execute_values(cur, sql, rows, page_size=1000)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5432)
    parser.add_argument("--db", default="chess_dw")
    parser.add_argument("--user", default="postgres")
    parser.add_argument("--password", default="postgres")
    args = parser.parse_args()

    conn = get_conn(args)
    conn.autocommit = False
    with conn.cursor() as cur:
        dims = {
            "DATE": (pd.read_csv("data/dim_date.csv"), ["full_date"]),
            "PLAYER": (pd.read_csv("data/dim_player.csv"), ["username"]),
            "OPENING": (pd.read_csv("data/dim_opening.csv"), ["eco"]),
            "TERMINATION": (pd.read_csv("data/dim_termination.csv"), ["termination"]),
            "TIMECONTROL": (pd.read_csv("data/dim_timecontrol.csv"), ["base_seconds", "increment_sec"]),
            "TOURNAMENT": (pd.read_csv("data/dim_tournament.csv"), ["url"]),
            "GAME_URL": (pd.read_csv("data/dim_game_url.csv"), ["url"]),
        }
        for table, (df, keys) in dims.items():
            load_table(cur, table, df.drop(columns=["date_key"]) if table == "DATE" else df, keys)

        cur.execute("SELECT TO_CHAR(full_date, 'YYYYMMDD'), date_key FROM DATE")
        date_keys = dict(cur.fetchall())

        fact_game = pd.read_csv("data/fact_game.csv")
        fact_game["date_key"] = fact_game["date_key"].astype(str).map(date_keys)
        load_table(cur, "GAME", fact_game, ["game_url_key"])

        fact_rating = pd.read_csv("data/fact_player_rating.csv")
        fact_rating["date_key"] = fact_rating["date_key"].astype(str).map(date_keys)
        load_table(cur, "RATING_SNAPSHOT", fact_rating)
    conn.commit()

if __name__ == "__main__":
    main()