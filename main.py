import sys
import time
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QLineEdit, QTreeWidget, QTabWidget, QFileDialog, QRadioButton, QLabel, QSlider, QProgressBar
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QPainter
from multiprocessing import Pool
import os
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from backend.roughplanning.GNSS import GNSS_Session, GNSS_Point
from backend.roughplanning.ReadWritePoints import ReadPoints, WritePoints
from backend.roughplanning.BBOX import BBOXCreator, BBOX
from backend.roughplanning.Downloader import LoadRasterDEM
from backend.roughplanning.Merger import RasterMerger
from backend.roughplanning.RoughPlanning import RoughPlanning
from backend.roughplanning.RoughPlanDrawer import RoughPlanDrawer
from backend.roughplanning.PDFCreator import PDFCreator

from backend.roughplanning.helper_functions.ui import update_progresBar


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

            # cut-off-angle slider
        self.cutoffL = self.findChild(QLabel, "L_cutoff")
        self.cutoff_slider = self.findChild(QSlider, "HS_cutoff")
        self.cutoff_slider.valueChanged.connect(self.update_cutoff_angle)

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
        update_progresBar(bar=self.progressbar, label=self.process_label, value=0, text="Projekt öffnen")
        self.parent_directory = QFileDialog.getExistingDirectory(self, "Wähle einen Ordner aus!")
        if self.parent_directory:
            self.open_project_LE.setText(self.parent_directory)
            self.load_points_PBU.setEnabled(True)

            self.raster_directory = os.path.join(self.parent_directory, "raster")
            self.results_directory = os.path.join(self.parent_directory, "results")
            if not os.path.exists(self.results_directory):
                os.mkdir(self.results_directory)

                update_progresBar(bar=self.progressbar, label=self.process_label, value=100, text="Projekt erstellt")
            update_progresBar(bar=self.progressbar, label=self.process_label, value=100, text="Projekt geöffnet")
            return
        return

    def ask_open_points(self) -> None:
        # get filepath
        update_progresBar(bar=self.progressbar, label=self.process_label, value=0, text="lade Punkte")
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

            # update graphic
            self.update_preview_image()
            update_progresBar(bar=self.progressbar, label=self.process_label, value=100, text="Punkte geladen")
            return
        update_progresBar(bar=self.progressbar, label=self.process_label, value=0, text="Fehlgeschlagen: lade Punkte")
        return
    
    def load_dem(self) -> None:
        update_progresBar(bar=self.progressbar, label=self.process_label, value=0, text="Berechne BBox")
        creator = BBOXCreator(session=self.gnss_session)
        bbox: BBOX = creator.get_bbox()

        update_progresBar(bar=self.progressbar, label=self.process_label, value=10, text="Puffere BBox")
        bbox = bbox.puffer_box(distance=self.get_distance_slider())

        merger = RasterMerger(path=self.raster_directory)
        merger.remove_downloads()

        update_progresBar(bar=self.progressbar, label=self.process_label, value=20, text="Lade DEM herunter")
        loader: LoadRasterDEM = LoadRasterDEM(bbox=bbox, download_folder=self.raster_directory)
        tiles: list = loader.get_tiles()
        loader.load_raster(tiles=tiles)

        update_progresBar(bar=self.progressbar, label=self.process_label, value=80, text="Füge Raster zusammen")
        merger.merge_raster()
        merger.remove_downloads()
        
        update_progresBar(bar=self.progressbar, label=self.process_label, value=100, text="DEM heruntergeladen")

        return

    def single_point_rough(self) -> None:
        pass

    def all_points_rough(self) -> None:
        if self.ransac_radio_button.isChecked():
            method = 'RANSAC'
        else:
            method = 'CONVENTIONAL'

        min_elevation = self.get_cutoff()

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

        pdf_creator = PDFCreator(results_path=self.results_directory)
        pdf_creator.create_protocol(points=self.gnss_session.get_points(), projectname=self.project_name_LE.text(), projectleader=self.project_leader_LE.text())

        return

    def get_distance_slider(self) -> float | int:
        value = self.distance_slider.value()
        return value

    def update_distance(self) -> None:
        # update graphic
        self.update_preview_image()
        
        # update values
        value = self.get_distance_slider()
        self.distance_L.setText(f"Distanz: {value} m")
        return
    
    def get_segment_resolution(self) -> float | int:
        value = self.segment_slider.value()
        return value

    def update_segment_resolution(self) -> None:
        # update values
        value = self.get_segment_resolution()
        self.segment_L.setText(f"Auflösung: {value} m")
        return
    
    def get_cutoff(self) -> float | int:
        value = self.cutoff_slider.value()
        return value
    
    def update_cutoff_angle(self) -> None:
        # update graphic
        self.update_preview_image()
        
        # update values
        value = self.get_cutoff()
        self.cutoffL.setText(f"Cut-Off-Winkel: {value} gon")
        return
    
    def get_number_of_lines(self) -> float | int:
        value = self.number_of_lines_slider.value()
        return value

    def update_number_of_lines(self) -> None:
        # update graphic
        self.update_preview_image()
        
        # update values
        value = self.get_number_of_lines()
        self.number_of_lines_L.setText(f"Anzahl Linien: {value}")
        return
    
    def update_preview_image(self) -> None:
        drawer = RoughPlanDrawer()

        num_lines = self.get_number_of_lines()  # Annahme: Funktionen zur Rückgabe der Slider-Werte
        min_elevation = self.get_cutoff()
        line_length = self.get_distance_slider()

        figure = drawer.draw_polar_preview(num_lines=num_lines, min_elevation=min_elevation, line_length=line_length)

        canvas = FigureCanvas(figure)
        canvas.draw()

        # Erstellen eines QPixmap, das die gerenderte Figur enthält
        img = QPixmap(canvas.size())

        # Verwenden von QPainter, um die gerenderte Figur auf das QPixmap zu zeichnen
        painter = QPainter(img)
        canvas.render(painter)
        painter.end()

        # Anzeigen des QPixmap im QLabel
        self.line_graph_L.setPixmap(img)

        return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


