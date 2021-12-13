'''
Author: Callum Jackson

https://github.com/CallumJackson90/

A Python script to examine currency pairs for their cointegration, 
and test the statistical significance of this. For significant pairs,
the spread is calculated and statistically tested, and a hedge ratio
is calculated. Files containing the p-values and hedge ratios are 
created.
'''


import json
import numpy as np
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import statsmodels.tsa.stattools as ts
import matplotlib.pyplot as plt

# Define timeframes, the amount of days to look back over, and the symbols to fetch.
time_interval = mt5.TIMEFRAME_H1
lookback = timedelta(days=180)
symbols= ['GBPUSD', 'GBPJPY', 'EURUSD', 'USDJPY', 
'USDCAD', 'EURGBP', 'XAUUSD', 'XAGUSD', 
'AUDJPY', 'AUDCAD', 'EURJPY', 'EURCHF']



def get_quotes(time_frame, year = 2020, day=1, month=11, symbols=[], lookback=180):
    '''
    A function to create a dictionary comprised of symbols and their corresponding -
    - ohlc data.
    '''

    # Establish Connection to MT5
    mt5.initialize(login=1051050429, password="PASSWORD", server="SERVER",
                    path="PATH")

    datefrom = datetime(year=year, day=day, month=month)
    dateto = datefrom + lookback

    # A dictionary is created with each symbol corresponding to a dataframe of ohlc data.
    d = {}
    for symbol in symbols:
            rates = mt5.copy_rates_range(symbol, time_frame, datefrom, dateto)
            print(mt5.last_error())
            d[symbol] = pd.DataFrame(rates)
            d[symbol] = d[symbol].drop(columns=['tick_volume', 'real_volume',
                                            'spread', 'open', 'high', 'low'])
            d[symbol]['time'] = pd.to_datetime(d[symbol]['time'], unit='s')
            d[symbol].set_index('time', inplace=True)
    mt5.shutdown()
    
    return d

# Get dict of dataframes with symbol ohlc data. 
now = datetime.now()
symbols_dict = get_quotes(time_frame=time_interval, year=(now-lookback).year, 
                        day=(now-lookback).day, month=(now-lookback).month, 
                        symbols=symbols, lookback=lookback)


def create_pairs_df(symbols_dict, symbols):
    '''
    A function to extract dataframes from a dictionary of dataframes returned 
    from the previous function, get_quotes.
    '''
    df = pd.DataFrame()
    names = list()

    for symbol in symbols:
        df = pd.concat([df, symbols_dict[symbol]], axis =1)
        names.append(symbol)
        df.columns = names

    return df

# Create the dataframe of symbols data, and remove any NA values.
df = create_pairs_df(symbols_dict, symbols)
df = df.dropna()

def coint_p_values(symbols, df):
    '''
    Determine the cointegration p-values for all possible asset pairings.
    A p-value of < 0.05 is required to be statistically confident with
    cointegration, therefore all values that do not meet this criteria
    are not returned.
    '''
    p_vals = dict()
    for i in range(len(symbols)):
        for j in range(len(symbols)-1):
            result = ts.coint(df[symbols[i]], df[symbols[j]])
            p_vals[symbols[i]+'_'+symbols[j]] = result[1]

    sig_pairs = dict()
    for key in p_vals:
        if 0 < p_vals[key] < 0.05:
            sig_pairs[key] = p_vals[key]
    
    return sig_pairs

# Create a save of the cointegration values. 
# If the file already exists, load the file.
timestamp = datetime.now().strftime("%d-%m-%y")
path = Path(f'PATH/{timestamp}coint_values.json')

if path.is_file():
    with open(path, 'r') as fp:
        sig_pairs = json.loads(fp.read())
else:
    sig_pairs = coint_p_values(symbols, df)
    with open(path,  'w+') as fp:
        json.dump(sig_pairs, fp)

print('Significant Pairs:')
for key, value in sig_pairs.items():
    print(f'{key} : {value}')

def spread_calculation(sig_pairs, df):
    '''
    A function to calculate the spreads of the two assets, and
    determine the hedge ratio.
    formula: spread = log(a) - nlog(b), where n is the hedge ratio.
    therefore, to calculate the hedge ratio, perform a linear 
    regression on log(a) and log(b)
    
    '''
    sig_pairs_list = list(sig_pairs.keys())
    hedge_ratios = dict()
    df_spread = pd.DataFrame(index=df.index)
    names = list()
    
    for pairs in range(len(sig_pairs_list)):
        pair_split = sig_pairs_list[pairs].split("_")

        x = np.log(np.array(df[pair_split[0]]))
        x= x.reshape((-1, 1))

        y = np.log(np.array(df[pair_split[1]]))

        model_OLS = ts.OLS(x,y)
        results_OLS = model_OLS.fit()
        n = results_OLS.params[0]

        hedge_ratios[sig_pairs_list[pairs]] = n

        spread = []
        for i in range(len(x)):
            spread.append(x[i] - (hedge_ratios[sig_pairs_list[pairs]]*y[i]))

        names.append(sig_pairs_list[pairs])
        df_spread[sig_pairs_list[pairs]] = spread
        df_spread.columns = names

    return df_spread, hedge_ratios

spread_df, hedge_ratios = spread_calculation(sig_pairs, df)

def adf_spread_values(spread_df):
    '''
    A function which takes calculated spreads between two assets and
    determines if they are stationary. Stationary spreads are theorised
    to revert to a given mean over time. only statistically significant
    values are returned, determined by a p-value < 0.05.

    '''
    sig_spread = dict()
    for column in spread_df:
        adf_result = ts.adfuller(spread_df[column])
    
        if adf_result[1] < 0.05:
            sig_spread[column] = adf_result[1]
    
    return sig_spread



path2 = Path(f'PATH/{timestamp}spread_adf_values.json')
if path2.is_file():
    with open(path2, 'r') as fp:
        sig_spreads = json.loads(fp.read())
else:
    sig_spreads = adf_spread_values(spread_df)
    with open(path2,  'w+') as fp:
        json.dump(sig_spreads, fp)

print('Stationary Spreads:')
for key, value in sig_spreads.items():
    print(f'{key} : {value}')

hedge_ratios = {list(sig_spreads.keys())[x]: hedge_ratios[list(sig_spreads)[x]] 
                for x in range(len(list(sig_spreads.keys())))}

path3 = Path(f'PATH/{timestamp}hedge_ratios.json')
with open(path3,  'w+') as fp:
    json.dump(hedge_ratios, fp)

columns = list(sig_spreads.keys())
spread_df = spread_df[[x for x in spread_df if x in columns]]

def zscore_calculation(spread_df_column, window):
    '''
    A function to calculate the z-scores of the asset pair spreads,
    expressed as standard deviations away from the mean.
    '''
    window = window
    pair = spread_df_column
    df_zscores = pd.DataFrame(index=spread_df_column.index, 
                            columns=['z-score'])

    rolling_mean = pair.rolling(window).mean()
    rolling_std = pair.rolling(window).std()
    zscore = (pair - rolling_mean) / rolling_std

    for i in range(len(df_zscores)):
        df_zscores['z-score'][i] = zscore[i][0]


    return df_zscores

# Save the Z-Scores to csv files for later use.
for column in spread_df.columns:
    zscore = zscore_calculation(spread_df[column], 20)
    zscore_path = Path(f'PATH/{column}.csv')
    zscore.to_csv(zscore_path)

def plot_zscore(df_zscores, pair):
    '''
    A small function to plot the desired z-score with two standard divations
    from the mean shown via dashed lines.
    '''
    plt.plot(df_zscores)
    plt.axhline(-2, color='r', linestyle='--')
    plt.axhline(0, color='black')
    plt.axhline(2, color='r', linestyle='--')
    plt.title(f'Z-Score for {pair}')
    plt.show()

#Plot the last Z-score 
plot_zscore(zscore, 'EURJPY_CADUSD')