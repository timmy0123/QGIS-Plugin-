import processing
from qgis.core import *


class grassCal():
    def __init__(self, DEM, threshold, slope):
        self.__DEM_Path = DEM
        self.__threshold = threshold
        self.__max_slope_length = slope
        self.__Save_Basin_File = QgsProcessing.TEMPORARY_OUTPUT
        self.__Save_Stream_File = QgsProcessing.TEMPORARY_OUTPUT


    def run_fill_dir(self):
        print ("==================")
        print ('Process: run fill dir')
        # r.fill.dir
        param = {'input': self.__DEM_Path,
                 'output': QgsProcessing.TEMPORARY_OUTPUT,
                 'direction': QgsProcessing.TEMPORARY_OUTPUT,
                 'areas': QgsProcessing.TEMPORARY_OUTPUT}
        #print(processing.algorithmHelp("grass7:r.fill.dir"))
        result = processing.run("grass7:r.fill.dir",param)
        return result


    def run_watershed(self):
        print ("==================")
        print ('Process: run watershed')

        # r.in.gdal
        param = {'elevation': self.__DEM_Path,
                 'threshold': self.__threshold,
                 'max_slope_length': self.__max_slope_length,
                 'convergence': 5,
                 'memory': 300,
                 'accumulation': None,
                 'drainage': None,
                 'basin': self.__Save_Basin_File,
                 'stream': self.__Save_Stream_File,
                 'half_basin': None,
                 'length_slope': None,
                 'slope_steepness': None,
                 'tcl': None,
                 'spl': None,
                 '-b':True,
                 '-s':False}
        #print(processing.algorithmHelp("grass7:r.watershed"))
        result = processing.run("grass7:r.watershed",param)
        return result


    def Output_Vector(self,file,savetype):
        print("===================")
        print("output geojson")

        param = {'input': file,
                 'type': savetype,
                 'output': QgsProcessing.TEMPORARY_OUTPUT}
        #print(processing.algorithmHelp("grass7:r.to.vect"))
        result = processing.run("grass7:r.to.vect",param)
        return result


    def Split_Select_Basin_from_Buffer(self, AinputVector, BinputVector, Atype, Btype):
        print("===================")
        print("Split the selected area")

        param = {"ainput": AinputVector,
                 "binput": BinputVector,
                 "atype": Atype,
                 "btype": Btype,
                 "operator":0,
                 "output":QgsProcessing.TEMPORARY_OUTPUT,
                 "GRASS_OUTPUT_TYPE_PARAMETER": 0,
                 "GRASS_MIN_AREA_PARAMETER": 0.0001,
                 "GRASS_SNAP_TOLERANCE_PARAMETER": -1}
        #print(processing.algorithmHelp("grass7:v.overlay"))
        result = processing.run("grass7:v.overlay",param)
        return result



