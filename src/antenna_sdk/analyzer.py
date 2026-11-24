"""Matrix extraction (Action 10) and 2D cut-plane computation (Action 13)."""
from __future__ import annotations

import logging
from typing import Dict

import numpy as np

from .models import ParsedCSV, CutPlaneSet, AntennaMeasurement

logger = logging.getLogger(__name__)


class PatternAnalyzer:
    """Extracts 24x13 matrices and computes 25-point closed 2D cut planes."""

    MATRIX_ROWS = 24
    MATRIX_COLS = 13
    DATA_COL_START = 3   # 0-based column where numeric data begins
    DATA_COL_END = 16    # exclusive

    def extract_matrices(self, parsed: ParsedCSV) -> Dict[str, Dict[str, np.ndarray]]:
        """Extract 24x13 matrices for each frequency in each block."""
        out: Dict[str, Dict[str, np.ndarray]] = {}
        for name, blk in parsed.blocks.items():
            freq_list = parsed.block_frequencies.get(name, [])
            per_freq: Dict[str, np.ndarray] = {}
            for global_row, freq_str in freq_list:
                rel = global_row - blk.start_row
                data_start = rel + 3  # skip header rows inside block
                mat = np.zeros((self.MATRIX_ROWS, self.MATRIX_COLS), dtype=float)
                for i in range(self.MATRIX_ROWS):
                    r = data_start + i
                    if r < len(blk.data):
                        row = blk.data[r]
                        cells = row[self.DATA_COL_START:self.DATA_COL_END]
                        for j, c in enumerate(cells[:self.MATRIX_COLS]):
                            try:
                                mat[i, j] = float(str(c).strip())
                            except (ValueError, TypeError):
                                mat[i, j] = 0.0
                per_freq[freq_str] = mat
            out[name] = per_freq
            logger.info(
                "[%s] 提取 %d 個頻率的 %dx%d 矩陣。",
                name, len(per_freq), self.MATRIX_ROWS, self.MATRIX_COLS,
            )
        return out

    def extract_cut_planes(
        self,
        ephi: Dict[str, np.ndarray],
        etheta: Dict[str, np.ndarray],
    ) -> Dict[str, CutPlaneSet]:
        """Compute 25-point closed 2D cut planes (XY, XZ, YZ) for H and V polarizations."""
        planes: Dict[str, CutPlaneSet] = {}
        for freq in ephi:
            if freq not in etheta:
                continue
            eh = self._close(ephi[freq])      # 24 -> 25 rows (360° = 0°)
            ev = self._close(etheta[freq])

            # XZ plane: Phi=0° (row 0) + Phi=180° (row 12, reversed)
            xz_h = np.concatenate([eh[0, 0:13], eh[12, 11::-1]])
            xz_v = np.concatenate([ev[0, 0:13], ev[12, 11::-1]])

            # YZ plane: Phi=90° (row 6) + Phi=270° (row 18, reversed)
            yz_h = np.concatenate([eh[6, 0:13], eh[18, 11::-1]])
            yz_v = np.concatenate([ev[6, 0:13], ev[18, 11::-1]])

            # XY plane: Theta=90° (col 6) for all 25 rows
            xy_h = eh[:, 6].copy()
            xy_v = ev[:, 6].copy()

            planes[freq] = CutPlaneSet(
                frequency=freq,
                H={"XZ": xz_h, "YZ": yz_h, "XY": xy_h},
                V={"XZ": xz_v, "YZ": yz_v, "XY": xy_v},
            )
        logger.info("提取 %d 個頻率的 25 點閉合切面。", len(planes))
        return planes

    @staticmethod
    def _close(mat: np.ndarray) -> np.ndarray:
        """Append row 0 as row 24 so 0° and 360° coincide (24x13 -> 25x13)."""
        if mat.shape[0] == 24:
            return np.vstack([mat, mat[0:1, :]])
        return mat

    def analyze(self, parsed: ParsedCSV) -> AntennaMeasurement:
        """Orchestrate the full analysis pipeline."""
        matrices = self.extract_matrices(parsed)
        ephi = matrices.get("ePhi", {})
        etheta = matrices.get("eTheta", {})
        cut_planes = (
            self.extract_cut_planes(ephi, etheta)
            if ephi and etheta else {}
        )
        return AntennaMeasurement(
            file_path=parsed.file_path,
            encoding=parsed.encoding,
            matrices=matrices,
            cut_planes=cut_planes,
        )