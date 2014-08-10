#! /usr/bin/env python

from sedclient import sedPlot
from sedclient import globs

def main():
    """
        testing function
    """
    globs.name = 'ddd'
    globs.ra = '00 53 10.17'
    globs.dec = '-72 29 20.8'

    objectHandler = globs.logging.FileHandler("{}{}.log".format(globs.dirLog, globs.name.replace(' ', '_')))
    objectHandler.setLevel(globs.logging.DEBUG)
    objectHandler.setFormatter(fmt=globs.logFormat)

    globs.logger.addHandler(objectHandler)

    globs.logger.info('hello this is a test')
    
    SED = sedPlot.Plot()
    SED.plotPh()
    SED.plotSp()
    SED.annotate(globs.name)
    SED.legend()
    SED.saveSed()
    SED.show()

    globs.logger.removeHandler(objectHandler)

    globs.logger.warning('test of the warning system')

if __name__ == '__main__':
    main()

#if __name__ == '__main__':
#    main.main()
