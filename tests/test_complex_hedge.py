import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from moving_averages_2 import moving_average_range
from scipy.optimize import minimize

# Complex PCA to create portfolio based on vertical correlations / vertical integration
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


def correlations(pf, cf):
    # For each security, correlate the moving average with the index. Moving average timescale is assumed to be 1 day, and the parameter is based on this.
    indexdif = pf['idx'].diff(1) / pf['idx'].shift(1)
    expected_returns = [indexdif.mean()]
    corarr = pd.DataFrame({'idx': indexdif})
    for i in cf.sec:
        pf[i] = moving_average_range(cf.dates.arr, 
                                     contract_name=i, 
                                     av_specs=[cf.dates.interval, '1d'], 
                                     date=pf['date'].values[0], 
                                     weight_func='half_life', 
                                     wt_param= 31/6.64) # time_horizon.total_days / 6.64)
        pfdif = pf[i].diff(1) / pf[i].shift(1)
        expected_returns.append(pfdif.mean())
        corarr[i] = pfdif

    corarr = corarr.fillna(0)
    correlation_matrix = corarr.corr()
    covariance_matrix = corarr.cov()
    
    return pf, correlation_matrix, covariance_matrix, expected_returns


# Calculates the portfolio parameters: expected return, standard deviation, pseudo-sharpe ratio.
def combined_parameters(cov, wt, sec, exreturn):
    pvar = []
    for i in range(len(sec)):
        j=0
        for m in sec:
            pvar.append(wt[i] * wt[j] * cov[m].values[i]); j+=1
    xret = [wt[i] * exreturn[i] for i in range(len(wt))]

    return sum(xret), sum(pvar)


# Objective function outputs the sharpe ratio, using parameters of the portfolio.
def objective_function(sec_wt, cov, sec, exreturn):
    # Index weight is assumed equal to 1.
    index_wt = 1
    wt = np.array([index_wt])
    wt = np.concatenate((wt, sec_wt), axis=0)

    # Objective function to maximise is the sharpe ratio, not including the risk-free rate.
    er, std = combined_parameters(cov, wt, sec, exreturn)
    sharpe = er/std

    return 1 - sharpe


# Minimise the sharpe ratio, subject to constraints. Return weights, portfolio epxected return, and portfolio standard deviation.
def optimal_wt(cov, sec, exreturn):
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((-1, 1) for i in range(len(sec)))
    guess =  [1 / len(sec) for i in range(len(sec))]
    optimal_wts = minimize(objective_function, guess, args=(cov, sec, exreturn), method='SLSQP', bounds=bounds, constraints=constraints)

    return optimal_wts.x


def complex_hedge(cf):
    # Dataframe of dates, cash-flow values, index values. Securities prices are added using correlation function.
    idx_df = moving_average_range(cf.dates.arr, 
                                  contract_name=cf.index, 
                                  av_specs=[cf.dates.interval, '1d'], 
                                  date=cf.dates.arr[0], 
                                  weight_func='half_life', 
                                  wt_param= 31/6.64) # time_horizon.total_days / 6.64)

    # Delocalize and include only date of datetime objects.
    filter_dates = [d.date() for d in cf.dates.arr]

    # Combine input dates, cashflow values, and index prices into one dataframe. Security prices will be added inside the correlations function.
    pf = pd.DataFrame({'date':filter_dates, 'val':cf.vals, 'idx': idx_df})
    
    # Find correlations between securities and index, securities mean return, and securities standard deviations. Add security prices to pf dataframe.
    pf, cor, cov, exreturn = correlations(pf, cf)

    # Optimise portfolio of securities with portfolio parameters.
    portfolio = optimal_wt(cov, cf.sec, exreturn)

    return portfolio



def test():
    # Number of times cashflow is input (n), input every 30 days, first input is on 15th of January 2025.
    n = 24
    interval = timedelta(days = 30)
    x = datetime(day=15, month=1, year=2023)
    label = 'Arabica Coffee'
    cf_type = 'expense'
    vals = np.zeros(n) # Only index is used for this test, so cashflow values are not needed.
    tolerance = 1

    # Assumed outputs from NLM; index and associated securities.
    index = 'KC=F'
    securities = ['SBUX', '6L=F', 'EWZ', 'CIG', '2758.TWO'] # Starbucks Corporation, Brazilian Real futures, and iShares MSCI Brazil ETF.
    
    # Generating the range of dates of each input.
    date_array = [x]
    for i in range(n - 1):
        x += interval
        if x.weekday() in [5,6]: date_array.append(x + timedelta(days=3))
        else: date_array.append(x)

    # Create cashflow line class. Run complex hedging algorithm.
    cf = cf_component(label, cf_type, vals, index, securities, date_array, interval)
    portfolio_weights = complex_hedge(cf)

    # Print optimal portfolio weights.
    i=0
    print('\nAssumption: index (cashflow) weight is equal to portfolio. The weights of each hedge security are...')
    for s in cf.sec:
        print(s, ': ', portfolio_weights[i]); i+=1
    print('\nSum of weights: ', sum(portfolio_weights))

    return 0


test()