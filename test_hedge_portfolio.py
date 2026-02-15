# Test protfolio by simulating cashflows and hedgesover time.
import yfinance
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from moving_averages_2 import moving_average_range
from scipy.optimize import minimize
import plotly.graph_objects as go
from complex_hedge import complex_hedge

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


def hedge_sim_1(cf):
    # Get portfolio of hedging instruments, and dataframe of prices for the index and its associated securities.
    portfolio, pf = complex_hedge(cf)

    # Normalise securities values like an index, starting at 0. Apply portfolio weights to securities, relative to initial index value.
    i=0; base = pf['idx'].values[0]
    for col in cf.sec:
        pf[col] = (pf[col] / pf[col].values[0] - 1) * base * portfolio[i]; i+=1

    # Transpose normalised dataframe. Sum up all values to get hedged cashflow values.
    #pf.drop(columns=['date'], inplace=True)
    pf_trans = pf.drop(columns=['date','idx','val']).transpose(); hedged_cashflows = []
    for col in pf_trans.columns: hedged_cashflows.append(pf_trans[col].sum())

    print(hedged_cashflows)
    match cf.type:
        case 'expense': pf['hedge_portfolio'] = [i * -1 for i in hedged_cashflows]
        case 'income': pf['hedge_portfolio'] = hedged_cashflows

    pf['hedged_cashflows'] = pf['idx'] + pf['hedge_portfolio']

    # Plot cashflows hedged and un-hedged, for comparison.
    fig = go.Figure(data=[go.Scatter(x=cf.dates.arr, y=pf['idx'], mode='lines', line=dict(color='rgb(255, 0, 0)'), showlegend=True, name='Un-hedged Cashflows'),
                          go.Scatter(x=cf.dates.arr, y=pf['hedged_cashflows'], mode='lines', line=dict(color='rgb(0, 0, 255)'), showlegend=True, name='Hedged Cashflows'),
                          go.Scatter(x=cf.dates.arr, y=pf['hedge_portfolio'], mode='lines', line=dict(color='rgb(0, 255, 0)'), showlegend=True, name='Hedge Portfolio')],
                    layout=go.Layout(title=f'Hedged {cf.type} for {cf.label}', xaxis=dict(title='Date'), yaxis=dict(title=cf.type))
                    )
    fig.show()
    return 0
