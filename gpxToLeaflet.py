"""
gpxToLeaflet.py

Original code: https://github.com/CoderAllan/gpx-to-leaflet

conda create --name leaflet_env python==3.8 geopy gpxpy
conda install -c anaconda python-dateutil
conda activate leaflet_env

The gpx file path is specified in `gpxToLeaflet.py`. To generate `index.html` run:
```
python gpxToLeaflet.py
```
"""
import os
from dateutil import tz
from datetime import timedelta

import gpxpy
import geopy.distance


class DistanceMarker:
    def __init__(self, latitude, longitude, label):
        self.latitude = latitude
        self.longitude = longitude
        self.label = label

    def toJsString(self):
        return f"""
            L.marker([{self.latitude},{self.longitude}], {{
              icon: L.divIcon({{ html: '<span style="font-size: 20px; font-weight: bold">{self.label}</span>' }})
            }}).addTo(myMap);"""


class Track:
    def __init__(self, track, distance, startTime, endTime, distanceMarkers=[]):
        self.track = track
        self.distance = distance
        self.startTime = startTime
        self.endTime = endTime
        self.distanceMarkers = distanceMarkers

    def duration(self):
        if self.startTime != "" and self.endTime != "":
            return self.endTime - self.startTime
        else:
            return timedelta(0)

    def durationToStr(self):
        duration = self.duration()
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

    def distanceMarkersToJsStr(self):
        return "\n".join(map(lambda marker: marker.toJsString(), self.distanceMarkers))


def main(gpxFilename, htmlFilename) -> None:
    track: Track = load_track(gpxFilename)
    if(track != None and len(track.track) > 0):
        generate_html(track, htmlFilename)
        print("Done generating html page: ", htmlFilename)


def load_track(filename: str) -> Track:
    if(os.path.exists(filename) == False):
        print(f"File not found: {filename}")
        return None
    localtime = tz.tzlocal()
    gpx_file = open(filename)
    current_track = Track([], 0, "", "")
    try:
        gpx = gpxpy.parse(gpx_file)
        prevPoint = (0, 0)
        prevDistance = 0
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    current_track.track.append([float(point.latitude), float(point.longitude)])
                    if current_track.startTime == "":
                        current_track.startTime = point.time.astimezone(localtime)
                    current_track.endTime = point.time.astimezone(localtime)
                    if prevPoint != (0, 0):
                        pointDistance = geopy.distance.distance(prevPoint, (float(point.latitude), float(point.longitude))).km
                        current_track.distance = current_track.distance + pointDistance
                    if(int(current_track.distance) > prevDistance):
                        prevDistance = int(current_track.distance)
                        newDistanceMarker = DistanceMarker(point.latitude, point.longitude, f"{int(prevDistance)}km")
                        current_track.distanceMarkers.append(newDistanceMarker)
                    prevPoint = (float(point.latitude), float(point.longitude))
    except Exception as error:
        print(f"\nParsing file '{filename}' failed. Error: {error}")
        current_track = None
    gpx_file.close()
    return(current_track)


def generate_html(track: Track, file_out: str) -> None:
    """Generates a new html file with points"""
    template = """
    <html><head>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" integrity="sha512-xodZBNTC5n17Xt2atTPuE1HxjVMSvLVW9ocqUKLsCC5CXdbqCmblAshOMAS6/keqq/sMZMZ19scR4PsZChSR7A==" crossorigin=""/>
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js" integrity="sha512-XQoYMqMTK8LvdxXYG3nZ448hOEQiglfqkJs1NOQV44cWnUrBc8PkAOcXy20w0vlaXaVUearIOBhiXZ5V3ynxwA==" crossorigin=""></script>
  <style type="text/css">
  #mapId {
    position: absolute;
    top: 0px;
    width: 800px;
    left: 0px;
    height: 800px;
    border: 1px solid #000;
  }
  #info {
    position: absolute;
    top: 0px;
    left: 805px;
    border: 1px solid #000;
    background-color: #ddd;
    font-size: larger;
    padding: 5px;
  }
</style>
</head>
<body>
  <div id="mapId"></div>
  <div id="info">
    <h1>Track info</h1>
    <div id="duration"></div>
    <div id="distance"></div>
  </div>
  <script>
    var myMap = L.map('mapId', {
        tap: false
        }).setView({lon: -3.1, lat: 53.3}, 11);
    L.tileLayer(
      'https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
          '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
          'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        id: 'mapbox/satellite-v9',
        tileSize: 512,
        zoomOffset: -1
      }).addTo(myMap);
    var track = [];
    var duration = '';
    var distance = '';
        const polyline = L.polyline(track, {color: 'blue'}).addTo(myMap);
    var highlightMarker = undefined;
    polyline.on('click', function(e) {
      const closestIdx = findPointIdxOnPolyline(track, e.latlng);
      const trackLength = lengthOfTrack(track, closestIdx);
      if(highlightMarker != undefined) {
        myMap.removeLayer(highlightMarker);
      }
      highlightMarker = L.marker(track[closestIdx], {icon: L.divIcon({ html: '<span style="font-size: 20px; font-weight: bold">' + Math.round(trackLength) + 'm</span>' })}).addTo(myMap);
    });

    function findPointIdxOnPolyline(track, latlng) {
      let prevDiffLat = prevDiffLng = 99999;
      let closestIdx = 0;
      for(var i = 0; i < track.length; i++) {
        var diffLat =  Math.abs(track[i][0] - latlng.lat);
        var diffLng = Math.abs(track[i][1] - latlng.lng);
        if(diffLat + diffLng < prevDiffLat + prevDiffLng) {
          prevDiffLat = diffLat;
          prevDiffLng = diffLng;
          closestIdx = i;
        }
      }
      return closestIdx;
    }
    function lengthOfTrack(track, idx) {
      var length = 0;
      for(var i = 1; i < track.length && i < idx; i++) {
        let from = L.latLng(track[i-1]);
        let to = L.latLng(track[i]);
        length += from.distanceTo(to);
      }
      return length;
    }
    <!--DISTANCEMARKERS-->
  </script>
</body></html>
    """

    track_points = ",".join([f"[{g_track_point[0]}, {g_track_point[1]}, 0.1]" for g_track_point in track.track])
    track_points = f"var track=[{track_points}];"
    template = template.replace("var track = [];", track_points)
    template = template.replace('<div id="duration"></div>', '<div id="duration">Duration: ' + track.durationToStr() + '</div>')
    template = template.replace('<div id="distance"></div>', '<div id="distance">Distance: ' + str(round(track.distance, 2)) + ' km</div>')
    template = template.replace('<!--DISTANCEMARKERS-->', track.distanceMarkersToJsStr())
    f = open(file_out, "w")
    f.write(template)
    f.close()


if __name__ == '__main__':
    main("media/SUP4SPACE_13Oct21.gpx", "index.html")
