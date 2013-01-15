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

from ui_aboutdialogbase import Ui_Dialog

from __init__ import version
import resources_rc

class AboutDialog( QDialog, Ui_Dialog ):
  def __init__( self ):
    QDialog.__init__( self )
    self.setupUi( self )

    self.btnHelp = self.buttonBox.button( QDialogButtonBox.Help )

    self.lblLogo.setPixmap( QPixmap(":/icons/scanexexpress.png") )
    self.lblVersion.setText( self.tr( "Version: %1" ).arg( version() ) )
    doc = QTextDocument()
    doc.setHtml( self.getAboutText() )
    self.textBrowser.setDocument( doc )

    self.buttonBox.helpRequested.connect( self.openHelp )

  def reject( self ):
    QDialog.reject( self )

  def openHelp( self ):
    overrideLocale = QSettings().value( "locale/overrideFlag", QVariant( False ) ).toBool()
    if not overrideLocale:
      localeFullName = QLocale.system().name()
    else:
      localeFullName = QSettings().value( "locale/userLocale", QVariant( "" ) ).toString()

    localeShortName = localeFullName[ 0:2 ]
    if localeShortName in [ "ru", "uk" ]:
      QDesktopServices.openUrl( QUrl( "http://scanex.ru" ) )
    else:
      QDesktopServices.openUrl( QUrl( "http://scanex.ru" ) )

  def getAboutText( self ):
    return self.tr( """<p>Waiting for text</p>
""")
