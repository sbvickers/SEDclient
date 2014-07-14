
import load as dl
import download as dw

def buildPhStruct(ra, dec):
    """
        Builds and fills a dictionary of photometric data for the SED.

        Parameters
        ----------
                ra : string
                Right-ascension in 'HH MM SS.S' format.

                dec : string
                Declination in '+/-DD MM SS.S' format.

        Returns
        ----------
                data : dictionary
                A dictionary of lists of wavelengths and fluxes.
    """
    data = {}

    if dl.dataExists('ph'):
        data = loadSource(data, sources, dl.loadPh)
    else:
        data = downSource(data, sources, dw.downPh, ra, dec)

    return data

def loadSource(data, sources, func):
    """
        Cycles through the sources and uses the given function to load either
        photometry or spectroscopy.

        Parameters
        ----------
                data : dictionary
                The data dictionary.

                sources : list
                The list of cats/surveys to get data for.

                func : function 
                The function to used to load the data either loadPh or loadSp.

        Returns
        ----------
                data : dictionary
                Returns the populated data dictionary.
    """
    for source in sources:
        currData = data[source] = {}
        currData['wave'], currData['flux'] = func(source)

    return data

def downSource(data, sources, func, ra, dec):
    """
        Cycles through the sources and uses the given function to download either
        photometry or spectroscopy.

        Parameters
        ----------
                data : dictionary
                The data dictionary.

                sources : list
                The list of cats/surveys to get data for.

                func : function 
                The function to used to download the data either downPh or downSp.

        Returns
        ----------
                data : dictionary
                Returns the populated data dictionary.
    """
    for source in sources:
        currData = data[source] = {}
        currData['wave'], currData['flux'] = func(ra, dec, source)

    return data

def buildSpStruct(ra, dec):
    """
        Builds and fills a dictionary of spectroscopic data for the SED.

        Parameters
        ----------
                ra : string
                Right-ascension in 'HH MM SS.S' format.

                dec : string
                Declination in '+/-DD MM SS.S' format.

        Returns
        ----------
                data : dictionary
                A dictionary of lists of wavelengths and fluxes.
    """
    data = {}

    if dl.dataExists('sp'):
        data = loadSource(data, sources, dl.loadSp)
    else:
        data = downSource(data, sources, dw.downSp, ra, dec)

    return data
