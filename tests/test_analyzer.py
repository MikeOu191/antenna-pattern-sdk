"""Unit tests for the PatternAnalyzer module."""
from pathlib import Path
import numpy as np
import pytest

from antenna_sdk.analyzer import PatternAnalyzer
from antenna_sdk.models import ParsedCSV, BlockSlice


def test_cut_planes_indices_and_closure() -> None:
    """
    Test if cut-plane extraction correctly maps 24x13 matrix indices
    and enforces 25-point closure where physically appropriate.

    Note: Only XY plane is truly closed (Theta=90°, Phi 0°→360°).
    XZ and YZ planes are composed of two different Phi angles,
    so their start/end points are NOT the same physical location.
    """
    analyzer = PatternAnalyzer()

    # Create synthetic 24x13 matrices
    # ephi: values 0 to 311
    ephi_mat = np.arange(24 * 13).reshape(24, 13).astype(float)
    # etheta: values 0 to 623 (multiplied by 2)
    etheta_mat = (np.arange(24 * 13) * 2).reshape(24, 13).astype(float)

    ephi_dict = {"2400": ephi_mat}
    etheta_dict = {"2400": etheta_mat}

    planes = analyzer.extract_cut_planes(ephi_dict, etheta_dict)

    assert "2400" in planes
    cp = planes["2400"]

    # 1. Verify shapes (must be 25 points)
    assert cp.H["XY"].shape == (25,)
    assert cp.V["XZ"].shape == (25,)
    assert cp.H["YZ"].shape == (25,)

    # 2. Verify XY plane maps to column index 6 (Theta=90°)
    np.testing.assert_array_equal(cp.H["XY"][:24], ephi_mat[:, 6])
    np.testing.assert_array_equal(cp.V["XY"][:24], etheta_mat[:, 6])

    # 3. Verify XZ plane front half maps to row 0 (Phi=0°), cols 0..12
    np.testing.assert_array_equal(cp.H["XZ"][:13], ephi_mat[0, 0:13])
    np.testing.assert_array_equal(cp.V["XZ"][:13], etheta_mat[0, 0:13])

    # 4. Verify YZ plane front half maps to row 6 (Phi=90°), cols 0..12
    np.testing.assert_array_equal(cp.H["YZ"][:13], ephi_mat[6, 0:13])
    np.testing.assert_array_equal(cp.V["YZ"][:13], etheta_mat[6, 0:13])

    # 5. Verify XY plane closure (0° == 360°, same physical point)
    # XY plane: Theta=90° fixed, Phi goes 0°→360°, so start=end
    assert cp.H["XY"][0] == cp.H["XY"][-1], "XY plane must be closed (0° == 360°)"
    assert cp.V["XY"][0] == cp.V["XY"][-1], "XY plane must be closed (0° == 360°)"

    # 6. XZ and YZ planes are NOT closed (different Phi angles at start/end)
    # XZ: start=(Theta=0°, Phi=0°), end=(Theta=0°, Phi=180°)
    # YZ: start=(Theta=0°, Phi=90°), end=(Theta=0°, Phi=270°)
    # These are different physical locations, so values differ.
    assert cp.H["XZ"][0] != cp.H["XZ"][-1], "XZ plane start/end are different Phi angles"
    assert cp.H["YZ"][0] != cp.H["YZ"][-1], "YZ plane start/end are different Phi angles"


def test_analyze_orchestrator(sample_csv: Path) -> None:
    """Test the full analyze pipeline using the synthetic CSV fixture."""
    from antenna_sdk import CSVParser

    parsed = CSVParser(sample_csv).parse()
    measurement = PatternAnalyzer().analyze(parsed)

    assert measurement.file_path == str(sample_csv)
    assert "ePhi" in measurement.matrices
    assert "eTheta" in measurement.matrices
    # Note: The synthetic CSV in conftest.py has dummy data,
    # so cut_planes might be empty or contain zeros, but the structure should be valid.
    assert isinstance(measurement.cut_planes, dict)