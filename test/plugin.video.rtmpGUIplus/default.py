#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
__settings__   = xbmcaddon.Addon()

BASE=[
('http://raspberrypi.cl/raspbmctv/Chile.xml', 'Chile'),
]
BASE2=[
('http://raspberrypi.cl/raspbmctv/Chile.xml', 'Chile')
]
if (__name__ == "__main__") and (__settings__.getSetting("habilitarmodoadultos") == 'true'): from resources.lib.main import main;main(BASE2)
else: from resources.lib.main import main;main(BASE)
