from dataclasses import dataclass

from backend.roughplanning.GNSS import GNSS_Session, GNSS_Point

@dataclass
class BBOX:
    Emin: float
    Emax: float

    Nmin: float
    Nmax: float

    def puffer_box(self, distance: float | int):
        Emin = self.Emin - distance
        Emax = self.Emax + distance
        
        Nmin = self.Nmin - distance
        Nmax = self.Nmax + distance

        bbox = BBOX(Emin=Emin, Emax=Emax, Nmin=Nmin, Nmax=Nmax)
        
        return bbox


@ dataclass
class BBOXCreator:
    session: GNSS_Session

    def get_bbox(self) -> BBOX:
        Emin = min([point.easting for point in self.session.points])
        Emax = max([point.easting for point in self.session.points])

        Nmin = min([point.northing for point in self.session.points])
        Nmax = max([point.northing for point in self.session.points])

        bbox = BBOX(Emin=Emin, Emax=Emax, Nmin=Nmin, Nmax=Nmax)

        return bbox


