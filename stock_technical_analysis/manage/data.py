from sqlite3 import DatabaseError
import psycopg2
import pandas as pd
from configparser import ConfigParser
import yaml
from yaml.loader import SafeLoader
import datetime
from manage.utils import timeit

with open('./config/conf.yaml', 'r') as f:
    conf = yaml.load(f, Loader=SafeLoader)

def database_conn():
    """Connects to database specified in database.ini config file.
    Returns the connection object. User is responsible to close the connection after use."""
    parser = ConfigParser()
    parser.read(conf['db_params'])
    dbconfig = dict(parser.items('dbparams'))
    try:
        con = psycopg2.connect(**dbconfig)
        return con
    except psycopg2.DatabaseError as ex:
        raise psycopg2.DatabaseError from ex


def read_table(query):
    """
    Returns data from table
    """
    try:
        con = database_conn()
        curser = con.cursor()
        curser.execute(query)
        data = curser.fetchall()
        if curser.rowcount <= 0:
            return None, None
        columns = [desc[0] for desc in curser.description]
        return columns, data
    except (Exception, psycopg2.DatabaseError) as e:
        print(e)
    finally:
        curser.close()
        con.close()


def create_template_tables():
    """
    Creates template tables for stock, rsi and macd. 
    """
    try:
        con = database_conn()
        curser = con.cursor()
        with open('./sql/create-template-tables.sql', 'r') as f:
            sql = f.read()
        curser.execute(sql)
        con.commit()
    except (psycopg2.DatabaseError, Exception) as e:
        print(e)
    finally:
        con.close()
        curser.close()

@timeit
def create_tables(stock):
    """
    Creates tables for stock, rsi and macd of the provided stock.
    If table already exists then ignores.
    """
    try:
        con = database_conn()
        curser = con.cursor()
        with open('./sql/create-initials.sql', 'r') as f:
            sql = f.read()
        query = sql.format(
            stock=stock
        )
        curser.execute(query)
        con.commit()
        print(f"{stock}", end = " ")
    except (psycopg2.DatabaseError, Exception) as e:
        print(e)
    finally:
        curser.close()
        con.close()


def get_timestamp(table, desc = True):
    """
    Returns the last or first timestamp value of provided table based on desc value.
    if desc=True -> Last timestamp
    if desc=False -> First timestamp
    """
    try:
        con = database_conn()
        curser = con.cursor()
        order = 'desc' if desc else 'asc'
        query = f"select timestamp from {table} order by timestamp {order} limit 1"
        curser.execute(query)
        res = curser.fetchone()
        return res[0] if res else None
    except(psycopg2.DatabaseError, Exception) as e:
        print(e)
    finally:
        curser.close()
        con.close()


def rsi_macd_init(stock):
    """
    Fills rsi and macd tables with dates and close values from stock table.
    If dates already exists then ignores. In short sync dates and close with stock table.
    """
    try:
        con = database_conn()
        curser = con.cursor()
        with open('./sql/insert-stock-update.sql', 'r') as f:
            sql = f.read()
        rsitable=f"{stock}_rsi"
        macdtable=f"{stock}_macd"
        rsi_t = get_timestamp(rsitable)
        macd_t = get_timestamp(macdtable)
        rsi_t = datetime.datetime(1970, 1, 1) if not rsi_t else rsi_t
        macd_t = datetime.datetime(1970, 1, 1) if not macd_t else macd_t

        query = sql.format(
            rsitable=rsitable,
            macdtable=macdtable,
            stocktable=stock,
            timestamp_rsi=rsi_t,
            timestamp_macd=macd_t
        )
        curser.execute(query)
        con.commit()
    except(psycopg2.DatabaseError, Exception) as e:
        print(e)
    finally:
        curser.close()
        con.close()

def load(table, sql, csv_path):
    """
    Loads data from csv to provided table by validating timestamp value.
    """
    try:
        con = database_conn()
        curser = con.cursor()
        last = get_timestamp(table)
        timestamp = datetime.datetime(1970, 1, 1) if not last else last
        create_temp = sql['create_temp']
        copy = sql['copy']
        insert = sql['insert'].format(table=table,timestamp=timestamp)

        curser.execute(create_temp)
        with open(csv_path, 'r') as f:
            curser.copy_expert(copy, f)
        curser.execute(insert)
        con.commit()
    except psycopg2.DatabaseError as e:
        print(e.pgerror)
    except Exception as e:
        print(e)
    finally:
        curser.close()
        con.close()

def load_stock_table(stock, csv_path):
    """
    Loads the stock table with new values read from csv.
    If table not empty then it only updates the new dates else fills table from csv. 
    Also prints the execution time.
    """
    with open('./sql/load-data.yaml', 'r') as f:
        sql = yaml.load(f, Loader=SafeLoader)
    load(stock, sql, csv_path)


def load_rsi_table(stock, csv_path):
    """
    Loads the rsi table with new values read from csv with calculations.
    If table not empty then it only updates the new dates else fills table from csv. 
    Also prints the execution time.
    """
    with open('./sql/load-rsi.yaml', 'r') as f:
        sql = yaml.load(f, Loader=SafeLoader)
    load(stock+"_rsi", sql, csv_path)


def load_macd_table(stock, csv_path):
    """
    Loads the macd table with new values read from csv with calculations.
    If table not empty then it only updates the new dates else fills table from csv. 
    Also prints the execution time.
    """
    with open('./sql/load-macd.yaml', 'r') as f:
        sql = yaml.load(f, Loader=SafeLoader)
    load(stock+"_macd", sql, csv_path)


def db_to_df(columns, query):
    try:
        con = database_conn()
        cursor = con.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=columns)
        return df
    except(psycopg2.DatabaseError, Exception) as e:
        print(e)
    finally:
        cursor.close()
        con.close()


def get_last_calc(stock):
    """
    Get last macd rsi
    """
    try:
        con = database_conn()
        curser = con.cursor()
        with open("./sql/select.yaml", "r") as f:
            sql = yaml.load(f, Loader=SafeLoader)
        rsi_query = sql['pre_rsi'].format(stock=stock)
        macd_query = sql['pre_macd'].format(stock=stock)
        curser.execute(rsi_query)
        col_rsi = [desc[0] for desc in curser.description]
        rsi = dict(zip(col_rsi, curser.fetchone()))
        curser.execute(macd_query)
        col_macd = [desc[0] for desc in curser.description]
        macd = dict(zip(col_macd, curser.fetchone()))
        return {'rsi':rsi, 'macd': macd}
    except psycopg2.DatabaseError as ex:
        print(ex.pgerror())
    except Exception as ex:
        print(ex)
    finally:
        curser.close()
        con.close()
        

def update_rsi(stock, nexts):
    """
    Updates rsi with provided data
    """
    values = ",".join(list(map(str, nexts)))
    query = """insert into {stock}_rsi 
    (timestamp, close, gain, loss, avg_gain, avg_loss, rs, rsi) 
    values {values};""".format(stock=stock, values=values)
    try:
        con = database_conn()
        curser = con.cursor()
        curser.execute(query)
        con.commit()
    except psycopg2.DatabaseError as ex:
        print(ex.pgerror)
    except Exception as ex:
        print(ex)
    finally:
        curser.close()
        con.close()

def update_macd(stock, nexts):
    """
    Updates macd with provided data
    """
    values = ",".join(list(map(str, nexts)))
    query = """insert into {stock}_macd 
    (timestamp, close, ema12, ema26, macd, signal, hist) 
    values {values};""".format(stock=stock, values=values)
    try:
        con = database_conn()
        curser = con.cursor()
        curser.execute(query)
        con.commit()
    except psycopg2.DatabaseError as ex:
        print(ex.pgerror)
    except Exception as ex:
        print(ex)
    finally:
        curser.close()
        con.close()