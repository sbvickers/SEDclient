"""
    This module builds the data structure that houses the photometry and
    spectroscopy data. The data structure is a dictionary of photometric surveys
    i.e. data['iras'] where data['iras'] is a dictionary of wavelengths and
    fluxes i.e. data['iras'] has data['iras']['waves'] and
    data['iras']['fluxes'] which are lists of wavelengths and fluxes.
"""

import load as dl
import download as dw
import globs
import deredden as dr

def buildPhStruct():
    """
        Builds and fills a dictionary of photometric data for the SED.

        Parameters
        ----------
                None

        Returns
        ----------
                data : dictionary
                A dictionary of lists of wavelengths and fluxes.
    """
    data = {}

    if dl.dataExists():
        data = loadSource(data, dl.loadPh, globs.phSources)
    else:
        data = downSource(data, dw.downPh, globs.phSources)

    return data

def loadSource(data, func, sources):
    """
        Cycles through the sources and uses the given function to load either
        photometry or spectroscopy.

        Parameters
        ----------
                data : dictionary
                The data dictionary.

                func : function 
                The function to used to load the data either loadPh or loadSp.

                sources : list
                List of the cats/surveys to query.

        Returns
        ----------
                data : dictionary
                Returns the populated data dictionary.
    """
    for source in sources:
        currData = data[source] = {}
        currData['wave'], currData['flux'] = func(source)

    return data

def downSource(data, func, sources):
    """
        Cycles through the sources and uses the given function to download either
        photometry or spectroscopy.

        Parameters
        ----------
                data : dictionary
                The data dictionary.

                func : function 
                The function to used to download the data either downPh or downSp.

                sources : list
                List of cats/surveys to query.

        Returns
        ----------
                data : dictionary
                Returns the populated data dictionary.
    """
    for source in sources:
        currData = data[source] = {}
        currData['wave'], currData['flux'] = func(source)

    return data

def buildSpStruct():
    """
        Builds and fills a dictionary of spectroscopic data for the SED.

        Parameters
        ----------
                None

        Returns
        ----------
                data : dictionary
                A dictionary of lists of wavelengths and fluxes.
    """
    data = {}

    if dl.dataExists('iso'):
        data = loadSource(data, dl.loadSp, globs.specSources)
    else:
        data = downSource(data, dw.downSp, globs.specSources)

    return data
