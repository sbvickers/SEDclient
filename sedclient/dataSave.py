"""
    Here the data is written to files in the ../data/(photometry or
    spectroscopy) directories where the filename is the name of the object i.e.
    globs.name.
"""

import globs

def savePh(red, wave, source):
    """
        Saves downloaded data in a reduced format.

        Parameters
        ----------
                red : list of astropy.units ufloats
                A list of the fluxes with errors in erg/s/cm**2.

                wave : list
                A list of wavelengths of the data.

                source : string
                The name of the cat/survey.

        Returns
        ----------
                None
    """
    filename = "{}{}".format(globs.dirPh, globs.name.replace(' ', '_'))

    with open(filename, 'a') as saveFile:
        saveFile.write("[{}] \n".format(source))

        if red:
            waveStr = "wave=" + "{} " * len(wave) + "\n"
            saveFile.write(waveStr.format(*wave))

            redStr = "fluxes=" + "{:.3E} " * len(red) * 2 + "\n"
            redEx = [y for x in red for y in (x.value.n, x.value.s)]
            saveFile.write(redStr.format(*redEx))

    globs.logger.info("{} data saved for {}.".format(source, globs.name))

    saveFile.close()

def saveSp(wave, flux, source):
    """
        Saves downloaded spectral data and saves in txt files.

        Parameters
        ----------
                wave : list
                A list of wavelengths of the data in microns.

                flux : list
                A list of fluxes in erg/s/cm**2.

                source : string
                The name of the cat/survey.

        Returns
        ----------
                None
    """
    filename = "{}{}_iso".format(globs.dirSp, globs.name.replace(' ', '_'))

    with open(filename, 'a') as saveFile:
        if flux:
            for w, f in zip(wave, flux):
                dataStr = "{:.3F}, {:.3E}, {:.3E} \n"
                data = [w, f.value.n, f.value.s]
                saveFile.write(dataStr.format(*data))

    globs.logger.info("ISO data saved for {}.".format(globs.name))

    saveFile.close()

def saveSed(fig, filename=None):
    """
        Saves the image of an SED.

        Parameters
        ----------
                fig : matplotlib figure object
                The figure containing the SED to save.

                filename : string, optional
                If filename is given SED is saved in that name.

        Returns
        ----------
                None
    """
    if filename:
        fig.savefig(filename, figsize=(5,4), transparent=True, bbox_inches='tight')
        globs.logger.info("SED for {} saved as {}.".format(globs.name, filename))
    else:
        fig.savefig("{}{}.eps".format(globs.dirSed, globs.name.replace(' ', '_')), figsize=(5,4), transparent=False, bbox_inches='tight')
        globs.logger.info("SED for {} saved.".format(globs.name))
