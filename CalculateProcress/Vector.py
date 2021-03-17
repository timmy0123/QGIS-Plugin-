from qgis.core import *
import processing
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QVariant
from qgis.core import *
import qgis


class VectorProcress:
    def __init__(self , Channel_Layer, Select_Area_Layer):
        self.__ChannelLayer = Channel_Layer
        self.__SelectAreaLayer = Select_Area_Layer
        self.__ChannelLayerPath = self.__ChannelLayer.source()
        self.__SelectAreaLayerPath = self.__SelectAreaLayer.source()
        

    def Channel_Buffer(self):
        savename = self.__ChannelLayerPath[:-4]
        savename = savename + "bufferNew.shp"
        param = {"INPUT": self.__ChannelLayerPath,
                 "Distance": 0,
                 "DISSOLVE": False,
                 "END_CAP_STYLE":0,
                 "JOIN_STYLE":0,
                 "SEGMENTS":5,
                 "MITER_LIMIT":2,
                 "OUTPUT":savename}
        processing.run("native:buffer",param)
        self.__ChannelLayerPath = savename


    def Check_Select_Area(self):
        select_feature = self.__SelectAreaLayer.getSelectedFeatures()
        select_feature_num = 0
        for feature in select_feature:
            select_feature_num += 1
        
        if select_feature_num != 0: return True
        else: return False


    def Generate_Select_Area(self):
        savename = self.__SelectAreaLayerPath[:-4]
        savename = savename + "New.shp"
        QgsVectorFileWriter.writeAsVectorFormat(self.__SelectAreaLayer,
                                                savename,
                                                "utf-8",
                                                self.__ChannelLayer.crs(),
                                                "ESRI Shapefile",
                                                onlySelected=True)
        
        self.__SelectAreaLayerPath = savename
        self.__SelectAreaLayer = QgsVectorLayer(self.__SelectAreaLayerPath, "Airports layer", "ogr")
        #self.Merge_features()


    def Generate_New_Extent_Layer(self):
        # Get area extent
        ext = self.__SelectAreaLayer.extent()
        xmin = ext.xMinimum() - 200
        xmax = ext.xMaximum() + 200
        ymin = ext.yMinimum() - 200
        ymax = ext.yMaximum() + 200
        
        # Generate new shpfile
        savename = self.__SelectAreaLayerPath[:-4]
        savename = savename + "New.shp"

        # create fields
        layerFields = QgsFields()
        layerFields.append(QgsField('ID', QVariant.Int))

        writer = QgsVectorFileWriter(savename, 
                                    'UTF-8', 
                                    layerFields,
                                    QgsWkbTypes.Polygon,
                                    self.__SelectAreaLayer.crs(),
                                    'ESRI Shapefile')

        p1 = QgsPointXY(xmin, ymin)
        p2 = QgsPointXY(xmin, ymax)
        p3 = QgsPointXY(xmax, ymax)
        p4 = QgsPointXY(xmax, ymin)
        points = [p1,p2,p3,p4]

        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPolygonXY([points]))
        feat.setAttributes([1])
        writer.addFeature(feat)
        del(writer)

        self.__SelectAreaLayerPathBuffer = savename

    
    def Get_Area_Path(self):
        return self.__SelectAreaLayerPath


    def Get_Buffer_Area_Path(self):
        return self.__SelectAreaLayerPathBuffer

    
    def Get_Channel_Path(self):
        return self.__ChannelLayerPath


    def Merge_Layer(self, ALayer, BLayer, savefile):
        layer = [BLayer,ALayer]
        print(layer)
        param = {"CRS": self.__SelectAreaLayer.crs(),
                 "LAYERS":layer,
                 "OUTPUT":savefile}

        print(processing.algorithmHelp("native:mergevectorlayers"))
        result = processing.run("native:mergevectorlayers",param)
        return result


    def Difference(self, input, savefile):
        param = {"INPUT": input,
                 "OVERLAY": self.__SelectAreaLayerPath,
                 "OUTPUT": savefile}
        
        result = processing.run("native:difference",param)
        return result


    def Merge_features(self):
        geom = None
        for feature in self.__SelectAreaLayer.getFeatures():
            if geom == None: geom = feature.geometry()
            else:geom = geom.combine(feature.geometry())
        points = []
        for i in geom.asPolygon():
            for point in i:
                points.append(point)
        print(points)
        
        layerFields = QgsFields()
        layerFields.append(QgsField('ID', QVariant.Int))
        writer = QgsVectorFileWriter(self.__SelectAreaLayerPath, 
                                    'UTF-8', 
                                    layerFields,
                                    QgsWkbTypes.Polygon,
                                    self.__SelectAreaLayer.crs(),
                                    'ESRI Shapefile')
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPolygonXY([points]))
        feat.setAttributes([1])
        writer.addFeature(feat)
        del(writer)
        


