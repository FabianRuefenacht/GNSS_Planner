from dataclasses import dataclass
from fpdf import FPDF
import os
import glob

from backend.roughplanning.GNSS import GNSS_Point

@dataclass
class PDFCreator:
    results_path: str

    def create_protocol(self, points: list[GNSS_Point], projectname: str, projectleader: str) -> None:
        if not projectname: projectname = "Nicht angegeben"
        if not projectleader: projectleader = "Nicht angegeben"

        pdf = FPDF('landscape', 'mm', 'A4')

        pdf.add_page('portrait')
        pdf.set_font('helvetica', '', 32)
        pdf.cell(w=40, text="Protokoll GNSS Grobplanung", ln=1)
        pdf.cell(w=40, h=50, text="", ln=1)
        pdf.set_font('helvetica', '', 16)
        pdf.cell(w=40, text=f"Projektname:", ln=0)
        pdf.cell(w=0, text=f"{projectname}", ln=1)
        pdf.cell(w=40, text=f"Projektleitung:", ln=0)
        pdf.cell(w=0, text=f"{projectleader}", ln=1)

        for point in points:
            name = point.name
            easting = point.easting
            northing = point.northing
            floorheight = point.floor_height
            antennaheight = point.antenna_height

            pdf.add_page()
            pdf.set_font('helvetica', '', 16)
            pdf.cell(w=60, text=f"Punktname:", ln=0)
            pdf.cell(w=30, text=f"{name}", ln=1, align='r')
            pdf.set_font('helvetica', '', 12)
            pdf.cell(w=60, text=f"Ost-Koordinate:", ln=0)
            pdf.cell(w=30, text=f"{easting:.4f} m", ln=1, align='r')
            pdf.cell(w=60, text=f"Nord-Koordinate:", ln=0)
            pdf.cell(w=30, text=f"{northing:.4f} m", ln=1, align='r')
            pdf.cell(w=60, text=f"Punkthöhe:", ln=0)
            pdf.cell(w=30, text=f"{floorheight:.4f} m", ln=1, align='r')
            pdf.cell(w=60, text=f"Antennenhöhe:", ln=0)
            pdf.cell(w=30, text=f"{antennaheight:.1f} m", ln=1, align='r')

            panorama_image = self.find_image(name=f"panorama{name}.png")
            polar_image = self.find_image(name=f"polar{name}.png")
            legend = self.find_image(name=f"legend.png")

            pdf.image(name=panorama_image, x=10, y=50, w=140)
            pdf.image(name=legend, x=100, y=160, w=80)
            pdf.image(name=polar_image, x=147, y=50, w=140)


        pdf.output(os.path.join(self.results_path, "results.pdf"))
        
        return
    
    def find_image(self, name: str) -> str | None:
        files = glob.glob(os.path.join(self.results_path, name))

        if files:
            return files[0]
        else:
            raise FileNotFoundError("Die Datei wurde nicht gefunden!")