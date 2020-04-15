# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#

import skbio
import pandas as pd

from q2_types.feature_data import (
    AlignedDNAFASTAFormat, DNAIterator)

from .plugin_setup import plugin


# copied from q2-types/q2_types/feature_data/_transformer.py
def _read_dna_fasta(path):
    return skbio.read(path, format='fasta', constructor=skbio.DNA)


@plugin.register_transformer
def _0(fmt: AlignedDNAFASTAFormat) -> DNAIterator:
    generator = _read_dna_fasta(str(fmt))
    return DNAIterator(generator)


@plugin.register_transformer
def _1(data: pd.Series) -> AlignedDNAFASTAFormat:
    ff = AlignedDNAFASTAFormat()
    with ff.open() as f:
        for id_, seq in data.iteritems():
            sequence = skbio.DNA(seq, metadata={'id': id_})
            skbio.io.write(sequence, format='fasta', into=f)
    return ff
