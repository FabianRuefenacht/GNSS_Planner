from dataclasses import dataclass
import requests
import xml.etree.ElementTree as ET
import os
import math

from backend.roughplanning.BBOX import BBOX
from backend.roughplanning.Merger import RasterMerger

@ dataclass
class LoadRasterDEM:
    bbox: BBOX
    download_folder: str

    def load_raster(self, tiles: list) -> None:
        if not os.path.exists(self.download_folder): # check if download-path exists
            os.makedirs(self.download_folder)

        for tile in tiles:
            tile_key = tile[0]
            tile_key = tile_key.replace("_", "-") # string-replacement
            timestamp = tile[1]

            filename = f"{tile_key}_{timestamp}"
            filepath = os.path.join(self.download_folder, f"{filename}.tif")
            response = requests.get(
                f"https://data.geo.admin.ch/ch.swisstopo.swisssurface3d-raster/swisssurface3d-raster_{timestamp}_{tile_key}/swisssurface3d-raster_{timestamp}_{tile_key}_0.5_2056_5728.tif"
            ) # download raster-tile
            with open(filepath, "wb") as f:
                f.write(response.content) # write content of response to file
        return


    def get_tiles(self) -> list:
        """
        Creates a list of raster-tiles based on the calculated bounding-box using response from the web-feature-service: ch.swisstopo.swisssurface3d.metadata.
        
        Returns
        -------
        list
            List containing [(tilekey, temporalkey)]
        """
        tiles = []

        e = self.bbox.Emin
        n = self.bbox.Nmin

        while e <= self.bbox.Emax + 1500:
            while n <= self.bbox.Nmax:
                url = f"https://wms.geo.admin.ch/?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetFeatureInfo&QUERY_LAYERS=ch.swisstopo.swisssurface3d.metadata&LAYERS=ch.swisstopo.swisssurface3d.metadata&INFO_FORMAT=text/xml&LANG=de&I=50&J=50&CRS=EPSG%3A2056&WIDTH=101&HEIGHT=101&BBOX={e}%2C{n}%2C{e+1}%2C{n+1}" # WFS-adress

                response = requests.get(url) # API-request

                root = ET.fromstring(response.content) # Using elementtree to handle xml --> get important details (tilekey, temporalkey)
                for feature_member in root.findall(
                    ".//{http://www.opengis.net/gml}featureMember"
                ):
                    tilekey = feature_member.find(
                        ".//ogr:tilekey", namespaces={"ogr": "http://ogr.maptools.org/"}
                    ).text
                    temporalkey = feature_member.find(
                        ".//ogr:temporalkey",
                        namespaces={"ogr": "http://ogr.maptools.org/"},
                    ).text
                    tiles.append((tilekey, temporalkey))
                n += 1000
            e += 1000
            n = self.bbox.Nmin
        return tiles
