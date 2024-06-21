"""
Code by Fabian Rüfenacht.

Codedocumentation assisted by ChatGPT version 3.5
"""

from dataclasses import dataclass
from typing import Literal, List
import rasterio
import numpy as np
import rasterio.transform

from backend.roughplanning.GNSS import GNSS_Point
from backend.roughplanning.ObjectDefinition import TransformParam, Point2D, Line2D, PointLineSegment, Profile

@dataclass
class RoughPlanning:
    """
    Performs rough planning for a GNSS-Point.

    Attributes
    ----------
    point : GNSS_Point
        A GNSS_Point object representing the point for rough planning.

    dem_path : str
        Path to the digital elevation model (DEM) data.

    method : Literal['RANSAC', 'CONVENTIONAL']
        Method for rough planning: RANSAC or CONVENTIONAL.

    Methods
    -------
    __post_init__()
        Initializes the object and performs type validation for attributes.

    plan() -> None:
        Performs rough planning based on the selected method ('RANSAC' or 'CONVENTIONAL').

    read_raster() -> TransformParam:
        Reads and returns transformation parameters from the digital elevation model (DEM).

    create_lines(number_of_lines: int, line_length: float) -> List[Line2D]:
        Creates a list of Line2D objects based on the specified number of lines and line length.

    get_delta_e(line: Line2D) -> float:
        Computes and returns the difference in easting coordinates between the start and end points of the Line2D.

    get_delta_n(line: Line2D) -> float:
        Computes and returns the difference in northing coordinates between the start and end points of the Line2D.

    segment_line(number_of_segments: int, line: Line2D) -> List[PointLineSegment]:
        Segments a Line2D into multiple PointLineSegment objects based on the specified number of segments.

    transform_linesegments(line_points: list[PointLineSegment]) -> None:
        Transforms the coordinates of PointLineSegment objects using parameters read from the DEM.

    get_raster_height(index: tuple[float, float], line_point: PointLineSegment) -> None:
        Retrieves and calculates height information from the DEM for a given index and updates a PointLineSegment object.

    create_profile(line_points: list[PointLineSegment]) -> Profile:
        Creates a profile object from a list of PointLineSegment objects.

    get_max_angle(profile: Profile) -> float:
        Finds and returns the maximum elevation angle from a Profile object.

    draw_panorama_diagram(azimuths: list[float], elevation_angles: list[float], min_elevation: float | int, image_path: str, pointname: str) -> None:
        Draws and saves a panorama diagram based on azimuths and elevation angles.

    draw_polar_diagram(azimuths: list[float], elevation_angles: list[float], min_elevation: float | int, image_path: str, pointname: str) -> None:
        Draws and saves a polar diagram based on azimuths and elevation angles.

    save_legend(legend_path: str) -> None:
        Saves a legend image for the polar diagram.

    """

    point: GNSS_Point
    dem_path: str
    method: Literal['RANSAC', 'CONVENTIONAL']

    def __post_init__(self) -> None:
        """
        Initializes the object and performs type validation for attributes.
        """
        GNSS_Point._validate_type('point', self.point, GNSS_Point)

# ------------------------------------------------- Main Entry -------------------------------------------------

    def plan(self, number_of_lines: float | int, line_length: float | int, number_of_segments: float | int) -> None:
        """
        Main entry point --> performs analysis with RANSAC or CONVENTIONAL based on Initialisation of class RoughPlanning.
        """
        if self.method == 'RANSAC':
            azimuths, elevation_angles = self.plan_ransac()
        elif self.method == 'CONVENTIONAL':
            azimuths, elevation_angles = self.plan_conventional(number_of_lines=number_of_lines, line_length=line_length, number_of_segments=number_of_segments)
        else:
            raise AttributeError("Unsupported method. Use 'RANSAC' or 'CONVENTIONAL'!")
        
        return (azimuths, elevation_angles)
  

# ------------------------------------------------ CONVENTIONAL ------------------------------------------------

    def plan_conventional(self, number_of_lines: float | int, line_length: float | int, number_of_segments: float | int) -> tuple:
        """
        Entrypoint for CONVENTIONAL method.
        """
    # ToDo main handler CONVENTIONAL
        transformation: TransformParam = self.read_raster()
        pix_size: float = transformation.pix_size_u # pixel-size for transformation of line

        # if segmentsize is smaller than the actual width of a cell -> segmentsize will be overwritten with cell size
        if line_length / pix_size < number_of_segments:
            number_of_segments = line_length / pix_size
        
        # get lines, azimuths and initialize elevation angles
        lines = self.create_lines(number_of_lines=number_of_lines, line_length=line_length)
        
        azimuths = [400 / number_of_lines * i for i in range(number_of_lines)]
        elevation_angles = []

        # iterate over each line
        for line in lines: # may  later be seperated on many cores
            segments = self.segment_line(number_of_segments=number_of_segments, line=line) # segment per line
            self.transform_linesegments(line_points=segments) # transformed segment per line
            profile = self.create_profile(line_points=segments) # create profile-Object
            max_alpha = self.get_max_angle(profile=profile) # get maximal elevation angle for each line
            elevation_angles.append(max_alpha * 200 / np.pi) # append elevation angle to array

        return (azimuths, elevation_angles)
        
    def read_raster(self) -> TransformParam:
        """
        Reading raster transformation parameters.
        """
        with rasterio.open(self.dem_path) as dem:
            # read transformation an specify each param
            transform = dem.transform
            
            pix_size_u: float = transform[0]
            pix_size_v: float = transform[4]

            shear_u: float = transform[1]
            shear_v: float = transform[3]

            translate_e: float = transform[2]
            translate_n: float = transform[5]

        # return as class instance for accessibility
        return TransformParam(pix_size_u=pix_size_u, pix_size_v=pix_size_v, shear_u=shear_u, shear_v=shear_v, translate_e=translate_e, translate_n=translate_n)
    
    def segment_line(self, number_of_segments: int, line: Line2D) -> List[PointLineSegment]:
        """
        Segments a given line into a specified number of segments along the easting and northing axis.

        Parameters
        ----------
        number_of_segments : int
            The number of segments to divide the line into.

        line : Line2D
            A line defined by its start and end points (both of type Point2D).

        Returns
        -------
        List[PointLineSegment]
            A list of PointLineSegment objects representing the segmented points along the line.

        """
        # calculate coordinate difference between startpoint and endpoint
        delta_e = self.get_delta_e(line=line)
        delta_n = self.get_delta_n(line=line)

        # create segmented line along easting and northing axis
        easting_line = [delta_e / number_of_segments * (i + 1) for i in range(number_of_segments)]
        northing_line = [ delta_n / number_of_segments * (i + 1) for i in range(number_of_segments)]

        # create line-element
        line_points = [PointLineSegment(easting=line.start_point.easting + e, northing=line.start_point.northing + n, distance_from_start=np.sqrt(e**2 + n**2)) for e, n in zip(easting_line, northing_line)]
        return line_points

    def transform_linesegments(self, line_points: list[PointLineSegment]) -> None:
        """
        Transforms a list of PointLineSegment objects by calculating their height and elevation angle based on raster data.

        Parameters
        ----------
        line_points : List[PointLineSegment]
            A list of PointLineSegment objects representing points along a line.

        Returns
        -------
        None

        Notes
        -----
        This method requires a raster file to be read beforehand to establish the transformation parameters.
        The transformation updates the height_difference and elevation_angle attributes of each PointLineSegment object in place.
        """
        # get transformer Object (own implementation) -> create transformation Object (rasterio implementation) -> create transformer Object to apply on coord (rasterio implementation)
        transform = self.read_raster()
        transform = rasterio.Affine(
                            transform.pix_size_u,
                            transform.shear_u,
                            transform.translate_e,
                            transform.shear_v,
                            transform.pix_size_v,
                            transform.translate_n
                        )
        transformer = rasterio.transform.AffineTransformer(transform)

        # iterate over each point of the delivered line, get pixel-value and make calcs (next comment)
        for idx, line_point in enumerate(line_points):
            index = transformer.rowcol(xs=line_points[idx].easting, ys=line_points[idx].northing)
            # works  so far
        
            # make calcs -> update height and elevation-angle information in PointLineSegment-Object
            self.get_raster_height(index=index, line_point=line_point)
                    
        return

    def get_raster_height(self, index: tuple[float, float], line_point: PointLineSegment) -> None:
        """
        Retrieves the height information from a raster file at a specified index and updates a PointLineSegment object.

        Parameters
        ----------
        index : Tuple[float, float]
            The row and column indices representing the pixel location in the raster file.
        line_point : PointLineSegment
            The PointLineSegment object to update with height information.

        Returns
        -------
        None

        Raises
        ------
        EOFError
            If the provided index is out of bounds relative to the raster dimensions.

        Notes
        -----
        This method requires the 'dem_path' attribute to be set with the path to the digital elevation model (DEM) data.
        It updates the 'height_difference' and 'elevation_angle' attributes of the provided PointLineSegment object.
        """
        with rasterio.open(self.dem_path) as src:
            width = src.width
            height = src.height
        

            if index[1] < 0 or index[0] < 0:
                raise EOFError(f"Expansion DEM not sufficient!{width} {index[0]} {height} {index[1]}")
            if index[1] > width or index[0] > height:
                raise EOFError(f"Expansion DEM not sufficient!{width} {index[0]} {height} {index[1]}")

            # read value of pixel on first (1) band
            pixel_value = src.read(1)[index]

            # Height of GNSS at its position to calculate height difference between itself and the terrain-points
            gnss_height = self.point.floor_height + self.point.antenna_height
            height_difference = pixel_value - gnss_height

            # updates height-difference and elevation-angle
            line_point.update_height(new_height=height_difference)
            
        return

# --------------------------------------------------- RANSAC ---------------------------------------------------

    def plan_ransac(self) -> None:
        """
        Entrypoint for RANSAC method.
        """
        # ToDo main handler RANSAC
        pass

# --------------------------------------------------- shared ---------------------------------------------------
  
    def create_lines(self, number_of_lines: int, line_length: float) -> List[Line2D]:
        """
        Creates multiple lines originating from a GNSS position (center_point) in different azimuth directions.

        Parameters
        ----------
        number_of_lines : int
            Number of lines to create, representing the number of directions to spread from the center_point.
        
        line_length : float
            Length of each line in meters.

        Returns
        -------
        List[Line2D]
            A list of Line2D objects, each representing a line segment starting from the center_point
            and extending to an endpoint calculated based on the azimuth and line_length.

        Raises
        ------
        TypeError
            If number_of_lines is not of type int or line_length is neither of type int nor float.

        """
        # handle type-error
        if not type(number_of_lines) == int:
            raise TypeError("Attribute 'number_of_lines' must be of type int.")
        if not type(line_length) == int and not type(line_length) == float:
            raise TypeError("Attribute 'line_leght' must be of type int or type float.")

        # get GNSS-position
        center_point = Point2D(easting=self.point.get_easting(), northing=self.point.get_northing())

        # calculate azimuths based on the number of lines
        azimuths = [2 * np.pi / number_of_lines * i for i in range(number_of_lines)]

        # calculate partial distances (easting and northing) for each line
        delta_easts = [line_length * np.sin(azimuth) for azimuth in azimuths]
        delta_norths = [line_length * np.cos(azimuth) for azimuth in azimuths]

        # crete endpoints for each line
        endpoints = [Point2D(easting=center_point.easting + delta_east, northing=center_point.northing + delta_north) for delta_east, delta_north in zip(delta_easts, delta_norths)]

        # create lines between GNSS-position and endpoint 
        lines = [Line2D(start_point=center_point, end_point=endpoint) for endpoint in endpoints]

        return lines
    
    def get_delta_e(self, line: Line2D) -> float:
        """
        Computes the difference in easting coordinates between the start and end points of a line.

        Parameters
        ----------
        line : Line2D
            A line consisting of a start point and an end point (both of type Point2D).

        Returns
        -------
        float
            The difference in easting coordinates (end point - start point).

        """
        start = line.start_point.easting
        end = line.end_point.easting

        diff = end - start
        return diff
    
    def get_delta_n(self, line: Line2D) -> float:
        """
        Computes the difference in northing coordinates between the start and end points of a line.

        Parameters
        ----------
        line : Line2D
            A line consisting of a start point and an end point (both of type Point2D).

        Returns
        -------
        float
            The difference in northing coordinates (end point - start point).

        """
        start = line.start_point.northing
        end = line.end_point.northing

        diff = end - start
        return diff

    def create_profile(self, line_points: list[PointLineSegment]) -> Profile:
        """
        Creates a profile object from a list of PointLineSegment objects.

        Parameters
        ----------
        line_points : list[PointLineSegment]
            A list of PointLineSegment objects representing points along a line.

        Returns
        -------
        Profile
            A Profile object containing the provided line points.

        Notes
        -----
        This method initializes a Profile object with the given line points and returns it.
        """
        profile = Profile(line_points)
        
        return profile    
    
    def get_max_angle(self, profile: Profile) -> float:
        """
        Retrieves the maximum elevation angle from a given Profile object.

        Parameters
        ----------
        profile : Profile
            The Profile object from which to find the maximum elevation angle.

        Returns
        -------
        float
            The maximum elevation angle found within the Profile object.

        Notes
        -----
        This method calls the 'find_max_elevation_angle()' method of the Profile object
        to retrieve the maximum elevation angle from its stored PointLineSegment objects.
        """
        return profile.find_max_elevation_angle()
    
