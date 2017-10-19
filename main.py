import pandas as pd
import matplotlib.pyplot as plt
import pandas_datareader.data as web
import datetime
import numpy as np

start = '20150101'
end = datetime.date.today()

print('download AAPL ...')
apple = web.DataReader('AAPL', 'yahoo', start, end)

print('download MSFT ...')
microsoft = web.DataReader('MSFT', 'yahoo', start, end)

print('download GOOG ...')
google = web.DataReader('GOOG', 'yahoo', start, end)

stocks = pd.DataFrame({"AAPL": apple["Adj Close"], 
	"MSFT": microsoft["Adj Close"], 
	"GOOG": google["Adj Close"]})
  
# calculate return
stocks_return = stocks.apply(lambda x: x / x[0])

# calculate change per day
stock_change = stocks.apply(lambda x: np.log(x) - np.log(x.shift(1))) 

# draw
fig = plt.figure(facecolor='#000606')
plt.subplots_adjust(left=.12, bottom=.08, right=.95, top=.96, hspace=.0, wspace=.06)

g_stocks_return = plt.subplot2grid((8, 4), (0, 0), rowspan=4, colspan=4, facecolor='#000606')
g_stock_change = plt.subplot2grid((8, 4), (4, 0), sharex=g_stocks_return, rowspan=4, colspan=4, facecolor='#000606')

# *** graph return ***
g_stocks_return.set_title('return')
g_stocks_return.grid(linestyle='dotted')

g_stocks_return.yaxis.label.set_color('#00decc')

g_stocks_return.plot(stocks_return.index, stocks_return['AAPL'], label='AAPL', color='#00decc', linewidth=0.5)
g_stocks_return.plot(stocks_return.index, stocks_return['MSFT'], label='MSFT', color='#ffba00', linewidth=0.5)
g_stocks_return.plot(stocks_return.index, stocks_return['GOOG'], label='GOOG', color='#f600ff', linewidth=0.5)

g_stocks_return.legend(loc='upper left')
g_stocks_return.spines['bottom'].set_color('#037f7a')
g_stocks_return.spines['left'].set_color('#037f7a')
g_stocks_return.tick_params(axis='y', colors='#037f7a')
g_stocks_return.set_ylabel("stock's return")


# *** graph change ***
g_stock_change.set_title('return')
g_stock_change.grid(linestyle='dotted')

g_stock_change.yaxis.label.set_color('#00decc')

g_stock_change.plot(stock_change.index, stock_change['AAPL'], label='AAPL', color='#00decc', linewidth=0.5)
g_stock_change.plot(stock_change.index, stock_change['MSFT'], label='MSFT', color='#ffba00', linewidth=0.5)
g_stock_change.plot(stock_change.index, stock_change['GOOG'], label='GOOG', color='#f600ff', linewidth=0.5)

g_stock_change.legend(loc='upper left')
g_stock_change.spines['bottom'].set_color('#037f7a')
g_stock_change.spines['left'].set_color('#037f7a')
g_stock_change.tick_params(axis='y', colors='#037f7a')
g_stock_change.tick_params(axis='x', colors='#037f7a')
g_stock_change.set_ylabel('change per day')

plt.show()
