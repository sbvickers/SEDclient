"""
    This module is where the downloading of the photometry and spectroscopy
    happens. This module also checks the data against quality flags and returns
    the data in cgs spectral flux density.
"""

import subprocess
import configparser
import unitConversion as uc
import dataSave as ds
import globs

def downPh(source):
    """
        Downloads photometry from vizier for a given cat/survey 'source'.

        Parameters
        ----------
                source : string
                Name of the cat/survey to query.

        Returns
        ---------
                waves : list
                List of the wave lengths of the data points.

                fluxes : list of astropy.units ufloats
                The fluxes with corresponding units and uncertainties.
    """

    conf = configparser.ConfigParser()
    conf.read("{}{}.ini".format(globs.confPath, source))

    quer = queryParams(source)
    result = query(quer)
    fluxes, waves, zeros = reduction(result, source)

    if fluxes:
        cgsFluxes = []

        import numpy as np
        for f, w, z in zip(fluxes, waves, zeros):
            if not np.isnan(f.value.n):
                cgsFluxes.append(uc.convert(f, w, z)) 
    
        ds.savePh(cgsFluxes, waves, source)
    else:
        # logger.info("no {} photometric data found for {}.".format(source, name)
        return waves, None

    return waves, cgsFluxes

def downSp(source):
    """
        Downloads spectra from IRSA (ISO)
        "http://irsa.ipac.caltech.edu/data/SWS/spectra/sws/{}_sws.txt"

        Parameters
        ----------
                source : string
                Name of the cat/survey to query.

        Returns
        ---------
                waves : list
                List of the wave lengths of the data points.

                fluxes : list
                The fluxes for the spectra.
    """
    quer = queryParams(source)
    result = query(quer)

    TDT = getTDT(result)

    if not TDT:
        # logger.info("No ISO spectra found for {}".format(name))
        return None, None

    if len(TDT) != 8:
        TDT = "0{}".format(TDT)

    filename = "http://irsa.ipac.caltech.edu/data/SWS/spectra/sws/{}_sws.txt".format(TDT)

    wave, flux = getISO(filename)
    
    ds.saveSp(wave, flux, source)

    return wave, flux

def getISO(filename):
    """
        Gets and formats the ISO spectra.

        Parameters
        ----------
                filename : string
                The URL of the ISO spectra to download.

        Returns
        ----------
                wave : list
                A list of wavelengths in microns.

                flux : list of astropy.units ufloats
                A list of the corresponding fluxes for the spectra.
    """
    import urllib2
    from uncertainties import ufloat
    from astropy import units as u

    f = urllib2.urlopen(filename)
    wave, flux = [], []

    for line in f.readlines():
        data = [value for value in line.split()]
        if data[1] > 0:
            wave.append(data[0] * u.um)
            flux.append(uc.convert(ufloat(data[1], data[2]) * u.Jy, data[0]))

    f.close()

    return wave, flux

def getTDT(result):
    """
        Gets the TDT ID for the SWS01 ISO spectra.

        Parameters
        ----------
                result : list
                A list of lines of output from the query.

        Returns
        ----------
                TDT : string
                The TDT ID for the SWS01 ISO spectra.
    """
    for res in result:
        exclude = False
        if (res):
            for ele in ['#', '---', ' ', 'AOT']:
                if ele in res.split(';')[0]:
                    exclude = True
        else:
            exclude = True
            
        if not exclude:
            if 'SWS01' in res.split(';')[0]:
                return res.split(';')[1]

    return None

def getZeroPoints(conf):
    """
        Gets the zero magnitude fluxes from the .ini file for the source.

        Parameters
        ----------
                conf : configparser object
                The configparser object for a specific source.

        Returns
        ----------
                zeros : list of floats
                The zero magnitude fluxes in Jansky's.
    """

    zeros = conf['reduce']['zero']

    if zeros:
        return [float(x) for x in zeros.split()]
    else:
        return [None] * len(conf['reduce']['wave'].split())

def queryParams(source):
    """
        Makes a dictionary with the query parameters.

        Parameters
        ----------
                source : string
                Name of the catalogue to query. Each survey/source has a .ini
                file with the parameters for querying that survey/source.

        Returns
        ---------
                query : dictionary
                A dictionary of the parameters for the query.
    """

    query = {}

    query['object'] = "{} {}".format(globs.ra, globs.dec)

    conf = configparser.ConfigParser()
    conf.read("{}{}.ini".format(globs.confPath, source))

    for par in ['source', 'radius', 'max', 'output']:
        query[par] = conf['query'][par]

    return query

def query(params):
    """
        Performs vizieR query using the parameters in the dictionary 'params'

        Parameters
        ----------
                params : dictionary
                A dictionary listing the parameters of the query.

        Returns
        ---------
                result : list
                A list of the resulting data from the query.
    """

    query = "vizquery -source='{source}' -c='{object}' -c.rs='{radius}' -out='{output}' -sort='_r' -out.max='{max}' -mime='csv'".format(**params)

    (output, err) = subprocess.Popen(query, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()

    return output.split('\n')

def reduction(raw, source):
    """
        Reduces the raw data list by removing all the associated crap.

        Parameters
        ----------
                raw : list
                A list of the lines of data returned from the query.

                source : string
                The name of the data source being reduced.

        Returns
        ----------
                data : list
                A list of the requested data columns.
    """

    conf = configparser.ConfigParser()
    conf.read("{}{}.ini".format(globs.confPath, source))

    ex = ['#', '----'] + conf['reduce']['exclude'].split()
    waves = [float(w) for w in conf['reduce']['wave'].split()]
    
    for row in raw:
        exclude = False
        if (row):
            for ele in ex:
                if ele in row.split(';')[0]:
                    exclude = True
        else:
            exclude = True
            
        if not exclude:
            data = checkTypes(row.split(';'), conf['reduce']['types'].split())
            data, waves, zeros = checkUnits(data, conf['reduce']['units'].split(), source, waves)

            return data, waves, zeros
        
    return None, waves, None

def checkTypes(data, types):
    """
        Converts each element of the data list into the required data type.

        Parameters
        ----------
                data : list
                A list of the data from the query.

                types : list
                A list of the data types for each column of data.

        Returns
        ----------
                data : list
                A list of the data in the correct data type.
    """
    import numpy as np
    
    typeDict = {'int':int, 'float':float, 'string':str}

    for i in range(len(data)):
        if data[i].strip() == '':
            data[i] = np.nan
        else:
            data[i] = typeDict[types[i]](data[i])

    return data

def checkUnits(data, units, source, waves):
    """
        Checks the 'units' of the survey and converts the data list into a list
        of ufloats.

        Parameters
        ----------
            data : list
            A list of the data columns requested during the query.

            units : list
            A list of the units of each column of the data.

            source : string
            The name of the data source being reduced.

            waves : list
            List of the wavelengths of the data.

        Returns
        ----------
            data : list
            A list of ufloats of the data:

            waves : list
            List of the wavelengths of the data with invalid points removed.

            zeros : list
            List of the zero points of the data with invalid points removed.
    """
    from uncertainties import ufloat
    from astropy import units as u

    dat = [d for d in data if type(d) == float]
    qua = [q for q in data if type(q) == str]

    if len(qua) == 1:
        qua = [q for q in qua[0]]

    if qua:
        units *= len(qua)
    else:
        units *= len(dat) / 2

    units = [str(un) for un in units]

    for i in range(len(units)):
        dat[i] *= eval(units[i])
        if dat[i].unit.is_equivalent(u.percent):
            dat[i] = dat[i].decompose() * dat[i-1]

    redData = []

    for i in range(len(dat)/2):
        if dat[2*i].unit.is_equivalent(dat[2*i+1]):
            redData.append(ufloat(dat[2*i].value,dat[2*i+1].to(dat[2*i].unit).value) * dat[2*i].unit)
        else:
            #logger.warning("Units for data point and the error do not correspond")
            pass

    if len(redData) == len(qua):
        redData, waves, zeros = qualCheck(redData, qua, source, waves)
    elif not qua:
        redData, waves, zeros = qualCheck(redData, qua, source, waves)
    
    return redData, waves, zeros

def qualCheck(data, qual, source, waves):
    """
        Removes data points that don't fulfill the quality flag requirements.

        Parameters
        ----------
                data : list of astropy.units ufloats
                The list of the data points with errors and associated units.

                qual : list
                A list of the quality flags or signal-to-noise ratios.

                source : string
                The catalogue source.

                waves : list
                List of the wavelengths of the data.

        Returns
        ----------
                data : list of astropy.units ufloats
                Returns the list of data points with those points not satisfying
                the requirements removed.

                waves : list
                List of wavelengths with invalid data removed.

                zeros : list
                List of zero points with invalid data removed.
    """

    conf = configparser.ConfigParser()
    conf.read("{}{}.ini".format(globs.confPath, source))

    qualReq = conf['quality']['qual'].split()
    zeros = getZeroPoints(conf)

    if len(qualReq) > 1:
        for qua in reversed(qual):
            if qua not in qualReq:
                index = qual.index(qua)
                data.pop(index)
                waves.pop(index)
                if zeros:
                    zeros.pop(index)
    elif len(qualReq) == 0:
        return data, waves, zeros
    else:
        for qua in reversed(qual):
            if float(qua) < float(qualReq[0]):
                index = qual.index(qua)
                data.pop(index)
                waves.pop(index)
                if zeros:
                    zeros.pop(index)

    return data, waves, zeros
