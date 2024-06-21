from dataclasses import dataclass
import rasterio
import glob
import os

import rasterio.merge

@dataclass
class RasterMerger:
    path: str

    def merge_raster(self) -> None:
        file_paths = glob.glob(os.path.join(self.path, '*.tif'))

        src_files_to_mosaic = []

        for file_path in file_paths:
            src = rasterio.open(file_path)
            src_files_to_mosaic.append(src)

        mosaic, out_trans = rasterio.merge.merge(src_files_to_mosaic)

        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": out_trans
        })
        
        self.merged_path = os.path.join(self.path, "raster.tif")

        output_file = self.merged_path
        with rasterio.open(output_file, "w", **out_meta) as dest:
            dest.write(mosaic)

        return
    
    def remove_downloads(self) -> None:
        # list all files in dir
        if os.path.exists(self.path):
            files = os.listdir(self.path)
            self.merged_path = os.path.join(self.path, "raster.tif")

            
            # remove downloads
            files_to_remove = [os.path.join(self.path, file) for file in files if not os.path.join(self.path, file) == self.merged_path]
            _ = [os.remove(file) for file in files_to_remove]
        
        return
