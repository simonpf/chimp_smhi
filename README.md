# CHIMP retrievals for SMHI

This repository provides preprocessing functionality and instructions for running a CHIMP retrieval on SEVIRI observations.

## Installation

First clone the repository
``` shellsession
git clone https://github.com/simonpf/chimp_smhi.git
```
All the requirements for running chimp is in [chimp_smhi.yaml](./envs/chimp_smhi.yaml).
The file provides a conda environment with the same name (excluding the `.yaml` extension).

To install and activate the available conda environment, run:

``` shellsession
<conda_exec> env create -f chimp_smhi/envs/chimp_smhi.yaml
<conda_exec> activate chimp_smhi
```
where `<conda_exec>` can be either [mamba](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html)
or [micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html).

Finally install the present package, i.e. `chimp_smhi` via
``` shellsession
pip install chimp_smhi
```

### Downloading the model file

The retrieval models can be downloaded from:
 - versions `<  v3`: [https://rain.atmos.colostate.edu/gprof_nn/chimp/](https://rain.atmos.colostate.edu/gprof_nn/chimp/).
 - versions `>= v3`: [https://huggingface.co/simonpf/chimp_smhi](https://huggingface.co/simonpf/chimp_smhi).

## Running retrievals

Running CHIMP retrievals on SEVIRI files involves three steps as described further below.


1- First, one needs to set the `CHIMP_EXTENSION_MODULES` environment variable as follows:
```
export CHIMP_EXTENSION_MODULES=chimp_ext_seviri
```
This makes the `chimp` command-line interface (CLI) aware of the `chimp_ext_seviri` module, which is needed to read the SEVIRI files.

2- Then the `chimp_ext_seviri` module needs to be made available to and discoverable by the `chimp`. This can be done by downloading the `chimp_ext_seviri.py` module and modifying the python path accordingly, i.e.
```
export PYTHONPATH="${PYTHONPATH}:<chimp-ext-seviri-directory>"
```
where `<chimp-ext-seviri-directory>` is the directory that includes `chimp_ext_seviri.py`.

3- Finally, the `chimp` CLI must be run to reprocess the input files.

> ***NOTE:*** The conda environment contains the CPU-only version of PyTorch. Therefore, retrievals can only be run on the CPU. Since the default is running retrievals on the GPU, the ``--device cpu`` flag must be passed when ``chimp`` is invoked.

> ***NOTE:*** One can run `chimp process --help` to be informed about the available options and the exact order of command-line arguments that can be passed to the `chimp` CLI.

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
