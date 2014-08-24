from sedclient import sedPlot
from sedclient import globs

def make():
    """
        The function for building an SED for an object. Takes no inputs as they
        are taken from the globals 'globs' file.

        Parameters
        ----------
                None

        Returns
        ----------
                None
    """

    openLogger()

    # builds SED skeleton
    SED = sedPlot.Plot()

    # plots the data
    SED.plotPh()
    SED.plotSp()

    # ------------------------------------------- #
    # space here to call a fitting function and 
    # return some data to plot on the SED.
    # ------------------------------------------- #

    # standard annotations; name, ra, dec, ebv
    for annotation in makeAnns():
        SED.annotate(annotation)

    SED.legend()

    SED.saveSed()

    SED.show()

    closeLogger()

def makeAnns():
    """
        Prepares the strings for the Annotations. Takes no arguments as the data
        are taken from the globs module.

        Parameters
        ----------
                None

        Returns
        ----------
                Anns : list of strings
                The list of the strings that are to be annotated on the plot
                area.
    """
    annotations = []

    annotations.append("$\\rm{{ {} }}$".format(globs.name))
    coordStr = "$l={:.3F}^\circ, \,b={:.3F}^\circ$".format(globs.l, globs.b)
    annotations.append(coordStr)
    annotations.append("$\\rm{{ E(B-V) }}={}\pm{}\,\\rm{{ mag }}$".format(globs.ebv.n, globs.ebv.s))

    return annotations

def openLogger():
    """
        Opens a log file for each object.

        Parameters
        ----------
                None

        Returns
        ----------
                None
    """
    # sets up logging file for each object
    globs.objectHandler = globs.logging.FileHandler("{}{}.log".format(globs.dirLog, globs.name.replace(' ', '_')))
    globs.objectHandler.setLevel(globs.logging.DEBUG)
    globs.objectHandler.setFormatter(fmt=globs.logFormat)

    # adds new logging file to logger
    globs.logger.addHandler(globs.objectHandler)

    globs.logger.info("************************************************")
    globs.logger.info("Building SED for {}, added objectHandler to logger.".format(globs.name))

def closeLogger():
    """
        Closes the log file for each object.

        Parameters
        ----------
                None

        Returns
        ----------
                None
    """
    globs.logger.info("Finished building SED for {}, and removed objectHandler from logger.".format(globs.name))
    globs.logger.info("************************************************")

    globs.logger.removeHandler(globs.objectHandler)
