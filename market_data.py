from binance.client import Client
import time

class Get_data():
    def __init__(self,symbol,timeframe,start_date,end_date):
        self.client = Client()

        self.symbol = symbol
        self.timeframe = self.get_timeframe(timeframe)
        self.uend_date = end_date #u stands for unformatted
        self.start_date = self.format_date(start_date)
        self.end_date = self.format_date(end_date)

        self.close_prices = []

        self.add_data(self.get_data())

    def format_date(self,date):
        date = time.strptime(date,'%d-%m-%Y')
        day = date.tm_mday
        month = self.get_month(date.tm_mon)
        year = date.tm_year
        return str(day)+' '+month+','+' '+str(year)

    def get_month(self,month):
        switch = {
            1: 'Jan',
            2: 'Feb',
            3: 'Mar',
            4: 'Apr',
            5: 'May',
            6: 'Jun',
            7: 'Jul',
            8: 'Aug',
            9: 'Sep',
            10: 'Oct',
            11: 'Nov',
            12: 'Dec'
        }
        return switch.get(month,'Invalid month')
        
    def get_timeframe(self,timeframe):
        switch = {
            '1m': Client.KLINE_INTERVAL_1MINUTE,
            '3m': Client.KLINE_INTERVAL_3MINUTE,
            '5m': Client.KLINE_INTERVAL_5MINUTE,
            '15m': Client.KLINE_INTERVAL_15MINUTE,
            '30m': Client.KLINE_INTERVAL_30MINUTE,
            '1h': Client.KLINE_INTERVAL_1HOUR,
            '2h': Client.KLINE_INTERVAL_2HOUR,
            '4h': Client.KLINE_INTERVAL_4HOUR,
            '6h': Client.KLINE_INTERVAL_6HOUR,
            '8h': Client.KLINE_INTERVAL_8HOUR,
            '12h': Client.KLINE_INTERVAL_12HOUR,
            '1D': Client.KLINE_INTERVAL_1DAY,
            '3D': Client.KLINE_INTERVAL_3DAY,
            '1W':Client.KLINE_INTERVAL_1WEEK,
            '1M':Client.KLINE_INTERVAL_1MONTH
        }
        return switch.get(timeframe, 'Invalid timeframe')

    def get_data(self):
        print('Getting historical data', end='\n')
        return self.client.get_historical_klines(self.symbol, self.timeframe, self.start_date, self.end_date)

    def add_data(self,historical_data):
        for idx, val in enumerate(historical_data):
            self.close_prices.append(float(val[4]))



