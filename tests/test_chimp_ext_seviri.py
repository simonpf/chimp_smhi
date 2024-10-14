"""The testing module for :obj:`chimp_smhi.chimp_ext_seviri`."""

from collections import Counter

from satpy.readers.seviri_base import CHANNEL_NAMES

from chimp_smhi import seviri_instance


def test_channel_names():
    """Test if channel names and numbers are correct."""
    assert Counter(seviri_instance.variables) == Counter(CHANNEL_NAMES.values())
    assert seviri_instance.n_channels == len(CHANNEL_NAMES.values())
