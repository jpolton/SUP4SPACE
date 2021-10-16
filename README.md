# SUP4SPACE

gpx track onto map:
https://github.com/CoderAllan/gpx-to-leaflet

Original code: https://github.com/CoderAllan/gpx-to-leaflet

conda create --name leaflet_env python==3.8 geopy gpxpy
conda install -c anaconda python-dateutil
conda activate leaflet_env

The gpx file path is specified in `gpxToLeaflet.py`. To generate `index.html` run:
```
python gpxToLeaflet.py
```
