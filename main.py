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

# colors_set = ['#00decc', '#ffba00', '#f600ff', '#00de1d', '#b7de00',
#               '#de5700', '#b700de', '#4700de', '#0081de', '#de0000']

colors_set = ['#de5700', '#00de1d', '#f600ff', '#00decc', '#ffba00',
              '#b7de00', '#b700de', '#4700de', '#0081de', '#de0000']

start = '20170101'
symbols = ['TSLA', 'MSFT', 'NFLX', 'AMZN', 'GOOG', 'AAPL']
# symbols = ['^GSPC', 'NFLX']
reload = True

# Colors:
label_colors = '#1b1b1b'  # '#c9c9c9'
background_color = '#f8ffef'  # '#070d00'

# 1) *** download data ***

if reload:
    _symbols = symbols
    stocks = pd.DataFrame()
    for s in _symbols:
        d = []
        temp_df = None
        try:
            print('downloading ' + s + ' ...')

            data = web.DataReader(s, 'morningstar', start, datetime.date.today())

            # calculate return
            x = pd.DataFrame(data['Close']).apply(lambda x: (x / x[0]) - 1)
            x.rename(columns={'Close': s}, inplace=True)
            d.append(x)

            # Volume
            x = pd.DataFrame(data['Volume'])
            x.rename(columns={'Volume': s + '_volume'}, inplace=True)
            d.append(x)

            # calculate change per day
            x = pd.DataFrame(data['Close']).apply(lambda x: np.log(x) - np.log(x.shift(1)))
            x.rename(columns={'Close': s + '_change'}, inplace=True)
            d.append(x)

        except RemoteDataError as rde:
            print('error downloading ' + s + ': ' + str(rde))
            symbols.remove(s)
        temp_df = pd.concat(d, axis=1).reset_index()
        stocks = stocks.append(temp_df)

    pd.to_pickle(stocks, 'data.pcl')

else:
    stocks = pd.read_pickle('data.pcl')[symbols]

# 2) *** plot data ***
print('plot ...')

fig = plt.figure(facecolor=background_color)
plt.subplots_adjust(left=.15, bottom=.08, right=.97, top=.96, hspace=.30, wspace=.0)

graph = []

graph.append(plt.subplot2grid((12, 4), (0, 0), rowspan=4, colspan=4, facecolor=background_color))
graph.append(plt.subplot2grid((12, 4), (4, 0), sharex=graph[0], rowspan=4, colspan=4, facecolor=background_color))
graph.append(plt.subplot2grid((12, 4), (8, 0), sharex=graph[0], rowspan=4, colspan=4, facecolor=background_color))

BoxStyle._style_list["angled"] = MyStyle
trans_offset = mtrans.offset_copy(graph[0].transData, fig=fig, x=0.15, y=0.0, units='inches')

i = 0
for s in symbols:

    graph[0].plot(stocks.index, stocks[s], label=s, color=colors_set[i], linewidth=0.5)

    """
    value = stocks[s].tail(1)
    graph[0].text(value.index, str(value.values), str(truncate(value.values[0], 2)),
                  size=7, va="center", ha="center", transform=trans_offset,
                  bbox=dict(boxstyle="angled,pad=0.2", alpha=0.6, color=colors_set[i]))
    """

    graph[1].plot(stocks.index, stocks[s + '_volume'], label=s + ' volume', color=colors_set[i], linewidth=0.5)

    graph[2].plot(stocks.index, stocks[s + '_change'], label=s + ' change', color=colors_set[i], linewidth=0.5)

    i += 1

for g in graph:
    g.grid(linestyle='dotted')
    g.yaxis.label.set_color(label_colors)
    g.spines['left'].set_color(label_colors)
    g.spines['right'].set_color(background_color)
    g.spines['top'].set_color(background_color)
    g.spines['bottom'].set_color(background_color)
    g.tick_params(axis='y', colors=label_colors)
    g.tick_params(axis='x', colors=background_color)

graph[0].set_ylabel("stock's return")
legend = graph[0].legend(loc='best', fancybox=True, framealpha=0.5)
legend.get_frame().set_facecolor(background_color)
for line,text in zip(legend.get_lines(), legend.get_texts()):
    text.set_color(line.get_color())

graph[1].set_ylabel('volume')

graph[2].set_ylabel('change per day')
graph[2].tick_params(axis='x', colors=label_colors)
labels = graph[2].get_xticklabels()
plt.setp(labels, rotation=30, fontsize=10)

plt.show()
