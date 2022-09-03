import requests as req
import os
import yaml
import re
from yaml.loader import SafeLoader
from time import sleep
import pandas as pd

from manage import data
from manage.utils import timeit
from manage import macd_calc, rsi_calc

with open('./config/conf.yaml', 'r') as f:
    conf = yaml.load(f, Loader=SafeLoader)
api_url = conf['api_url']
api_key = conf['api_key']
data_dir = conf['data_dir']
offline = conf['offline']


with open('./config/stock-list.yaml', 'r') as f:
    stocklist = yaml.load(f, Loader=SafeLoader)['stocklist']


@timeit
def create_data_tables():
    """
    Compiles table name for special charactors of each stock.
    Creates table for stock, rsi and macd of all stocks in stocklist.
    Prints execution time as well.
    """
    regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
    print('Tables created for: ')
    for stock in stocklist:
        if regex.match(str(stock)) is None:
            data.create_tables(stock)
        else:
            print(f"Stock {stock} with special charactors is not allowed.")


@timeit
def load_stock(stock):
    """
    Reads data from api of current stock daily data and loads to respective table.
    """
    if offline:
        print("offline mode")
        filepath = os.path.join(data_dir, f'stock_{stock}.csv')
    else:
        url = api_url.format(stock=stock, api_key=api_key)
        res = req.get(url)
        filepath = os.path.join(data_dir, f'stock_{stock}.csv')
        with open(filepath, 'w') as f:
            f.write(res.text)
            f.close()
    data.load_stock_table(stock, filepath)
    print(stock, end=" ")


@timeit
def load_all_stocks():
    """
    Fills all stocks with current available data from api
    """
    count = 0
    for stock in stocklist:
        if count == 5:
            if not offline:
                sleep(60)
            count = 0
        load_stock(stock)
        count += 1
    print(f"{len(stocklist)} stocks")


@timeit
def load_calc(stock):
    """
    Update rsi and macd tables with macd and rsi values for provided stock.
    Initialize the table for first time caclulation.
    """
    with open(f"{conf['sql_path']}/select.yaml", 'r') as f:
        queries = yaml.load(f, Loader=SafeLoader)
    rsi_query = queries['load_stocks'].format(stock=stock)

    df = data.db_to_df(['timestamp', 'close'], rsi_query)
    rsi_calcs = rsi_calc.rsi_calc(df)
    macd_calcs = macd_calc.macd_calc(df)

    filepath = os.path.join(data_dir, f'rsi_{stock}.csv')
    print(filepath)
    rsi_calcs.to_csv(filepath, index=False)
    data.load_rsi_table(stock, filepath)

    filepath = os.path.join(data_dir, f'macd_{stock}.csv')
    print(filepath)
    macd_calcs.to_csv(filepath, index=False)
    data.load_macd_table(stock, filepath)

    print(stock, end=" ")


@timeit
def load_all_calc():
    """
    Update rsi and macd tables with macd and rsi values for all stocks in stocklist.
    Initialize the table for first time calculation.
    """
    for stock in stocklist:
        load_calc(stock)
    print(f"{len(stocklist)} stocks")


@timeit
def update_calc(stock):
    """
    Update the rsi and macd tables with calculations.
    It assumes that rsi and macd calculations are already initialized.
    It works only to update the calculation till end using the current calc's of rsi and macd.
    """
    last_calc = data.get_last_calc(stock)
    try:
        rsi_nexts = update_rsi(stock, last_calc['rsi'])
        data.update_rsi(stock, rsi_nexts)
        print(f"{stock}_rsi", end=" ")
    except ValueError as ex:
        print(ex)
    try:
        macd_nexts = update_macd(stock, last_calc['macd'])
        data.update_macd(stock, macd_nexts)
        print(f"{stock}_macd", end=" ")
    except ValueError as ex:
        print(ex)


def update_rsi(stock, prev):
    """
    Update rsi for next day by data of previous day
    """

    with open("./sql/select.yaml", "r") as f:
        sql = yaml.load(f, Loader=SafeLoader)
    columns, values = data.read_table(sql['update_rsi'].format(stock=stock))
    if columns is None or values is None:
        raise ValueError("RSI table {} is up to date already.".format(stock))
    nexts = []
    for d in values:
        n = rsi_calc.next(prev, d[columns.index('close')])
        prev = n
        nexts.append(
            (d[columns.index('timestamp')].strftime("%Y/%m/%d"), *prev.values()))
    return nexts


def update_macd(stock, prev):
    """
    Update macd for next day by data of previous day
    """
    with open("./sql/select.yaml", "r") as f:
        sql = yaml.load(f, Loader=SafeLoader)
    columns, values = data.read_table(sql['update_macd'].format(stock=stock))
    if columns is None or values is None:
        raise ValueError("MACD table {} is up to date already.".format(stock))
    nexts = []
    for d in values:
        n = macd_calc.next(prev, d[columns.index('close')])
        prev = n
        nexts.append(
            (d[columns.index('timestamp')].strftime("%Y/%m/%d"), *prev.values()))
    return nexts


@timeit
def update_all_calc():
    """Updates calc for all stocks"""
    for stock in stocklist:
        update_calc(stock)
    print(f"{len(stocklist)} stocks")


@timeit
def analyse_calcs(date):
    """Creates view of analysis"""
    check = re.compile("^(\d{2})\/(\d{2})\/(\d{4})$")
    if check.match(date) is not None:
        data.create_analytic_view(stocklist, date)
    else:
        raise ValueError("Date is invalid. Please use <dd/mm/yyyy> format.")


def view_analysis(query_num=1):
    """Prints the stocks as per setting of rsi and macd"""
    try:
        res = data.view_analysis(
            conf['uphist'], conf['lowhist'], conf['uprsi'], conf['lowrsi'], query_num)
        columns = ['stock', 'timestamp', 'close',
                   'macd', 'signal', 'hist', 'rsi']
        df = pd.DataFrame(res, columns=columns)
        print(df.to_string())
    except Exception as ex:
        print(ex)


@timeit
def recalculate(stock):
    """Recalculates the rsi and macd based on data in stock tables"""
    data.clear_rsi_macd(stock)
    load_calc(stock)


@timeit
def recalculate_all():
    """Recalculates the rsi and macd for all stock based on data in stock tables."""
    for stock in stocklist:
        recalculate(stock)
    print(f"{len(stocklist)} stocks")
