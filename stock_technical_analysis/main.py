import sys

from manage.rsi_calc import rsi_calc
from manage import data, data_loading

rsi_col= ['index', 'timestamp', 'close', 'gain', 'loss', 'avg_gain', 'avg_loss', 'rs', 'rsi']

def create_tables(*args):
    """
    Creates stock, rsi, macd tables for all stocks in 'stocklist'
    """
    if len(args) > 0 and len(args[0]) > 0:
        data.create_tables(args[0])
    else:
        data_loading.create_data_tables()


def load_data(*args):
    """
    Loads data from api to respective stock table.
    """
    if len(args) > 0 and len(args[0]) > 0:
        data_loading.load_stock(args[0])
    else:
        data_loading.load_all_stocks()


def test_connection():
    """Testing database connection based on params on database.ini file"""
    try:
        con = data.database_conn()
        if con:
            print("Database connection established.")
    except Exception as ex:
        print("Error Connecting database. Check connection parameters in database.ini")
    else:
        con.close()


def help():
    message = "Help is under process"
    print(message)


def display(*args):
    data_loading.update_calc(args[0])


def init_calc(*args):
    """
    Fill the rsi and macd tables with calculated data
    """
    if len(args) > 0 and len(args[0]) > 0:
        data_loading.load_calc(args[0])
    else:
        data_loading.load_all_calc()


def update_calc(*args):
    """
    Update calc to rsi and macd for missing dates present in stocks
    """
    if len(args) > 0 and len(args[0]) > 0:
        data_loading.update_calc(args[0])
    else:
        data_loading.update_all_calc()

if __name__ == "__main__":
    # try:
    if len(sys.argv) > 2:
        globals()[sys.argv[1]](*sys.argv[2:])
    else:
        globals()[sys.argv[1]]()
    # except KeyError as ex:
    #     print(f"{sys.argv[1]} method not available. Please check valid options with 'python manage.py help'")
    # except Exception as ex:
    #     print("Error:",ex)
