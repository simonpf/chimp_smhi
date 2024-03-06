"""
hrit2chimp
==========

Preprocessing script to convert High Rate Seviri images to CHIMP SEVIRI
input data.
"""
from datetime import datetime, timedelta
import logging
from pathlib import Path
from typing import Dict, List

import numpy as np
from satpy import Scene
import xarray as xr

from chimp.areas import NORDICS_4
from chimp.data.seviri import CHANNEL_CONFIGURATIONS
from chimp.data.utils import get_output_filename


logging.basicConfig(level="INFO")
LOGGER = logging.getLogger(__name__)


def find_hrit_files(path: Path) -> Dict[datetime, List[Path]]:
    """
    Find available HRIT files in a given directory and sort them
    by time.

    Args:
        path: A path object pointing to the directory containing SEVIRI
            observation in HRIT format.

    Return:
        A dictionary mapping datetime objects to the corresponding observation
        files.
    """
    files = sorted(list(path.glob("H-???-MSG?__*__")))
    files_sorted = {}
    for path in files:
        filename = path.name
        date = datetime.strptime(filename[-15:-3], "%Y%m%d%H%M")
        files_sorted.setdefault(date, []).append(path)
    return files_sorted


def load_and_resample_data(hrit_files: List[Path]) -> xr.Dataset:
    """
    Loads and resamples and combines seviri data into a single xarray.Dataset.

    Args:
        hrit_files: List of SEVIRI files for a given time step.

    Return:
        An xarray.Dataset containing SEVIRI observations resampled to the BALTRAD
        domain and combined into a single observation dataset.
    """
    datasets = CHANNEL_CONFIGURATIONS["all"]
    scene = Scene(hrit_files)
    scene.load(datasets)
    scene_r = scene.resample(
        NORDICS_4,
        radius_of_influence=12e3,
        reader="seviri_hrit"
    )

    obs = []
    names = []
    for name in datasets:
        obs.append(scene_r[name].compute().data)

    acq_time = scene[datasets[0]].compute().acq_time.mean().data

    obs = np.stack(obs, -1)

    data = xr.Dataset({"obs": (("y", "x", "channels"), obs)})
    return data


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_path",
        type=str,
        help="Directory containing the SEVIRI input observations in HRIT format."
    )
    parser.add_argument(
        "output_path",
        type=str,
        help="Directory to which to write the 'chimp' input files."
    )
    args = parser.parse_args()

    input_path = Path(args.input_path)
    output_path = Path(args.output_path) / "seviri"


    if not output_path.exists():
        output_path.mkdir(parents=True)

    files = find_hrit_files(input_path)
    LOGGER.info("Found input files for %s time steps.")
    for time, hrit_files in files.items():
        data = load_and_resample_data(next(iter(files.values())))
        output_filename = get_output_filename("seviri", time, timedelta(minutes=15))
        data.to_netcdf(output_path / output_filename)
