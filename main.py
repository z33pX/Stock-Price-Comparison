import pandas as pd
from matplotlib.path import Path
from matplotlib.patches import BoxStyle
import matplotlib.pyplot as plt
import pandas_datareader.data as web
import datetime
import matplotlib.transforms as mtrans
from pathlib import Path as pl
import numpy as np

# Tutorial: https://ntguardian.wordpress.com/2016/09/19/introduction-stock-market-data-python-1/

colors_set = ['#00decc', '#ffba00', '#f600ff']


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


start = '20150101'
end = datetime.date.today()
file_path = 'prices_combined.ple'

## 1) *** download data ***

file = pl(file_path)

if file.exists():
    print('load data from file ...')
    stocks = pd.read_pickle(file_path)

else:
    print('download AAPL ...')
    apple = web.DataReader('AAPL', 'yahoo', start, end)

    print('download MSFT ...')
    microsoft = web.DataReader('MSFT', 'yahoo', start, end)

    print('download GOOG ...')
    google = web.DataReader('GOOG', 'yahoo', start, end)

    stocks = pd.DataFrame({"AAPL": apple["Adj Close"],
        "MSFT": microsoft["Adj Close"],
        "GOOG": google["Adj Close"]})

    print('save data to file ...')
    stocks.to_pickle(file_path)

print('draw ...')

## 2) *** calculate data ***

# calculate return
stocks_return = stocks.apply(lambda x: (x / x[0]) - 1)

# calculate change per day
stock_change = stocks.apply(lambda x: np.log(x) - np.log(x.shift(1))) 

## 3) *** draw data ***

BoxStyle._style_list["angled"] = MyStyle

fig = plt.figure(facecolor='#000606')
plt.subplots_adjust(left=.14, bottom=.13, right=.97, top=.96, hspace=.0, wspace=.06)

g_stocks_return = plt.subplot2grid((8, 4), (0, 0),
                                   rowspan=4, colspan=4, facecolor='#000606')

trans_offset = mtrans.offset_copy(g_stocks_return.transData, fig=fig,
                                  x=0.15, y=0.0, units='inches')

g_stock_change = plt.subplot2grid((8, 4), (4, 0), sharex=g_stocks_return,
                                  rowspan=4, colspan=4, facecolor='#000606')

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
g_stocks_return.yaxis.label.set_color('#00decc')
g_stocks_return.spines['bottom'].set_color('#037f7a')
g_stocks_return.spines['left'].set_color('#037f7a')
g_stocks_return.tick_params(axis='y', colors='#037f7a')
g_stocks_return.set_ylabel("stock's return")

legend = g_stocks_return.legend(loc='best', fancybox=True, framealpha=0.5)
legend.get_frame().set_facecolor('#000606')
for line,text in zip(legend.get_lines(), legend.get_texts()):
    text.set_color(line.get_color())

## *** graph change ***
i = 0
for column in stock_change:
    g_stock_change.plot(stock_change.index, stock_change[column],
                        label=column, color=colors_set[i], linewidth=0.5)

    i += 1

g_stock_change.grid(linestyle='dotted')
g_stock_change.yaxis.label.set_color('#00decc')
g_stock_change.legend(loc='upper left')
g_stock_change.spines['bottom'].set_color('#037f7a')
g_stock_change.spines['left'].set_color('#037f7a')
g_stock_change.tick_params(axis='y', colors='#037f7a')
g_stock_change.tick_params(axis='x', colors='#037f7a')
g_stock_change.set_ylabel('change per day')

legend = g_stock_change.legend(loc='best', fancybox=True, framealpha=0.5)
legend.get_frame().set_facecolor('#000606')
for line,text in zip(legend.get_lines(), legend.get_texts()):
    text.set_color(line.get_color())

labels = g_stock_change.get_xticklabels()
plt.setp(labels, rotation=30, fontsize=10)

plt.show()
