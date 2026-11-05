# Week 04 notes: lotbook

## Hand-worked example (D05)

Trades from `examples/trades.csv`, worked on paper first and then checked against the code.
Fee rule: 0.12% of trade value, minimum S$10.00, rounded half-up to the cent.

| # | Trade | Value | Commission | Effect |
|---|-------|-------|------------|--------|
| 1 | BUY 300 @ 35.20 | 10,560.00 | 0.12% = 12.672, rounds to **12.67** | cost = 10,560.00 + 12.67 = **10,572.67** |
| 2 | BUY 200 @ 36.10 | 7,220.00 | 0.12% = 8.664, under the minimum, so **10.00** | cost = 7,220.00 + 10.00 = **7,230.00** |
| | After both buys | 500 shares | | total cost = 10,572.67 + 7,230.00 = **17,802.67**, average cost = 17,802.67 / 500 = **35.60534** |
| 3 | SELL 400 @ 37.00 | 14,800.00 | 0.12% = 17.76 | proceeds = 14,800.00 - 17.76 = **14,782.24** |

Selling 400 of the 500 shares removes 400/500 of the cost:

- cost removed = 17,802.67 x 400 / 500 = **14,242.136**
- realised profit = 14,782.24 - 14,242.136 = **540.104**, which the report prints as 540.10
- the 100 shares left keep a cost of 17,802.67 - 14,242.136 = **3,560.534**

At the price in `prices.csv` (37.50) those 100 shares are worth 3,750.00, so the unrealised profit is 3,750.00 - 3,560.534 = **189.47**.

These are the same numbers the code produces: average cost 35.6053, realised 540.10 and unrealised 189.47 all appear in the report, and `tests/test_domain.py` asserts 35.60534, 540.104 and 3560.534.