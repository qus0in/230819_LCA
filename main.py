import yfinance as yf
import pandas as pd

TICKERS = 'TICKER.csv'
PERIOD = '1y'
RISK = 0.02
SPAN = (3, 5, 8, 13, 21)

def run(num) -> pd.DataFrame:
    # util
    floor = lambda x: int(x * 100) / 100
    concat = lambda x, y: pd.concat([x, y], axis=1)
    # price
    tickers = pd.read_csv(TICKERS).TICKER.to_list()
    price : pd.DataFrame = yf.download(tickers, period=PERIOD)
    # ma
    close = price.Close.iloc[-1].apply(floor).rename('close')
    # print(close)
    sma = [price.Close.rolling(s).mean().iloc[-1]\
           .apply(floor).rename(f'sma_{s}') for s in SPAN]
    ema = [price.Close.ewm(s).mean().iloc[-1]\
           .apply(floor).rename(f'ema_{s}') for s in SPAN]
    # aatr
    th = concat(price.Close.shift(1), price.High).T.groupby(level=0).max().T
    tl = concat(price.Close.shift(1), price.Low).T.groupby(level=0).min().T
    aatr = ((th - tl).ewm(max(SPAN)).mean() / price.Close).iloc[-1].rename('aatr').apply(floor)
    # screener
    avg = pd.read_csv(TICKERS).set_index('TICKER').join(close)\
        .apply(lambda x: x.AVG if not pd.isna(x.AVG) else x.close, axis=1).rename('price')
    # print(avg)
    loc = ((1+aatr) * avg).rename('loc').apply(floor)
    lo = ((1+aatr*2) * avg).rename('lo').apply(floor)
    scoring = lambda x : pd.concat([close > el for el in x], axis=1).sum(axis=1)
    score = (scoring(sma) + scoring(ema)).rename('score')
    # print(score)
    # unit
    unit = (num * (RISK / aatr).apply(lambda x: min(1, x)) * score / len(SPAN)).div(2).apply(int).rename('unit')
    # print(score)
    screener = pd.concat([avg, lo, loc, unit, score], axis=1)\
        [['unit', 'price', 'loc', 'lo']]\
        .query('unit > price')\
        .sort_values('unit', ascending=False)
    print(screener)
    print(f'합계: ${screener.unit.sum()} ({len(screener)} / {len(tickers)})')
    return screener

if __name__ == '__main__':
    run()
