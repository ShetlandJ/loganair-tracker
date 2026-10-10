# loganair-tracker

Logs Loganair's cheapest daily one-way fare for Sumburgh ↔ Edinburgh/Aberdeen, every 3 hours, for the next 120 days.

- `track.py` hits the date-picker endpoint (`/Umbraco/Api/FlightApi/FlightPrices`) and appends to `data/fares.csv` only when a date's price changes. `data/runs.csv` logs every run.
- `.github/workflows/track.yml` runs it on a cron and commits the data.
- `index.html` is the GitHub Pages view; it reads the CSVs from raw.githubusercontent.com.

Run locally: `python3 track.py` (on python.org builds of Python on macOS, prefix with `SSL_CERT_FILE=/etc/ssl/cert.pem`).
