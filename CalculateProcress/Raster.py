import gdal
import processing
from qgis.core import *
import numpy as np



def clip_raster_by_vector( DEM, Shp, crop:bool, keep:bool):

    out_file = QgsProcessing.TEMPORARY_OUTPUT
    params = {'INPUT': DEM,
            'MASK': Shp,
            'NO_DATA': 0,
            'SOURCE_CRS': "ESRI:102443",
            'TARGET_CRS': "ESRI:102443",
            'ALPHA_BAND': False,
            'CROP_TO_CUTLINE': crop,
            'KEEP_RESOLUTION': keep,
            'EXTRA': "",
            'OUTPUT': out_file,
            }

    alg_name = 'gdal:cliprasterbymasklayer'
    #print(processing.algorithmHelp('gdal:cliprasterbymasklayer'))
    result = processing.run(alg_name, params)
    return result


def GetCoverRowandCol(data):
    array_search = np.copy(data)
    index = np.where(array_search != 0)
    row_index = index[0]
    col_index = index[1]

    index_array = np.zeros((index[0].shape[0],2),dtype = int)

    index_array[:,0] = np.copy(row_index)
    index_array[:,1] = np.copy(col_index)

    return index_array


def CreateNewData(filename, data, transform, projection):
    driver = gdal.GetDriverByName("GTiff")
    driver.Register()
    outdata = driver.Create(filename,
                            xsize = data.shape[1],
                            ysize = data.shape[0],
                            bands = 1,
                            eType = gdal.GDT_Float32
                            )
    outdata.SetGeoTransform(transform)
    outdata.SetProjection(projection)
    outband = outdata.GetRasterBand(1)
    outband.WriteArray(data)
    outband.SetNoDataValue(np.nan)
    outband.FlushCache()
    outband = None
    outdata = None


def SetValueByCoveredDEM(data, rasterBand, index, savefilename, dig_value: float, transform, projection):
    for i in index:
        try:
            value = data[i[0],i[1]]
            data[i[0],i[1]] = value - dig_value
            rasterBand.WriteRaster(int(i[0]),int(i[1]),0,0,bytes((value - dig_value)))
        except:
            continue

    CreateNewData(savefilename,data,transform,projection)

class RasterProcress():
    def __init__(self, DEM_path, Select_Area_path, Channel_Path, Dig_Value):
        
        self.__DEM_path = DEM_path
        self.__SelectAreaPath = Select_Area_path
        self.__ChannelPath = Channel_Path
        self.__Dig_Value = Dig_Value

        # read DEM
        self.DEM_read()
        

    def DEM_read(self):
        # DEM read
        self.rasterData = gdal.Open(self.__DEM_path)
        self.transform = self.rasterData.GetGeoTransform()
        self.projection = self.rasterData.GetProjection()
        
        # 1-based index
        self.rasterBand = self.rasterData.GetRasterBand(1)
        self.data = self.rasterBand.ReadAsArray()


    # create DEM covered by polygons
    def Select_Extent_And_Dig_Channel(self):

        # Select extent
        result_area = clip_raster_by_vector(self.__DEM_path,self.__SelectAreaPath,True,False)

        rasterData_areaout = gdal.Open(result_area["OUTPUT"])
        transform_areaout = rasterData_areaout.GetGeoTransform()
        projection_areaout = rasterData_areaout.GetProjection()

        rasterBand_areaout = rasterData_areaout.GetRasterBand(1)
        data_areaout = rasterBand_areaout.ReadAsArray()

        # Dig DEM channel
        self.Dig_Channel(result_area["OUTPUT"],data_areaout,rasterBand_areaout,transform_areaout,projection_areaout)



    def Dig_Channel(self, DEM_path, arraydata, rasterband, transform, projection):
        result_cut = clip_raster_by_vector(DEM_path,self.__ChannelPath,False,True)

        rasterData_out = gdal.Open(result_cut["OUTPUT"])
        transform_out = rasterData_out.GetGeoTransform()
        projection_out = rasterData_out.GetProjection()

        rasterBand_out = rasterData_out.GetRasterBand(1)
        data_out = rasterBand_out.ReadAsArray()

        # find which band is covered by polygons
        covered_index = GetCoverRowandCol(data_out)

        # create save filename
        filenamesave = self.__DEM_path[:-4]
        filenamesave = filenamesave + "New.tif"

        # Start to Dig the channel
        SetValueByCoveredDEM(arraydata,rasterband,covered_index,filenamesave,self.__Dig_Value,transform,projection)
        self.__DEM_path = filenamesave


    def Get_Calculate_DEM(self):
        return self.__DEM_path
    

    ''' Testing Function
    get DEM values
    def getValue(self,x,y):

        xOrigin = self.transform[0] 
        yOrigin = self.transform[3] 
        pixelWidth = self.transform[1] 
        pixelHeight = self.transform[5] 

        xOffset = int((x - xOrigin) / pixelWidth) - 1
        yOffset = int((y - yOrigin) / pixelHeight) - 1

        # get individual pixel values
        value = self.data[yOffset,xOffset]

        return (xOffset,yOffset,value)


    def setValue(self,x,y):
        xOffset,yOffset,value = self.getValue(x,y)
        self.data[yOffset,xOffset] = value - 150
        self.rasterBand.WriteRaster(xOffset,yOffset,0,0,bytes((value - 150)))
        self.CreateNewData('r.tif')

    '''