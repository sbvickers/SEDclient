#! /usr/bin/env python

from sedclient import sedPlot
from sedclient import globs
from sedclient import makeSED

def main():
    """
        testing function
    """
    globs.name = 'red rect'
    globs.ra = '06 19 58.2'
    globs.dec = '-10 38 14.69'
    globs.l = 122.0483
    globs.b = -4.5325
    from uncertainties import ufloat
    globs.ebv = ufloat(0.00,0.01)

    makeSED.make()

if __name__ == '__main__':
    main()

#if __name__ == '__main__':
#    main.main()
