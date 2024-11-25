import tempfile
from pathlib import Path

import chimp.areas
import pytest
import yaml
from satpy.readers import FSFile

from chimp_smhi.resampler import resample_seviri_native_file

area_definition = dict(
    CHIMP_NORDIC=dict(
        description="CHIMP region of interest over the nordic countries",
        projection=dict(
            proj="stere",
            lat_0=90,
            lat_ts=60,
            lon_0=14,
            x_0=0,
            y_0=0,
            datum="WGS84",
            no_defs=None,
            type="crs"),
        shape=dict(
            height=564,
            width=452
        ),
        area_extent=dict(
            lower_left_xy=[-745322.8983833211, -3996217.269197446],
            upper_right_xy=[1062901.0232376591, -1747948.2287755085],
            units="m"
        )
    )
)


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        yield tmpdir


def test_resample_seviri_native_file_raise_for_file_extension(temp_dir):
    with pytest.raises(ValueError, match="does not end in `.nc`"):
        resample_seviri_native_file(make_fs_file(temp_dir, "test"), temp_dir, lambda x: x)


@pytest.mark.parametrize("area_func", [
    lambda x: make_area_file(x),
    lambda x: chimp.areas.NORDICS_4,
])
def test_resample_seviri_native_file_with_area(temp_dir, area_func):
    fs_file = make_fs_file(temp_dir, "test.nc")
    area = area_func(temp_dir)
    with pytest.raises(ValueError, match="No supported files"):
        resample_seviri_native_file(fs_file, temp_dir, lambda x: x, area=area)


def test_resample_seviri_native_file_with_area_raise(temp_dir):
    fs_file = make_fs_file(temp_dir, "test.nc")
    with pytest.raises(ValueError, match="Invalid area"):
        resample_seviri_native_file(fs_file, temp_dir, lambda x: x, area=area_definition)


def make_area_file(directory: Path):
    yaml_file_path = directory / Path("sample_area.yaml")
    with open(yaml_file_path, "w") as f:
        yaml.dump(area_definition, f, default_flow_style=False)
    return yaml_file_path


def make_fs_file(directory: Path, filename: str) -> FSFile:
    full_filename = directory / Path(filename)
    with open(full_filename, "wb"):
        pass
    return FSFile(full_filename)
