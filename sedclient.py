#! /usr/bin/env python

from sedclient import sedPlot
from sedclient import globs
from sedclient import makeSED

def main():
    """
        testing function
    """
    globs.name = 'clover'
    globs.ra = '19 49 54.91'
    globs.dec = '+24 08 53.30'
    globs.l = 122.0483
    globs.b = -4.5325
    from uncertainties import ufloat
    globs.ebv = ufloat(0.04,0.01)

    makeSED.make()

if __name__ == '__main__':
    main()

#if __name__ == '__main__':
#    main.main()
