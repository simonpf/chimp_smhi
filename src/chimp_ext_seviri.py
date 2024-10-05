import logging
from pathlib import Path
from typing import Generator, Optional, Tuple, Union

import numpy as np
import torch
import xarray as xr
from chimp.data import InputDataset
from chimp.data.utils import scale_slices
from satpy.readers.seviri_base import CHANNEL_NAMES

LOGGER = logging.getLogger(__name__)


class SEVIRI(InputDataset):
    def __init__(self, name: str):
        super().__init__(name, "seviri", scale=4, variables=CHANNEL_NAMES.values())

    @property
    def n_channels(self) -> int:
        return len(self.variables)

    def load_sample(
            self,
            input_file: Path,
            crop_size: Union[int, Tuple[int, int]],
            base_scale: int,
            slices: Tuple[slice, slice],
            rng: Optional[Generator] = np.random.Generator,
            rotate: Optional[float] = None,
            flip: Optional[bool] = False,
    ) -> torch.Tensor:
        """
        Load input data sample from file.

        Args:
            input_file: The path of the input file which includes the data.
            crop_size: The size of the final crop.
            base_scale: The scale of the reference data.
            slices: A tuple of slices defining which parts of the data should be loaded.
            rng: A random number generator.
            rotate: If given, it specifies the angle (in degrees) by which the input should be rotated.
            flip: A boolean flag indicating whether to flip the input along the last dimensions.

        Returns:
            A torch tensor containing the loaded input data.
        """
        rel_scale = self.scale / base_scale

        if isinstance(crop_size, int):
            crop_size = (crop_size,) * self.n_dims
        crop_size = tuple((int(size / rel_scale) for size in crop_size))

        x_s = np.full(((self.n_channels,) + crop_size), np.nan)
        if input_file is not None:
            slices = scale_slices(slices, rel_scale)
            try:
                with xr.open_dataset(input_file) as data:
                    vs = [data[v][dict(zip(self.spatial_dims, slices))].data for v in self.variables]
                    x_s = np.stack(vs, axis=0)
            except OSError:
                LOGGER.warning("Reading of the input file '%s' failed. Skipping.", input_file)
        return torch.tensor(x_s.copy(), dtype=torch.float32)


seviri = SEVIRI("seviri")
