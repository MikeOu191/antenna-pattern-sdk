"""Pytest shared fixtures for test data generation."""
import textwrap
from pathlib import Path
import pytest


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    """
    Generates a minimal synthetic CSV file exercising Theta/Phi/Total/All markers.
    This allows us to test the parser without needing a real 100MB measurement file.
    """
    content = textwrap.dedent("""\
        HDR,HDR,HDR,HDR
        ,eTheta start,,
        Theta,,,,
        f,1.0,2400,f1,f2
        d1,0.1,0.2,0.3,0.4
        d2,0.5,0.6,0.7,0.8
        ,ePhi start,,
        Phi,,,,
        f,1.0,2400,f1,f2
        d1,1.1,1.2,1.3,1.4
        d2,1.5,1.6,1.7,1.8
        ,Total start,,
        Total,,,,
        f,1.0,2400,f1,f2
        d1,2.1,2.2,2.3,2.4
        d2,2.5,2.6,2.7,2.8
        ,All,,
        ,Total,,,
        x,y,z,f1,f2
        ,Theta,,,
        x,y,z,f1,f2
        ,Phi,,,
        x,y,z,f1,f2
    """)
    p = tmp_path / "sample.csv"
    p.write_text(content, encoding="utf-8")
    return p