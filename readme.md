![preview thumb](http://i.imgur.com/OeXSAkU.png)

A fork of SickBeard VO/VF by sarakha63
Add TPI torrent provider
=====

This version is based on Midgetspy's and mr-oranges work:

IT includes :

French and english audio language

Interfaces change

![preview thumb](http://i.imgur.com/C6TPDCT.png)
![preview thumb](http://i.imgur.com/2nFcEbZ.png)
![preview thumb](http://i.imgur.com/YvAepaA.png)

Nzb Scraper added : binnews (with nzbindex, binsearch and nzbclub)

Torrent scraper added : t411, cpasbien, piratebay, gks, kat

![preview thumb](http://i.imgur.com/swc1lvx.png)

Torrent gestion with transmission, utorrent deluge gestion, download station

![preview thumb](http://i.imgur.com/K2DoPND.png)

subliminal integration

![preview thumb](http://i.imgur.com/plSD7lP.png)
![preview thumb](http://i.imgur.com/P2yTfpx.png)

subtitle cleaning

![preview thumb](http://i.imgur.com/5kG6d10.png)

torrent/nzb preferred choice

![preview thumb](http://i.imgur.com/1s7n4Lu.png)

torrent gestion with seeding possibility

![preview thumb](http://i.imgur.com/NDKNgLT.png)

Multiple notification system and trakt watchlist import

![preview thumb](http://i.imgur.com/xq3G3UI.png)
![preview thumb](http://i.imgur.com/MMtLuzm.png)
![preview thumb](http://i.imgur.com/N24lVgk.png)
![preview thumb](http://i.imgur.com/zEWzsJJ.png)
![preview thumb](http://i.imgur.com/u6GGX5P.png)
![preview thumb](http://i.imgur.com/uz5Ru1a.png)

multicolor progress bar with informative tooltip

![preview thumb](http://i.imgur.com/IfrAr7b.jpg)

local zone time for coming episodes

![preview thumb](http://i.imgur.com/gbQepiV.jpg)

ignore words and proper/auto french:

![preview thumb](http://i.imgur.com/bnkTqbY.png)

custom search name and more

![preview thumb](http://i.imgur.com/tSAvGcJ.png)
![preview thumb](http://i.imgur.com/5X3Vm5Y.png)
![preview thumb](http://i.imgur.com/axshXXM.png)
![preview thumb](http://i.imgur.com/ukrXA4C.png)
![preview thumb](http://i.imgur.com/ZTOCiRi.png)

and much more such as:

auto next available release download when failed
and much more

*Sick Beard is currently an alpha release. There may be severe bugs in it and at any given time it may not work at all.*

Sick Beard is a PVR for newsgroup users (with limited torrent support). It watches for new episodes of your favorite shows and when they are posted it downloads them, sorts and renames them, and optionally generates metadata for them. It currently supports NZBs.org, NZBMatrix, Bin-Req, NZBs'R'Us, EZTV.it, and any Newznab installation and retrieves show information from theTVDB.com and TVRage.com.

Features include:

* automatically retrieves new episode torrent or nzb files
* can scan your existing library and then download any old seasons or episodes you're missing
* can watch for better versions and upgrade your existing episodes (to from TV DVD/BluRay for example)
* XBMC library updates, poster/fanart downloads, and NFO/TBN generation
* configurable episode renaming
* sends NZBs directly to SABnzbd, prioritizes and categorizes them properly
* available for any platform, uses simple HTTP interface
* can notify XBMC, Growl, or Twitter when new episodes are downloaded
* specials and double episode support


Sick Beard makes use of the following projects:

* [cherrypy][cherrypy]
* [Cheetah][cheetah]
* [simplejson][simplejson]
* [tvdb_api][tvdb_api]
* [ConfigObj][configobj]
* [SABnzbd+][sabnzbd]
* [jQuery][jquery]
* [Python GNTP][pythongntp]
* [SocksiPy][socks]
* [python-dateutil][dateutil]
* [jsonrpclib][jsonrpclib]

## Dependencies

To run Sick Beard from source you will need Python 2.5+ and Cheetah 2.1.0+. The [binary releases][googledownloads] are standalone.

## Bugs

If you find a bug please report it or it'll never get fixed. Verify that it hasn't [already been submitted][googleissues] and then [log a new bug][googlenewissue]. Be sure to provide as much information as possible.

[cherrypy]: http://www.cherrypy.org
[cheetah]: http://www.cheetahtemplate.org/
[simplejson]: http://code.google.com/p/simplejson/ 
[tvdb_api]: http://github.com/dbr/tvdb_api
[configobj]: http://www.voidspace.org.uk/python/configobj.html
[sabnzbd]: http://www.sabnzbd.org/
[jquery]: http://jquery.com
[pythongntp]: http://github.com/kfdm/gntp
[socks]: http://code.google.com/p/socksipy-branch/
[dateutil]: http://labix.org/python-dateutil
[googledownloads]: http://code.google.com/p/sickbeard/downloads/list
[googleissues]: http://code.google.com/p/sickbeard/issues/list
[googlenewissue]: http://code.google.com/p/sickbeard/issues/entry
[jsonrpclib]: https://github.com/joshmarshall/jsonrpclib
