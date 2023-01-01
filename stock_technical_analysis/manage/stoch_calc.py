from manage import data
from manage.utils import timeit


period = 14


def calculate(stock):
    """
    Calculates and updates the stochastic tables with the calculations
    """
    table_name = f"{stock}_stoch"
    timestamp = data.get_timestamp(table_name)
    if timestamp is None:
        timestamp = data.get_timestamp(stock, desc=False)
    data.stoch_calc_update(stock, period, timestamp)

@timeit
def recalculate(stock):
    """
    Recalculates the stochastic data and overwrite the table
    """
    data.clear_stoch_calc(stock)
    calculate(stock)
    print(f"{stock} STOCH", end=" ")