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

    # TODO: update layers
    # TODO: update buttons

    self.update()

  def connectToServer( self ):
    apiKey = self.leApiKey.text()
    if apiKey.isEmpty():
      QMessageBox.warning( self, self.tr( "Missed API key" ), self.tr( "Please enter your API key and try again" ) )
      return

    # save settings
    settings = QSettings( "NextGIS", "ScanexExpress" )

    settings.setValue( "apiKey", self.leApiKey.text() )
    settings.setValue( "saveKey", self.chkSaveKey.isChecked() )

    # go-go-go
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

  def addLayers( self ):
    pass

  def showError( self, provider ):
    mv = QgsMessageViewer( self )
    mv.setWindowTitle( provider.errorCaption )

    if provider.errorFormat == "text/html":
      mv.setMessageAsHtml( provider.error )
    else:
      mv.setMessageAsPlainText( self.tr( "Could not understand the response. The provider said:\n%2" ).arg( provider.error ) )

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

    layers = []

    for item in currentSelection:
      layerName = item.data( 0, Qt.UserRole + 0 ).toString()

      if layerName.isEmpty():
        pass
      else:
        layers.append( layerName )
        if len( self.crss ) == 0:
          self.crss = set( item.data( 0, Qt.UserRole + 2 ).toStringList() )
        else:
          self.crss.intersection( set( item.data( 0, Qt.UserRole + 2 ).toStringList() ) )

    self.btnChangeCRS.setDisabled( True if len( self.crss ) == 0 else False )

    if len( layers ) > 0 and len( self.crss ) > 0:
      defaultCRS = ""
      notFound = True
      for crs in self.crss:
        if crs.lower() == self.crs.lower():
          notFound = False
          break

        if crs.lower() == self.crss[0].lower():
          defaultCRS = crs

        if crs.lower() == QGis.GEO_EPSG_CRS_AUTHID.lower():
          defaultCRS = crs

      if notFound:
        self.crs = defaultCRS
        self.lblCoordRefSys.setText( self.tr( "Coordinate Refrence System: %1" ).arg( self.descriptionForAuthId( self.crs ) ) )

      # TODO: update buttons
