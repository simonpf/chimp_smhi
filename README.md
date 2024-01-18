# CHIMP retrievals for SMHI

This repository provides provides preprocessing functionality and instructions for running a CHIMP retrieval on SEVIRI observations in HRIT format.

## Installation

All software required for running the retrievals is listed in the
`conda-environment.yml` file, which provides a conda environment named
`chimp_smhi`. To install and activate it, run:

``` shellsession
conda env create -f conda-environment.yml
conda activate chimp_smhi
```

### Downloading the model file

The retrieval model can be downloaded from [https://rain.atmos.colostate.edu/gprof_nn/chimp/chimp_smhi_v0.pt](https://rain.atmos.colostate.edu/gprof_nn/chimp/chimp_smhi_v0.pt).

## Running retrievals

Running CHIMP retrievals on SEVIRI files in HRIT format involves two steps: First the SEVIRI input files must be converted to the input data format expected by CHIMP. Secondly, input files must be processed using the ``chimp`` command.

### Extracting the CHIMP input data

The ``hrit2chimp.py`` script implements a command line application to convert all SEVIRI files in a given input folder to corresponding CHIMP input files. It can be used as follows.

``` shellsession
python hrit2chimp.py <path/to/folder/with/seviri/data> <path/to/chimp/input>
```

The script combines the observations from all SEVIRI channels and writes them into a single CHIMP input file. The seviri input files are written to ``<path/to/chimp/input>/seviri`` since `chimp` expects the inputs from all sensors to be organized into respective subfolders.

### Running CHIMP

Assuming ``hrit2chimp.py`` has been used to write CHIMP input files to ``<path/to/chimp/input>``, the retrieval can be run using:

``` shellsession
chimp process -v <path/to/model/> seviri <path/to/chimp/input> <path/to/chimp/output> --device cpu
```

> ***NOTE:*** The conda-environment contains the CPU-only version of PyTorch. Therefore, retrievals can only be run on the CPU. Since the default is running retrievals on the GPU, the ``--device cpu`` flag must be passed when ``chimp`` is invoked.

## Results

The results are written as NetCDF4 datasets to the provided output directory.
Currently the only retrieved variable is ``dbz_mean``. Since ``chimp``
retrievals are probabilistic, the ``_mean`` suffix is added to the variable name
highlight that it is the expected value of the retrieved posterior distribution.
