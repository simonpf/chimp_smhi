# CHIMP retrievals for SMHI

This repository provides preprocessing functionality and instructions for
running a CHIMP retrieval on SEVIRI observations.

## Installation

All software required for running a specific version of the retrievals is listed in files inside the `envs` directory. The files are named `chimp_smhi_<version-tag>.yml` file, where `<version-tag>` $\in$ `{v0, v1, v2, v3}`. Each file provides a conda environment with the same name (excluing the `.yml` extension).

To install and activate any of the available conda environments, run:

``` shellsession
<conda_exec> env create -f chimp_smhi_<version-tag>.yml
<conda_exec> activate chimp_smhi_<version-tag>
```
where `<conda_exec>` can be `mamba`, `micromamba`, or `conda` (not recommended).

### Downloading the model file

The retrieval models can be downloaded from:
 - Version 0: [https://rain.atmos.colostate.edu/gprof_nn/chimp/chimp_smhi_v0.pt](https://rain.atmos.colostate.edu/gprof_nn/chimp/chimp_smhi_v0.pt).
 - Version 1: [https://rain.atmos.colostate.edu/gprof_nn/chimp/chimp_smhi_v1.pt](https://rain.atmos.colostate.edu/gprof_nn/chimp/chimp_smhi_v1.pt).
 - Version 2: [https://rain.atmos.colostate.edu/gprof_nn/chimp/chimp_smhi_v2.pt](https://rain.atmos.colostate.edu/gprof_nn/chimp/chimp_smhi_v1.pt).
 - Version 3: [https://huggingface.co/simonpf/chimp_smhi](https://huggingface.co/simonpf/chimp_smhi).

## Running retrievals

Running CHIMP retrievals on SEVIRI files involves three steps as described further below.


1- First one needs to the set the `CHIMP_EXTENSION_MODULES` environment variable as follows:
```
export CHIMP_EXTENSION_MODULES=chimp_ext_seviri
```
This points the `chimp` to the `chimp_ext_seviri` which is needed to read the SEVIRI files.

2- Then the `chimp_ext_seviri` module needs to be made available to the `chimp`. This can be done by downloading the `chimp_ext_seviri.py` module and modifying the python path accordingly, i.e.
```
export PYTHONPATH="${PYTHONPATH}:<chimp-ext-seviri-directory>"
```
where `<chimp-ext-seviri-directory>` is the directory that includes `chimp_ext_seviri.py`.

3- Finally, the `chimp` command line interface must be run to reprocess the input files.

> ***NOTE:*** The conda environment contains the CPU-only version of PyTorch. Therefore, retrievals can only be run on the CPU. Since the default is running retrievals on the GPU, the ``--device cpu`` flag must be passed when ``chimp`` is invoked.


## Model versions

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

The results are written as `NetCDF4` datasets to the provided output directory.
Currently the only retrieved variable is ``dbz_mean``. Since ``chimp``
retrievals are probabilistic, the ``_mean`` suffix is added to the variable name
highlight that it is the expected value of the retrieved posterior distribution.

## Example

The animation below compares the retrieved radar reflectivity for the different model versions.

![Reference and retrieved radar reflectivity from 2024-05-06](figs/chimp_smhi.gif)
