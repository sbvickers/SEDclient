"""
    This module is designed to convert spectral flux densities and magnitudes
    into spectral flux densities in cgs units i.e. erg/s/cm^2.
"""

from astropy import units as u
import globs

c = 2.9979246e10 * u.cm / u.s
cgsBase = [u.g,u.cm,u.s]

def convert(val, wave, zero=None):
    """
        Converts astronomical spectral flux densities into erg/s/cm**2.

        Parameters
        ----------
                val : ufloat, astropy.units object
                A float or ufloat of spectral flux density with units from
                astropy.units.

                wave : float
                Wavelength required for magnitude conversion and from Jy to
                erg/s/cm**2.

                zero : float
                Flux at zero magnitude for the magnitude scale.

        Returns
        ----------
                result : float, ufloat
                A float or ufloat of spectral flux density in units of
                erg/s/cm**2.
    """

    try:
        val.value, val.value.n
    except AttributeError as e:
        globs.logger.warning("Value could not be converted.")
        return val

    if (val.unit == u.mag):
        if zero:
            val = magConversion(val, wave, zero)
        else:
            globs.logger.warning("Flux zero point required for magnitude conversion.")
            return val

    if (not val.unit.decompose(bases=cgsBase).is_equivalent(u.g/u.s**2)):
        val = toJansky(val, wave)
        
    return JyConversion(val, wave)

def splitUnit(unit):
    """
        Splits a unit to a power into a string of the unit and the power.

        Parameters
        ----------
                unit : string
                A string of the unit and the power i.e. 'cm3' is cm**3.

        Returns
        ----------
                unit : string
                A string of only the unit i.e. 'cm3' would return 'cm'.

                power : int
                An integer of the power of the unit i.e. 'cm3' would return 3.

    """
    for e in unit:
        if e.isdigit():
            digit = e

    return unit.replace(digit, ''), int(digit)

def hasDigits(string):
    """
        Returns true if string has digits.

        Parameters
        ----------
                string : string
                A string to check if any digits are present.

        Returns
        ----------
                digits : bool
                Returns False if no digits are present in the string and True if
                any digits are present.
    """
    return any(char.isdigit() for char in string)

def reqUnits(req, act):
    """
        Compares a list of require units against a list of actual units and
        returns a list of the units needed to correct the actual to the
        required.

        Parameters
        ----------
                req : list
                A list of the required units.

                act : list
                A list of the actual units in the quantity.

        Returns
        ----------
                needed : list
                A list of the needed units to ensure that the actual units are
                in accordance with the required units for the quantity.
    """
    while req:
        ele = req.pop()
        if act.count(ele) != 0:
            act.pop(act.index(ele))

    return act

def toJansky(val, wave):
    """
        Converts astronomical spectral flux densities into erg/s/cm**2.

        Parameters
        ----------
                val : ufloat, astropy.units object
                A float or ufloat of spectral flux density with units from
                astropy.units.

                wave : float
                Wavelength required for magnitude conversion and from Jy to
                erg/s/cm**2.
        
        Returns
        ----------
                val : ufloat, astropy.units object
                The spectral flux density converted into Janskys.
    """
# -----------------
# prepare for unit comparison
# -----------------
    wave = (wave*u.um).decompose(bases=cgsBase)
    oriUnit = val.unit.decompose(bases=cgsBase)
    scale = oriUnit.scale
    newVal = val.value * scale
    unit = [uni.strip('(').strip(')') for uni in str(oriUnit).split()]
    if scale != 1.0:
        unit = unit[1:]
# --------------------

# --------------------
# replace s2, with s, s
# --------------------
    for ele in unit:
        if (len(ele) > 1) and hasDigits(ele):
            uni, num = splitUnit(ele)
            unit[unit.index(ele):unit.index(ele)+1] = [uni] * num

    try:
        frac = unit.index('/')
    except ValueError as e:
        globs.logger.warning("Check units they don't seem to be in spectral flux density units")
        return val
    
    top = unit[:frac]
    bottom = unit[frac + 1:]

    top = reqUnits(['g'], top)
    bottom = reqUnits(['s', 's'], bottom)

    newVal = convertTop(newVal, wave, top)
    newVal = convertBottom(newVal, wave, bottom)

    return newVal.value * (1e23 * u.Jy)

def convertTop(val, wave, units):
    """
        Converts the top of a fraction of a spectral flux density quantity into
        the desired units by multiplying and dividing by the units given in the
        'units' list.

        Parameters
        ----------
                val : ufloat
                A ufloat of the value to convert.

                wave : float
                A float of the wavelength needed to remove wavelength
                dependencies.

                units : list
                A list of the units required to convert the value into the
                correct format.

        Returns 
        ----------
                val : ufloat
                Returns the converted value in the correct units.
    """
    while units:
        unit = units.pop()

        if unit == 'cm':
            val /= wave

        if unit == 's':
            val *= (c / wave)

    return val

def convertBottom(val, wave, units):
    """
        Converts the bottom of a fraction of a spectral flux density quantity into
        the desired units by multiplying and dividing by the units given in the
        'units' list.

        Parameters
        ----------
                val : ufloat
                A ufloat of the value to convert.

                wave : float
                A float of the wavelength needed to remove wavelength
                dependencies.

                units : list
                A list of the units required to convert the value into the
                correct format.

        Returns 
        ----------
                val : ufloat
                Returns the converted value in the correct units.
    """
    while units:
        unit = units.pop()

        if unit == 'cm':
            val *= wave

        if unit == 's':
            val /= (c / wave)

    return val

def JyConversion(val, wave):
    """
        Converts from Janskys to erg/s/cm**2.

        Parameters
        ----------
                val : ufloat, astropy.units object.
                The spectral flux density in Janskys.

                wave : float
                Wavelength of the data point.

        Returns
        ----------
                val : ufloat, astropy.units object
                The spectral flux density in units of erg/s/cm**2.
    """

    cgsJansky = val.value * val.unit.decompose(bases=cgsBase)
    cgsFreq = (c / (wave * u.um)).decompose(bases=cgsBase)

    cgsFlux = cgsJansky * cgsFreq

    return cgsFlux.value * cgsFlux.unit.scale * (u.erg/u.s/u.cm**2)

def magConversion(val, wave, zero):
    """
        Converts magnitudes into Janskys with an error.

        Parameters
        ----------
                val : ufloat, astropy.units object.
                The magnitude to be converted into Janskys.

                wave : float
                Wavelength required for magnitude conversion and from Jy to
                erg/s/cm**2.

                zero : float
                Flux at zero magnitude for the magnitude scale.

        Returns
        ----------
                val : ufloat, astropy.units object
                The magnitude represented in Janskys.
    """
    return zero * 10**(-0.4 * val.value) * u.Jy

