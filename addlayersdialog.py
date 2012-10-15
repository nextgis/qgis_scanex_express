# -*- coding: utf-8 -*-

#******************************************************************************
#
# ScanexExpress
# ---------------------------------------------------------
# Integrates Scanex Express service in QGIS
#
# Copyright (C) 2012 NextGIS (info@nextgis.org)
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/licenses/>. You can also obtain it by writing
# to the Free Software Foundation, 51 Franklin Street, Suite 500 Boston,
# MA 02110-1335 USA.
#
#******************************************************************************

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

import browserdialog
import openlayers_layer

from ui_addlayersdialogbase import Ui_Dialog

import wmsprovider

class AddLayersDialog( QDialog, Ui_Dialog ):
  def __init__( self, iface ):
    QDialog.__init__( self )
    self.iface = iface
    self.setupUi( self )

    self.crs = ""

    self.btnAdd = QPushButton( self.tr( "Add" ) )
    self.btnAdd.setToolTip( self.tr( "Add selected layers to map" ) )
    self.btnAdd.setEnabled( False )
    self.buttonBox.addButton( self.btnAdd, QDialogButtonBox.ActionRole )

    self.btnAdd.clicked.connect( self.addLayers )
    self.btnConnect.clicked.connect( self.connectToServer )
    self.btnGetKey.clicked.connect( self.getApiKey )
    self.btnChangeCRS.clicked.connect( self.changeCrs )
    self.lstLayers.itemSelectionChanged.connect( self.selectionChanged )

    self.manageGui()

  def manageGui( self ):
    settings = QSettings( "NextGIS", "ScanexExpress" )

    self.leApiKey.setText( settings.value( "apiKey", "" ).toString() )
    self.chkSaveKey.setChecked( settings.value( "saveKey", True ).toBool() )

    # set the current project CRS if available
    currentRefSys = QgsCoordinateReferenceSystem( "EPSG:3395" )
    if currentRefSys.isValid():
      self.crs = currentRefSys.authid()

    self.lblCoordRefSys.setText( self.tr( "Coordinate Refrence System: %1" ).arg( self.descriptionForAuthId( self.crs ) ) )

  def reject( self ):
    QDialog.reject( self )

  def descriptionForAuthId( self, authId ):
    qgisSrs = QgsCoordinateReferenceSystem()
    qgisSrs.createFromOgcWmsCrs( authId )
    return qgisSrs.description()

  def getApiKey( self ):
    dlg = browserdialog.BrowserDialog()
    dlg.exec_()

  def changeCrs( self ):
    mySelector = QgsGenericProjectionSelector( self )
    mySelector.setMessage()
    mySelector.setOgcWmsCrsFilter( ["EPSG:3395", "EPSG:3857"] )

    defaultCRS = QgsCoordinateReferenceSystem( "EPSG:3395" )
    mySelector.setSelectedCrsId( defaultCRS.srsid() )

    if not mySelector.exec_():
      return

    self.crs = mySelector.selectedAuthId()
    del mySelector
    self.lblCoordRefSys.setText( self.tr( "Coordinate Refrence System: %1" ).arg( self.descriptionForAuthId( self.crs ) ) )

    self.update()

  def connectToServer( self ):
    apiKey = self.leApiKey.text()
    if apiKey.isEmpty():
      QMessageBox.warning( self, self.tr( "Missed API key" ), self.tr( "Please enter your API key and try again" ) )
      return

    settings = QSettings( "NextGIS", "ScanexExpress" )
    if self.chkSaveKey.isChecked():
      settings.setValue( "apiKey", self.leApiKey.text() )
    settings.setValue( "saveKey", self.chkSaveKey.isChecked() )

    uri = QgsDataSourceURI()
    url = QString( "http://maps.kosmosnimki.ru/TileService.ashx/apikey%1" ).arg( apiKey )
    uri.setParam( "url", url  )

    provider = wmsprovider.WmsProvider( uri.encodedUri() )

    if not provider.supportedLayers():
      self.showError( provider.error )
      pass

    items = dict()
    layers = provider.layersSupported
    layerParents = provider.layerParents
    layerParentNames = provider.layerParentNames

    self.lstLayers.clear()

    self.layerAndStyleCount = -1
    for layer in layers:
      names = [ layer[ "name" ], layer[ "title" ], layer[ "abstract" ] ]
      item = self.createItem( layer[ "orderId" ], names, items, layerParents, layerParentNames )

      item.setData( 0, Qt.UserRole + 0, layer[ "name" ] )
      item.setData( 0, Qt.UserRole + 1, "" )
      item.setData( 0, Qt.UserRole + 2, layer[ "crs" ] )
      item.setData( 0, Qt.UserRole + 3, QVariant( layer[ "bbox" ] ) )

    if self.lstLayers.topLevelItemCount() == 1:
      self.lstLayers.expandItem( self.lstLayers.topLevelItem( 0 ) )

  def showError( self, provider ):
    mv = QgsMessageViewer( self )
    mv.setWindowTitle( provider.errorCaption )

    if provider.errorFormat == "text/html":
      mv.setMessageAsHtml( provider.error )
    else:
      mv.setMessageAsPlainText( self.tr( "Could not understand the response. The provider said:\n%1" ).arg( provider.error ) )

    mv.showMessage( True )

  def createItem( self, layerId, names, items, layerParents, layerParentNames ):
    if layerId in items:
      return items[ layerId ]

    if layerId in layerParents:
      parent = layerParents[ layerId ]
      item = QTreeWidgetItem( self.createItem( parent, layerParentNames[ parent ], items, layerParents, layerParentNames ) )
    else:
      item = QTreeWidgetItem( self.lstLayers )

    self.layerAndStyleCount += 1
    item.setText( 0, QString.number( self.layerAndStyleCount ) )
    item.setText( 1, names[ 0 ] )
    item.setText( 2, names[ 1 ] )
    item.setText( 3, names[ 2 ] )

    items[ layerId ] = item

    return item

  def selectionChanged( self ):
    if len( self.lstLayers.selectedItems() ) > 0:
      self.btnAdd.setEnabled( True )

  def collectLayers( self, item ):
    layerName = item.data( 0, Qt.UserRole + 0 ).toString()
    styleName = item.data( 0, Qt.UserRole + 1 ).toString()

    if layerName.isEmpty(): # this is a group
      for i in xrange( item.childCount() ):
        self.collectLayers( item.child( i ) )
    elif styleName.isEmpty(): # this is a layer
      self.addLayer( item )

  def addLayers( self ):
    apiKey = self.leApiKey.text()

    currentSelection = self.lstLayers.selectedItems()
    for item in currentSelection:
      layerName = item.data( 0, Qt.UserRole + 0 ).toString()
      if layerName.isEmpty(): # this is a group
        self.collectLayers( item )
      else:
        self.addLayer( item )

  def addLayer( self, item ):
    lName = unicode( item.data( 0, Qt.UserRole + 0 ).toString() )
    t = item.data( 0, Qt.UserRole + 3 ).toString().split( ";" )
    rect = QgsRectangle( float(t[0]), float(t[1]), float(t[2]), float(t[3]) )
    src = QgsCoordinateReferenceSystem()
    src.createFromOgcWmsCrs( t[4] )
    dst = QgsCoordinateReferenceSystem()
    dst.createFromOgcWmsCrs( self.crs )
    ct = QgsCoordinateTransform( src, dst )
    bbox = ct.transformBoundingBox( rect )

    apiKey = self.leApiKey.text()
    layer = openlayers_layer.OpenlayersLayer(self.iface, self.crs, lName, bbox, apiKey)
    if layer.isValid():
      layer.setLayerName( unicode( item.text( 2 ) ) )
      QgsMapLayerRegistry.instance().addMapLayers( [ layer ] )
