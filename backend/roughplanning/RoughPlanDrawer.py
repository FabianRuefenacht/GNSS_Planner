"""
Code by Fabian Rüfenacht.

Codedocumentation assisted by ChatGPT version 3.5
"""

import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass

# -------------------------------------------------- draw graphs --------------------------------------------------
@dataclass
class RoughPlanDrawer:
    def draw_panorama_diagram(self, azimuths: list[float], elevation_angles: list[float], min_elevation: float | int, image_path: str, pointname: str) -> None:
        """
        Draws a panorama diagram with azimuths and elevation angles.

        Parameters
        ----------
        azimuths : list[float]
            List of azimuth angles in gon (0-400).
        elevation_angles : list[float]
            List of elevation angles in gon.
        min_elevation : float | int
            Minimum elevation angle threshold to mark in the diagram.
        image_path : str
            File path where the diagram image will be saved.
        pointname : str
            Name of the point for which the diagram is drawn.

        Returns
        -------
        None

        Notes
        -----
        This method creates a line plot showing the elevation angles along with a threshold line.
        It also fills the area below each line with corresponding colors (grey for elevation angles,
        red for the minimum elevation threshold). The x-axis represents directions, while the y-axis
        represents elevation angles in gon. The diagram is saved as an image file specified by image_path.
        The plot is closed after saving to release memory resources.
        """
        # init directions
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
        direction_angles = np.linspace(0, 400, 9)

        elevation_angles.append(elevation_angles[0])
        azimuths.append(400)
        cut_off = [min_elevation for i in elevation_angles]

        fig, ax = plt.subplots()

        ax.plot(azimuths, elevation_angles, color='grey')
        ax.fill_between(azimuths, elevation_angles, color='grey', alpha=0.5)

        ax.plot(azimuths, cut_off, color='red')
        ax.fill_between(azimuths, cut_off, color='red', alpha=0.5)

        # Aset axis
        ax.set_xlim([0, 400])
        ax.set_ylim([0, 100])
        ax.set_xticks(direction_angles)
        ax.set_xticklabels(directions)
        ax.set_yticks(np.linspace(0, 100, 5))

        ax.set_xlabel('Himmelsrichtungen')
        ax.set_ylabel('Höhenwinkel [gon]')
        ax.set_title(f'Grobplanung {pointname}')

        plt.grid(True)
        plt.savefig(image_path)
        plt.close()

        return
    
    def draw_polar_diagram(self, azimuths, elevation_angles, min_elevation, image_path, pointname):
        """
        Draws a polar diagram representing elevation angles and a minimum elevation threshold.

        Parameters
        ----------
        azimuths : list[float]
            List of azimuth angles in gon (0-400).
        elevation_angles : list[float]
            List of elevation angles in gon.
        min_elevation : float | int
            Minimum elevation angle threshold to mark in the diagram.
        image_path : str
            File path where the diagram image will be saved.
        pointname : str
            Name of the point for which the diagram is drawn.

        Returns
        -------
        None
        """
        # Convert azimuths and elevation angles to radians
        azimuths_rad = np.deg2rad(np.array(azimuths) * 9 / 10)
        elevation_angles_rad = (100 - np.array(elevation_angles)) * np.pi / 200
        min_elevation_rad = (100 - min_elevation) * np.pi / 200

        # Interpolation
        interpolated_azimuths_rad = np.linspace(azimuths_rad[0], azimuths_rad[-1], 100)
        interpolated_elevation_angles_rad = np.interp(interpolated_azimuths_rad, azimuths_rad, elevation_angles_rad)

        # Create a polar plot
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

        # Adjust the direction so that 0 radians is at the top
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)  # Set the direction of the angles to clockwise

        # Plot the elevation angles
        ax.plot(interpolated_azimuths_rad, interpolated_elevation_angles_rad, color='grey')
        ax.fill_between(interpolated_azimuths_rad, interpolated_elevation_angles_rad, np.pi / 2, color='grey', alpha=0.5)

        # Plot the cutoff line
        cut_off_rad = np.full_like(interpolated_elevation_angles_rad, min_elevation_rad)
        ax.plot(interpolated_azimuths_rad, cut_off_rad, color='red')
        ax.fill_between(interpolated_azimuths_rad, cut_off_rad, np.pi / 2, color='red', alpha=0.5)

        # Customize the plot
        ax.set_ylim(0, np.pi / 2)  # Set the limit for the radial coordinate (0 to 100 gon)
        ax.set_yticks([0 * np.pi / 200, 20 * np.pi / 200, 40 * np.pi / 200, 60 * np.pi / 200, 80 * np.pi / 200, 100 * np.pi / 200])
        ax.set_yticklabels(['100', '80', '60', '40', '20', '0'])

        # Set x-ticks to represent the directions
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
        direction_angles_rad = np.linspace(0, 2 * np.pi, len(directions))
        ax.set_xticks(direction_angles_rad)
        ax.set_xticklabels(directions)

        ax.set_title(f'Grobplanung {pointname}')

        # Save the figure
        plt.savefig(image_path)

        plt.close(fig)  # Close the figure to release memory

        return
    
    def save_legend(self, legend_path: str):
        """
        Saves a legend as a separate image file.

        Parameters
        ----------
        legend_path : str
            File path where the legend image will be saved.

        Returns
        -------
        None

        Notes
        -----
        This method creates a figure with legend items representing different elements of a polar diagram:
        elevation angles, coverage areas, minimum elevation cutoff, and cutoff areas. The legend items are
        displayed using lines and filled areas with specified colors and labels. The figure is saved as an
        image file specified by legend_path. The plot axis is turned off, and the figure is closed to release
        memory resources after saving.
        """
        # Create a figure and axis just for the legend
        fig_legend, ax_legend = plt.subplots(figsize=(3, 2))
        
        # Create legend items
        line1, = ax_legend.plot([], [], color='grey', label='Höhenwinkel Hindernisse')
        fill1 = ax_legend.fill_between([], [], color='grey', alpha=0.5, label='Abdeckung Hindernisse')
        line2, = ax_legend.plot([], [], color='red', label='Cut-Off-Winkel')
        fill2 = ax_legend.fill_between([], [], color='red', alpha=0.5, label='Cut-Off-Fläche')
        
        # Add legend
        ax_legend.legend([line1, fill1, line2, fill2], ['Höhenwinkel Hindernisse', 'Abdeckung Hindernisse', 'Cut-Off-Winkel', 'Cut-Off-Fläche'])
        ax_legend.axis('off')  # Turn off axis

        ax_legend.set_title("Legende")
        
        # Save the legend figure
        fig_legend.savefig(legend_path)
        plt.close(fig_legend)  # Close the figure to release memory

        return