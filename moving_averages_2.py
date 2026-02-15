
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
# inputs:
# contract_name: abbreviation of the instrument as shown on yahoo finance.
# av_specs: array consisting of two datetime objects -- time to take an average over and granularity of time intervals (hoursly, 5 min, ect...)
def moving_average(contract_name='ES=F', av_specs=None, date=None, weight_func='simple', wt_param=None, wt_function=None, custom_weights=None):
    # MAV class allows updating mav to a specific date/time.
    class mav:
        def __init__(self, av, last_date, weight_func, wt_param, contract_name, av_specs, L):
            self.av = av
            self.dt = last_date
            self.wtfun = weight_func
            self.param = wt_param
            self.contract = contract_name
            self.specs = av_specs
            self.L = L
            if weight_func == 'simple' or weight_func == 'linear':
                self.data = df['s'].values
                self.weights = wt
            else:
                self.data = None
                self.weights = None

        def update(self, dt_now):
            dfu = yf.Ticker(self.contract).history(start = self.dt, end = dt_now, interval = self.specs[1])
            dfu['s'] = (dfu['Close'] + dfu['Open']) / 2
            LL = len(dfu['s']) - 1
            if LL >= self.L:
                self = moving_average(contract_name=self.contract, av_specs=self.specs, date=dt_now, weight_func=self.wtfun, wt_param=self.param)
            elif dfu.empty != True:
                new_s = dfu['s'].values[1::]
                match self.wtfun:
                    case 'simple' | 'linear' | 'inv_exp' | 'custom':
                        self.data = np.concatenate((self.data[LL::], new_s), axis=0)
                        self.av = sum([self.data[i] * self.weights[i] for i in range(self.L)])
                    case 'exp':
                        a = self.av * np.exp(-self.param * (LL))
                        c = [np.exp(-self.param * (LL - i)) for i in range(LL)]
                        self.av = (self.av * a + sum([new_s[i] * c[i] for i in range(LL)])) / (a + sum(c))
                    case 'half_life':
                        a = self.av * (0.5**LL)
                        c = [0.5**((LL - i)) for i in range(LL)]
                        self.av = (a + sum([new_s[i] * c[i] for i in range(LL)])) / (a + sum(c))
                    case 'geometric':
                        a = self.av * (wt_param[0]**(-wt_param[1]*LL))
                        c = [wt_param[0]**(-wt_param[1] * (LL - i)) for i in range(LL)]
                        self.av = (a + sum([new_s[i] * c[i] for i in range(LL)])) / (a + sum(c))
            self.dt = dfu.index[-1]
            return self

    # Initialise moving average values given an appropriate length to take the average over.
    st_date = date - av_specs[0]
    try:
        df = yf.Ticker(contract_name).history(start = st_date, end = date, interval = av_specs[1])
    except:
        print('yFinance Error: invalid instrument, date, or interval spec.')
        return 1
    df['s'] = (df['Close'] + df['Open']) / 2
    L = len(df['Close'])
    arr = list(range(L+1,1,-1))

    # Weight functions given an input.
    match weight_func:
        case 'simple':
            wt = 1
        case 'linear':
            wt = arr
        case 'exp':
            wt = [np.exp(-wt_param*x) for x in arr]
        case 'inv_exp':
            wt = [np.sqrt(L**2 - x**2) for x in arr]
        case 'half_life':
            wt = [0.5**(x/wt_param) for x in arr]
        case 'geometric':
            wt = [wt_param[0]**(- x * wt_param[1]) for x in arr]
        case 'custom':
            if wt_function == None & custom_weights != None:
                wt = [wt_function(x) for x in arr]
            elif wt_function == None & custom_weights != None:
                wt = custom_weights
            else: 
                print('Specify "wt_function" or "custom_weights", but not both.'), 
                return 1
    
    df['ws'] = wt * df['s'] / sum(wt)
    av = df['ws'].sum()
                
    return mav(av, df.index[-1], weight_func, wt_param, contract_name, av_specs, L)


def moving_average_range(time_array, contract_name='ES=F', av_specs=None, date=None, weight_func='simple', 
                         wt_param=None, wt_function=None, custom_weights=None): 
    mav = moving_average(contract_name, av_specs, date, weight_func, wt_param, wt_function, custom_weights)
    mavarr = [mav.av]
    for t in time_array[1::]:
        mav = mav.update(t)
        mavarr.append(mav.av)

    return mavarr