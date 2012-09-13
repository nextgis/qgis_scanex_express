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

from ui_addlayersdialogbase import Ui_Dialog

import wmsprovider

class AddLayersDialog( QDialog, Ui_Dialog ):
  def __init__( self, iface ):
    QDialog.__init__( self )
    self.iface = iface
    self.setupUi( self )

    self.crs = ""
    self.crss = []

    self.btnAdd = QPushButton( self.tr( "Add" ) )
    self.btnAdd.setToolTip( self.tr( "Add selected layers to map" ) )
    self.btnAdd.setEnabled( False )
    self.buttonBox.addButton( self.btnAdd, QDialogButtonBox.ActionRole )

    self.btnAdd.clicked.connect( self.addLayers )
    self.btnConnect.clicked.connect( self.connectToServer )
    self.btnGetKey.clicked.connect( self.getApiKey )
    self.btnChangeCRS.clicked.connect( self.changeCrs )
    self.lstLayers.itemSelectionChanged.connect( self.selectionChanged )
    self.btnLayerUp.clicked.connect( self.moveLayerUp )
    self.btnLayerDown.clicked.connect( self.moveLayerDown )

    self.manageGui()

  def manageGui( self ):
    settings = QSettings( "NextGIS", "ScanexExpress" )

    self.leApiKey.setText( settings.value( "apiKey", "" ).toString() )
    self.chkSaveKey.setChecked( settings.value( "saveKey", True ).toBool() )

    # set the current project CRS if available
    currentCRS = QgsProject.instance().readNumEntry( "SpatialRefSys", "/ProjectCRSID", -1 )[0]
    if currentCRS != -1:
      currentRefSys = QgsCoordinateReferenceSystem( currentCRS, QgsCoordinateReferenceSystem.InternalCrsId )
      if currentRefSys.isValid():
        self.crs = currentRefSys.authid()

    self.lblCoordRefSys.setText( self.tr( "Coordinate Refrence System: %1" ).arg( self.descriptionForAuthId( self.crs ) ) )

    # disable change CRS button
    self.btnChangeCRS.setEnabled( False )

    self.tabWidget.setCurrentIndex( 0 )
    self.tabWidget.setTabEnabled( self.tabWidget.indexOf( self.tabOrder ), False )

  def reject( self ):
    QDialog.reject( self )

  def descriptionForAuthId( self, authId ):
    qgisSrs = QgsCoordinateReferenceSystem()
    qgisSrs.createFromOgcWmsCrs( authId )
    return qgisSrs.description()

  def getApiKey( self ):
    pass

  def changeCrs( self ):
    mySelector = QgsGenericProjectionSelector( self )
    mySelector.setMessage()
    mySelector.setOgcWmsCrsFilter( self.CRSs )

    myDefaultCrs = QgsProject.instance().readEntry( "SpatialRefSys", "/ProjectCrs", GEO_EPSG_CRS_AUTHID )
    defaultCRS = QgsCoordinateReferenceSystem()
    if defaultCRS.createFromOgcWmsCrs( myDefaultCrs ):
      mySelector.setSelectedCrsId( defaultCRS.srsid() )

    if not mySelector.exec_():
      return

    self.crs = mySelector.selectedAuthId()
    del mySelector
    self.lblCoordRefSys.setText( self.tr( "Coordinate Refrence System: %1" ).arg( self.descriptionForAuthId( self.crs ) ) )

    for i in xrange( self.lstLayers.topLevelItemCount() ):
      self.enableLayersForCrs( self.lstLayers.topLevelItem( i ) )

    self.updateButtons()
    self.update()

  def connectToServer( self ):
    apiKey = self.leApiKey.text()
    if apiKey.isEmpty():
      QMessageBox.warning( self, self.tr( "Missed API key" ), self.tr( "Please enter your API key and try again" ) )
      return

    settings = QSettings( "NextGIS", "ScanexExpress" )
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
    currentSelection = self.lstLayers.selectedItems()

    self.crss = set()

    self.layers = []

    for item in currentSelection:
      layerName = item.data( 0, Qt.UserRole + 0 ).toString()

      if layerName.isEmpty():
        self.layers.extend( self.collectLayers( item ) )
      else:
        self.layers.append( layerName )
        if len( self.crss ) == 0:
          self.crss = set( item.data( 0, Qt.UserRole + 2 ).toStringList() )
        else:
          self.crss.intersection( set( item.data( 0, Qt.UserRole + 2 ).toStringList() ) )

    self.btnChangeCRS.setDisabled( True if len( self.crss ) == 0 else False )

    if len( self.layers ) > 0 and len( self.crss ) > 0:
      defaultCRS = ""
      notFound = True
      for crs in self.crss:
        if unicode( crs ).lower() == unicode( self.crs ).lower():
          notFound = False
          break

        if unicode( crs ).lower() == unicode( list(self.crss)[0] ).lower():
          defaultCRS = crs

        if unicode( crs ).lower() == unicode( GEO_EPSG_CRS_AUTHID ).lower():
          defaultCRS = crs

      if notFound:
        self.crs = defaultCRS
        self.lblCoordRefSys.setText( self.tr( "Coordinate Refrence System: %1" ).arg( self.descriptionForAuthId( self.crs ) ) )

    self.updateOrderTab( self.layers )
    self.updateButtons()

  def collectLayers( self, item ):
    layers = []
    layerName = item.data( 0, Qt.UserRole + 0 ).toString()
    styleName = item.data( 0, Qt.UserRole + 1 ).toString()

    if layerName.isEmpty(): # this is a group
      for i in xrange( item.childCount() ):
        layers.extend( self.collectLayers( item.child( i ) ) )
    elif styleName.isEmpty(): # this is a layer
      layers.append( layerName )

      if len( self.crss ) == 0:
        self.crss = set( item.data( 0, Qt.UserRole + 2 ).toStringList() )
      else:
        self.crss.intersection( set( item.data( 0, Qt.UserRole + 2 ).toStringList() ) )

    return layers

  def enableLayersForCrs( self, item ):
    layerName = item.data( 0, Qt.UserRole + 0 ).toString()

    if not layerName.isEmpty():
      disable = not item.data( 0, Qt.UserRole + 2 ).toStringList().contains( self.crs, Qt.CaseInsensitive )
      item.setDisabled( disable )
    else:
      for i in xrange( item.childCount() ):
        self.enableLayersForCrs( item.child( i ) )

  def updateButtons( self ):
    if len( self.crss ) == 0:
      self.btnAdd.setEnabled( False )
    elif self.crs.isEmpty():
      self.btnAdd.setEnabled( False )
    else:
      self.btnAdd.setEnabled( True )

  def updateOrderTab( self, layers ):
    # add layer to list if necessary
    for layer in layers:
      exists = False
      for i in xrange( self.lstOrder.topLevelItemCount() ):
        itemName = self.lstOrder.topLevelItem( i ).text( 0 )
        if itemName == layer:
          exists = True
          break

      if not exists:
        newItem = QTreeWidgetItem()
        newItem.setText( 0, layer )
        self.lstOrder.addTopLevelItem( newItem )

    # remove layer from list if necessary
    if self.lstOrder.topLevelItemCount() > 0:
      for i in xrange(self.lstOrder.topLevelItemCount() - 1, -1, -1):
        itemName = self.lstOrder.topLevelItem( i ).text( 0 )
        exists = False
        for layer in layers:
          if itemName == layer:
            exists = True
            break

        if not exists:
          self.lstOrder.takeTopLevelItem( i )

    self.tabWidget.setTabEnabled( self.tabWidget.indexOf( self.tabOrder ), True if self.lstOrder.topLevelItemCount() > 0 else False)

  def moveLayerUp( self ):
    selection = self.lstOrder.selectedItems()
    if len( selection ) < 1:
      return

    selectedIndex = self.lstOrder.indexOfTopLevelItem( selection[0] )
    if selectedIndex < 1:
      return

    selectedItem = self.lstOrder.takeTopLevelItem( selectedIndex )
    self.lstOrder.insertTopLevelItem( selectedIndex - 1, selectedItem )
    self.lstOrder.clearSelection()
    selectedItem.setSelected( True )

  def moveLayerDown( self ):
    selection = self.lstOrder.selectedItems()
    if len( selection ) < 1:
      return

    selectedIndex = self.lstOrder.indexOfTopLevelItem( selection[0] )
    if selectedIndex < 0 or selectedIndex > self.lstOrder.topLevelItemCount() - 2:
      return

    selectedItem = self.lstOrder.takeTopLevelItem( selectedIndex )
    self.lstOrder.insertTopLevelItem( selectedIndex + 1, selectedItem )
    self.lstOrder.clearSelection()
    selectedItem.setSelected( True )

  def addLayers( self ):
    apiKey = self.leApiKey.text()

    myUri = QgsDataSourceURI()
    url = QString( "http://maps.kosmosnimki.ru/TileService.ashx/apikey%1" ).arg( apiKey )
    myUri.setParam( "url", url  )

    crs = self.crs
    layers = []
    styles = []

    for i in xrange( self.lstOrder.topLevelItemCount() - 1, -1, -1 ):
      layers.append( unicode( self.lstOrder.topLevelItem( i ).text( 0 ) ) )
      styles.append( "" )

    myUri.setParamList( "layers", layers )
    myUri.setParamList( "styles", styles )
    myUri.setParam( "format", "png" )
    myUri.setParam( "crs", crs )

    layer = QgsRasterLayer( unicode( myUri.encodedUri() ), unicode( "/".join( layers ) ), "wms" )
    QgsMapLayerRegistry.instance().addMapLayers( [ layer ] )
