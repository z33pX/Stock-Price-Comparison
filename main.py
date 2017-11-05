import pandas as pd
from matplotlib.path import Path
from matplotlib.patches import BoxStyle
import matplotlib.pyplot as plt
import pandas_datareader.data as web
import datetime
import matplotlib.transforms as mtrans
from pandas_datareader._utils import RemoteDataError
import numpy as np

# Tutorial: https://ntguardian.wordpress.com/2016/09/19/introduction-stock-market-data-python-1/

colors_set = ['#00decc', '#ffba00', '#f600ff', '#00de1d', '#b7de00', '#de5700', '#b700de', '#4700de', '#0081de', '#de0000']


def truncate(f, n):
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])


class MyStyle(BoxStyle._Base):

    def __init__(self, pad=0.3):
        self.pad = pad
        super(MyStyle, self).__init__()

    def transmute(self, x0, y0, width, height, mutation_size):

        # padding
        pad = mutation_size * self.pad

        # width and height with padding added.
        width, height = width + 2.*pad, height + 2.*pad,

        # boundary of the padded box
        # x0 = x0 + 3 + width / 2
        x0, y0 = x0-pad, y0-pad,
        x1, y1 = x0+width, y0 + height

        cp = [(x0, y0),
              (x1, y0), (x1, y1), (x0, y1),
              (x0-pad, (y0+y1)/2.), (x0, y0),
              (x0, y0)]

        com = [Path.MOVETO,
               Path.LINETO, Path.LINETO, Path.LINETO,
               Path.LINETO, Path.LINETO,
               Path.CLOSEPOLY]

        path = Path(cp, com)

        return path


start = '20170101'
symbols = ['^GSPC', 'TSLA', 'MSFT', 'AAPL', 'GOOG', 'ORCL', 'AMZN', 'NFLX', 'FB2A', 'XOM',]
reload = True

## 1) *** download data ***

if reload:
    d = {}
    for s in symbols:
        print('downloading ' + s + ' ...')
        try:
            d[s] = web.DataReader(s, 'yahoo', start, datetime.date.today())['Adj Close']
        except RemoteDataError as rde:
            pass

    stocks = pd.DataFrame(d)
    pd.to_pickle(stocks, 'data.pcl')
else:
    stocks = pd.read_pickle('data.pcl')

print('draw ...')

## 2) *** calculate data ***

# calculate return
stocks_return = stocks.apply(lambda x: (x / x[0]) - 1)

# calculate change per day
stock_change = stocks.apply(lambda x: np.log(x) - np.log(x.shift(1))) 

## 3) *** draw data ***

BoxStyle._style_list["angled"] = MyStyle

fig = plt.figure(facecolor='#070d00')
plt.subplots_adjust(left=.09, bottom=.13, right=.97, top=.96, hspace=.22, wspace=.0)

g_stocks_return = plt.subplot2grid((8, 4), (0, 0),
                                   rowspan=4, colspan=4, facecolor='#070d00')

trans_offset = mtrans.offset_copy(g_stocks_return.transData, fig=fig,
                                  x=0.15, y=0.0, units='inches')

g_stock_change = plt.subplot2grid((8, 4), (4, 0), sharex=g_stocks_return,
                                  rowspan=4, colspan=4, facecolor='#070d00')

## *** graph return ***
i = 0
for column in stocks_return:
    g_stocks_return.plot(stocks_return.index, stocks_return[column],
                         label=column, color=colors_set[i], linewidth=0.5)


    value = stocks_return[column].tail(1)
    g_stocks_return.text(value.index, value.values, truncate(value.values[0], 2),
                         size=7, va="center", ha="center", transform=trans_offset,
                         bbox=dict(boxstyle="angled,pad=0.2", alpha=0.6, color=colors_set[i]))

    i += 1

g_stocks_return.grid(linestyle='dotted')
g_stocks_return.yaxis.label.set_color('#c9c9c9')
g_stocks_return.spines['left'].set_color('#c9c9c9')
g_stocks_return.spines['right'].set_color('#070d00')
g_stocks_return.spines['top'].set_color('#070d00')
g_stocks_return.spines['bottom'].set_color('#070d00')
g_stocks_return.tick_params(axis='y', colors='#c9c9c9')
g_stocks_return.tick_params(axis='x', colors='#070d00')
g_stocks_return.set_ylabel("stock's return")

legend = g_stocks_return.legend(loc='best', fancybox=True, framealpha=0.5)
legend.get_frame().set_facecolor('#070d00')
for line,text in zip(legend.get_lines(), legend.get_texts()):
    text.set_color(line.get_color())

## *** graph change ***
i = 0
for column in stock_change:
    g_stock_change.plot(stock_change.index, stock_change[column],
                        label=column, color=colors_set[i], linewidth=0.5)

    i += 1

g_stock_change.grid(linestyle='dotted')
g_stock_change.yaxis.label.set_color('#c9c9c9')
g_stock_change.spines['left'].set_color('#c9c9c9')
g_stock_change.spines['right'].set_color('#070d00')
g_stock_change.spines['top'].set_color('#070d00')
g_stock_change.spines['bottom'].set_color('#070d00')
g_stock_change.tick_params(axis='y', colors='#c9c9c9')
g_stock_change.tick_params(axis='x', colors='#c9c9c9')
g_stock_change.set_ylabel('change per day')

labels = g_stock_change.get_xticklabels()
plt.setp(labels, rotation=30, fontsize=10)

plt.show()
