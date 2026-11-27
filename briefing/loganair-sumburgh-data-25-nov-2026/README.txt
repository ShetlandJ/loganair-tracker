Sumburgh fares: data to 25 November 2026, 13:28 GMT
====================================================

Source: the fare calendar (date picker) on loganair.co.uk, read automatically from
10 October 2026. Each check records the lowest one-way fare per person shown for
every date up to 330 days ahead, on six routes: Sumburgh to and from Aberdeen,
Edinburgh and Glasgow. Full fares and Air Discount Scheme (ADS) fares are read
separately. Edinburgh and Aberdeen full fares from 10 October; Glasgow and all ADS
fares from 19 October. Times are UTC (GMT). Prices are in pounds.

The full method is at https://shetlandj.github.io/loganair-tracker/loganair-data.html
The code and complete history are at https://github.com/ShetlandJ/loganair-tracker

Files
-----

same-date-comparison.csv
  Every route and flight date, with the fare at the check at 11:31 on 4 November
  (before the change) and at 23:29 on 6 November (after it), and at 13:28 on
  25 November. ADS columns are the same for ADS fares. Blank means the calendar
  showed no fare. in_headline_comparison = "yes" marks the 1,730 dates with a fare
  at both checks and a flight on or after 7 November.

lowest-and-highest-fare-by-check.csv
  For every check and route: the lowest full fare shown on any flight date from
  that day on, how many dates carried it, the highest full fare shown, and how
  many dates had a fare.

old-lowest-fare-dates.csv
  Every date that carried its route's lowest full fare at 11:31 on 4 November,
  and its fare at 13:28 on 25 November. Dates that have since flown have no
  change value.

change-by-flight-month.csv
  The headline comparison (4 Nov 11:31 against 6 Nov 23:29) grouped by route and
  month of flight.

checks.csv
  Every check, with how many flight dates' fares changed, and how many dates were
  seen for the first time (new dates coming into the 330-day window, or a route
  being added).

fare-change-log-full.csv, fare-change-log-ads.csv
  The raw record. A row is written only when a date's fare differs from the
  last one recorded. status is the calendar's own marker for the date.

Limits
------
- Each figure is the lowest fare shown for the whole day, not the price of a
  particular flight.
- We take the calendar to show the Fly fare. Fly Flex and Fly Flex Plus prices
  are not visible to us.
- Calendar prices have not been checked against the final checkout total.
- A blank fare can mean sold out, not on sale or no flight.
- Checks ran about every 5.5 hours, so a fare that changed and changed back
  between checks would not be seen.
- The ADS calendar often shows no fare for dates far ahead, even where a full
  fare is shown.
