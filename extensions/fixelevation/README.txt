  Fix Elevation pytrainer extension
  ===============================
  This extension allows you to correct elevations within gpx data.
  Code is based on Wojciech Lichota's gpxtools
  http://lichota.pl/blog/topics/gpxtools
  Elevations are corrected using SRTM data, therefore on first usage the necessary  
  SRTM tile will be downloaded (large!). Tiles will be cached.

  Extension requires 'GDAL python bindings'. Install e.g.
  apt-get install python-gdal
  or 
  yum install gdal-python


  CONFIG OPTIONS
  ==============
  n.n.

  USAGE
  =====
  Simply submit the fixelevation extension preferences form and then go
  to the record tab and press "Fix Elevation".

---------------------------

  IMPORTANT 
  =========

  - On first use, the extension will download a geo_tif File (about 79mb) for your region, there is no warning dialog or similiar.
  - Original gpx data (in '.pytrainer/gpx/') will be overwritten.
  - The main record isn't forced to be reloaded at the moment, so restart pytrainer to study the manipulated heights. 

  TODO
  ====
  (?) Interface to specify source of SRTM data (at the moment hardcoded CGIAR mirror)
  (?) Interface to specify where to store SRTM data (at the moment .pytrainer/SRTM_data)
  (?) Store original gpx elevation data (gpx extension or whole backup file?); offer revert possibility
  (?) Improve Wojciech's border trick.
  (?) Offer alternative SRTM/DEM Sources eg http://www.viewfinderpanoramas.org/dem3.html
  (?) Offer batch mode to fix bundle of tracks
  (?) Higher order of interpolation (ie bicubic)
