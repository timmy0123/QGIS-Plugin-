# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DigCrossSection
                                 A QGIS plugin
 Dig the cross section
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-02-04
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Yu Shen
        email                : t106340103@ntut.org.tw
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from sys import flags
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from qgis.core import *
from qgis.gui import QgisInterface
from qgis.utils import iface
from .Dig_CrossSection_dialog import DigCrossSectionDialog
import os.path
import os,sys
import gdal
import numpy as np
import time
import processing
from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.QtWidgets import QApplication,QPushButton,QLabel,QComboBox,QFileDialog
from qgis.gui import QgsFileWidget



class DigCrossSection:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DigCrossSection_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&DigCrossSection')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None



    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DigCrossSection', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Dig_CrossSection/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Dig cross section'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = False

        self.dlg = DigCrossSectionDialog()
        self.dlg.pushButton_difference.clicked.connect(self.select_output_file_difference)
        self.dlg.pushButton_merge.clicked.connect(self.select_output_file_merge)




    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&DigCrossSection'),
                action)
            self.iface.removeToolBarIcon(action)


    def select_output_file_difference(self):
        filename = QFileDialog.getSaveFileName(self.dlg, "Select difference output file ","", '*.shp')
        name = str(filename[0])
        self.dlg.lineEdit_difference.setText(name)


    def select_output_file_merge(self):
        filename = QFileDialog.getSaveFileName(self.dlg, "Select merge output file ","", '*.shp')
        name = str(filename[0])
        self.dlg.lineEdit_merge.setText(name)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = DigCrossSectionDialog()

        
        lyr = [layer for layer in QgsProject.instance().mapLayers().values()]
        self.comboBox = self.dlg.findChild(QComboBox , "Shp_File")
        self.comboBox.clear()
        for layer in lyr:
            if layer.type() == QgsMapLayer.VectorLayer:
                self.comboBox.addItems([layer.name()])

        self.comboBox3 = self.dlg.findChild(QComboBox , "Shp_File_Area")
        self.comboBox3.clear()
        for layer in lyr:
            if layer.type() == QgsMapLayer.VectorLayer:
                self.comboBox3.addItems([layer.name()])

        self.comboBox2 = self.dlg.findChild(QComboBox , "DEM_File")
        self.comboBox2.clear()
        for layer in lyr:
            if layer.type() == QgsMapLayer.RasterLayer:
                self.comboBox2.addItems([layer.name()])

        # Clear save file path
        self.dlg.lineEdit_difference.clear()
        self.dlg.lineEdit_merge.clear()

        # show the dialog
        self.dlg.show()

        # Run the dialog event loop
        result = self.dlg.exec_()

        # Select DEM
        self.DEM_layer = QgsProject.instance().mapLayersByName(self.comboBox2.currentText())[0]
        self.DEM_path = self.DEM_layer.source()

        # Select layer
        self.shp_layer = QgsProject.instance().mapLayersByName(self.comboBox.currentText())[0]

        self.Area_layer = QgsProject.instance().mapLayersByName(self.comboBox3.currentText())[0]

        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            strtime = time.time()
            # Get parameters
            
            save1 = self.dlg.lineEdit_difference.text()
            save2 = self.dlg.lineEdit_merge.text()
            threshold = int(self.dlg.threshold.text())
            slope = float(self.dlg.max_slope_length.text())
            dig_value = float(self.dlg.Dig_value.text())

            print("shapfile procress")
            from .CalculateProcress.Vector import VectorProcress
            VecterLayer = VectorProcress(self.shp_layer,self.Area_layer)
            

            if VecterLayer.Check_Select_Area(): VecterLayer.Generate_Select_Area()

            VecterLayer.Channel_Buffer()
            VecterLayer.Merge_features()
            VecterLayer.Generate_New_Extent_Layer()
            
            print("DEM procress")
            from .CalculateProcress.Raster import RasterProcress
            RasterLayer = RasterProcress(self.DEM_path,VecterLayer.Get_Buffer_Area_Path(),VecterLayer.Get_Channel_Path(),dig_value)
            RasterLayer.Select_Extent_And_Dig_Channel()

            print("grass procress")
            from .CalculateProcress.GrassCalculate import grassCal
            grassfile = grassCal(RasterLayer.Get_Calculate_DEM(),threshold,slope)
            grassresult = grassfile.run_watershed()

            
            basinresult = grassfile.Output_Vector(grassresult['basin'],2)
            
            streamresult = grassfile.Output_Vector(grassresult['stream'],0)

            print("start to merge calculated layer to origin")

            self.Area_layer = VecterLayer.Fix_Error(self.Area_layer.source())
            Splitresult = grassfile.Split_Select_Basin_from_Buffer(basinresult["output"],VecterLayer.Get_Area_Path(),0,0)
            Difreault = VecterLayer.Difference(self.Area_layer.source(),save1)
            Mergeresult = VecterLayer.Merge_Layer(save1,Splitresult["output"],save2)
            #print(Mergeresult["OUTPUT"])
            endtime = time.time()
            print("cost time:",(endtime - strtime))
            #self.iface.addVectorLayer(save2, "Stream")
           
