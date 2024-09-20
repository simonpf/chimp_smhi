# CHIMP retrievals for SMHI

This repository provides preprocessing functionality and instructions for
running a CHIMP retrieval on SEVIRI observations in HRIT format.

## Installation

All software required for running a specific version of the retrievals is listed in the
`chimp_smhi_<version-tag>.yml` file (where "<version-tag>" can be `v0` for instance), which provides a conda environment named
`chimp_smhi_<version-tag>`. To install and activate it, run (here for version `v1`):

``` shellsession
conda env create -f chimp_smhi_v1.yml
conda activate chimp_smhi_v1
```

### Downloading the model file

The retrieval models can be downloaded from:
 - Version 0: [https://rain.atmos.colostate.edu/gprof_nn/chimp/chimp_smhi_v0.pt](https://rain.atmos.colostate.edu/gprof_nn/chimp/chimp_smhi_v0.pt).
 - Version 1: [https://rain.atmos.colostate.edu/gprof_nn/chimp/chimp_smhi_v1.pt](https://rain.atmos.colostate.edu/gprof_nn/chimp/chimp_smhi_v1.pt).
 - Version 2: [https://rain.atmos.colostate.edu/gprof_nn/chimp/chimp_smhi_v2.pt](https://rain.atmos.colostate.edu/gprof_nn/chimp/chimp_smhi_v1.pt).
 - Version 3: [https://huggingface.co/simonpf/chimp_smhi](https://huggingface.co/simonpf/chimp_smhi).

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
For the sequence-based model the process command also needs to specify the number of input steps using the ``sequence_length`` option.

``` shellsession
chimp process -v <path/to/model/> seviri <path/to/chimp/input> <path/to/chimp/output> --device cpu --sequence_length 16
```

> ***NOTE:*** The conda-environment contains the CPU-only version of PyTorch. Therefore, retrievals can only be run on the CPU. Since the default is running retrievals on the GPU, the ``--device cpu`` flag must be passed when ``chimp`` is invoked.

### Model versions

### ``chimp_smhi_v0``

- ResNeXt architecture with 5M parameters
- Trained on 1-year of collocations
- Scene size 128


### ``chimp_smhi_v1``

- EfficientNet-V2 architecture with 20M parameters
- Trained on 1-year of collocations
- Scene size 256

> **NOTE:** The ``chimp_smhi_v1``  models should be run with a tile size of 256.

### ``chimp_smhi_v2``

- EfficientNet-V2 2p1 architecture with ~40M parameters
- Trained on 2-year of collocations over Europe and the Nordics
- Scene size 256

> **NOTE:** The ``chimp_smhi_v2``  models should be run with a tile size of 256 and
a sequence length of 16.

### ``chimp_smhi_v3``

There are two ``chimp_smhi`` version 3 models. The ``chimp_smhi_v3`` model processes single inputs, while the ``chimp_smhi_v3_seq`` model processes multiple inputs.

> **NOTE:** The ``chimp_smhi_v3``  model should be run with a tile size of 256.

> **NOTE:** The ``chimp_smhi_v3_seq``  model should be run with a tile size of 256 and a sequence length of 16.

## Results

The results are written as NetCDF4 datasets to the provided output directory.
Currently the only retrieved variable is ``dbz_mean``. Since ``chimp``
retrievals are probabilistic, the ``_mean`` suffix is added to the variable name
highlight that it is the expected value of the retrieved posterior distribution.

## Example 

The animation below compares the retrieved radar reflectivity for the different model versions.

![Reference and retrieved radar reflectivity from 2024-05-06](chimp_smhi.gif)
