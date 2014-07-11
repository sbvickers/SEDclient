
saveDirPh = "data/photometry/"
saveDirSp = "../data/spectroscopy/"
saveDirSed = "data/sed/"

def savePh(raw, red, wave, source):
    """
        Saves downloaded data in both a raw and a reduced format.

        Parameters
        ----------
                raw : list
                A list of values, errors, and qflags.

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
    files = ['raw', 'red']

    for f in files:
        # need to get name of object from somewhere
        filename = "{}{}_{}".format(saveDirPh, name, f)

        with open(filename, 'a') as saveFile:
            saveFile.write("[{}] \n".format(source))

            if raw and ('raw' in f):
                rawStr = "raw=" + "{} " * len(raw) + "\n"
                saveFile.write(rawStr.format(*raw))

            if red and ('red' in f):
                waveStr = "wave=" + "{} " * len(wave) + "\n"
                saveFile.write(waveStr.format(*wave))

                redStr = "red=" + "{:.3E} " * len(red) * 2 + "\n"
                redEx = [y for x in red for y in (x.value.n, x.value.s)]
                saveFile.write(redStr.format(*redEx))

        # logger.info("{} {} data saved for {}.".format(f, source, name))
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
    name ='test'
    files = ['iso']

    for f in files:
        # need to get name of object from somewhere
        filename = "{}{}_{}".format(saveDirSp, name, f)

        with open(filename, 'a') as saveFile:
            if flux:
                for w, f in zip(wave, flux):
                    dataStr = "{:.3F}, {:.3E}, {:.3E} \n"
                    data = [w.scale, f.value.n, f.value.s]
                    saveFile.write(dataStr.format(*data))

        # logger.info("{} data saved for {}.".format(f, name))
        saveFile.close()

def saveSed(fig):
    """
        Saves the image of an SED.

        Parameters
        ----------
                fig : matplotlib figure object
                The figure containing the SED to save.

        Returns
        ----------
                None
    """
    fig.savefig("{}{}.eps".format(saveDirSed, name), figsize=(5,4), transparent=True, bbox_inches='tight')
    # logger.info("SED for {} saved.".format(name))
