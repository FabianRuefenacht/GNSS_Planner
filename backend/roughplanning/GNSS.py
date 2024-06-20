from dataclasses import dataclass, field
from typing import List, Any

@dataclass # automatically creates init and other magic functions
class GNSS_Point:
    """
    Create a single GNSS-Measurement

    Attributes
    ----------
    name: str
        Name of the point

    easting: float
        easting coordinate in LV95 [Meters]

    northing: float
        northing coordinate in LV95 [Meters]

    floor_height: float
        height coordinate in LV95 [Meters]

    antenna_height: float
        antenna_height at the point [Meters]. Default 2m

    Methods
    -------
    __post_init__():
        Validates the types of the attributes after initialization.

    _validate_type(attribute_name: str, attribute_value: any, expected_type: type) -> None:
        Validates the type of a given attribute.

    get_GNSS_name() -> str:
        Returns the name of the GNSS point.

    get_easting() -> float:
        Returns the easting coordinate of the GNSS point.

    get_northing() -> float:
        Returns the northing coordinate of the GNSS point.

    get_floorheight() -> float:
        Returns the floor height of the GNSS point.

    get_antenna_height() -> float:
        Returns the antenna height of the GNSS point.
    """
    name: str
    easting: float
    northing: float
    floor_height: float
    antenna_height: float = 2.00 # default value

    def __post_init__(self) -> None:
        # Check type for each Attribute
        self._validate_type('name', self.name, str)
        self._validate_type('easting', self.easting, (float, int))
        self._validate_type('northing', self.northing, (float, int))
        self._validate_type('floor_height', self.floor_height, (float, int))
        self._validate_type('antenna_height', self.antenna_height, (float, int))

    @staticmethod # can be accessed without creating instance of GNSS_Point
    def _validate_type(attribute_name: str, attribute_value: Any, expected_type: type | tuple) -> None:
        if not isinstance(attribute_value, expected_type):
            raise TypeError(f"Attribut '{attribute_name}' muss vom Typ {expected_type} sein, ist aber {type(attribute_value).__name__}.")

    def get_GNSS_name(self) -> str:
        return self.name
    
    def get_easting(self) -> float:
        return self.easting
    
    def get_northing(self) -> float:
        return self.northing
    
    def get_floorheight(self) -> float:
        return self.floor_height
    
    def get_antenna_height(self) -> float:
        return self.antenna_height

@dataclass # automatically creates init and other magic functions
class GNSS_Session:
    """
    A collection of GNSS Points

    Attributes
    ----------
    points: List[GNSS_Point]
        A list of GNSS_Point objects

    Methods
    -------
    add_point(point: GNSS_Point) -> None:
        Adds a GNSS_Point to the session.

    get_points() -> List[GNSS_Point]:
        Returns the list of GNSS_Point objects in the session.

    get_point_by_name(name: str) -> GNSS_Point | None:
        Retrieves a GNSS_Point by its name, returns None if not found.
    """
    points: List[GNSS_Point] = field(default_factory=list)

    def add_point(self, point: GNSS_Point) -> None:
        self.points.append(point)

    def get_points(self) -> List[GNSS_Point]:
        return self.points

    def get_point_by_name(self, name: str) -> GNSS_Point | None:
        for point in self.points:
            if point.name == name:
                return point
        return None
