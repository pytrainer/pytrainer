import time, datetime
from matplotlib.numerix import *
from matplotlib.numerix.mlab import *
from matplotlib.dates import date2num


def load_quotes(fname, maxq=None):
    """
    Load quotes from the representative data files vineet sent If any
    of the values are missing I force all missing.  Quotes are sorted
    in increasing time.  Return value is a list of tuples

      (epoch, open, high, low, close, volume )
    """
    quotes = []
    
    for i, line in enumerate(file(fname)):
        if maxq is not None and i>maxq: break
        ts,o,h,l,c,v = line.split(',')

        dt = datetime.datetime(*time.strptime(ts.strip('"'), '%Y%m%d%H%M%S')[:6]) # convert to float days
        d = date2num(dt)
        o,h,l,c,v = [float(val) for val in o,h,l,c,v]

        if o==-1 or h==-1 or l==-1 or c==-1 or v==-1:
            o,h,l,c,v = -1, -1, -1, -1,-1
        quotes.append((d,o,h,l,c,v))

    quotes.sort()  # increasing time
    return quotes


def ema(s, n):
    """
    returns an n period exponential moving average for
    the time series s

    s is a list ordered from oldest (index 0) to most recent (index
    -1) n is an integer

    returns a numeric array of the exponential moving average
    """
    s = array(s)
    ema = []
    j = 1
    #get n sma first and calculate the next n period ema
    sma = sum(s[:n]) / n
    multiplier = 2 / float(1 + n)
    ema.append(sma)
    #EMA(current) = ( (Price(current) - EMA(prev) ) xMultiplier) + EMA(prev)
    ema.append(( (s[n] - sma) * multiplier) + sma)
    #now calculate the rest of the values
    for i in s[n+1:]:
        tmp = ( (i - ema[j]) * multiplier) + ema[j]
        j = j + 1
        ema.append(tmp)
    return ema

def movavg(s, n):
    """
    returns an n period moving average for the time series s
       
    s is a list ordered from oldest (index 0) to most recent (index -1)
    n is an integer

        returns a numeric array of the moving average

    See also ema in this module for the exponential moving average.
    """
    s = array(s)
    c = cumsum(s)
    return (c[n-1:] - c[:-n+1]) / float(n-1)

def fill_over(ax, x, y, val, color, over=True):
    """
    Plot filled x,y for all y over val
    if over = False, fill all areas < val
    """
    ybase = asarray(y)-val
    crossings = nonzero(less(ybase[:-1] * ybase[1:],0))
    
    if ybase[0]>=0: fillon = over
    else:           fillon = not over


    indLast = 0
    for ind in crossings:        
        if fillon:
            thisX = x[indLast:ind+1]
            thisY = y[indLast:ind+1]
            thisY[0] = val
            thisY[-1] = val
            ax.fill(thisX, thisY, color)
        fillon = not fillon
        indLast = ind

    
def random_signal(N, tau):
    'generate a length N  random signal with time constant tau'
    t = arange(float(N))
    filter = exp(-t/tau)
    return convolve( randn(N), filter, mode=2)[:len(t)]

