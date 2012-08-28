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
from PyQt4.QtNetwork import *
from PyQt4.QtGui import *

from qgis.core import *

DEFAULT_LATLON_CRS = "CRS:84"

class WmsProvider( QObject ):
  def __init__( self, uri ):
    QObject.__init__( self )

    self.httpUri = None
    self.baseUrl = None
    self.httpCapabilitiesResponse = QByteArray()
    self.capabilitiesReply = None

    self.valid = True

    self.parseUri( uri )

  def parseUri( self, uriString ):
    uri = QgsDataSourceURI()
    uri.setEncodedUri( uriString )

    self.httpUri = uri.param( "url" )
    self.baseUrl = self.prepareUri( self.httpUri )

  def prepareUri( self, uri ):
    if uri.contains( "SERVICE=WMTS" ) or uri.contains( "/WMTSCapabilities.xml" ):
      return uri

    if not uri.contains( "?" ):
      uri.append( "?" );
    elif uri.right( 1 ) != "?" and uri.right( 1 ) != "&":
      uri.append( "&" )

    return uri

  def supportedLayers( self ):
    if not retrieveServerCapabilities():
      return False

    return True

  def retrieveServerCapabilities( self ):
    print "load capabilities"
    if self.httpCapabilitiesResponse.isNull():
      url = self.baseUrl
      if not url.contains( "SERVICE=WMTS" ) and not url.contains( "/WMTSCapabilities.xml" ):
        url += "SERVICE=WMS&REQUEST=GetCapabilities"

      self.error = ""

      request = QNetworkRequest( url )
      self.setAuthorization( request )
      request.setAttribute( QNetworkRequest.CacheLoadControlAttribute, QNetworkRequest.PreferNetwork )
      request.setAttribute( QNetworkRequest.CacheSaveControlAttribute, True )

      self.capabilitiesReply = QgsNetworkAccessManager.instance().get( request )

      self.capabilitiesReply.finished.connect( self.capabilitiesReplyFinished )
      self.capabilitiesReply.downloadProgress.connect( self.capabilitiesReplyProgress )

      while self.capabilitiesReply:
        QCoreApplication.processEvents( QEventLoop.ExcludeUserInputEvents )

  def capabilitiesReplyProgress( self, bytesReceived, bytesTotal ):
    bt = QString( "unknown number of" )
    if bytesTotal > 0:
      bt = QString.number( bytesTotal )
    msg = self.tr( "%1 of %2 bytes of capabilities downloaded." ).arg( bytesReceived ).arg( bt )
    print unicode( msg )
    #self.statusChanged.emit()

  def capabilitiesReplyFinished( self ):
    if self.capabilitiesReply.error() == QNetworkReply.NoError:
      print "reply ok"
