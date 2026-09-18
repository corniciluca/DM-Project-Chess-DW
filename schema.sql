DROP TABLE IF EXISTS RATING_SNAPSHOT CASCADE;
DROP TABLE IF EXISTS GAME CASCADE;
DROP TABLE IF EXISTS GAME_URL CASCADE;
DROP TABLE IF EXISTS PLAYER CASCADE;
DROP TABLE IF EXISTS TOURNAMENT CASCADE;
DROP TABLE IF EXISTS TIMECONTROL CASCADE;
DROP TABLE IF EXISTS OPENING CASCADE;
DROP TABLE IF EXISTS DATE CASCADE;

CREATE TABLE DATE (
    date_key  SERIAL PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    day       INT NOT NULL,
    month     INT NOT NULL,
    year      INT NOT NULL

    CONSTRAINT chk_day     CHECK (day     BETWEEN 1 AND 31),
    CONSTRAINT chk_month   CHECK (month   BETWEEN 1 AND 12),
    CONSTRAINT chk_year    CHECK (year    BETWEEN 2000 AND 2100)
);

CREATE TABLE PLAYER (
    player_key   SERIAL PRIMARY KEY,
    username     VARCHAR(100) UNIQUE NOT NULL,
    title        VARCHAR(10) CHECK (title IN ('GM', 'IM', 'FM', 'CM', 'WGM', 'WIM', 'WFM', 'WCM', NULL)),
    country_code CHAR(2),
    country_name VARCHAR(100),
    continent    VARCHAR(50) CHECK (continent IN (
                     'Africa','Asia','Europe',
                     'North America','South America',
                     'Oceania','Antarctica','World',
                     NULL
                 ))
);

CREATE TABLE OPENING (
    opening_key    SERIAL PRIMARY KEY,
    eco            CHAR(3) UNIQUE NOT NULL,
    opening_name   VARCHAR(200) UNIQUE NOT NULL,
    opening_family CHAR(2) NOT NULL,
    category       CHAR(1) NOT NULL,
    
    CONSTRAINT chk_category CHECK (category IN ('A','B','C','D','E')),
    CONSTRAINT chk_family_prefix CHECK (opening_family = SUBSTRING(eco FROM 1 FOR 2)),
    CONSTRAINT chk_category_prefix CHECK (category = SUBSTRING(eco FROM 1 FOR 1))
);

CREATE TABLE TIMECONTROL (
    time_control_key SERIAL PRIMARY KEY,
    name             VARCHAR(20) NOT NULL,
    base_seconds     INT NOT NULL,
    increment_sec    INT NOT NULL,
    UNIQUE (base_seconds, increment_sec)
);

CREATE TABLE TOURNAMENT (
    tournament_key SERIAL PRIMARY KEY,
    url           VARCHAR(200) NOT NULL UNIQUE
);

CREATE TABLE GAME_URL (
    game_url_key SERIAL PRIMARY KEY,
    url           VARCHAR(200) NOT NULL UNIQUE
);

CREATE TABLE TERMINATION (
    termination_key SERIAL PRIMARY KEY,
    termination     VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE GAME (
    game_key          SERIAL PRIMARY KEY,
    game_url_key      INT NOT NULL REFERENCES GAME_URL(game_url_key),
    termination_key   INT NOT NULL REFERENCES TERMINATION(termination_key),
    date_key          INT NOT NULL REFERENCES DATE(date_key),
    white_player_key  INT NOT NULL REFERENCES PLAYER(player_key),
    black_player_key  INT NOT NULL REFERENCES PLAYER(player_key),
    opening_key       INT NOT NULL REFERENCES OPENING(opening_key),
    time_control_key  INT NOT NULL REFERENCES TIMECONTROL(time_control_key),
    tournament_key    INT REFERENCES TOURNAMENT(tournament_key),
    num_moves         INT CHECK (num_moves >= 0),
    white_rating      INT CHECK (white_rating BETWEEN 100 AND 3000),
    black_rating      INT CHECK (black_rating BETWEEN 100 AND 3000),
    rating_diff       INT,
    white_score       NUMERIC(2,1) CHECK (white_score IN (0.0, 0.5, 1.0)),
    expected_score    NUMERIC(6,5) CHECK (expected_score BETWEEN 0.0 AND 1.0),

    UNIQUE (game_url_key),
    CONSTRAINT chk_different_players CHECK (white_player_key <> black_player_key)
);

CREATE TABLE RATING_SNAPSHOT (
    snapshot_key     SERIAL PRIMARY KEY,
    player_key       INT NOT NULL REFERENCES PLAYER(player_key),
    date_key         INT NOT NULL REFERENCES DATE(date_key),
    time_control_key INT NOT NULL REFERENCES TIMECONTROL(time_control_key),
    rating           INT NOT NULL CHECK (rating BETWEEN 100 AND 3000),
    rating_change    INT,
    UNIQUE (player_key, date_key, time_control_key)
);
