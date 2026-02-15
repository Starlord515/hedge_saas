import numpy as np
from datetime import datetime, date, timedelta
from test_hedge_portfolio import hedge_sim_1

class subheading:
    pass
class cf_component:
    def __init__(self, label, cf_type, vals, index, securities, date_array, interval):
        self.label = label
        self.type = cf_type
        self.vals = vals
        self.index = index
        self.sec = securities
        self.dates = subheading()
        self.dates.arr = date_array
        self.dates.interval = interval
    def len(self):
        try:
            return len(self.vals)
        except:
            print('Invalid length')


## Cashflow specifications, input by user. The values of the cashflow is presumed to be equal to the price of the coffee future price.
label = 'Arabica Coffee'
cf_type = 'expense'
n = 2*12 # Number of cashflows input by user.
vals = np.zeros(n)  # Only index is used for this test, so cashflow values are not needed.
tolerance = 10 # Tolerance defines how extensively the cashflow is hedged -- a value of 1 means completely hedged, a value of 0 means no hedge is applied.

## Assumed outputs from NLM; index and associated securities.
index = 'KC=F'
securities = ['SBUX', '6L=F', 'EWZ', 'CIG']#, '2758.TWO']  # Starbucks Corporation, Brazilian Real futures, and iShares MSCI Brazil ETF.

## Number of times cashflow is input (n), input every 30 days, first input is on the 15th of January 2025. Create array of cashflow dates.
interval = timedelta(days=30)
x = datetime(day=15, month=1, year=2022)
date_array = [x]
for i in range(n - 1):
    x += interval
    if x.weekday() in [5, 6]: date_array.append(x + timedelta(days=3))
    else: date_array.append(x)

## Create cashflow line class.
cf = cf_component(label, cf_type, vals, index, securities, date_array, interval)

## Run hedge comparison
hedge_sim_1(cf)
