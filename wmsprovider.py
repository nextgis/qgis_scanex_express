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

class QgsWmsOnlineResourceAttribute:
  self.xlinkHref = QString()

class QgsWmsGetProperty:
  self.onlineResource = QgsWmsOnlineResourceAttribute()

class QgsWmsPostProperty:
  self.onlineResource = QgsWmsOnlineResourceAttribute()

class QgsWmsHttpProperty:
  self.get = QgsWmsGetProperty()
  self.post = QgsWmsPostProperty()

class QgsWmsDcpTypeProperty:
  self.http = QgsWmsHttpProperty()

class QgsWmsOperationType:
  self.format = QStringList()
  self.dcpType = []
  self.allowedEncodings = QStringList()

class QgsWmsRequestProperty:
  self.getMap = QgsWmsOperationType()
  self.getFeatureInfo = QgsWmsOperationType()
  self.getTile = QgsWmsOperationType()

class QgsWmsExceptionProperty:
  self.format = QStringList()

class QgsWmsContactPersonPrimaryProperty:
  self.contactPerson = QString()
  self.contactOrganization = QString()

class QgsWmsContactAddressProperty:
  self.addressType = QString()
  self.address = QString()
  self.city = QString()
  self.stateOrProvince = QString()
  self.postCode = QString()
  self.country = QString()

class QgsWmsContactInformationProperty:
  self.contactPersonPrimary = QgsWmsContactPersonPrimaryProperty()
  self.contactPosition = QString()
  self.contactAddress = QgsWmsContactAddressProperty()
  self.contactVoiceTelephone = QString()
  self.contactFacsimileTelephone = QString()
  self.contactElectronicMailAddress = QString()

class QgsWmsServiceProperty:
  self.title = QString()
  self.abstract = QString()
  self.keywordList = QStringList()
  self.onlineResource = QgsWmsOnlineResourceAttribute()
  self.contactInformation = QgsWmsContactInformationProperty()
  self.fees = QString()
  self.accessConstraints = QString()
  self.layerLimit = -1
  self.maxWidth = -1
  self.maxHeight = -1

class QgsWmsBoundingBoxProperty:
  self.crs = QString()
  self.box = QgsRectangle()
  self.resx = 0.0
  self.resy = 0.0

class QgsWmsDimensionProperty:
  self.name = QString()
  self.units = QString()
  self.unitSymbol = QString()
  self.defaultValue = QString()
  self.multipleValues = False
  self.nearestValue = False
  self.current = False

class QgsWmsLogoUrlProperty:
  self.format = QString()
  self.onlineResource = QgsWmsOnlineResourceAttribute()
  self.width = -1
  self.height = -1

class QgsWmsAttributionProperty:
  self.title = QString()
  self.onlineResource = QgsWmsOnlineResourceAttribute()
  self.logoUrl = QgsWmsLogoUrlProperty()

class QgsWmsLegendUrlProperty:
  self.format = QString()
  self.onlineResource = QgsWmsOnlineResourceAttribute()
  self.width = -1
  self.height = -1

class QgsWmsStyleSheetUrlProperty:
  self.format = QString()
  self.onlineResource = QgsWmsOnlineResourceAttribute()

class QgsWmsStyleUrlProperty:
  self.format = QString()
  self.onlineResource = QgsWmsOnlineResourceAttribute()

class QgsWmsStyleProperty:
  self.name = QString()
  self.title = QString()
  self.abstract = QString()
  self.legendUrl = []
  self.styleSheetUrl = QgsWmsStyleSheetUrlProperty()
  self.styleUrl = QgsWmsStyleUrlProperty()

class QgsWmsAuthorityUrlProperty:
  self.onlineResource = QgsWmsOnlineResourceAttribute()
  self.name = QString()

class QgsWmsIdentifierProperty:
  self.authority = QString()

class QgsWmsMetadataUrlProperty:
  self.format = QString()
  self.onlineResource = QgsWmsOnlineResourceAttribute()
  self.type = QString()

class QgsWmsDataListUrlProperty:
  self.format = QString()
  self.onlineResource = QgsWmsOnlineResourceAttribute()

class QgsWmsFeatureListUrlProperty:
  self.format = QString()
  self.onlineResource = QgsWmsOnlineResourceAttribute()

class QgsWmsLayerProperty:
  self.orderId = -1
  self.name = QString()
  self.title = QString()
  self.abstract = QString()
  self.keywordList = QStringList()
  self.crs = QStringList()
  self.ex_GeographicBoundingBox = QgsRectangle()
  self.boundingBox = []
  self.dimension = []
  self.attribution = QgsWmsAttributionProperty()
  self.authorityUrl = []
  self.identifier = []
  self.metadataUrl = []
  self.dataListUrl = []
  self.featureListUrl = []
  self.style = []
  self.minimumScaleDenominator = 0.0
  self.maximumScaleDenominator = 0.0
  self.layer = []

  self.queryable = False
  self.cascaded = -1
  self.opaque = False
  self.noSubsets = False
  self.fixedWidth = -1
  self.fixedHeight = -1

class QgsWmtsTheme:
  self.identifier = QString()
  self.title = QString()
  self.abstract = QString()
  self.keywords = QStringList()
  self.subTheme = None
  self.layerRefs = QStringList()

class QgsWmtsTileMatrix:
  self.identifier = QString()
  self.title = QString()
  self.abstract = QString()
  self.keywords = QStringList()
  self.scaleDenom = 0.0
  self.topLeft = QgsPoint()
  self.tileWidth = -1
  self.tileHeight = -1
  self.matrixWidth = -1
  self.matrixHeight = -1

class QgsWmtsTileMatrixSet:
  self.identifier = QString()
  self.title = QString()
  self.abstract = QString()
  self.keywords = QString()
  self.boundingBox = QString()
  self.crs = None
  self.wkScaleSet = None
  self.tileMatrices = None

class QgsWmtsTileMatrixLimits:
  self.tileMatrix = -1
  self.minTileRow = -1
  self.maxTileRow = -1
  self.minTileCol = -1
  self.maxTileCol = -1

class QgsWmtsTileMatrixSetLink:
  self.tileMatrixSet = None
  self.limits = None

class QgsWmtsLegendURL:
  self.format = None
  self.minScale = None
  self.maxScale = None
  self.href = None
  self.width = None
  self.height = None

class QgsWmtsStyle:
  self.identifier = None
  self.title = None
  self.abstract = None
  self.keywords = None
  self.isDefault = None
  self.legendURLs = None

class QgsWmtsDimension:
  self.identifier = None
  self.title = None
  self.abstract = None
  self.keywords = None
  self.UOM = None
  self.unitSymbol = None
  self.defaultValue = None
  self.current = None
  self.values = None

class QgsWmtsTileLayer:
  self.tileMode = None
  self.identifier = None
  self.title = None
  self.abstract = None
  self.keywords = None
  self.boundingBox = None
  self.formats = None
  self.infoFormats = None
  self.defaultStyle = None
  self.dimensions = None
  self.styles = None
  self.setLinks = None

  self.getTileURLs = None
  self.getFeatureInfoURLs = None

class QgsWmsCapabilityProperty:
  self.request = None
  self.exception = None
  self.layer = None

  self.tileLayers = None
  self.tileMatrixSets = None

class QgsWmsCapabilitiesProperty:
  self.service = None
  self.capability = None
  self.version = None

class QgsWmsSupportedFormat:
  self.format = None
  self.label = None

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
    n1 = e.firstChild()
    while not n1.isNull():
      e1 = n1.toElement()
      if e1.isNull():
        continue

      tagName = e1.tagName()
      if tagName.startsWith( "wms:" ):
        tagName = tagName.mid( 4 )

      if tagName == "Request":
        self.parseRequest( e1 )
      elif tagName == "Layer":
        self.parseLayer( e1 )
      elif tagName == "VendorSpecificCapabilities":
        for i in xrange( e1.childNodes().size() ):
          n2 = e1.childNodes().item( i )
          e2 = n2.toElement()
          tName = e2.tagName()
          if tName.startsWith( "wms:" ):
            tName = tName.mid( 4 )

          if tName == "TileSet":
            self.parseTileSetProfile( e2 )
      elif tagName == "ows:Operation":
        name = e1.attribute( "name" )
        get = n1.firstChildElement( "ows:DCP" ).firstChildElement( "ows:HTTP" ).firstChildElement( "ows:Get" )
        href = get.attribute( "xlink:href" )

        dcp = QgsWmsDcpTypeProperty()
        dcp.http.get.onlineResource.xlinkHref = href

        ot = QgsWmsOperationType()
        if href.isNull():
          print "http get missing from ows:Operation '%s'" % unicode(name)
        elif name == "GetTile":
          self.capabilityProperty.request.getTile = dcp
        elif name == "GetFeatureInfo":
          self.capabilityProperty.request.getFeatureInfo = dcp
        else:
          print "ows:Operation %s ignored" % unicode( name )

      n1 = n1.nextSibling()

  def parseWMTSContents( self, e ):
    pass
