from dataclasses import dataclass, field
import numpy as np
from typing import List

@dataclass
class TransformParam:
    """
    Used to easily access transformation parameters of rasterio transformation.

    Attributes
    ----------
    pix_size_u : float
        Pixel size in the u-direction (e.g., x-direction in georeferenced space).
    
    shear_u : float
        Shear parameter in the u-direction.
    
    translate_e : float
        Translation parameter in the e-direction (e.g., x-offset in georeferenced space).
    
    shear_v : float
        Shear parameter in the v-direction.
    
    pix_size_v : float
        Pixel size in the v-direction (e.g., y-direction in georeferenced space).
    
    translate_n : float
        Translation parameter in the n-direction (e.g., y-offset in georeferenced space).
    """

    pix_size_u: float
    shear_u: float
    translate_e: float
    shear_v: float
    pix_size_v: float
    translate_n: float

@dataclass
class Point2D:
    easting: float
    northing: float

@dataclass
class Line2D:
    start_point: Point2D
    end_point: Point2D

    def get_length(self):
        start_e: float = self.start_point.easting
        start_n: float = self.start_point.northing

        end_e: float = self.end_point.easting
        end_n: float = self.end_point.northing

        delta_e = end_e - start_e
        delta_n = end_n - start_n

        length = np.sqrt(delta_e**2 + delta_n**2)
        return length

@dataclass
class PointLineSegment:
    easting: float
    northing: float
    distance_from_start: float
    height_difference: float = 0
    elevation_angle: float = 0

    def update_height(self, new_height: float) -> None:
        """
        Update the height difference based on a new height value.

        Parameters
        ----------
        new_height : float
            The new height value to set.
        """
        self.height_difference = new_height

        self.elevation_angle = np.arctan(new_height / self.distance_from_start)
        return
    
@dataclass
class Profile:
    segments: List[PointLineSegment] = field(default_factory=list)

    def add_segment(self, segment: PointLineSegment) -> None:
        """
        Add a PointLineSegment to the profile.

        Parameters
        ----------
        segment : PointLineSegment
            The PointLineSegment to add.
        """
        self.segments.append(segment)

    def find_max_elevation_angle(self) -> float:
        """
        Find the maximum elevation angle among all segments.

        Returns
        -------
        float
            The maximum elevation angle.
        """
        if not self.segments:
            return 0.0  # Return 0 if there are no segments

        return max(segment.elevation_angle for segment in self.segments)
