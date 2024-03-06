"""
hritfiles2chimp
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


logging.basicConfig(level="INFO", force=True)
LOGGER = logging.getLogger(__name__)


def sort_hrit_files(hrit_files: List[Path]) -> Dict[datetime, List[Path]]:
    """
    Sort HRIT files by time.

    Args:
        path: A path object pointing to the directory containing SEVIRI
            observation in HRIT format.

    Return:
        A dictionary mapping datetime objects to the corresponding observation
        files.
    """
    files = sorted(list(hrit_files))
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
    scene = Scene(hrit_files, reader="seviri_l1b_hrit")
    scene.load(datasets)
    scene_r = scene.resample(NORDICS_4, radius_of_influence=4e3)

    obs = []
    # names = []
    for name in datasets:
        obs.append(scene_r[name].compute().data)

    # acq_time = scene[datasets[0]].compute().acq_time.mean().data

    obs = np.stack(obs, -1)

    data = xr.Dataset({"obs": (("y", "x", "channels"), obs)})
    return data


def process(model, input_datasets, input_path, output_path, device="cuda", precision="single", verbose=0):
    from chimp.processing import InputDataset, load_model, torch, retrieval_step, to_datetime

    input_data = InputDataset(input_path, input_datasets)
    model = load_model(model)

    output_path = Path(output_path)
    if not output_path.exists():
        output_path.mkdir(parents=True)

    if verbose > 0:
        logging.basicConfig(level="INFO", force=True)

    if precision == "single":
        float_type = torch.float32
    else:
        float_type = torch.bfloat16

    for time, model_input in input_data:
        LOGGER.info("Starting processing input @ %s", time)
        results = retrieval_step(
            model,
            model_input,
            tile_size=128,
            device=device,
            float_type=float_type
        )
        LOGGER.info("Finished processing input @ %s", time)

        results["time"] = time.astype("datetime64[ns]")
        date = to_datetime(time)
        date_str = date.strftime("%Y%m%d_%H_%M")
        output_file = output_path / f"chimp_{date_str}.nc"
        LOGGER.info("Writing results to %s", output_file)
        results.to_netcdf(output_file)



if __name__ == '__main__':
    import argparse
    import tempfile
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_files",
        nargs="*",
        type=Path,
        help="Directory containing the SEVIRI input observations in HRIT format."
    )
    parser.add_argument(
        "-o",
        "--output-path",
        type=Path,
        help="Directory to which to write the 'chimp' input files.",
        default="/tmp/chimp"
    )
    parser.add_argument(
        "-m",
        "--model-file",
        type=str,
        help="Model file"
    )
    args = parser.parse_args()

    input_files = args.input_files
    model_file = args.model_file

    files = sort_hrit_files(input_files)
    LOGGER.info("Found input files.")
    for time, hrit_files in files.items():
        output_filename = get_output_filename("seviri", time, timedelta(minutes=15))
        with tempfile.TemporaryDirectory() as td:
            temp_path = Path(td)
            output_path = temp_path / "seviri"
            output_path.mkdir(parents=True)
            data_file = output_path / output_filename
            data = load_and_resample_data(next(iter(files.values())))
            data.to_netcdf(data_file)
            process(model_file, ["seviri"], temp_path,  args.output_path, device="cpu")
