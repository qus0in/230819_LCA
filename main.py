import yfinance as yf
import pandas as pd
from notion import TICKER_DB, get_notion_db
import streamlit as st

TICKERS = 'TICKER.csv'
PERIOD = '1y'
RISK = 0.02
SPAN = (3, 5, 8, 13, 21)

# Util
def floor(x):
    return int(x * 100) / 100
def concat(x, y):
    return pd.concat([x, y], axis=1)

# Data
@st.cache_data
def get_data_from_db():
    return get_notion_db(TICKER_DB)

@st.cache_data
def get_tickers_from_db():
    return [el.get('TICKER').get('title')[0].get('plain_text')\
            for el in get_data_from_db()]

@st.cache_data
def get_prices_from_db():
    return [el.get('평단가').get('number') or 0\
            for el in get_data_from_db()]

def run(num) -> pd.DataFrame:
    tickers = get_tickers_from_db()
    price : pd.DataFrame = yf.download(tickers, period=PERIOD)

    close = price.Close.iloc[-1].apply(floor).rename('close')
    sma = [price.Close.rolling(s).mean().iloc[-1]\
           .apply(floor).rename(f'sma_{s}') for s in SPAN]
    ema = [price.Close.ewm(s).mean().iloc[-1]\
           .apply(floor).rename(f'ema_{s}') for s in SPAN]

    th = concat(price.Close.shift(1), price.High).T.groupby(level=0).max().T
    tl = concat(price.Close.shift(1), price.Low).T.groupby(level=0).min().T
    aatr = ((th - tl).ewm(max(SPAN)).mean() / price.Close).iloc[-1].rename('aatr').apply(floor)

    avg = pd.DataFrame({'TICKER': tickers, 'AVG': get_prices_from_db()})\
        .set_index('TICKER').join(close)\
        .apply(lambda x: x.AVG if x.AVG != 0 else x.close, axis=1)\
        .rename('price').apply(lambda x: int(x * 100) / 100)
    
    loc = ((1+aatr) * avg).rename('loc').apply(floor)
    lo = ((1+aatr*2) * avg).rename('lo').apply(floor)
    scoring = lambda x : pd.concat([close > el for el in x], axis=1).sum(axis=1)
    score = (scoring(sma) + scoring(ema)).rename('score')

    unit = (num * (RISK / aatr)\
        .apply(lambda x: min(1, x)) * score / len(SPAN))\
        .div(2).apply(int).rename('unit')
    
    screener = pd.concat([avg, lo, loc, unit, score], axis=1)\
        .query('score > 7')\
        [['unit', 'price', 'loc', 'lo']]\
        .sort_values('unit', ascending=False)
    print(screener)
    print(f'합계: ${screener.unit.sum()} ({len(screener)} / {len(tickers)})')
    return screener

if __name__ == '__main__':
    run()
