"""Snapshot Loganair's cheapest daily fares and log every change.

Hits the same endpoint the loganair.co.uk date picker uses. Each run fetches
the next HORIZON_DAYS of fares for every route and appends a row to
data/fares.csv only when a (route, flight_date) price differs from the last
one recorded. Every run is also logged to data/runs.csv so gaps in the
change log can be told apart from gaps in collection.
"""

import csv
import datetime as dt
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROUTES = [("LSI", "EDI"), ("EDI", "LSI"), ("LSI", "ABZ"), ("ABZ", "LSI")]
HORIZON_DAYS = 330
ENDPOINT = "https://www.loganair.co.uk/Umbraco/Api/FlightApi/FlightPrices"
# A bare "Mozilla/5.0" gets an empty 200 back; a full browser UA is needed.
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)

DATA = Path(__file__).parent / "data"
FARES = DATA / "fares.csv"
RUNS = DATA / "runs.csv"
FARE_FIELDS = ["snapshot_utc", "origin", "dest", "flight_date", "days_out", "price", "status"]
RUN_FIELDS = ["snapshot_utc", "routes_ok", "days_seen", "changes"]
# Written only when a run sees a price drop; the workflow turns it into an issue.
DROPS = Path(__file__).parent / "drops.md"


def fetch_month(origin, dest, start, end):
    query = urllib.parse.urlencode({
        "_departCity": origin,
        "_arrivalCity": dest,
        "_flightDateStart": start.isoformat(),
        "_flightDateEnd": end.isoformat(),
        "_flightAvailabilityStartDate": start.isoformat(),
        "_isReturnJourney": 0,
        "_isADS": "false",
    })
    req = urllib.request.Request(f"{ENDPOINT}?{query}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read()
    # The response is a JSON string containing JSON.
    return json.loads(json.loads(body))


def month_windows(start, end):
    cur = start
    while cur <= end:
        next_month = (cur.replace(day=1) + dt.timedelta(days=32)).replace(day=1)
        yield cur, min(end, next_month - dt.timedelta(days=1))
        cur = next_month


def fetch_route(origin, dest, today, horizon_end):
    fares = {}
    for start, end in month_windows(today, horizon_end):
        for row in fetch_month(origin, dest, start, end):
            day = dt.date.fromisoformat(row["flightDate"])
            if today <= day <= horizon_end:
                # cssClass is e.g. flight-has-price / flight-no-price.
                fares[day] = (row["price"], row["cssClass"])
        time.sleep(1)
    return fares


def last_recorded():
    """Last (price, status) per key, plus the last non-empty price.

    The last price survives a no-price blip, so a date that vanishes and
    comes back cheaper still counts as a drop.
    """
    last, last_price = {}, {}
    if FARES.exists():
        with FARES.open() as f:
            for r in csv.DictReader(f):
                key = (r["origin"], r["dest"], r["flight_date"])
                last[key] = (r["price"], r["status"])
                if r["price"]:
                    last_price[key] = r["price"]
    return last, last_price


def append(path, fields, rows):
    new = not path.exists()
    with path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new:
            w.writeheader()
        w.writerows(rows)


def main():
    DATA.mkdir(exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    today = now.date()
    horizon_end = today + dt.timedelta(days=HORIZON_DAYS)
    last, last_price = last_recorded()

    changes, drops, routes_ok, days_seen = [], [], 0, 0
    for origin, dest in ROUTES:
        try:
            fares = fetch_route(origin, dest, today, horizon_end)
        except Exception as e:
            print(f"{origin}-{dest}: failed: {e}")
            continue
        routes_ok += 1
        days_seen += len(fares)
        for day, (price, status) in sorted(fares.items()):
            price = "" if price is None else f"{price:.2f}"
            key = (origin, dest, day.isoformat())
            if last.get(key) == (price, status):
                continue
            if price and key in last_price and float(price) < float(last_price[key]):
                drops.append((origin, dest, day, last_price[key], price))
            changes.append({
                "snapshot_utc": now.isoformat(),
                "origin": origin,
                "dest": dest,
                "flight_date": day.isoformat(),
                "days_out": (day - today).days,
                "price": price,
                "status": status,
            })

    append(FARES, FARE_FIELDS, changes)
    append(RUNS, RUN_FIELDS, [{
        "snapshot_utc": now.isoformat(),
        "routes_ok": routes_ok,
        "days_seen": days_seen,
        "changes": len(changes),
    }])
    if drops:
        lines = [f"| {o} → {d} | {day:%a %d %b %Y} | £{old} → £{new} | {(day - today).days} |"
                 for o, d, day, old, new in drops]
        DROPS.write_text("| Route | Flight | Change | Days out |\n|---|---|---|---|\n"
                         + "\n".join(lines) + "\n")
    print(f"{routes_ok}/{len(ROUTES)} routes, {days_seen} days, {len(changes)} changes, {len(drops)} drops")
    if routes_ok == 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
