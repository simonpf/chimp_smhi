# CHIMP retrievals for SMHI

This repository provides an example of running a CHIMP retrieval on SEVIRI input data in HRIT format.

## Installation

All  software is listed in the `conda-environment.yml` file, which provides a conda environment named `chimp_smhi`. To install and activate it, run:

``` shellsession
mamba env create -f conda-environment.yml
conda activate chimp_smhi
```

### Downloading the model file

The retrieval model can be downloaded from [https://rammb-slider.cira.colostate.edu/gprof_nn/chimp](https://rammb-slider.cira.colostate.edu/gprof_nn/chimp/chimp_smhi_v0.pt).

## Running retrievals

Running CHIMP retrievals involves two steps. First the SEVIRI input files must be converted to the input data files expected by CHIMP. Secondly, input files must be processed using the ``chimp`` command.

### Extracting the CHIMP input data

The ``hrit2chimp.py`` script implements a command line application to convert all SEVIRI files in a given input folder to corresponding CHIMP input files. It can be used as follows:

``` shellsession
python hrit2chimp.py <path/to/folder/with/seviri/data> <path/to/chimp/input>
```

> ***NOTE:** `hrit2chimp.py` writes the SEVIRI input data into a subfolder `<path/to/chimp/input>/seviri`. This is because `chimp` expects data from different sensors to be organized into corresponding subfolders in the input data directory. 


### Running CHIMP

Assuming ``hrit2chimp.py`` has been used to write CHIMP input files to ``input_data``, the retrieval can be run using:

``` shellsession
chimp process <path/to/model/> seviri <path/to/chimp/input> <path/to/chimp/output>
```

