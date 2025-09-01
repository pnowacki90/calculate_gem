import psycopg2
from config import load_config
import logging
from datetime import date
from datetime import timedelta

logger = logging.getLogger(__name__)

def get_closest_date_data(ticker, diff):
    logging.basicConfig(filename='/usr/local/files/gem.log', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s')
    logger.info("Loading DB connection config.")
    config = load_config()
    try:
        with  psycopg2.connect(**config) as conn:
            cur = conn.cursor()
            logger.info("Connected to the DB.")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        print(error)

    for i in range(0, 10):
        test_date = (date.today() - timedelta(days=i) - timedelta(days=diff)).isoformat()
        sql = "SELECT ticker, day, close_price FROM beta WHERE day=%s AND ticker=%s;"
        sql_parameters = (test_date, ticker)
        try:
            cur.execute(sql, sql_parameters)
            sql_output = cur.fetchone()
            if sql_output is None:
                log_warn = "Data from " + test_date + " for " + ticker + " is missing from the DB. Testing next day..."
                print(log_warn)
                logger.warning(log_warn)
                continue
            else:
                log_info = "Data for " + ticker + " from " + test_date + " is available. Using."
                print(log_info)
                logger.info(log_info)
                cur.close()
                conn.close()
                return sql_output
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            print(error)

def calculate_ytd_profit(ticker):
    todays_data = get_closest_date_data(ticker, 1)
    year_old_data = get_closest_date_data(ticker, 365)
    profit = round((todays_data[2] - year_old_data[2]) / year_old_data[2], 5)
    logger.info("ticker=%s, last year profit=%s", ticker, profit)
    return profit

if __name__ == '__main__':
    highest_profit = ['INIT', 0.00]
    with open('/usr/local/files/tickers.txt', 'r') as file:
        tickers = [line.strip() for line in file]
    for ticker in tickers:
        profit = calculate_ytd_profit(ticker)
        logger.info("%s ticker returned %s%% in the last 12 months.", ticker, round(profit * 100, 2))
        if profit > highest_profit[1]:
            highest_profit[0] = ticker
            highest_profit[1] = profit
    print(highest_profit)
    logger.info("GEM winner as of %s with %s%% profit is %s!", date.today().isoformat(), round(highest_profit[1] * 100, 2), highest_profit[0])
