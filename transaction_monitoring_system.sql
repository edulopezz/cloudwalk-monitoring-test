WITH status_pivot AS (

SELECT
timestamp,

SUM(CASE WHEN status='approved' THEN count ELSE 0 END) AS approved,
SUM(CASE WHEN status='denied' THEN count ELSE 0 END) AS denied,
SUM(CASE WHEN status='failed' THEN count ELSE 0 END) AS failed,
SUM(CASE WHEN status='reversed' THEN count ELSE 0 END) AS reversed,
SUM(CASE WHEN status='backend_reversed' THEN count ELSE 0 END) AS backend_reversed,
SUM(CASE WHEN status='refunded' THEN count ELSE 0 END) AS refunded

FROM transactions
GROUP BY timestamp

),

totals AS (

SELECT
*,
approved + denied + failed + reversed + backend_reversed + refunded AS total

FROM status_pivot

),

rates AS (

SELECT
timestamp,
approved,
denied,
failed,
reversed,
backend_reversed,
refunded,
total,

(denied / total) AS deny_rate,
(failed / total) AS fail_rate,
(reversed / total) AS reverse_rate

FROM totals

),

statistics AS (

SELECT
AVG(deny_rate) AS deny_mean,
PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY deny_rate) AS deny_median,
PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY deny_rate) AS deny_p95,
PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY deny_rate) AS deny_p99,

AVG(fail_rate) AS fail_mean,
PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY fail_rate) AS fail_p95,

AVG(reverse_rate) AS reverse_mean,
PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY reverse_rate) AS reverse_p95

FROM rates

)

SELECT
r.*,
s.*

FROM rates r
CROSS JOIN statistics s
ORDER BY r.timestamp;
