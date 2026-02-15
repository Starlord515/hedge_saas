import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, date, timedelta

class cf_component:
    def __init__(self, label, cf_type, vals, index, securities):
        self.label = label
        self.type = cf_type
        self.vals = vals
        self.index = index
        self.sec = securities
    def len(self):
        try:
            return len(self.vals)
        except:
            print('Invalid length')


class hedge:
    def __init__(self, type, component, contract, position):
        self.type = type
        self.comp = component
        self.contract = contract
        self.position = position


# Estimate a linear regression model with alpha as the fixed cost, and beta as the variable cost.
def fix_var_estimate(cost, name):
    from moving_averages_2 import moving_average
    a = cost['date'].values
    time_horizon = a[1] - a[0]
    ma = []
    for t in cost['date']:
        maret = moving_average(contract_name=name, 
                                av_specs=[time_horizon, '1d'], 
                                date=t, 
                                weight_func='half_life', 
                                wt_param= 31/6.64) # time_horizon.total_days / 6.64)
        ma.append(maret.av)
    cost['ma'] = ma
    
    from sklearn.linear_model import LinearRegression
    X = np.array(cost['ma']).reshape(-1, 1)
    Y = np.array(cost['val'])
    reg = LinearRegression().fit(X, Y)
    beta = reg.coef_

    return beta[0]


# simple_hedge expects the cost to be directly represented by a security
def simple_hedge(comp, tol, date_array):
    cost = pd.DataFrame({'date':date_array, 
                         'val':comp.vals})

    if comp.index[0] in comp.sec:
        if comp.len() == 1:
            if date_array[0] == datetime.today():
                n = comp.vals[-1] / yf.Ticker(comp.index[0]).fast_info.last_price # expense divided by current price
            else:
                df = yf.Ticker(comp.index[0]).history(start = date_array[-1], end = date_array[-1] + timedelta(days=1), interval='1d')
                last_p = df['Close'].values[-1]
                n = comp.vals[-1] / last_p
        else:
            n = fix_var_estimate(cost, comp.index[0]) # Sensitivity of variable costs to contract
        
        hedge_sub_p = ('simple', comp.label, comp.index[0], n*tol)
        return hedge_sub_p
    else:
        print('Not a simple hedge')
        return 1
    

def test():
    tolerance = 1
    test_expense_1 = cf_component(label='coffee', cf_type='expense', vals=[1000], index=['KC=F'], securities=['KC=F'])
    result_1 = simple_hedge(test_expense_1, tol=tolerance, date_array=[datetime(day=11,month=11,year=2025)])
    print('RESULT 1______________\n     ', result_1)

    test_expense_2 = cf_component(label='coffee', cf_type='expense', 
                                  vals=[1020, 1193, 1197, 1200], 
                                  index=['KC=F'], 
                                  securities=['KC=F'])
    result_2 = simple_hedge(test_expense_2, 
                            tol=tolerance, 
                            date_array=[datetime(day=1,month=1,year=2025),
                                        datetime(day=1,month=2,year=2025),
                                        datetime(day=1,month=3,year=2025),
                                        datetime(day=1,month=4,year=2025)])
    print('RESULT 2______________\n     ', result_2)

    return 0



test()
