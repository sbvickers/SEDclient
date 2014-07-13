
import configparser
from astropy import units as u
from uncertainties import ufloat 

loadDirPh = "data/photometry/"
loadDirSp = "data/spectroscopy/"
loadDirSed = "data/sed/"

def loadPh(source):
    """
        Loads photometric data from saved data files.

        Parameters
        ----------
                source : string
                The name of the cat/survey to retrieve data for.

        Returns
        ----------
                wave : list
                A list of the wavelengths of the cat/survey.

                fluxes : list of astropy.units ufloats
                The fluxes at each of the wavelengths with uncertainties and
                units.
    """

    conf = configparser.ConfigParser()
    conf.read("{}{}_red".format(loadDirPh, name))

    wave = [float(w) for w in conf[source]['wave'].split()]
    fluxVec = [float(f) for f in conf[source]['red'].split()]

    flux = fluxVec[0::2]
    e_flux = fluxVec[1::2]

    fluxes = []

    for f, e in zip(flux, e_flux):
        point = ufloat(f, e) * (u.erg/u.s/u.cm**2)
        fluxes.append(point)

    return wave, fluxes

def loadSp(source):
    """
        Loads photometric data from saved data files.

        Parameters
        ----------
                source : string
                The name of the cat/survey to retrieve spectra for.

        Returns
        ----------
                wave : list
                A list of the wavelengths of the spectra.

                flux : list of astropy.units ufloats
                The fluxes at each of the wavelengths with uncertainties and
                units.
    """
    import csv

    wave, flux = [], []

    with open("{}{}_{}".format(loadDirSp, name, source), 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            wave.append(float(row[0]))
            point = ufloat(float(row[1]), float(row[2])) * (u.erg/u.s/u.cm**2)
            flux.append(point)

    f.close()

    return wave, flux

