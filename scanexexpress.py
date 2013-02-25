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

from __init__ import version

import addlayersdialog
import aboutdialog

import resources_rc

class ScanexExpressPlugin:
  def __init__( self, iface ):
    self.iface = iface

    try:
      self.QgisVersion = unicode( QGis.QGIS_VERSION_INT )
    except:
      self.QgisVersion = unicode( QGis.qgisVersion )[ 0 ]

    # For i18n support
    userPluginPath = QFileInfo( QgsApplication.qgisUserDbFilePath() ).path() + "/python/plugins/scanex_express"
    systemPluginPath = QgsApplication.prefixPath() + "/python/plugins/scanex_express"

    overrideLocale = QSettings().value( "locale/overrideFlag", QVariant( False ) ).toBool()
    if not overrideLocale:
      localeFullName = QLocale.system().name()
    else:
      localeFullName = QSettings().value( "locale/userLocale", QVariant( "" ) ).toString()

    if QFileInfo( userPluginPath ).exists():
      translationPath = userPluginPath + "/i18n/scanexexpress_" + localeFullName + ".qm"
    else:
      translationPath = systemPluginPath + "/i18n/scanexexpress_" + localeFullName + ".qm"

    if QFileInfo( translationPath ).exists():
      self.translator = QTranslator()
      self.translator.load( translationPath )
      QCoreApplication.installTranslator( self.translator )

  def initGui( self ):
    if int( self.QgisVersion ) < 10800:
      qgisVersion = str( self.QgisVersion[ 0 ] ) + "." + str( self.QgisVersion[ 2 ] ) + "." + str( self.QgisVersion[ 3 ] )
      QMessageBox.warning( self.iface.mainWindow(),
                           QCoreApplication.translate( "ScanexExpress", "Error" ),
                           QCoreApplication.translate( "ScanexExpress", "Quantum GIS %1 detected.\n" ).arg( qgisVersion ) +
                           QCoreApplication.translate( "ScanexExpress", "This version of ScanexExpress requires at least QGIS version 1.9.0. Plugin will not be enabled." ) )
      return None

    self.loadBaseLayers = QAction( QCoreApplication.translate( "ScanexExpress", "Basic coverage" ), self.iface.mainWindow() )
    self.iface.registerMainWindowAction( self.loadBaseLayers, "Shift+C" )
    self.loadBaseLayers.setIcon( QIcon( ":/icons/basic_coverage.png" ) )
    self.loadBaseLayers.setWhatsThis( "Add basic free layers to map" )

    self.loadUserLayers = QAction( QCoreApplication.translate( "ScanexExpress", "My layers" ), self.iface.mainWindow() )
    self.iface.registerMainWindowAction( self.loadUserLayers, "Shift+U" )
    self.loadUserLayers.setIcon( QIcon( ":/icons/add_layers.png" ) )
    self.loadUserLayers.setWhatsThis( "Add your layers to map" )

    self.showAboutDialog = QAction( QCoreApplication.translate( "ScanexExpress", "About ScanexExpress..." ), self.iface.mainWindow() )
    self.showAboutDialog.setIcon( QIcon( ":/icons/about.png" ) )
    self.showAboutDialog.setWhatsThis( "About ScanexExpress plugin" )

    self.loadBaseLayers.triggered.connect( self.baseLayers )
    self.loadUserLayers.triggered.connect( self.userLayers )
    self.showAboutDialog.triggered.connect( self.about )

    self.iface.addPluginToWebMenu( QCoreApplication.translate( "ScanexExpress", "ScanexExpress" ), self.loadBaseLayers )
    self.iface.addPluginToWebMenu( QCoreApplication.translate( "ScanexExpress", "ScanexExpress" ), self.loadUserLayers )
    self.iface.addPluginToWebMenu( QCoreApplication.translate( "ScanexExpress", "ScanexExpress" ), self.showAboutDialog )
    self.iface.addWebToolBarIcon( self.loadBaseLayers )
    self.iface.addWebToolBarIcon( self.loadUserLayers )

  def unload( self ):
    self.iface.unregisterMainWindowAction( self.loadBaseLayers )
    self.iface.unregisterMainWindowAction( self.loadUserLayers )

    self.iface.removePluginWebMenu( QCoreApplication.translate( "ScanexExpress", "ScanexExpress" ), self.loadBaseLayers )
    self.iface.removePluginWebMenu( QCoreApplication.translate( "ScanexExpress", "ScanexExpress" ), self.loadUserLayers )
    self.iface.removePluginWebMenu( QCoreApplication.translate( "ScanexExpress", "ScanexExpress" ), self.showAboutDialog )
    self.iface.removeWebToolBarIcon( self.loadBaseLayers )
    self.iface.removeWebToolBarIcon( self.loadUserLayers )

  def baseLayers( self ):
    url = "crs=EPSG:3395&featureCount=10&format=image/png&layers=C9458F2DCB754CEEACC54216C7D1EB0A&styles=&url=http://maps.kosmosnimki.ru/TileService.ashx/apikeySA7F1UIEY0"
    layer = QgsRasterLayer( url,
                            QCoreApplication.translate( "ScanexExpress", "Basic coverage Kosmosnimki.Ru"),
                            "wms"
                          )

    QgsMapLayerRegistry.instance().addMapLayers( [ layer ] )

  def userLayers( self ):
    dlg = addlayersdialog.AddLayersDialog( self.iface )
    dlg.show()
    dlg.exec_()

  def about( self ):
    dlg = aboutdialog.AboutDialog()
    dlg.exec_()
