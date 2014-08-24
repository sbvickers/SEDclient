"""
    These are global variables accessible from anywhere in the client by
    prefacing the variables listed below with globs.name, provided that this
    file has been imported.
"""
import logging
import os

name = None
ra = None
dec = None
ebv = None
l = None
b = None

dirPh = "data/photometry/"
dirSp = "data/spectroscopy/"
dirSed = "data/sed/"
dirLog = "data/logfiles/"
masterLog = "master.log"
confPath = "sedclient/config/"

phSources = [f.replace('.ini', '') for f in os.listdir(confPath) if os.path.isfile(os.path.join(confPath, f))]
specSources=['iso']

logFormat = logging.Formatter("%(asctime)-15s ; %(levelname)s ; Mod: %(module)-5s ; LN: %(lineno)d ; %(message)s", "%Y-%m-%d %H:%M:%S")

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

masterHandler = logging.FileHandler("{}{}".format(dirLog, masterLog))
masterHandler.setLevel(logging.DEBUG)
masterHandler.setFormatter(fmt=logFormat)

logger.addHandler(masterHandler)

objectHandler = None
