import numpy as np

fastline = 12
slowline = 26
signalline = 9

def ema_n(ema_df, period=12):
    """
    Calculates ema (Exponential moving average) for provided data in dataframe.
    Creates ema_{period} columns to the provided dataframe itself.
    """
    avg12 = np.mean(ema_df['close'][:period])
    ema_prev = avg12
    ema_df['ema'+str(period)] = 0
    ema_df.at[period - 1, 'ema'+str(period)] = ema_prev
    for index, row in ema_df[period:].iterrows():
        ema1 = ema_df['close'][index] * \
            (2/(period + 1)) + ema_prev * (1 - (2 / (period + 1)))
        ema_df.at[index, 'ema'+str(period)] = ema1
        ema_prev = ema1


def signal(ema_df, period=9):
    """
    Calculates Signal line values from provided dataframe and period.
    Creates signal column in the same dataframe also.
    """
    avg = np.mean(ema_df['macd'][:(period+26-1)])
    signal_prev = avg
    ema_df['signal'] = 0
    ema_df.at[(period+26-1) - 1, 'signal'] = signal_prev
    for index, row in ema_df[(period+26-1):].iterrows():
        signal = ema_df['macd'][index] * \
            (2/(period + 1)) + signal_prev * (1 - (2 / (period + 1)))
        ema_df.at[index, 'signal'] = signal
        signal_prev = signal


def macd_calc(df):
    """Calculates EMA12, EMA 26, MACD, Signal and hist and returns same in
    a new dataframe with timestamp in provided Dataframe"""
    macd_df = df[['timestamp', 'close']].copy()
    ema_n(macd_df, period=fastline)
    ema_n(macd_df, period=slowline)
    macd_df['macd'] = macd_df['ema12'][25:] - macd_df['ema26'][25:]
    signal(macd_df, period=signalline)
    macd_df['hist'] = macd_df['macd'][33:] - macd_df['signal'][33:]
    return macd_df


def next(prev, close):
    """
    Calculates next macd based on previous day data and close of current day
    """

    ema12 = close * (2/(fastline + 1)) + prev['ema12'] * (1 - (2 / (fastline + 1)))
    ema26 = close * (2/(slowline + 1)) + prev['ema26'] * (1 - (2 / (slowline + 1)))
    macd = ema12 - ema26
    signal = macd * (2/(signalline + 1)) + prev['signal'] * (1 - (2 / (signalline + 1)))
    hist = macd - signal
    return {
        'close': close,
        'ema12': ema12,
        'ema26': ema26,
        'macd': macd,
        'signal': signal,
        'hist': hist
    }