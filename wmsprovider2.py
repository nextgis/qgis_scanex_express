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
from PyQt4.QtXml import *
from PyQt4.QtNetwork import *

from qgis.core import *

DEFAULT_LATLON_CRS = "CRS:84"

class WmsProvider( QObject ):
  def __init__( self, uri ):
    QObject.__init__( self )

    self.httpUri = None
    self.baseUrl = None
    self.error = QString()
    self.httpCapabilitiesResponse = QByteArray()
    self.capabilitiesReply = None
    self.layersSupported = []

    self.valid = True

    self.parseUri( uri )

  def parseUri( self, uriString ):
    uri = QgsDataSourceURI()
    uri.setEncodedUri( unicode( uriString ) )

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
    if not self.retrieveServerCapabilities():
      return False

    #for l in self.layersSupported:
    #  print l
    return True

  def retrieveServerCapabilities( self ):
    print "retrieveServerCapabilities"
    if self.httpCapabilitiesResponse.isNull():
      url = self.baseUrl
      if not url.contains( "SERVICE=WMTS" ) and not url.contains( "/WMTSCapabilities.xml" ):
        url += "SERVICE=WMS&REQUEST=GetCapabilities"

      request = QNetworkRequest( QUrl( url ) )
      request.setAttribute( QNetworkRequest.CacheLoadControlAttribute, QNetworkRequest.PreferNetwork )
      request.setAttribute( QNetworkRequest.CacheSaveControlAttribute, True )

      self.capabilitiesReply = QgsNetworkAccessManager.instance().get( request )

      self.capabilitiesReply.finished.connect( self.capabilitiesReplyFinished )
      self.capabilitiesReply.downloadProgress.connect( self.capabilitiesReplyProgress )

      while self.capabilitiesReply:
        QCoreApplication.processEvents( QEventLoop.ExcludeUserInputEvents )

      if self.httpCapabilitiesResponse.isEmpty():
        self.error = self.tr( "empty capabilities document" )
        if self.error.isEmpty():
          self.errorFormat = "text/plain"
          self.error = self.tr( "empty capabilities document" )
        return False

      if self.httpCapabilitiesResponse.startsWith( "<html>" ) or self.httpCapabilitiesResponse.startsWith( "<HTML>" ):
        self.errorFormat = "text/html"
        self.error = self.httpCapabilitiesResponse
        return False

      # converting to DOM
      print "converting to DOM"

      if not self.parseCapabilitiesDom():
        self.error += self.tr( "\nTried URL: %1" ).arg( url )
        print "!domOK"
        return False

    return True

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

      redirect = self.capabilitiesReply.attribute( QNetworkRequest.RedirectionTargetAttribute )
      if not redirect.isNull():
        print "Capabilities request redirected"
        #self.statusChanged.emit( tr( "Capabilities request redirected." ) )

        request = QNetworkRequest( redirect.toUrl() )
        request.setAttribute( QNetworkRequest.CacheLoadControlAttribute, QNetworkRequest.PreferNetwork )
        request.setAttribute( QNetworkRequest.CacheSaveControlAttribute, True )

        self.capabilitiesReply.deleteLater()
        self.capabilitiesReply = QgsNetworkAccessManager.instance().get( request )

        self.capabilitiesReply.finished.connect( self.capabilitiesReplyFinished )
        self.capabilitiesReply.downloadProgress.connect( self.capabilitiesReplyProgress )
        return

      self.httpCapabilitiesResponse = self.capabilitiesReply.readAll()

      if self.httpCapabilitiesResponse.isEmpty():
        self.errorFormat = "text/plain"
        self.error = self.tr( "empty of capabilities: %1" ).arg( self.capabilitiesReply.errorString() )
    else:
      self.errorFormat = "text/plain"
      self.error = self.tr( "Download of capabilities failed: %1" ).arg( self.capabilitiesReply.errorString() )
      self.httpCapabilitiesResponse.clear()

    self.capabilitiesReply.deleteLater()
    self.capabilitiesReply = None

  def parseCapabilitiesDom( self ):
    self.capabilitiesDom = QDomDocument()

    # convert completed document into a Dom
    contentSuccess, errorMsg, errorLine, errorColumn = self.capabilitiesDom.setContent( self.httpCapabilitiesResponse, False )
    if not contentSuccess:
      self.errorCaption = self.tr( "Dom Exception" )
      self.errorFormat = "text/plain"
      self.error = QString( "Could not get WMS capabilities: %1 at line %2 column %3\nThis is probably due to an incorrect WMS Server URL.\nResponse was:\n\n%4" ).arg( errorMsg ).arg( errorLine ).arg( errorColumn ).arg( QString( self.httpCapabilitiesResponse ) )
      return False

    docElem = self.capabilitiesDom.documentElement()

    # assert that the DTD is what we expected (i.e. a WMS Capabilities document)
    print "testing tagName", docElem.tagName()

    if docElem.tagName() not in [ "WMS_Capabilities", "WMT_MS_Capabilities", "Capabilities" ]:
      self.errorCaption = self.tr( "Dom Exception" )
      self.errorFormat = "text/plain"
      self.error = QString( "Could not get WMS capabilities in the expected format (DTD): no %1 or %2 found.\nThis might be due to an incorrect WMS Server URL.\nTag:%3\nResponse was:\n%4" ).arg( "WMS_Capabilities" ).arg( "WMT_MS_Capabilities" ).arg( docElem.tagName() ).arg( QString( self.httpCapabilitiesResponse ) )
      return False

    # start walking through XML
    n = docElem.firstChild()
    while not n.isNull():
      e = n.toElement()
      if e.tagName() in [ "Service", "ows:ServiceProvider", "ows:ServiceIdentification" ]:
        print "  Service"
        #self.parseService( e )
      elif e.tagName() in [ "Capability", "ows:OperationsMetadata" ]:
        print "  Capability"
        self.parseCapability( e )
      elif e.tagName() in [ "Contents" ]:
        print "  Contents"
        #self.parseWMTSContents( e )

      n = n.nextSibling()

    return True

  def parseCapability( self, e ):
    n1 = e.firstChild()
    while not n1.isNull():
      e1 = n1.toElement()
      if e1.isNull():
        continue

      tagName = e1.tagName()
      if tagName.startsWith( "wms:" ):
        tagName = tagName.mid( 4 )

      print "  ", e1.tagName()

      if tagName == "Request":
        print "  Request"
        #self.parseRequest( e1 )
      elif tagName == "Layer":
        print "  Layer"
        lay = self.parseLayer( e1 )
        self.layersSupported.append( lay )
      elif tagName == "VendorSpecificCapabilities":
        print "  Vendor Capabilities"
      elif tagName == "ows:Operation":
        print "  Operation"

      n1 = n1.nextSibling()

  def parseLayer( self, e ):
    print "parseLayer"
    layer = dict()
    layer[ "layer" ] = []

    n1 = e.firstChild()
    while not n1.isNull():
      e1 = n1.toElement()
      first = True
      if not e1.isNull():
        tagName = e1.tagName()
        if tagName.startsWith( "wms:" ):
          tagName = tagName.mid( 4 )

        if tagName == "Layer":
          print "      Nested layer."
          layer[ "layer" ].append( self.parseLayer( e1 ) )

        elif tagName == "Name":
          layer[ "name" ] = e1.text()
        elif tagName == "Title":
          layer[ "title" ] = e1.text()
        elif tagName == "Abstract":
          layer[ "abstract" ] = e1.text()
        elif tagName == "Description":
          layer[ "description" ] = e1.text()
        elif tagName == "CreateDate":
          layer[ "createDate" ] = e1.text()
        elif tagName == "Copyright":
          layer[ "copyright" ] = e1.text()
        elif tagName == "KeywordList":
          pass
        elif tagName in [ "SRS", "CRS" ]:
          print "SRS", e1.text().split( QRegExp( "\\s+" ) )
          for srs in e1.text().split( QRegExp( "\\s+" ) ):
            #print "***", srs
            if first:
              layer[ "crs" ] = [ srs ]
              first = False
            lst = layer[ "crs" ]
            lst.append( srs )
            layer[ "crs" ] = lst
            print layer[ "crs" ]
        elif tagName == "LatLonBoundingBox":
          pass
        elif tagName == "EX_GeographicBoundingBox":
          pass
        elif tagName == "BoundingBox":
          pass
        elif tagName == "Dimension":
          pass
        elif tagName == "Attribution":
          pass
        elif tagName == "AuthorityURL":
          pass
        elif tagName == "Identifier":
          pass
        elif tagName == "MetadataURL":
          pass
        elif tagName == "DataURL":
          pass
        elif tagName == "FeatureListURL":
          pass
        elif tagName == "Style":
          pass
        elif tagName == "MinScaleDenominator":
          pass
        elif tagName == "MaxScaleDenominator":
          pass

      n1 = n1.nextSibling()

    return layer
