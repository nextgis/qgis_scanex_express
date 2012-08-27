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

DEFAULT_LATLON_CRS = "CRS:84"

class WmsProvider:
  def __init__( self, uri):
    self.httpUri = uri
    self.httpCapabilitiesResponse = 0
    self.imageCrs = DEFAULT_LATLON_CRS
    self.cachedImage = 0
    self.cacheReply = 0
    self.cachedViewExtent = 0
    self.coordinateTransform = 0
    self.extentDirty = True
    self.getFeatureInfoUrlBase = ""
    self.layerCount = -1
    self.tileReqNo = 0
    self.cacheHits = 0
    self.cacheMisses = 0
    self.errors = 0
    self.userName = None
    self.password = None
    self.tiled = False
    self.tileLayer = 0
    self.tileMatrixSetId = None
    self.tileMatrixSet = 0
    self.featureCount = 0

    self.tileDimensionValues = dict()

    self.valid = True

    self.parseUri( uri )

  def parseUri( self, uriString ):
    uri = QgsDataSourceUri()
    uri.setEncodedUri( uriString )

    self.tiled = False
    self.tileMatrixSet = 0
    self.tileLayer = 0
    self.tileDimensionValues.clear()

    self.maxWidth = 0
    self.maxHeight = 0

    self.httpUri = uri.param( "url" )
    self.baseUrl = prepareUri( self.httpUri )

    self.ignoreGetMapUrl = uri.hasParam( "IgnoreGetMapUrl" )
    self.ignoreGetFeatureInfoUrl = uri.hasParam( "IgnoreGetFeatureInfoUrl" )
    self.ignoreAxisOrientation = uri.hasParam( "IgnoreAxisOrientation" )
    self.invertAxisOrientation = uri.hasParam( "InvertAxisOrientation" )

    self.userName = uri.param( "username" )
    self.password = uri.param( "password" )

    addLayers( uri.params( "layers" ), uri.params( "styles" ) )
    setImageEncoding( uri.param( "format" ) )

    if uri.hasParam( "maxWidth" and uri.hasParam( "maxHeight" ):
      self.maxWidth = uri.param( "maxWidth" ).toInt()[0]
      self.maxHeight = uri.param( "maxHeight" ).toInt()[0]

    if uri.hasParam( "tileMatrixSet" ):
      self.tiled = True
      self.tileMatrixSetId = uri.param( "tileMatrixSet" )

    if uri.hasParam( "tileDimensions" ):
      self.tiled = True
      for param in uri.params( "tileDimensions" ):
        kv = param.split( "=" )
        if kv.size() == 1:
          self.tileDimensionValues.insert( kv[0], None )
        elif kv.size() == 2:
          self.tileDimensionValues.insert( kv[0], kv[1] )
        else:
          print "skipped dimension", param

    setImageCrs( uri.param( "crs" ) )
    self.crs.createFromOgcWmsCrs( uri.param( "crs" ) )

    self.featureCount = uri.param( "featureCount" ).toInt()[0]

  def prepareUri( self, uri ):
    if uri.contains( "SERVICE=WMTS" ) or uri.contains( "/WMTSCapabilities.xml" ):
      return uri;

    if not uri.contains( "?" ):
      uri.append( "?" );
    elif uri.right( 1 ) != "?" and uri.right( 1 ) != "&":
      uri.append( "&" )

    return uri;

  def supportedLayers(self, layers):
    if not self.retrieveServerCapabilities():
      return False

    return True

  def retrieveServerCapabilities( self, forceRefresh ):
    if self.httpCapabilitiesResponse.isNull() or forceRefresh:
      url = self.baseUrl

      if not url.contains( "SERVICE=WMTS" ) and not url.contains( "/WMTSCapabilities.xml" ):
        url += "SERVICE=WMS&REQUEST=GetCapabilities"

      self.error = ""

      request = QNetworkRequest( url )
      self.setAuthorization( request )
      request.setAttribute( QNetworkRequest.CacheLoadControlAttribute, QNetworkRequest.PreferNetwork )
      request.setAttribute( QNetworkRequest.CacheSaveControlAttribute, true )

      self.capabilitiesReply = QgsNetworkAccessManager.instance().get( request )

      # TODO: add singals

      while self.capabilitiesReply:
        QCoreApplication.processEvents( QEventLoop.ExcludeUserInputEvents )

      if self.httpCapabilitiesResponse.isEmpty():
        if self.error.isEmpty():
          self.error = "empty capabilities document"
        return False

      if self.httpCapabilitiesResponse.startsWith( "<html>" ) or self.httpCapabilitiesResponse.startsWith( "<HTML>" ):
        self.error = self.httpCapabilitiesResponse
        return False

      domOk = self.parseCapabilitiesDom()
      if not domOk:
        self.error = "Tried URL: " + url
        return False

    return True

  def setAuthorization( self, request ):
    if not self.userName.isNull() or not self.password.isNull():
      request.setRawHeader( "Authorization", "Basic " + QString( "%1:%2" ).arg( mUserName ).arg( mPassword ).toAscii().toBase64() )

  def parseCapabilitiesDom( self, xml ):
    self.capabilitiesDom = QDomDocument()
    self.capabilitiesProperty = dict()

    contentSuccess, errorMsg, errorLine, errorColumn = self.capabilitiesDom.setContent( xml, False )
    if not contentSuccess:
      self.error = QString( "Could not get WMS capabilities: %1 at line %2 column %3\nThis is probably due to an incorrect WMS Server URL.\nResponse was:\n\n%4" )
                   .arg( errorMsg )
                   .arg( errorLine )
                   .arg( errorColumn )
                   .arg( QString( xml ) )
      return False

    docElem = self.capabilitiesDom.documentElement()
    if docElem.tagName() != "WMS_Capabilities"  and
       docElem.tagName() != "WMT_MS_Capabilities" and
       docElem.tagName() != "Capabilities":
      self.error = QString( "Could not get WMS capabilities in the expected format (DTD): no %1 or %2 found.\nThis might be due to an incorrect WMS Server URL.\nTag:%3\nResponse was:\n%4" )
                   .arg( "WMS_Capabilities" )
                   .arg( "WMT_MS_Capabilities" )
                   .arg( docElem.tagName() )
                   .arg( QString( xml ) )
      return False

    self.capabilitiesProperty["version"] = docElem.attribute( "version" )

  # Start walking through XML.
  QDomNode n = docElem.firstChild()
  while not n.isNull():
    e = n.toElement()
    if not e.isNull():
      if e.tagName() in [ "Service", "ows:ServiceProvider", "ows:ServiceIdentification" ]:
        print "  Service"
        self.parseService( e )
      elif e.tagName() in [ "Capability", "ows:OperationsMetadata" ]:
        print "  Capability"
        self.parseCapability( e )
      elif e.tagName() in [ "Contents" ]:
        print "  Contents"
        self.parseWMTSContents( e )

    n = n.nextSibling()

  return True

  def parseService( self, e ):
    self.serviceProperty = dict()
    n1 = e.firstChild()
    while not n1.isNull():
      e1 = n1.toElement()
      if not e1.isNull():
        tagName = e1.tagName()
        if tagName.startsWith( "wms:" ):
          tagName = tagName.mid( 4 )
        if tagName.startsWith( "ows:" ):
          tagName = tagName.mid( 4 )

        if tagName == "Title":
          self.serviceProperty["title"] = e1.text()
        elif tagName == "Abstract":
          self.serviceProperty["abstract"] = e1.text()
        elif tagName in [ "KeywordList", "Keywords" ]:
          self.parseKeywordList( e1 )
        elif tagName == "OnlineResource":
          self.parseOnlineResource( e1 )
        elif tagName in [ "ContactInformation", "ServiceContact" ]:
          parseContactInformation( e1 )
        elif tagName == "Fees":
          self.serviceProperty["fees"] = e1.text()
        elif tagName == "AccessConstraints":
          self.serviceProperty["accessConstraints"] = e1.text()
        elif tagName == "LayerLimit":
          self.serviceProperty["layerLimit"] = e1.text().toUInt()[0]
        elif tagName == "MaxWidth":
          self.serviceProperty["maxWidth"] = e1.text().toUInt()[0]
        elif tagName == "MaxHeight":
          self.serviceProperty["maxHeight"] = e1.text().toUInt()[0]

      n1 = n1.nextSibling()

  def parseCapability( self, e ):
    pass

  def parseWMTSContents( self, e ):
    pass
