import sys
import time
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QLineEdit, QTreeWidget, QTabWidget, QFileDialog, QRadioButton, QLabel, QSlider, QProgressBar
from PyQt5 import uic
from multiprocessing import Pool
import os

from backend.roughplanning.GNSS import GNSS_Session, GNSS_Point
from backend.roughplanning.ReadWritePoints import ReadPoints, WritePoints
from backend.roughplanning.BBOX import BBOXCreator, BBOX
from backend.roughplanning.Downloader import LoadRasterDEM
from backend.roughplanning.Merger import RasterMerger
from backend.roughplanning.RoughPlanning import RoughPlanning
from backend.roughplanning.RoughPlanDrawer import RoughPlanDrawer


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('./frontend/gnss_planner_dialog_base.ui', self)

        # find registers
        self.main_tab_widget = self.findChild(QTabWidget, "tabWidget")
        self.main_tab_widget.setTabEnabled(1, False)

        # register "Projekt öffnen"
            # Open Project
        self.open_project_PBU = self.findChild(QPushButton, "PBU_openProject")
        self.open_project_PBU.clicked.connect(self.open_project)

        self.open_project_LE = self.findChild(QLineEdit, "LE_projectEditor")

            # load points
        self.load_points_PBU = self.findChild(QPushButton, "PBU_loadFile")
        self.load_points_PBU.clicked.connect(self.ask_open_points)

        self.load_points_LE = self.findChild(QLineEdit, "LE_pointEditor")

        self.points_table_TW = self.findChild(QTreeWidget, "TW_tablePoints")

        # register "Grobplanung"
            # radiobutton
        self.convetional_radio_button = self.findChild(QRadioButton, "RB_conventional")
        self.ransac_radio_button = self.findChild(QRadioButton, "PB_ransac")

            # Project settings
        self.project_name_LE = self.findChild(QLineEdit, "LE_projectName")
        self.project_leader_LE = self.findChild(QLineEdit, "LE_projectLeader")

            # distance slider
        self.distance_L = self.findChild(QLabel, "L_distance")
        self.distance_slider = self.findChild(QSlider, "HS_distance")
        self.distance_slider.valueChanged.connect(self.update_distance)

            # segment resolution slider
        self.segment_L = self.findChild(QLabel, "L_resolution")
        self.segment_slider = self.findChild(QSlider, "HS_resolution")
        self.segment_slider.valueChanged.connect(self.update_segment_resolution)

            # number of lines slider
        self.number_of_lines_L = self.findChild(QLabel, "L_noLines")
        self.number_of_lines_slider = self.findChild(QSlider, "HS_noLines")
        self.number_of_lines_slider.valueChanged.connect(self.update_number_of_lines)

            # graphic distance and no lines
        self.line_graph_L = self.findChild(QLabel, "L_lineView")

            # load DEM
        self.load_dem_PBU = self.findChild(QPushButton, "PBU_loadDEM")
        self.load_dem_PBU.clicked.connect(self.load_dem)

            # single point analysis
        self.single_point_rough_PBU = self.findChild(QPushButton, "PBU_roughPlanningSingle")
        self.single_point_rough_PBU.clicked.connect(self.single_point_rough)

            # all points analyisis
        self.all_points_rough_PBU = self.findChild(QPushButton, "PBU_roughPlanningAll")
        self.all_points_rough_PBU.clicked.connect(self.all_points_rough)

        # progress bar
        self.process_label = self.findChild(QLabel, "processLabel")
        self.progressbar = self.findChild(QProgressBar, "progressBar")

        # initialize variables
        self.gnss_session = GNSS_Session()
        
    def open_project(self) -> None:
        self.parent_directory = QFileDialog.getExistingDirectory(self, "Wähle einen Ordner aus!")
        if self.parent_directory:
            self.open_project_LE.setText(self.parent_directory)
            self.load_points_PBU.setEnabled(True)

            self.raster_directory = os.path.join(self.parent_directory, "raster")
            self.results_directory = os.path.join(self.parent_directory, "results")
            if not os.path.exists(self.results_directory):
                os.mkdir(self.results_directory)

            return
        return
    
    def ask_open_points(self) -> None:
        # get filepath
        self.points_file, _ = QFileDialog.getOpenFileName(self, "Wähle eine Datei aus!", self.parent_directory, "CSV(*.csv), TXT(*.txt)")
        self.load_points_LE.setText(self.points_file)
        if self.points_file:
            # read file
            reader = ReadPoints()
            self.gnss_session: GNSS_Session = reader.read_file(path=self.points_file)

            # write points in table
            writer = WritePoints()
            writer.write_table(session=self.gnss_session, target=self.points_table_TW)

            # enable rest of UI
            self.points_table_TW.setEnabled(True)
            self.main_tab_widget.setTabEnabled(1, True)
            return
        return
    
    def load_dem(self) -> None:
        creator = BBOXCreator(session=self.gnss_session)
        bbox: BBOX = creator.get_bbox()

        bbox = bbox.puffer_box(distance=self.get_distance_slider())

        merger = RasterMerger(path=self.raster_directory)
        merger.remove_downloads()

        loader: LoadRasterDEM = LoadRasterDEM(bbox=bbox, download_folder=self.raster_directory)
        tiles: list = loader.get_tiles()
        loader.load_raster(tiles=tiles)

        merger.merge_raster()
        merger.remove_downloads()

        return

    def single_point_rough(self) -> None:
        pass

    def all_points_rough(self) -> None:
        if self.ransac_radio_button.isChecked():
            method = 'RANSAC'
        else:
            method = 'CONVENTIONAL'

        min_elevation = 10

        number_of_lines = int(self.get_number_of_lines())
        line_length = self.get_distance_slider()
        number_of_segments = int(line_length / self.get_segment_resolution())

        for point in self.gnss_session.get_points():
            rough_planner = RoughPlanning(point=point, dem_path=os.path.join(self.raster_directory, "raster.tif"), method=method)
            azimuths, elevation_angles = rough_planner.plan(number_of_lines=number_of_lines, line_length=line_length, number_of_segments=number_of_segments)

            drawer = RoughPlanDrawer()
            panorama_path = os.path.join(self.parent_directory, f"results/panorama{point.name}.png")
            polar_path = os.path.join(self.parent_directory, f"results/polar{point.name}.png")
            drawer.draw_panorama_diagram(azimuths=azimuths, elevation_angles=elevation_angles, min_elevation=min_elevation, image_path=panorama_path, pointname=point.name)
            drawer.draw_polar_diagram(azimuths=azimuths, elevation_angles=elevation_angles, min_elevation=min_elevation, image_path=polar_path, pointname=point.name)
        legend_path = os.path.join(self.parent_directory, "results/legend.png")
        drawer.save_legend(legend_path=legend_path)

    def get_distance_slider(self) -> float | int:
        value = self.distance_slider.value()
        return value

    def update_distance(self) -> None:
        value = self.get_distance_slider()
        self.distance_L.setText(f"Distanz: {value} m")
        return
    
    def get_segment_resolution(self) -> float | int:
        value = self.segment_slider.value()
        return value

    def update_segment_resolution(self) -> None:
        value = self.get_segment_resolution()
        self.segment_L.setText(f"Auflösung: {value} m")
        return
    
    def get_number_of_lines(self) -> float | int:
        value = self.number_of_lines_slider.value()
        return value

    def update_number_of_lines(self) -> None:
        value = self.get_number_of_lines()
        self.number_of_lines_L.setText(f"Anzahl Linien: {value} m")
        return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
