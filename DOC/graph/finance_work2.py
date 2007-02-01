"""
You need a additional files to run this example.  Save the following
in the same dir as this file

  http://matplotlib.sourceforge.net/screenshots/helpers.py

  http://matplotlib.sourceforge.net/screenshots/msft_nasdaq_d.csv

  http://matplotlib.sourceforge.net/screenshots/__init__.py

"""
from __future__ import division
import time, os, sys
from helpers import load_quotes, movavg, fill_over, random_signal
from matplotlib import rcParams



from matplotlib.ticker import  IndexLocator, FuncFormatter, NullFormatter, MultipleLocator
from matplotlib.dates import IndexDateFormatter
from matplotlib.finance import candlestick2, plot_day_summary2, volume_overlay, index_bar
from pylab import *

rcParams['timezone'] = 'US/Eastern'
rc('grid', color=0.75, linestyle='-', linewidth=0.5)

fname = 'msft_nasdaq_d.csv'
quotes = load_quotes(fname, 200)
times, opens, highs, lows, closes, volumes = zip(*quotes)

def get_valid(x):
    return array([thisx for thisx in x if thisx!=-1])
#valid opens, etc
vopens   = get_valid(opens)
vcloses  = get_valid(closes)
vlows    = get_valid(lows)
vhighs   = get_valid(highs)
vvolumes = get_valid(volumes)
vind = array([i for i, o in enumerate(opens) if o!=-1])

assert(len(vopens)==len(vcloses)==len(vlows)==len(vhighs)==len(vvolumes))

N = len(vopens)

figBG   = 'w'        # the figure background color
axesBG  = '#f6f6f6'  # the axies background color
textsize = 8        # size for axes text

# the demo data are intc from (2003, 9, 1) to (2004, 4, 12 ) with
# dates as epoch; I saved these to a file for ease of debugginh
ticker = 'MSFT'


figure(1, facecolor=figBG)

def get_locator():
    """
    the axes cannot share the same locator, so this is a helper
    function to generate locators that have identical functionality
    """
    
    return IndexLocator(10, 1)


formatter =  IndexDateFormatter(times, '%b %d %y')

nullfmt   = NullFormatter()         # no labels

def fmt_vol(x,pos):
    if pos>3: return ''  # only label the first 3 ticks
    return '%dM' % int(x*1e-6)

volumeFmt = FuncFormatter(fmt_vol)

left, width = 0.1, 0.8
rect2 = [left, 0.3, width, 0.4]
axMiddle     = axes(rect2, axisbg=axesBG)
axMiddleVol  = axes(rect2, axisbg=axesBG, frameon=False)  # the volume overlay


# set up two scales on middle axes with left and right ticks
axMiddle.yaxis.tick_left()
axMiddle.xaxis.set_major_locator( get_locator() )
axMiddle.yaxis.set_major_locator( MultipleLocator(5) )
axMiddle.xaxis.set_major_formatter(nullfmt)

axMiddleVol.yaxis.tick_right()    
axMiddleVol.xaxis.set_major_locator( get_locator() )
axMiddleVol.xaxis.set_major_formatter(nullfmt)
axMiddleVol.yaxis.set_major_formatter(volumeFmt)
axMiddle.grid(True)    

if 1:  ############### Middle axes #################

    #Estas son las leyendas del color
    left, height, top = 0.025, 0.06, 0.9
    t2 = axMiddle.text(left, top-height, 'MA(5)', color='b', fontsize=textsize, transform=axMiddle.transAxes)
    t3 = axMiddle.text(left, top-2*height, 'MA(20)', color='r', fontsize=textsize, transform=axMiddle.transAxes)

    # make up two signals; I don't know what the signals are in real life
    # so I'll just illustrate the plotting stuff
    s1 = random_signal(len(vind), 10)
    s2 = random_signal(len(vind), 20)
    print vind
    purple = '#660033'

    axMiddle.plot(vind, s1, color="b")
    axMiddle.plot(vind, s2, color='k', linewidth=1.0)
    
    thresh = 0
    # lower horiz line
    print N
    print "que es N"
    axMiddle.plot( (0, N), [-thresh, -thresh], color=purple, linewidth=1)  
    
    axMiddle.yaxis.set_major_locator(MultipleLocator(5))

    fill_over(axMiddle, vind, s1,  0,  purple, over=True)
    fill_over(axMiddle, vind, s1,  0,  purple,  over=False)

    # now add some text
    # make sure everyone has the same axes limits

    setp(axMiddle.get_xticklabels(), 'rotation', 45,
        'horizontalalignment', 'right', fontsize=8)

# force all the axes to have the same x data limits
allAxes = (axMiddle, axMiddleVol)
#allAxes = (axUpper, axMiddle, axMiddleVol, axLower)
xlim = 0, len(quotes)
for a in allAxes:
    a.dataLim.intervalx().set_bounds(*xlim)
    a.set_xlim(xlim)

show()
