
import matplotlib.pyplot as plt
import dataStruct as ds
import globs

class Plot:
    """
        class for Building SEDs.

    """

    def __init__(self):
        """

        """

        self.name = globs.name
        self.ra = globs.ra
        self.dec = globs.dec
        self.y_ann = 0.97

        self.photo = ds.buildPhStruct()
        self.spec = ds.buildSpStruct()

        self.fig = plt.figure()
        self.ax = plt.subplot(111)

        self.ax.set_xlabel(r'$\lambda\, \left[ \mu\rm{m} \right]$', fontsize=16)
        self.ax.set_ylabel(r'$\lambda F_\lambda\,\left[ \rm{erg\,\,s}^{-1}\,\rm{cm}^{-2} \right]$', fontsize=16)

        self.ax.set_xscale('log')
        self.ax.set_yscale('log')

        self.ax.set_xlim([0.1, 1000.0])
        self.ax.set_xticklabels(['', '$0.1$', '$1$', '$10$', '$100$', '$1000$'])

    def plotPh(self):
        """
            Plots the photometry.
        """
        import configparser

        for survey in self.photo:
            conf = configparser.ConfigParser()
            conf.read("{}{}.ini".format(globs.confPath, survey))

            conf = conf['plot']

            if self.photo[survey]['flux']:
                wave = self.photo[survey]['wave']
                flux = [f for x in self.photo[survey]['flux'] for f in (x.value.n, x.value.s)]
                if 'white' not in conf['mfc']:
                    self.ax.errorbar(wave, flux[0::2], yerr=flux[1::2], fmt=conf['marker'], mfc=conf['mfc'], mec=conf['mec'], ecolor=conf['mfc'], label=conf['label'])
                else:
                    self.ax.errorbar(wave, flux[0::2], yerr=flux[1::2], fmt=conf['marker'], mfc=conf['mfc'], mec=conf['mec'], ecolor=conf['mec'], label=conf['label'])

    def plotSp(self):
        """
            Plots the spectroscopy.
        """
        import configparser

        for survey in self.spec:
            conf = configparser.ConfigParser()
            conf.read("{}{}.ini".format(globs.confPath, survey))

            conf = conf['plot']

            if self.spec[survey]['flux']:
                wave = self.spec[survey]['wave']
                flux = [f for x in self.spec[survey]['flux'] for f in (x.value.n, x.value.s)]
                self.ax.plot(wave, flux[0::2], ls=conf['ls'], color=conf['col'], lw=float(conf['lw']), label=conf['label'])

    def annotate(self, string):
        """
            Annotates string in top right corner moving down after each line.
        """
        self.ax.text(0.97, self.y_ann, string, fontsize=14, transform=self.ax.transAxes, horizontalalignment='right', verticalalignment='top')
        self.y_ann -= 0.05

    def legend(self):
        """
            Displays the legend.
        """
        self.ax.legend(loc='lower right', bbox_to_anchor=(0.99, 0.01), fancybox=False, shadow=False, ncol=4, numpoints=1, prop={'size':6.5}, fontsize=14)

    def saveSed(self, filename=None):
        """
            Saves SED plot using the dataSave.py modules.
        """
        import dataSave as ds

        if filename:
            ds.saveSed(self.fig, filename)
        else:
            ds.saveSed(self.fig)

    def show(self):
        """
            Shows the figure.
        """
        plt.show()
