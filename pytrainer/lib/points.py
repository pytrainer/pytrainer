"""Encode/decode Google Maps points encoding
Matt King, 2005-06-16
"""

from __future__ import print_function
import random

def decodePoints(points):
    """Decodes a string of locations encoded using the GMap encoding
    Accepts the encoded string and
    returns an array of lat/lon pairs [lat1,lon1,lat2,lon2,...]"""
    if not points:
        return []
    Ch = len(points)
    pb = 0
    locations = []
    Ka = 0
    Pa = 0
    while pb < Ch:
        oc = 0
        Fa = 0
        while 1:
            ub = ord(points[pb])-63
            pb += 1
            Fa |= (ub&31)<<oc
            oc += 5
            if ub < 32: break
        if Fa & 1: i = ~(Fa>>1)
        else: i = Fa>>1
        Ka = Ka+i
        locations.append(Ka*1.0E-5)

        oc = 0
        Fa = 0
        while 1:
            ub = ord(points[pb])-63
            pb += 1
            Fa |= (ub&31)<<oc
            oc += 5
            if ub < 32: break
        if Fa & 1: i = ~(Fa>>1)
        else: i = Fa>>1
        Pa = Pa+i

        locations.append(Pa*1.0E-5)

    return locations


def encodePoints(locations):
    """Encodes lat/lon locations into a Gmap polyline encoding.
    Accepts an array of lat/lon pairs [lat1,lon1,lat2,lon2,...] and
    returns 2 strings, the encoded points and the corresponding levels"""
    points = []
    levels = []
    xo = yo = 0
    for i in locations:
        y = int(float(i[0])*100000)
        yd = y - yo
        yo = y
        f = (abs(yd) << 1) - (yd<0)
        while 1:
            e = f & 31
            f >>= 5
            if f:
                e |= 32
            points.append(chr(e+63))
            if f == 0: break

        x = int(float(i[1])*100000)
        xd = x - xo
        xo = x
        f = (abs(xd) << 1) - (xd<0)
        while 1:
            e = f & 31
            f >>= 5
            if f:
                e |= 32
            points.append(chr(e+63))
            if f == 0: break

        levels.append(nextLevel())
    levels[0] = 'B'
    levels[-1] = 'B'
    return "".join(points), "".join(levels)

def nextLevel():
    r = random.random()
    if r < 0.65: return '?'
    if r < 0.92: return '@'
    if r < 0.97: return 'A'
    return 'B'

if __name__ == '__main__':
    locs = [(38.5, -120.2), (40.7, -120.95), (43.252, -126.453)]
    locs = [(37.4419, -122.1419),(37.4519, -122.1519),( 37.4619, -122.1819)]
    points, levels = encodePoints(locs)
    print(points)
    print(levels)
    decodedLocs = decodePoints(points)
    print(decodePoints(points))
    def _cmpFloat(x,y):
        if abs(x-y) > 0.0001: return 0
        return 1

    assert(len(locs) == len(decodedLocs))
    assert(len(levels) == 3)
    for i in range(len(locs)):
        assert(_cmpFloat(locs[i], decodedLocs[i]))

    
