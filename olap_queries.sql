WITH opening_counts AS (
    SELECT d.year, d.month,
           o.opening_name, o.eco,
           COUNT(*) AS games,
           RANK() OVER (
               PARTITION BY d.year, d.month
               ORDER BY COUNT(*) DESC
           ) AS rnk
    FROM GAME g
    JOIN DATE    d ON g.date_key    = d.date_key
    JOIN OPENING o ON g.opening_key = o.opening_key
    GROUP BY d.year, d.month, o.opening_name, o.eco
)
SELECT year, month, rnk, eco, opening_name, games
FROM opening_counts
WHERE rnk <= 10
ORDER BY year, month, rnk;


SELECT o.category,
       o.eco,
       o.opening_name,
       COUNT(*)                        AS games,
       ROUND(AVG(g.white_score), 3)    AS white_win_rate,
       ROUND(1 - AVG(g.white_score), 3) AS black_win_rate,
       ROUND(AVG(CASE WHEN g.white_score = 0.5 THEN 1.0 ELSE 0.0 END), 3) AS draw_rate
FROM GAME g
JOIN OPENING o ON g.opening_key = o.opening_key
GROUP BY o.category, o.eco, o.opening_name
ORDER BY o.category, o.eco, white_win_rate DESC;

SELECT o.category,
       COUNT(*) FILTER (WHERE tc.name = 'Bullet')    AS bullet_games,
       COUNT(*) FILTER (WHERE tc.name = 'Blitz')     AS blitz_games,
       COUNT(*) FILTER (WHERE tc.name = 'Rapid')     AS rapid_games,
       COUNT(*) FILTER (WHERE tc.name = 'Classical') AS classical_games,
       ROUND(AVG(g.white_score) FILTER (WHERE tc.name = 'Bullet'),    3) AS bullet_white_rate,
       ROUND(AVG(g.white_score) FILTER (WHERE tc.name = 'Blitz'),     3) AS blitz_white_rate,
       ROUND(AVG(g.white_score) FILTER (WHERE tc.name = 'Rapid'),     3) AS rapid_white_rate,
       ROUND(AVG(g.white_score) FILTER (WHERE tc.name = 'Classical'), 3) AS classical_white_rate
FROM GAME g
JOIN OPENING     o  ON g.opening_key      = o.opening_key
JOIN TIMECONTROL tc ON g.time_control_key = tc.time_control_key
GROUP BY o.category
ORDER BY o.category;

SELECT p.username,
       d.year, d.month, tc.name AS time_control,
       ROUND(AVG(pr.rating_change), 2) AS avg_daily_change,
       SUM(pr.rating_change)           AS net_monthly_change,
       MIN(pr.rating)                  AS min_rating,
       MAX(pr.rating)                  AS max_rating
FROM RATING_SNAPSHOT pr
JOIN PLAYER p ON pr.player_key = p.player_key
JOIN DATE   d ON pr.date_key   = d.date_key
JOIN TIMECONTROL tc ON pr.time_control_key = tc.time_control_key
GROUP BY p.username, d.year, d.month, tc.name
HAVING AVG(pr.rating_change)is not NULL
ORDER BY  d.year, d.month,avg_daily_change DESC;

WITH monthly_growth AS (
    SELECT p.username,
           tc.name AS time_control,
           d.year, d.month,
           SUM(pr.rating_change) AS monthly_gain
    FROM RATING_SNAPSHOT pr
    JOIN PLAYER      p  ON pr.player_key      = p.player_key
    JOIN TIMECONTROL tc ON pr.time_control_key = tc.time_control_key
    JOIN DATE        d  ON pr.date_key         = d.date_key
    GROUP BY p.username, tc.name, d.year, d.month
)
SELECT time_control,
       ROUND(AVG(monthly_gain), 2) AS avg_monthly_gain,
       MAX(monthly_gain)           AS best_single_month,
       COUNT(DISTINCT username)    AS players_tracked,
       RANK() OVER (
           ORDER BY AVG(monthly_gain) DESC
       ) AS growth_rank
FROM monthly_growth
GROUP BY time_control
ORDER BY growth_rank;

WITH daily_ratings AS (
    SELECT p.username,
           tc.name       AS time_control,
           d.full_date,
           pr.rating,
           MAX(pr.rating) OVER (
               PARTITION BY p.username, tc.name
           ) AS peak_rating
    FROM RATING_SNAPSHOT pr
    JOIN PLAYER      p  ON pr.player_key      = p.player_key
    JOIN DATE        d  ON pr.date_key         = d.date_key
    JOIN TIMECONTROL tc ON pr.time_control_key = tc.time_control_key
),
at_peak AS (
    SELECT username, time_control,
           full_date, peak_rating
    FROM daily_ratings
    WHERE rating = peak_rating
)
SELECT username,
       time_control,
       peak_rating,
       MIN(full_date)                  AS peak_first_reached,
       MAX(full_date)                  AS peak_last_held,
       MAX(full_date) - MIN(full_date) AS days_at_peak
FROM at_peak
GROUP BY username, time_control, peak_rating
ORDER BY days_at_peak DESC;


WITH month_start_rating AS (
    SELECT pr.player_key,
           d.year, d.month,
           pr.rating
    FROM RATING_SNAPSHOT pr
    JOIN DATE d ON pr.date_key = d.date_key
    WHERE d.day = 1
)
SELECT p.username,
       d.year, d.month,
       msr.rating             AS rating_at_month_start,
       COUNT(*)               AS games_played,
       ROUND(AVG(g.white_score), 3) AS white_avg_rate
FROM GAME g
JOIN DATE   d   ON g.date_key         = d.date_key
JOIN PLAYER p   ON g.white_player_key = p.player_key
JOIN month_start_rating m
     ON  m.player_key = g.white_player_key
     AND m.year       = d.year
     AND m.month      = d.month
GROUP BY p.username, d.year, d.month, m.rating
ORDER BY p.username, d.year, d.month;
