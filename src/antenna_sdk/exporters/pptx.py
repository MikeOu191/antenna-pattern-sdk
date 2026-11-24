"""PPTX Exporter — Heavy third-party deps are lazy-loaded."""
from pathlib import Path
import io
import numpy as np
from scipy.interpolate import make_interp_spline
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.util import Inches

from .base import BaseExporter
from ..models import AntennaMeasurement


class PPTXExporter(BaseExporter):
    """Export AntennaMeasurement data to a PowerPoint presentation with 2D polar plots."""

    def __init__(self, dpi: int = 150, slide_w_in: float = 13.333, slide_h_in: float = 7.5):
        """
        Initialize the PPTX Exporter.

        Args:
            dpi: Resolution for the saved images.
            slide_w_in: Slide width in inches.
            slide_h_in: Slide height in inches.
        """
        self.dpi = dpi
        self.slide_w = slide_w_in
        self.slide_h = slide_h_in

    def export(self, data: AntennaMeasurement, output_path: Path) -> Path:
        """
        Persist `data` to `output_path` as a PPTX file.
        """
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False

        prs = Presentation()
        prs.slide_width = Inches(self.slide_w)
        prs.slide_height = Inches(self.slide_h)

        angles_25 = np.linspace(0, 2 * np.pi, 25, endpoint=True)
        freq_keys = list(data.cut_planes.keys())

        for freq in freq_keys:
            slide_layout = prs.slide_layouts[6]
            slide = prs.slides.add_slide(slide_layout)
            fig, axs = plt.subplots(2, 3, subplot_kw={'projection': 'polar'}, figsize=(16, 9))
            fig.suptitle(f'Frequency: {freq} Hz', fontsize=20, fontweight='bold', y=0.98)

            planes = ['XZ', 'YZ', 'XY']
            pols = ['H', 'V']

            for i, pol in enumerate(pols):
                for j, plane in enumerate(planes):
                    ax = axs[i, j]
                    # 修正：使用 dataclass 的屬性存取方式
                    if pol == "H":
                        raw_data = data.cut_planes[freq].H[plane]
                    else:
                        raw_data = data.cut_planes[freq].V[plane]

                    theta_np = angles_25
                    data_np = np.array(raw_data)
                    data_np[-1] = data_np[0]

                    theta_smooth = np.linspace(theta_np.min(), theta_np.max(), 300)
                    spl = make_interp_spline(theta_np, data_np, k=3, bc_type='periodic')
                    data_smooth = spl(theta_smooth)

                    ax.plot(theta_smooth, data_smooth, linewidth=1.5, color='blue' if pol == 'H' else 'red')
                    title_text = f"{pol} ({'EPHI' if pol == 'H' else 'ETHETA'}) - {plane} Plane"
                    ax.set_title(title_text, fontsize=12, pad=10)
                    ax.set_theta_zero_location('N')
                    ax.set_theta_direction(-1)
                    ax.grid(True, linestyle='--', alpha=0.7)

            plt.tight_layout(rect=[0, 0, 1, 0.93])
            img_data = io.BytesIO()
            fig.savefig(img_data, format='png', dpi=self.dpi, bbox_inches='tight')
            img_data.seek(0)
            plt.close(fig)
            slide.shapes.add_picture(img_data, Inches(0.5), Inches(0.5), width=Inches(self.slide_w - 1))
        prs.save(output_path)
        return output_path