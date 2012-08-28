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

from ui_addlayersdialogbase import Ui_Dialog

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

    self.manageGui()

  def manageGui( self ):
    settings = QSettings( "NextGIS", "ScanexExpress" )

    self.leApiKey.setText( settings.value( "apiKey", "" ).toString() )
    self.chkSaveKey.setChecked( settings.value( "saveKey", True ).toBool() )

    # set the current project CRS if available
    currentCRS = QgsProject.instance().readNumEntry( "SpatialRefSys", "/ProjectCRSID", -1 )[0]
    print currentCRS
    if currentCRS != -1:
      currentRefSys = QgsCoordinateReferenceSystem( currentCRS, QgsCoordinateReferenceSystem.InternalCrsId )
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

    uri = QgsDataSourceURI()
    url = QString( "http://maps.kosmosnimki.ru/TileService.ashx/apikey%1" ).arg( apikey )
    uri.setParam( "url", url  )

    provider = wmsprovider.WmsProvider( uri.encodedUri() )

  def addLayers( self ):
    pass