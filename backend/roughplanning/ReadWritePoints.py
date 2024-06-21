from dataclasses import dataclass
from backend.roughplanning.GNSS import GNSS_Session, GNSS_Point

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


@dataclass
class ReadPoints:
    def read_file(self, path: str) -> GNSS_Session:
        gnss_session = GNSS_Session()
        with open(path) as file:
            data = file.read().split("\n")
            for line in data:
                name, easting, northing, floorheight, antennaheight = line.split(",")
                if name and easting and northing and floorheight and antennaheight:
                    gnss_session.add_point(GNSS_Point(name=str(name), easting=float(easting), northing=float(northing), floor_height=float(floorheight), antenna_height=float(antennaheight)))
                else:
                    raise ValueError("not Enough values to unpack into GNSSPoint! Check input file.")
        return gnss_session
    
@dataclass
class WritePoints:
    def write_table(self, session: GNSS_Session, target: QTreeWidget) -> None:
        for point in session.points:
            item = QTreeWidgetItem()
            item.setText(0, str(point.name))
            item.setText(1, str(point.easting))
            item.setText(2, str(point.northing))
            item.setText(3, str(point.floor_height))
            item.setText(4, str(point.antenna_height))
            target.addTopLevelItem(item)

        return
