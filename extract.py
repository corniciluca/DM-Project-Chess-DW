import argparse
import csv
import json
import os
import re
import sys
import time

import requests

csv.field_size_limit(sys.maxsize)

os.makedirs("data", exist_ok=True)

GAMES_OUT   = "data/games_raw.csv"
ECO_OUT     = "data/eco_raw.csv"
PLAYERS_OUT = "data/players_raw.csv"

GAME_FIELDS = [
    "Event", "Site", "UTCDate", "UTCTime", "White", "Black",
    "Result", "WhiteElo", "BlackElo", "WhiteRatingDiff", "BlackRatingDiff",
    "ECO", "Opening", "TimeControl", "Termination", "Moves",
]

def parse_pgn(path: str, limit: int) -> list[dict]:
    import io
    import zstandard as zstd

    games   = []
    current = {}
    moves   = []

    if path.endswith(".zst"):
        raw_fh = open(path, "rb")
        ctx    = zstd.ZstdDecompressor()
        stream = ctx.stream_reader(raw_fh)
        fh     = io.TextIOWrapper(stream, encoding="utf-8")
    else:
        fh = open(path, "r", encoding="utf-8")

    with fh:
        for raw_line in fh:
            line = raw_line.strip()

            if line.startswith("["):
                # tag line: [Key "Value"]
                m = re.match(r'\[(\w+)\s+"(.*)"\]', line)
                if m:
                    current[m.group(1)] = m.group(2)

            elif line and not line.startswith("["):
                # move text line
                moves.append(line)

            elif line == "" and current:
                # blank line = end of game record
                if moves:
                    move_str = " ".join(moves)
                    # count moves: tokens like "1." "e4" "e5" "2." ...
                    # move number tokens match \d+\.
                    current["Moves"] = move_str
                    tokens = move_str.split()
                    num_moves = sum(1 for t in tokens
                                   if not re.match(r'^\d+\.', t)
                                   and not t.startswith('{')
                                   and t not in ('1-0','0-1','1/2-1/2','*'))
                    current["_num_moves"] = num_moves // 2

                games.append({f: current.get(f, "") for f in GAME_FIELDS + ["_num_moves"]})
                current = {}
                moves   = []

                if len(games) >= limit:
                    break

    return games


def save_games(games: list[dict], path: str):
    fields = GAME_FIELDS + ["_num_moves"]
    merge_csv(path, fields, games, key=lambda row: row.get("Site", "").strip())



def merge_csv(path: str, fields: list[str], incoming: list[dict], key):
    existing = []
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            existing = list(csv.DictReader(f))

    positions = {}
    merged = []
    for row in existing + incoming:
        row = {field: row.get(field, "") for field in fields}
        row_key = key(row)
        if not row_key:
            row_key = "__row__" + json.dumps(row, sort_keys=True)
        if row_key in positions:
            merged[positions[row_key]] = row
        else:
            positions[row_key] = len(merged)
            merged.append(row)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(merged)


def extract_eco(src: str, dst: str):
    import pandas as pd
    if src.endswith(".parquet"):
        df = pd.read_parquet(src)
    else:
        df = pd.read_csv(src, dtype=str)

    col_map = {}
    for c in df.columns:
        if c.lower() in ("eco_volume", "eco-volume", "ecovolume"):
            col_map[c] = "eco-volume"
        elif c.lower() == "eco":
            col_map[c] = "eco"
        elif c.lower() == "name":
            col_map[c] = "name"
    df = df.rename(columns=col_map)

    if "eco-volume" not in df.columns:
        df["eco-volume"] = df["eco"].str[0]

    rows = df.to_dict(orient="records")
    fields = list(df.columns)
    merge_csv(dst, fields, rows, key=lambda row: str(row.get("eco", "")).strip())

LICHESS_API = "https://lichess.org/api/users"

PLAYER_FIELDS = [
    "username", "title", "country_code"
]

def fetch_players(usernames: list[str], dst: str):
    BATCH      = 300
    SLEEP_SEC  = 2.0
    MAX_RETRY  = 3
    rows       = []

    for i in range(0, len(usernames), BATCH):
        batch = usernames[i:i + BATCH]

        for attempt in range(MAX_RETRY):
            try:
                resp = requests.post(
                    LICHESS_API,
                    data=",".join(batch),
                    headers={
                        "Content-Type": "text/plain",
                        "Accept":       "application/json",
                    },
                    timeout=30,
                )
                if resp.status_code == 429:
                    wait = 60 * (attempt + 1)
                    print(f"\n[extract] rate limit {wait}s …")
                    time.sleep(wait)
                    continue
                resp.raise_for_status()

                # POST /api/users returns a JSON ARRAY
                users = resp.json()          # list of user dicts
                for d in users:
                    rows.append({
                        "username":     d.get("username", ""),
                        "title":        d.get("title", ""),
                        "country_code": d.get("profile", {}).get("flag", ""),
                        "created_at":   d.get("createdAt", ""),
                    })
                break

            except Exception as e:
                print(f"\n[extract] API error batch {i//BATCH} attempt {attempt}: {e}")
                if attempt < MAX_RETRY - 1:
                    time.sleep(10)

        time.sleep(SLEEP_SEC)
        done = min(i + BATCH, len(usernames))
        print(f"[extract] players fetched: {done:,}/{len(usernames):,}", end="\r")

    merge_csv(
        dst,
        PLAYER_FIELDS,
        rows,
        key=lambda row: row.get("username", "").strip().lower(),
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pgn",   required=True)
    parser.add_argument("--eco",   required=True)
    parser.add_argument("--limit", type=int, default=100_000)
    args = parser.parse_args()

    print("[extract] PGN")
    games = parse_pgn(args.pgn, args.limit)
    save_games(games, GAMES_OUT)

    print("[extract] ECO")
    extract_eco(args.eco, ECO_OUT)

    usernames = list({g["White"] for g in games} | {g["Black"] for g in games})
    usernames = [u for u in usernames if u]

    print(f"[extract] Fetching {len(usernames):,} player profiles")
    fetch_players(usernames, PLAYERS_OUT)

    print("[extract] Done")


if __name__ == "__main__":
    main()