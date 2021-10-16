# SUP4SPACE

GPS track and geotagged photos from a 50km zero carbon paddleboard 'commute' from Chester to
Liverpool (well, New Brighton).
View map [HERE](https://jpolton.github.io/SUP4SPACE/)

Sources:
put gpx track onto map:
https://github.com/CoderAllan/gpx-to-leaflet
Updated to include positioned photo markers

Exiftool python wrapper: https://smarnach.github.io/pyexiftool/

## Set up environment
```
conda create --name leaflet_env python==3.8 geopy gpxpy
conda install ipython
conda install -c anaconda python-dateutil
conda activate leaflet_env
```

## Generate the html file

The gpx file path is specified in `gpxToLeaflet.py`. To generate `index.html` run:
```
python gpxToLeaflet.py
```

### Primer on getting the exiftool wrapper to work
To use exiftool to extract the geotagged photo information
```ipython
import exiftool
files = ["media/imgs/IMG_4253.jpeg","media/imgs/IMG_4254.jpeg"]
tags = ["EXIF:GPSLatitude","EXIF:GPSLongitude"]
with exiftool.ExifTool() as et:
  metadata = et.get_tags_batch(tags, files)
  print(metadata)
```  
