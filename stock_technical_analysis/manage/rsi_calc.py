import numpy as np

period = 14


def avg_gain_loss(df, gain=True):
    """
    Calculates the average gain and loss using the gain and loss columns of provided dataframe.
    Creates two new columns for avg_gain and avg_loss for average gain and average loss respectively
    """
    mode = 'gain' if gain else 'loss'
    # avg = np.mean(df[mode][1:period+1])
    avg_prev = np.mean(df.loc[1:period, mode])
    df["avg_"+str(mode)] = 0
    df.at[period, "avg_"+str(mode)] = avg_prev
    for index, row in df[period+1:].iterrows():
        avg_mode = (avg_prev * (period - 1) + df[mode][index]) / period
        df.loc[index, "avg_" + str(mode)] = avg_mode
        avg_prev = avg_mode


def gain_loss(rsi_df):
    """Calculation of gains and losses. Creates two new columns gain and loss in provided dataframe itself."""
    rsi_df['gain'] = 0
    rsi_df['loss'] = 0
    for index, row in rsi_df[1:].iterrows():
        if row['close'] > rsi_df['close'][index - 1]:
            # gain
            rsi_df.loc[index, 'gain'] = row['close'] - \
                rsi_df['close'][index - 1]
        else:
            rsi_df.loc[index, 'gain'] = 0
        if row['close'] < rsi_df['close'][index - 1]:
            # loss
            rsi_df.loc[index, 'loss'] = rsi_df['close'][index - 1] - \
                row['close']
        else:
            rsi_df.loc[index, 'loss'] = 0


def rsi_calc(df):
    """
    RSI (Relative Strength Index) of provided stock data which must have closing price and timestamp.
    Creates four columns namely gain, loss, avg_gain, avg_loss, RS and RSI calculated using the close prices.
    Returns: Dataframe contaning all caculated values.
    """
    rsi_df = df[['timestamp', 'close']].copy()
    gain_loss(rsi_df)
    avg_gain_loss(rsi_df)
    avg_gain_loss(rsi_df, gain=False)
    rsi_df['RS'] = rsi_df.loc[period-1:, 'avg_gain'] / \
        rsi_df.loc[period-1:, 'avg_loss']
    rsi_df['RSI'] = 100 - 100 / (1 + rsi_df['RS'])
    rsi_df.loc[:period, 'RSI'] = 0
    rsi_df.loc[:period, 'RS'] = 0
    return rsi_df


def next(prev, close):
    """
    Takes previos day calculation and provide next day calculation for RSI
    """
    gain = close >= prev['close']
    gain = 0 if not gain else close - prev['close']
    loss = 0 if gain else prev['close'] - close
    avg_gain = (prev['avg_gain'] * (period - 1) + gain) / period
    avg_loss = (prev['avg_loss'] * (period - 1) + loss) / period
    rs = avg_gain/avg_loss
    rsi = 100 - 100/(1 + rs)
    return {'close': close, 'gain': gain, 'loss': loss, 'avg_gain': avg_gain,
            'avg_loss': avg_loss, 'rs': rs, 'rsi': rsi}


