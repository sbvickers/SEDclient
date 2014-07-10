
import subprocess
import configparser

def downPhoto(ra, dec):
    """
        Downloads photometry from vizier
    """

    for source in sources:
        quer = queryParams(source, ra, dec)
        result = query(q)
        # save raw data
        result = reduction(result, source)
        # save reduced data

    return result

def queryParams(source, ra, dec):
    """
        Makes a dictionary with the query parameters.

        Parameters
        ----------
                source : string
                Name of the catalogue to query. Each survey/source has a .ini
                file with the parameters for querying that survey/source.

                ra : string
                The right ascension of the object/region to query.

                dec : string 
                The declination of the object/region to query.

        Returns
        ---------
                query : dictionary
                A dictionary of the parameters for the query.
    """

    query = {}

    query['object'] = "{} {}".format(ra, dec)

    conf = configparser.ConfigParser()
    conf.read("config/{}.ini".format(source))

    for par in ['source', 'radius', 'max', 'output']:
        query[par] = conf['query'][par]

    # get rest of parameters from source .ini file

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
    conf.read("config/{}.ini".format(source))

    ex = ['#', '----'] + conf['reduce']['exclude'].split()

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
            data = checkUnits(data, conf['reduce']['units'].split(), source)

            return data
        
    return None

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

def checkUnits(data, units, source):
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

        Returns
        ----------
            data : list
            A list of ufloats of the data:
    """
    from uncertainties import ufloat
    from astropy import units as u

    dat = [d for d in data if type(d) == float]
    qua = [q for q in data if type(q) == str]

    if len(qua) == 1:
        qua = [q for q in qua]

    units *= len(qua)

    for i in range(len(units)):
        dat[i] *= eval(units[i])
        if dat[i].unit.is_equivalent(u.percent):
            dat[i] = dat[i].decompose() * dat[i-1]

    redData = []

    for i in range(len(qua)):
        if dat[2*i].unit.is_equivalent(dat[2*i+1]):
            redData.append(ufloat(dat[2*i].value,dat[2*i+1].value) * dat[2*i].unit)
        else:
            pass
            #logger.warning("Units for data point and the error do not correspond")

    if len(redData) == len(qua):
        redData = qualCheck(redData, qua, source)
    
    return redData

def qualCheck(data, qual, source):
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

        Returns
        ----------
                data : list of astropy.units ufloats
                Returns the list of data points with those points not satisfying
                the requirements removed.
    """

    conf = configparser.ConfigParser()
    conf.read("config/{}.ini".format(source))

    qualReq = conf['quality']['qual'].split()

    if len(qualReq) > 1:
        for qua in qual:
            if qua not in qualReq:
                index = qual.index(qua)
                data.pop(index)
    else:
        for qua in qual:
            if float(qua) < qual:
                index = qual.index(qua)
                data.pop(index)

    return data
