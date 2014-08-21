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
from uncertainties import ufloat
from astropy import units as u
import deredden as dr
import numpy as np

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

    kwargs = build_kwargs(result, conf)

    kwargs = reduction(**kwargs)

    steps = [checkTypes, checkUnits, qualCheck, convertFluxes]

    if kwargs['fluxes']:
        for step in steps:
            kwargs = step(**kwargs)

        kwargs['fluxes'] = list(dr.dered(kwargs['wave'], kwargs['fluxes'], globs.ebv))

        debugPrint(source, **kwargs)

        ds.savePh(kwargs['fluxes'], kwargs['wave'], source)

        return kwargs['wave'], kwargs['fluxes']

    globs.logger.info("no {} photometric data found for {}.".format(source, name))

    return None, None


def debugPrint(source, **kwargs):
    """
        A simple print statement to print the reduced and corrected data for
        each source.

        Parameters
        ----------
                source : string
                Name of survey/cat that has been queried.

                **kwargs : dictionary 
                A dictionary of parameters required to reduce the data.
    """
    print( "converted and reddened corrected fluxes for {}".format(source) )
    for w,f in zip(kwargs['wave'], kwargs['fluxes']):
        print( "wave = ", w, "um \t flux = ", f )


def build_kwargs(data, conf):
    """
        Builds a dictionary of kwargs to be used in the data reduction process.

        Parameters
        ----------
                data list
                A list of the requested data in raw form.

                conf : configparser
                The configparser object for a particular survey.

        Returns
        ----------
                kwargs : dictionary
                Dictionary of objects required to reduce the data.
    """

    kwargs = {}

    red_conf = conf['reduce']

    keys = ['wave', 'zero', 'units', 'types', 'exclude']
    val_types = [float, float, eval, eval, str]

    for key, val_type in zip(keys, val_types):
        kwargs[key] = [val_type(val) for val in red_conf[key].split()]

    kwargs['qualReq'] = conf['quality']['qual'].split()
    kwargs['fluxes'] = data

    return kwargs

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
    quer = queryParams("spec/" + source)
    result = query(quer)

    TDT = getTDT(result)

    if not TDT:
        # logger.info("No ISO spectra found for {}".format(name))
        return None, None

    if len(TDT) != 8:
        TDT = "0{}".format(TDT)

    filename = "http://irsa.ipac.caltech.edu/data/SWS/spectra/sws/{}_sws.txt".format(TDT)

    wave, flux = getISO(filename)
    
    flux = list(dr.dered(wave, flux, globs.ebv))

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

def reduction(**kwargs):
    """
        Reduces the raw data list by removing all the associated crap.

        Parameters
        ----------
                kwargs : dictionary
                Dictionary of objects required to reduce the data.

        Returns
        ----------
                kwargs : dictionary
                Dictionary of objects required to reduce the data.
    """
    kwargs['exclude'] += ['#', '---']

    for row in kwargs['fluxes']:
        exBool = False
        if row:
            for ele in kwargs['exclude']:
                if ele in row.split(';')[0]:
                    exBool = True
        else:
            exBool = True

        if not exBool:
            kwargs['fluxes'] = row.split(';')
            return kwargs
        else:
            kwargs['fluxes'] = None

    return kwargs

def checkTypes(**kwargs):
    """
        Converts each element of the data list into the required data type.

        Parameters
        ----------
                kwargs : dictionary
                Dictionary of objects required to reduce the data.

        Returns
        ----------
                kwargs : dictionary
                Dictionary of objects required to reduce the data.
    """
    import numpy as np

    data = kwargs['fluxes']
    types = kwargs['types']

    for i in range(0, len(kwargs['fluxes'])):
        if kwargs['fluxes'][i].strip() == '':
            kwargs['fluxes'][i] = np.nan
        else:
            kwargs['fluxes'][i] = kwargs['types'][i](kwargs['fluxes'][i])

    return kwargs

def get_qual(data):
    """
        Extracts the quality flag(s) from the data list.

        Parameters
        ----------
                data : list
                The list of the data returned from the query.

        Returns
        ----------
                qua : list
                A list of the quality flags if any exist.
    """
    qua = [q for q in data if type(q) == str]

    # for 2mass quality flag
    if len(qua) == 1:
        qua = [q for q in qua[0]]

    return qua

def checkUnits(**kwargs):
    """
        Checks the 'units' of the survey and converts the data list into a list
        of ufloats.

        Parameters
        ----------
                kwargs : dictionary
                Dictionary of objects required to reduce the data.

        Returns
        ----------
                kwargs : dictionary
                Dictionary of objects required to reduce the data.
    """
    kwargs['qua'] = get_qual(kwargs['fluxes'])
    kwargs['fluxes'] = [d for d in kwargs['fluxes'] if type(d) == float]

    fluxes = kwargs['fluxes']
    units = kwargs['units']

    if len(units) == 1:
        if units[0].is_equvalent(u.mag):
            p_data = [0.1 for d in fluxes] 
        else:
            p_data = [0.1 * d for d in fluxes]

        fluxes = [y for x in zip(fluxes, p_data) for y in x]
        units *= len(fluxes)
    elif len(units) == 2:
        if units[1].is_equivalent(u.percent):
            for i in range(1, len(units)*len(fluxes)/2, 2):
                fluxes[i] = (fluxes[i] / 100) * fluxes[i-1]
            units = [units[0]] * 2

        units *= len(fluxes) / 2

    fluxes = [x*y for x, y in zip(fluxes, units)]

    blendZip = zip(fluxes[0::2], fluxes[1::2])
    fluxes = [equiv_unit(val, err) for val, err in blendZip if equiv_unit(val, err)]

    kwargs['fluxes'] = fluxes
    kwargs['units'] = units

    return kwargs

def equiv_unit(val, err):
    """
        Compares the units of the value and its error and returns a ufloat
        combining the value and its error and the units if the units are
        equivalent otherwise returns false.

        Parameters
        ----------
                val : float + astropy.units
                The value of the datum with its units.

                err : float + astropy.units
                The error of the datum with its units.

        Returns
        ----------
                ufloat 
                Returns ufloat of the datum if units are equivalent otherwise
                will logger warning and return None.
    """
    if val.unit.is_equivalent(err):
        return ufloat(val.value, err.to(val.unit).value) * val.unit

    globs.logger.warning("Units for data point and the error do not correspond")

    return None

def qualCheck(**kwargs):
    """
        Removes data points that don't fulfill the quality flag requirements.

        Parameters
        ----------
                kwargs : dictionary
                A dictionary of the parameters used in the reduction of the
                data.

        Returns
        ----------
                kwargs : dictionary
                A dictionary of the parameters used in the reduction of the
                data.
    """

    if kwargs['qua']:
        if len(kwargs['qualReq']) == 1:
            kwargs = popBad('float(qua) < float(qualReq[0])', **kwargs)
        else:
            kwargs = popBad('qua not in qualReq', **kwargs)

    return kwargs

def popBad(cond, **kwargs):
    """
        Removes wavelengths and zeropoints for data that do not satisfy quality
        flags. Also removes data with errors larger than the actual data, data
        which is negative and has units not equivalent to magnitudes and nan's.

        Parameters
        ----------
                cond : string
                A string with the condition defining the type of quality flag
                the data has.

                **kwargs : dictionary
                A dictionary of the parameters for the data reduction.

        Returns
        ----------
                **kwargs : dictionary
                A dictionary of the parameters for the data reduction.
    """
    qualReq = kwargs['qualReq']
    qual = kwargs['qua']

    errCond = "kwargs['fluxes'][index].value.s > kwargs['fluxes'][index].value.n"
    negCond = "(kwargs['fluxes'][index].value.n < 0) & (not kwargs['fluxes'][index].unit.is_equivalent(u.mag))"
    nanCond = "np.isnan(kwargs['fluxes'][index].value.n)"

    for qua in reversed(qual):
        index = qual.index(qua)
        if (eval(cond)) or (eval(errCond)) or (eval(negCond)) or (eval(nanCond)):
            pops = ['fluxes', 'wave', 'zero']

            for pop in pops:
                if kwargs[pop]:
                    kwargs[pop].pop(index)

    return kwargs

def convertFluxes(**kwargs):
    """
        Function that uses the uc module to convert the data to spectral flux
        densities (erg/s/cm**2).

        Parameters
        ----------
                **kwargs : dictionary
                A dictionary of the parameters for the data reduction.

        Returns
        ----------
                **kwargs : dictionary
                A dictionary of the parameters for the data reduction.
    """
    wave = kwargs['wave']
    fluxes = kwargs['fluxes']
    zero = kwargs['zero']

    if zero:
        new_fluxes = [uc.convert(f, w, z) for f, w, z in zip(fluxes, wave, zero)]
    else:
        new_fluxes = [uc.convert(f, w) for f, w in zip(fluxes, wave)]

    kwargs['fluxes'] = new_fluxes

    return kwargs
