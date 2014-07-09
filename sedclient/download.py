
import subprocess
import configparser

def downPhoto(ra, dec):
    """
        Downloads photometry from vizier
    """

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

def reduce(raw, source):
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
            #data = checkUnits(data, conf['reduce']['units'].split())

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

def checkUnits(data, units):
    """
        Checks the 'units' of the survey and converts the data list into a list
        of ufloats.

        Parameters
        ----------
            data : list
            A list of the data columns requested during the query.

            units : list
            A list of the units of each column of the data.

        Returns
        ----------
            data : list
            A list of ufloats of the data:
    """
    from uncertainties import ufloat

    dat = [d for d in data if type(d) == float]
    qua = [q for q in data if type(q) == str]

    redData = []

    for i in range(len(dat) / 2):
        redData.append(ufloat(dat[2*i],dat[2*i+1]))

    print redData

    if len(redData) == len(qua):
        print 'do some quality check'
        pass
    
    return data
