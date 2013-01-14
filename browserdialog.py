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
from PyQt4.QtNetwork import *

from qgis.core import *
from qgis.gui import *

from ui_browserdialogbase import Ui_Dialog

class BrowserDialog( QDialog, Ui_Dialog ):
  def __init__( self ):
    QDialog.__init__( self )
    self.setupUi( self )

    self.__setupProxy()

    self.webView.load( QUrl("http://my.kosmosnimki.ru/Account/LoginDialog?client_id=6472&redirect_uri=http%3A%2F%2Flocalhost%3A1760%2FSite%2FoAuth%2FoAuthCallback.ashx%3Fcallback%3Dhttp%3A%2F%2Flocalhost%2Fapi%2FoAuthCallback.html&scope=basic&state=XAYLTRT6&partnerID=3be2ac3e-22cf-466c-9dda-66d0ec107352", QUrl.StrictMode) )
    self.webView.urlChanged.connect(self.processUrl)

  def processUrl(self, url):
    print "New URL\n", url

    if url.toString() == "http://my.kosmosnimki.ru/Account/LoginDialog?client_id=6472&redirect_uri=http%3A%2F%2Flocalhost%3A1760%2FSite%2FoAuth%2FoAuthCallback.ashx%3Fcallback%3Dhttp%3A%2F%2Flocalhost%2Fapi%2FoAuthCallback.html&scope=basic&state=XAYLTRT6&partnerID=3be2ac3e-22cf-466c-9dda-66d0ec107352":
      return

    self.webView.stop()

    if url.hasQueryItem( "code" ):
      mystate = url.queryItemValue( "state" )
      if mystate != "XAYLTRT6":
        print "state error", mystate
        self.done( QDialog.Rejected )

      self.mycode = url.queryItemValue( "code" )
      self.done( QDialog.Accepted )
    elif url.hasQueryItem( "error_reason" ):
      self.webView.load( QUrl("http://my.kosmosnimki.ru/Account/LoginDialog?client_id=6472&redirect_uri=http%3A%2F%2Flocalhost%3A1760%2FSite%2FoAuth%2FoAuthCallback.ashx%3Fcallback%3Dhttp%3A%2F%2Flocalhost%2Fapi%2FoAuthCallback.html&scope=basic&state=XAYLTRT6&partnerID=3be2ac3e-22cf-466c-9dda-66d0ec107352", QUrl.StrictMode) )
    else:
      self.webView.load( QUrl("http://my.kosmosnimki.ru/Account/LoginDialog?client_id=6472&redirect_uri=http%3A%2F%2Flocalhost%3A1760%2FSite%2FoAuth%2FoAuthCallback.ashx%3Fcallback%3Dhttp%3A%2F%2Flocalhost%2Fapi%2FoAuthCallback.html&scope=basic&state=XAYLTRT6&partnerID=3be2ac3e-22cf-466c-9dda-66d0ec107352", QUrl.StrictMode) )

  def getSecretCode( self ):
    return self.mycode

  def __setupProxy(self):
    settings = QSettings()
    if settings.value("/proxyEnabled", False).toBool():
      proxyHost = settings.value("/proxyHost", "").toString()
      proxyPost = settings.value("/proxyPort", "").toString().toInt()[0]
      proxyUser = settings.value("/proxyUser", "").toString()
      proxyPass = settings.value("/proxyPassword", "").toString()
      proxyTypeString = settings.value( "proxy/proxyType", "" ).toString()

      proxyType = QNetworkProxy.NoProxy
      if proxyTypeString == "DefaultProxy":
        proxyType = QNetworkProxy.DefaultProxy
      elif proxyTypeString == "Socks5Proxy":
        proxyType = QNetworkProxy.Socks5Proxy
      elif proxyTypeString == "HttpProxy":
        proxyType = QNetworkProxy.HttpProxy
      elif proxyTypeString == "HttpCachingProxy":
        proxyType = QNetworkProxy.HttpCachingProxy
      elif proxyTypeString == "FtpCachingProxy":
        proxyType = QNetworkProxy.FtpCachingProxy

      proxy = QNetworkProxy( proxyType, proxyHost, proxyPort, proxyUser, proxyPass )
      self.webView.page().networkAccessManager().setProxy( proxy )
