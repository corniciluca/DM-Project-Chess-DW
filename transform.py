import re
import pandas as pd
import numpy as np
import os

os.makedirs("data", exist_ok=True)



COUNTRY_MAP = {
    "US": ("United States",    "North America"),
    "DE": ("Germany",          "Europe"),
    "FR": ("France",           "Europe"),
    "RU": ("Russia",           "Europe"),
    "IN": ("India",            "Asia"),
    "CN": ("China",            "Asia"),
    "BR": ("Brazil",           "South America"),
    "GB": ("United Kingdom",   "Europe"),
    "UA": ("Ukraine",          "Europe"),
    "ES": ("Spain",            "Europe"),
    "IT": ("Italy",            "Europe"),
    "NL": ("Netherlands",      "Europe"),
    "PL": ("Poland",           "Europe"),
    "AR": ("Argentina",        "South America"),
    "TR": ("Turkey",           "Europe"),
    "IR": ("Iran",             "Asia"),
    "EG": ("Egypt",            "Africa"),
    "NG": ("Nigeria",          "Africa"),
    "AU": ("Australia",        "Oceania"),
    "CA": ("Canada",           "North America"),
    "MX": ("Mexico",           "North America"),
    "JP": ("Japan",            "Asia"),
    "KR": ("South Korea",      "Asia"),
    "SE": ("Sweden",           "Europe"),
    "NO": ("Norway",           "Europe"),
    "FI": ("Finland",          "Europe"),
    "CZ": ("Czech Republic",   "Europe"),
    "HU": ("Hungary",          "Europe"),
    "RO": ("Romania",          "Europe"),
    "GR": ("Greece",           "Europe"),
    "PT": ("Portugal",         "Europe"),
    "AZ": ("Azerbaijan",       "Asia"),
    "GE": ("Georgia",          "Asia"),
    "AM": ("Armenia",          "Asia"),
    "IL": ("Israel",           "Asia"),
    "CU": ("Cuba",             "North America"),
    "VN": ("Vietnam",          "Asia"),
    "PH": ("Philippines",      "Asia"),
    "ID": ("Indonesia",        "Asia"),
    "ZA": ("South Africa",     "Africa"),
    "PF": ("French Polynesia", "Oceania"),
    "AD": ("Andorra", "Europe"), "AE": ("United Arab Emirates", "Asia"),
    "AF": ("Afghanistan", "Asia"), "AG": ("Antigua and Barbuda", "North America"),
    "AI": ("Anguilla", "North America"), "AL": ("Albania", "Europe"),
    "AO": ("Angola", "Africa"), "AQ": ("Antarctica", "Antarctica"),
    "AS": ("American Samoa", "Oceania"), "AT": ("Austria", "Europe"),
    "AW": ("Aruba", "North America"), "BA": ("Bosnia and Herzegovina", "Europe"),
    "BB": ("Barbados", "North America"), "BD": ("Bangladesh", "Asia"),
    "BE": ("Belgium", "Europe"), "BF": ("Burkina Faso", "Africa"),
    "BG": ("Bulgaria", "Europe"), "BH": ("Bahrain", "Asia"),
    "BI": ("Burundi", "Africa"), "BJ": ("Benin", "Africa"),
    "BM": ("Bermuda", "North America"), "BN": ("Brunei", "Asia"),
    "BO": ("Bolivia", "South America"), "BQ": ("Caribbean Netherlands", "North America"),
    "BS": ("Bahamas", "North America"), "BT": ("Bhutan", "Asia"),
    "BV": ("Bouvet Island", "Antarctica"), "BW": ("Botswana", "Africa"),
    "BY": ("Belarus", "Europe"), "BZ": ("Belize", "North America"),
    "CD": ("Democratic Republic of the Congo", "Africa"), "CF": ("Central African Republic", "Africa"),
    "CG": ("Republic of the Congo", "Africa"), "CH": ("Switzerland", "Europe"),
    "CI": ("Cote d'Ivoire", "Africa"), "CK": ("Cook Islands", "Oceania"),
    "CL": ("Chile", "South America"), "CM": ("Cameroon", "Africa"),
    "CO": ("Colombia", "South America"), "CR": ("Costa Rica", "North America"),
    "CV": ("Cape Verde", "Africa"), "CX": ("Christmas Island", "Oceania"),
    "CY": ("Cyprus", "Asia"), "DJ": ("Djibouti", "Africa"),
    "DK": ("Denmark", "Europe"), "DM": ("Dominica", "North America"),
    "DO": ("Dominican Republic", "North America"), "DZ": ("Algeria", "Africa"),
    "EC": ("Ecuador", "South America"), "EE": ("Estonia", "Europe"),
    "EH": ("Western Sahara", "Africa"), "ER": ("Eritrea", "Africa"),
    "ET": ("Ethiopia", "Africa"), "EU": ("European Union", "Europe"),
    "FJ": ("Fiji", "Oceania"), "FK": ("Falkland Islands", "South America"),
    "FM": ("Micronesia", "Oceania"), "FO": ("Faroe Islands", "Europe"),
    "GA": ("Gabon", "Africa"), "GD": ("Grenada", "North America"),
    "GF": ("French Guiana", "South America"), "GG": ("Guernsey", "Europe"),
    "GH": ("Ghana", "Africa"), "GI": ("Gibraltar", "Europe"),
    "GL": ("Greenland", "North America"), "GM": ("Gambia", "Africa"),
    "GN": ("Guinea", "Africa"), "GP": ("Guadeloupe", "North America"),
    "GQ": ("Equatorial Guinea", "Africa"), "GS": ("South Georgia and the South Sandwich Islands", "Antarctica"),
    "GT": ("Guatemala", "North America"), "GW": ("Guinea-Bissau", "Africa"),
    "GY": ("Guyana", "South America"), "HK": ("Hong Kong", "Asia"),
    "HM": ("Heard Island and McDonald Islands", "Antarctica"), "HN": ("Honduras", "North America"),
    "HR": ("Croatia", "Europe"), "HT": ("Haiti", "North America"),
    "IE": ("Ireland", "Europe"), "IM": ("Isle of Man", "Europe"),
    "IO": ("British Indian Ocean Territory", "Asia"), "IQ": ("Iraq", "Asia"),
    "IS": ("Iceland", "Europe"), "JE": ("Jersey", "Europe"),
    "JM": ("Jamaica", "North America"), "JO": ("Jordan", "Asia"),
    "KE": ("Kenya", "Africa"), "KG": ("Kyrgyzstan", "Asia"),
    "KI": ("Kiribati", "Oceania"), "KM": ("Comoros", "Africa"),
    "KN": ("Saint Kitts and Nevis", "North America"), "KP": ("North Korea", "Asia"),
    "KW": ("Kuwait", "Asia"), "KY": ("Cayman Islands", "North America"),
    "KZ": ("Kazakhstan", "Asia"), "LA": ("Laos", "Asia"),
    "LB": ("Lebanon", "Asia"), "LC": ("Saint Lucia", "North America"),
    "LI": ("Liechtenstein", "Europe"), "LK": ("Sri Lanka", "Asia"),
    "LR": ("Liberia", "Africa"), "LS": ("Lesotho", "Africa"),
    "LT": ("Lithuania", "Europe"), "LU": ("Luxembourg", "Europe"),
    "LV": ("Latvia", "Europe"), "LY": ("Libya", "Africa"),
    "MA": ("Morocco", "Africa"), "MC": ("Monaco", "Europe"),
    "MD": ("Moldova", "Europe"), "ME": ("Montenegro", "Europe"),
    "MG": ("Madagascar", "Africa"), "MH": ("Marshall Islands", "Oceania"),
    "MK": ("North Macedonia", "Europe"), "ML": ("Mali", "Africa"),
    "MM": ("Myanmar", "Asia"), "MN": ("Mongolia", "Asia"),
    "MO": ("Macao", "Asia"), "MQ": ("Martinique", "North America"),
    "MR": ("Mauritania", "Africa"), "MS": ("Montserrat", "North America"),
    "MT": ("Malta", "Europe"), "MU": ("Mauritius", "Africa"),
    "MV": ("Maldives", "Asia"), "MW": ("Malawi", "Africa"),
    "MZ": ("Mozambique", "Africa"), "NA": ("Namibia", "Africa"),
    "NC": ("New Caledonia", "Oceania"), "NE": ("Niger", "Africa"),
    "NF": ("Norfolk Island", "Oceania"), "NI": ("Nicaragua", "North America"),
    "NP": ("Nepal", "Asia"), "NR": ("Nauru", "Oceania"),
    "NU": ("Niue", "Oceania"), "NZ": ("New Zealand", "Oceania"),
    "OM": ("Oman", "Asia"), "PA": ("Panama", "North America"),
    "PE": ("Peru", "South America"), "PG": ("Papua New Guinea", "Oceania"),
    "PK": ("Pakistan", "Asia"), "PN": ("Pitcairn", "Oceania"),
    "PR": ("Puerto Rico", "North America"), "PS": ("Palestine", "Asia"),
    "PW": ("Palau", "Oceania"), "PY": ("Paraguay", "South America"),
    "QA": ("Qatar", "Asia"), "RE": ("Reunion", "Africa"),
    "RS": ("Serbia", "Europe"), "RW": ("Rwanda", "Africa"),
    "SA": ("Saudi Arabia", "Asia"), "SC": ("Seychelles", "Africa"),
    "SD": ("Sudan", "Africa"), "SG": ("Singapore", "Asia"),
    "SH": ("Saint Helena", "Africa"), "SI": ("Slovenia", "Europe"),
    "SJ": ("Svalbard and Jan Mayen", "Europe"), "SK": ("Slovakia", "Europe"),
    "SL": ("Sierra Leone", "Africa"), "SM": ("San Marino", "Europe"),
    "SN": ("Senegal", "Africa"), "SO": ("Somalia", "Africa"),
    "SR": ("Suriname", "South America"), "SS": ("South Sudan", "Africa"),
    "ST": ("Sao Tome and Principe", "Africa"), "SV": ("El Salvador", "North America"),
    "SX": ("Sint Maarten", "North America"), "SY": ("Syria", "Asia"),
    "SZ": ("Eswatini", "Africa"), "TC": ("Turks and Caicos Islands", "North America"),
    "TD": ("Chad", "Africa"), "TF": ("French Southern Territories", "Antarctica"),
    "TG": ("Togo", "Africa"), "TJ": ("Tajikistan", "Asia"),
    "TK": ("Tokelau", "Oceania"), "TL": ("Timor-Leste", "Asia"),
    "TM": ("Turkmenistan", "Asia"), "TN": ("Tunisia", "Africa"),
    "TO": ("Tonga", "Oceania"), "TR": ("Turkey", "Asia"),
    "TT": ("Trinidad and Tobago", "North America"), "TV": ("Tuvalu", "Oceania"),
    "TW": ("Taiwan", "Asia"), "TZ": ("Tanzania", "Africa"),
    "UG": ("Uganda", "Africa"), "UM": ("United States Minor Outlying Islands", "Oceania"),
    "UY": ("Uruguay", "South America"), "UZ": ("Uzbekistan", "Asia"),
    "VA": ("Vatican City", "Europe"), "VC": ("Saint Vincent and the Grenadines", "North America"),
    "VE": ("Venezuela", "South America"), "VG": ("British Virgin Islands", "North America"),
    "VI": ("United States Virgin Islands", "North America"), "VU": ("Vanuatu", "Oceania"),
    "WF": ("Wallis and Futuna", "Oceania"), "WS": ("Samoa", "Oceania"),
    "YE": ("Yemen", "Asia"), "YT": ("Mayotte", "Africa"),
    "ZM": ("Zambia", "Africa"), "ZW": ("Zimbabwe", "Africa"),
    "XK": ("Kosovo", "Europe"),
    "ZZ": ("Unknown", "World"),
}

COUNTRY_CODE_ALIASES = {
    "_ADYGEA": "RU",
    "_BELARUS-WRW": "BY",
    "_RUSSIA-WBW": "RU",
    "_UNITED-NATIONS": "ZZ",
    "_EARTH": "ZZ",
    "AM-RA": "AM",
    "CA-QC": "CA",
    "ES-CT": "ES",
    "ES-EU": "ES",
    "GB-ENG": "GB",
    "GB-NIR": "GB",
    "GB-SCT": "GB",
    "GB-WLS": "GB",
    "PT-20": "PT",
}


def normalize_country_code(value: str):
    if value is None:
        return None
    code = str(value).strip().upper()
    if not code:
        return None
    code = COUNTRY_CODE_ALIASES.get(code, code)
    if code in COUNTRY_MAP:
        return code
    return None



def classify_tc(base: int, inc: int) -> str:
    total = base + 40 * inc
    if total < 179:
        return "Bullet"
    elif total <= 479:
        return "Blitz"
    elif total <= 1499:
        return "Rapid"
    else:
        return "Classical"


def parse_time_control(tc_str: str):
    """'180+2' -> (180, 2, 'Blitz')."""
    if not tc_str:
        return 0, 0, "Unknown"
    if tc_str == "-":
        return 0, 0, "Correspondence"
    match = re.match(r"(\d+)\+(\d+)", tc_str)
    if not match:
        return 0, 0, "Unknown"
    base = int(match.group(1))
    inc = int(match.group(2))
    return base, inc, classify_tc(base, inc)



def elo_expected(white_rating: float, black_rating: float) -> float:
    return 1.0 / (1.0 + 10 ** ((black_rating - white_rating) / 400.0))


def result_to_score(result: str):
    if result == "1-0":
        return 1.0
    elif result == "0-1":
        return 0.0
    elif result == "1/2-1/2":
        return 0.5
    return np.nan

def date_key(d: pd.Timestamp) -> int:
    return int(d.strftime("%Y%m%d"))


def tournament_url(event: str):
    match = re.search(r"https?://lichess\.org/tournament/[A-Za-z0-9]+", str(event))
    return match.group(0) if match else None



games_raw = pd.read_csv("data/games_raw.csv", dtype=str).fillna("")
eco_raw = pd.read_csv("data/eco_raw.csv", dtype=str).fillna("")
players_raw = pd.read_csv("data/players_raw.csv", dtype=str).fillna("")

print(f"  games   : {len(games_raw):,}")
print(f"  eco     : {len(eco_raw):,}")
print(f"  players : {len(players_raw):,}")

games_raw["_date"] = pd.to_datetime(
    games_raw["UTCDate"].str.replace(".", "-", regex=False),
    format="%Y-%m-%d", errors="coerce"
)



print("[transform] Building DIM_DATE")

dim_date = games_raw[["_date"]].dropna().drop_duplicates().reset_index(drop=True)
dim_date["date_key"] = dim_date["_date"].dt.strftime("%Y%m%d").astype(int)
dim_date["full_date"] = dim_date["_date"].dt.date
dim_date["day"] = dim_date["_date"].dt.day
dim_date["month"] = dim_date["_date"].dt.month
dim_date["year"] = dim_date["_date"].dt.year
dim_date = dim_date.drop(columns="_date").sort_values("date_key").reset_index(drop=True)

dim_date.to_csv("data/dim_date.csv", index=False)
print(f"  DIM_DATE rows: {len(dim_date):,}")



print("[transform] Building DIM_TIMECONTROL")

base_list, inc_list, name_list = [], [], []
for tc in games_raw["TimeControl"]:
    base, inc, name = parse_time_control(tc)
    base_list.append(base)
    inc_list.append(inc)
    name_list.append(name)

games_raw["base_seconds"] = base_list
games_raw["increment_sec"] = inc_list
games_raw["name"] = name_list

dim_tc = games_raw[["base_seconds", "increment_sec", "name"]].drop_duplicates().reset_index(drop=True)
dim_tc.insert(0, "time_control_key", range(1, len(dim_tc) + 1))
dim_tc.to_csv("data/dim_timecontrol.csv", index=False)
print(f"  DIM_TIMECONTROL rows: {len(dim_tc):,}")

tc_lookup = dim_tc.set_index(["base_seconds", "increment_sec"])["time_control_key"].to_dict()



print("[transform] Building DIM_OPENING")

eco_lookup = eco_raw.set_index("eco")["name"].to_dict()
eco_cat_lookup = eco_raw.set_index("eco")["eco-volume"].to_dict()  # A/B/C/D/E

UNKNOWN_ECO = "A??"
UNKNOWN_OPENING_KEY = 1

opening_rows = [{
    "opening_key": UNKNOWN_OPENING_KEY,
    "eco": UNKNOWN_ECO,
    "opening_name": "Unknown",
    "opening_family": UNKNOWN_ECO[:2],
    "category": UNKNOWN_ECO[:1],
}]

key = 2
for eco in games_raw["ECO"].dropna().unique():
    eco = str(eco).strip()
    if not re.fullmatch(r"[A-E]\d{2}", eco):
        continue
    opening_rows.append({
        "opening_key": key,
        "eco": eco,
        "opening_name": eco_lookup.get(eco, "Unknown"),
        "opening_family": eco[:2],
        "category": eco_cat_lookup.get(eco, eco[:1]),
    })
    key += 1

dim_opening = pd.DataFrame(opening_rows).drop_duplicates("eco").reset_index(drop=True)
duplicate_names = dim_opening.groupby("opening_name").cumcount()
duplicate_mask = duplicate_names > 0
dim_opening.loc[duplicate_mask, "opening_name"] = (
    dim_opening.loc[duplicate_mask, "opening_name"]
    + " ["
    + dim_opening.loc[duplicate_mask, "eco"]
    + "]"
)
dim_opening.to_csv("data/dim_opening.csv", index=False)
print(f"  DIM_OPENING rows: {len(dim_opening):,}")

opening_lookup = dim_opening.set_index("eco")["opening_key"].to_dict()


print("[transform] Building DIM_TERMINATION")

termination_rows = []

key = 1
for termination in games_raw["Termination"].dropna().unique():
    term = str(termination).strip().lower()
    if not term:
        continue
    termination_rows.append({
        "termination_key": key,
        "termination": term,
    })
    key += 1

dim_termination = pd.DataFrame(termination_rows).drop_duplicates("termination").reset_index(drop=True)
dim_termination.to_csv("data/dim_termination.csv", index=False)
print(f"  DIM_TERMINATION rows: {len(dim_termination):,}")

termination_lookup = dim_termination.set_index("termination")["termination_key"].to_dict()


print("[transform] Building DIM_PLAYER")

players_raw["username"] = players_raw["username"].fillna("").astype(str).str.strip()
players_raw["username_lower"] = players_raw["username"].str.lower()
players_raw["title"] = players_raw["title"].replace("", None)
players_raw["country_code"] = players_raw["country_code"].apply(normalize_country_code)
players_raw["country_name"] = players_raw["country_code"].map(
    lambda c: COUNTRY_MAP[c][0] if c else None
)
players_raw["continent"] = players_raw["country_code"].map(
    lambda c: COUNTRY_MAP[c][1] if c else None
)

# check if there are player that are in games (obatained via lichess dataset) but not in plyers table (obtained via API)
game_players = pd.concat([games_raw["White"], games_raw["Black"]]).dropna().astype(str).str.strip()
game_players = pd.DataFrame({"username": game_players}).query("username != ''")
game_players["username_lower"] = game_players["username"].str.lower()
missing_players = game_players[
    ~game_players["username_lower"].isin(players_raw["username_lower"])
].drop_duplicates("username_lower")
missing_players = missing_players.assign(
    title=None, country_code=None, country_name=None, continent=None
)

player_rows = pd.concat([
    players_raw[["username", "title", "country_code", "country_name", "continent"]],
    missing_players,
], ignore_index=True)
player_rows["username_lower"] = player_rows["username"].str.lower()

# One row per distinct player (case-insensitive username match)
dim_player = player_rows.drop_duplicates("username_lower").reset_index(drop=True)
dim_player.insert(0, "player_key", range(1, len(dim_player) + 1))

player_lookup = dict(zip(dim_player["username_lower"], dim_player["player_key"]))

dim_player = dim_player[["player_key", "username", "title", "country_code", "country_name", "continent"]]
dim_player.to_csv("data/dim_player.csv", index=False)

print(f"  DIM_PLAYER rows: {len(dim_player):,}")



print("[transform] Building DIM_TOURNAMENT")

games_raw["tournament_url"] = games_raw["Event"].apply(tournament_url)
tournament_urls = sorted(games_raw["tournament_url"].dropna().unique())

dim_tournament = pd.DataFrame({
    "tournament_key": range(1, len(tournament_urls) + 1),
    "url": tournament_urls,
})
dim_tournament.to_csv("data/dim_tournament.csv", index=False)
print(f"  DIM_TOURNAMENT rows: {len(dim_tournament):,}")

tournament_lookup = dict(zip(tournament_urls, dim_tournament["tournament_key"]))



print("[transform] Building DIM_GAME_URL")

game_urls = sorted(games_raw["Site"].str.strip().dropna().unique())

dim_game_url = pd.DataFrame({
    "game_url_key": range(1, len(game_urls) + 1),
    "url": game_urls,
})
dim_game_url.to_csv("data/dim_game_url.csv", index=False)
print(f"  DIM_GAME_URL rows: {len(dim_game_url):,}")

game_url_lookup = dict(zip(game_urls, dim_game_url["game_url_key"]))



print("[transform] Building GAME_FACT")


def build_fact_row(row):
    """Turn one raw game row into a GAME_FACT row, or None if it can't be resolved."""
    
    game_url_key = game_url_lookup.get(row["Site"].strip())
    white_key = player_lookup.get(row["White"].strip().lower())
    black_key = player_lookup.get(row["Black"].strip().lower())
    tc_key = tc_lookup.get((int(row["base_seconds"]), int(row["increment_sec"])))
    termination_key = termination_lookup.get(str(row["Termination"]).strip().lower())

    white_rating = pd.to_numeric(row.get("WhiteElo"), errors="coerce")
    black_rating = pd.to_numeric(row.get("BlackElo"), errors="coerce")

    rating_diff = None
    if pd.notna(white_rating) and pd.notna(black_rating):
        rating_diff = int(white_rating - black_rating)

    expected_score = None
    if pd.notna(white_rating) and pd.notna(black_rating):
        expected_score = round(elo_expected(white_rating, black_rating), 3)

    return {
        "game_url_key": game_url_key,
        "termination_key": termination_key,
        "date_key": date_key(pd.Timestamp(row["_date"])),
        "white_player_key": white_key,
        "black_player_key": black_key,
        "opening_key": opening_lookup.get(row["ECO"].strip(), UNKNOWN_OPENING_KEY),
        "time_control_key": tc_key,
        "tournament_key": tournament_lookup.get(row["tournament_url"]),
        "num_moves": (row.get("_num_moves")),
        "white_rating": white_rating,
        "black_rating": black_rating,
        "rating_diff": rating_diff,
        "white_score": result_to_score(row.get("Result", "")),
        "expected_score": expected_score,
    }


fact_rows = [build_fact_row(row) for _, row in games_raw.iterrows()]
fact_rows = [r for r in fact_rows if r is not None]

fact_game = pd.DataFrame(fact_rows)
fact_game.to_csv("data/fact_game.csv", index=False)
print(f"  GAME_FACT rows: {len(fact_game):,}")



print("[transform] Building PLAYER_RATING_FACT")

# Turn each game into two rows for White and Black.
white_events = games_raw[[
    "White", "_date", "UTCTime", "base_seconds", "increment_sec", "WhiteElo"
]].rename(columns={"White": "username", "WhiteElo": "elo"})

black_events = games_raw[[
    "Black", "_date", "UTCTime", "base_seconds", "increment_sec", "BlackElo"
]].rename(columns={"Black": "username", "BlackElo": "elo"})

events = pd.concat([white_events, black_events], ignore_index=True)
events = events[events["username"].str.strip() != ""]
events["elo"] = pd.to_numeric(events["elo"], errors="coerce")
events = events.dropna(subset=["elo", "_date"])


events = events.sort_values("UTCTime")
daily = events.groupby(
    ["username", "_date", "base_seconds", "increment_sec"], as_index=False
).last()

daily = daily.sort_values(["username", "base_seconds", "increment_sec", "_date"])
daily["rating_change"] = daily.groupby(
    ["username", "base_seconds", "increment_sec"]
)["elo"].diff()

daily["player_key"] = daily["username"].str.lower().map(player_lookup)
daily["date_key"] = daily["_date"].apply(lambda d: date_key(pd.Timestamp(d)))
daily["time_control_key"] = daily.apply(
    lambda r: tc_lookup.get((int(r["base_seconds"]), int(r["increment_sec"]))),
    axis=1
)

fact_rating = daily.dropna(subset=["player_key", "date_key", "time_control_key"])
fact_rating = fact_rating[["player_key", "date_key", "time_control_key", "elo", "rating_change"]]
fact_rating = fact_rating.rename(columns={"elo": "rating"})

fact_rating["player_key"] = fact_rating["player_key"].astype(int)
fact_rating["date_key"] = fact_rating["date_key"].astype(int)
fact_rating["time_control_key"] = fact_rating["time_control_key"].astype(int)
fact_rating["rating"] = fact_rating["rating"].astype(int)
fact_rating["rating_change"] = fact_rating["rating_change"].round(0).astype("Int64")

fact_rating.to_csv("data/fact_player_rating.csv", index=False)
print(f"  PLAYER_RATING_FACT rows: {len(fact_rating):,}")

print("[transform] Done.")