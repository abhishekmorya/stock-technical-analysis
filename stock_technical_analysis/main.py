import sys

from manage import data, data_loading


def create_tables(*args):
    """
    Creates stock, rsi, macd tables for all stocks in 'stocklist'
    """
    if len(args) == 1 and len(args[0]) > 0:
        data.create_tables(args[0])
    else:
        data_loading.create_data_tables()


def create_templates(*args):
    """create template tables for stock, rsi and macd"""
    data.create_template_tables()


def load(*args):
    """
    Loads data from api to respective stock table.
    """
    if len(args) == 1 and len(args[0]) > 0:
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
    with open("./config/help.txt", 'r') as f:
        doc = f.read()
    print(doc)


def analyse(*args):
    """Creates the analytic view"""
    if len(args) == 1 and len(args[0]) > 0:
        data_loading.analyse_calcs(args[0])
    else:
        print("provide date as 'python main.py view 29/08/2022' <dd/mm/yyyy> format.")


def recalculate(*args):
    """Recalculates the rsi/macd values based on data from stock table"""
    if len(args) == 1 and len(args[0]) > 0:
        data_loading.recalculate(args[0])
    else:
        data_loading.recalculate_all()


def view(*args):
    """To View the analysis saved in analytic_vw"""
    if len(args) == 1 and len(args[0]) > 0:
        if not str.isnumeric(args[0]):
            raise ValueError(
                "Only numeric value is allowed for Query number. Check 'python main.py help'")
        data_loading.view_analysis(query_num=int(args[0]))
    else:
        data_loading.view_analysis(1)


def init_calc(*args):
    """
    Fill the rsi and macd tables with calculated data
    """
    if len(args) > 0 and len(args[0]) > 0:
        data_loading.load_calc(args[0])
        data_loading.update_stoch(args[0])
    else:
        data_loading.load_all_calc()


def update(*args):
    """
    Update calc to rsi and macd for missing dates present in stocks
    """
    if len(args) == 1 and len(args[0]) > 0:
        data_loading.update_calc(args[0])
        data_loading.update_stoch(args[0])
    else:
        data_loading.update_all_calc()

def test(*args):
    if len(args) == 1 and len(args[0]) > 0:
        data_loading.update_stoch(args[0])
    else:
        print("Arguments not passed")

if __name__ == "__main__":
    # if len(sys.argv) > 2:
    #     globals()[sys.argv[1]](*sys.argv[2:])
    # else:
    #     globals()[sys.argv[1]]()
    try:
        if len(sys.argv) > 2:
            globals()[sys.argv[1]](*sys.argv[2:])
        else:
            globals()[sys.argv[1]]()
    except KeyError as ex:
        print(f"{sys.argv[1]} method not available. Please check valid options with 'python manage.py help'")
    except Exception as ex:
        print("Error:", ex)
