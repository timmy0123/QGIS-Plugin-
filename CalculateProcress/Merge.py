from qgis.core import *
import time


layer = iface.activeLayer()
feature = layer.getFeatures()
geome = [feat.geometry() for feat in feature]
print(len(geome))
n = 0
while n < 20:
    new_geome = geome
    for geom in geome:
        if geom.isMultipart() is False:
            polyg = geom.asPolygon()
            area = calculator.measurePolygon(polyg[0])
            landArea = area
        else:
            multi = geom.asMultiPolygon()
            area = 0
            calculator = QgsDistanceArea()
            calculator.setEllipsoid('ESRI:102443')
            for polyg in multi:
                area = area + calculator.measurePolygon(polyg[0])
                landArea = area

        if landArea < 3000:
            Merge = False
            for checkgeom in geome:
                if checkgeom.isMultipart() is False:
                    polyg = checkgeom.asPolygon()
                    area = calculator.measurePolygon(polyg[0])
                    landAreac = area
                else:
                    multi = checkgeom.asMultiPolygon()
                    area = 0
                    calculator = QgsDistanceArea()
                    calculator.setEllipsoid('ESRI:102443')
                    for polyg in multi:
                        area = area + calculator.measurePolygon(polyg[0])
                        landAreac = area

                if geom.intersects(checkgeom) and landAreac > 3000:
                    new_geom = geom.combine(checkgeom)
                    new_geome.remove(geom)
                    new_geome.remove(checkgeom)
                    new_geome.append(new_geom)
                    break

    geome = new_geome
    AreaCheck = True
    for geom in geome:
        if geom.isMultipart() is False:
            polyg = geom.asPolygon()
            area = calculator.measurePolygon(polyg[0])
            landArea = area
        else:
            multi = geom.asMultiPolygon()
            area = 0
            calculator = QgsDistanceArea()
            calculator.setEllipsoid('ESRI:102443')
            for polyg in multi:
                area = area + calculator.measurePolygon(polyg[0])
                landArea = area

        if landArea < 3000 : AreaCheck = False
    
    if AreaCheck is True:break
    n = n + 1
print(n)
print(len(geome))
layerFields = QgsFields()
layerFields.append(QgsField('ID', QVariant.Int))

writer = QgsVectorFileWriter("C:\Data\SMM\catchment_generate\Test\save.shp", 
                            'UTF-8', 
                            layerFields,
                            QgsWkbTypes.Polygon,
                            layer.crs(),
                            'ESRI Shapefile')


for geom in geome:
    feat = QgsFeature()
    feat.setGeometry(geom)
    feat.setAttributes([1])
    writer.addFeature(feat)
del(writer)



'''
start = time.time()

n = 0
while n<100:
    n = n + 1
    layer = iface.activeLayer()
    feature = layer.getFeatures()
    featurec = layer.getFeatures()

    for feat in feature:
        
        geom = feat.geometry()
        if geom.isMultipart() is False:
            pol = geom.asPolygon()
            area = calculator.measurePolygon(polyg[0])
            landArea = area
        else:
            multi = geom.asMultiPolygon()
            area = 0
            calculator = QgsDistanceArea()
            calculator.setEllipsoid('ESRI:102443')
            for polyg in multi:
                area = area + calculator.measurePolygon(polyg[0])
                landArea = area

        if landArea < 2:
          
            for checkfeat in featurec:
                
                checkgeom = checkfeat.geometry()
                if checkgeom.isMultipart() is False:
                    
                    pol = checkgeom.asPolygon()
                    area = calculator.measurePolygon(polyg[0])
                    landAreac = area
                else:
                    multi = checkgeom.asMultiPolygon()
                    area = 0
                    calculator = QgsDistanceArea()
                    calculator.setEllipsoid('ESRI:102443')
                    for polyg in multi:
                        area = area + calculator.measurePolygon(polyg[0])
                        landAreac = area
                    

                if geom.intersects(checkgeom) and landAreac > 2 and (landAreac - landArea) > 2:
                    geom = geom.combine(checkgeom)
                    newFeature = QgsFeature()
                    values = [1,1,1,1]  
                    newFeature.setGeometry(geom)
                    newFeature.setAttributes(values)
                    layer.startEditing()
                    layer.deleteFeature(feat.id())
                    layer.deleteFeature(checkfeat.id())
                    layer.addFeature(newFeature)
                    layer.removeSelection()
                    layer.commitChanges()
                    break


    AreaCheck = True
    feature = layer.getFeatures()
    for feat in feature:
        geom = feat.geometry()
        if geom.isMultipart() is False:
            pol = geom.asPolygon()
            area = calculator.measurePolygon(polyg[0])
            landArea = area
        else:
            multi = geom.asMultiPolygon()
            area = 0
            calculator = QgsDistanceArea()
            calculator.setEllipsoid('ESRI:102443')
            for polyg in multi:
                area = area + calculator.measurePolygon(polyg[0])
                landArea = area

        
        if landArea < 2 : AreaCheck = False
    
    if AreaCheck == True:break
    
print(time.time() - start)
print(n,"times")
print("=====================================")

sfeat = layer.getSelectedFeatures()
for sfeat in sfeat:
    geom = sfeat.geometry()
    multi = geom.asMultiPolygon()
    area = 0
    calculator = QgsDistanceArea()
    calculator.setEllipsoid('ESRI:102443')
    for polyg in multi:
        area = area + calculator.measurePolygon(polyg[0])
        landArea = area
    print(landArea)
    print(geom.boundingBox())

sfeat = layer.getSelectedFeatures()
for sfeat in sfeat:
    for feat in layer.getFeatures():
        sgeom = sfeat.geometry()
        geom = feat.geometry()
        if sgeom == geom: continue
        if sgeom.intersects(geom):
            print(feat)
'''