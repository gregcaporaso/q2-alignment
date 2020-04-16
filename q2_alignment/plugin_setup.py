# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from qiime2.plugin import (
    Plugin, Float, Int, Bool, Range, Citations, Str, Choices, TypeMatch)
from q2_types.feature_data import FeatureData, Sequence, AlignedSequence

import q2_alignment

citations = Citations.load('citations.bib', package='q2_alignment')
plugin = Plugin(
    name='alignment',
    version=q2_alignment.__version__,
    website='https://github.com/qiime2/q2-alignment',
    package='q2_alignment',
    description=('This QIIME 2 plugin provides support for generating '
                 'and manipulating sequence alignments.'),
    short_description='Plugin for generating and manipulating alignments.'
)

importlib.import_module('q2_alignment._transformers')

plugin.methods.register_function(
    function=q2_alignment.mafft,
    inputs={'sequences': FeatureData[Sequence]},
    parameters={'n_threads': Int % Range(1, None) | Str % Choices(['auto']),
                'parttree': Bool},
    outputs=[('alignment', FeatureData[AlignedSequence])],
    input_descriptions={'sequences': 'The sequences to be aligned.'},
    parameter_descriptions={
        'n_threads': 'The number of threads. (Use `auto` to automatically use '
                     'all available cores)',
        'parttree': 'This flag is required if the number of sequences being '
                    'aligned are larger than 1000000. Disabled by default'},
    output_descriptions={'alignment': 'The aligned sequences.'},
    name='De novo multiple sequence alignment with MAFFT',
    description=("Perform de novo multiple sequence alignment using MAFFT."),
    citations=[citations['katoh2013mafft']]
)

plugin.methods.register_function(
    function=q2_alignment.mafft_add,
    inputs={'alignment': FeatureData[AlignedSequence],
            'sequences': FeatureData[Sequence]},
    parameters={'n_threads': Int % Range(1, None) | Str % Choices(['auto']),
                'parttree': Bool},
    outputs=[('expanded_alignment', FeatureData[AlignedSequence])],
    input_descriptions={'alignment': 'The alignment to which '
                                     'sequences should be added.',
                        'sequences': 'The sequences to be added.'},
    parameter_descriptions={
        'n_threads': 'The number of threads. (Use `auto` to automatically use '
                     'all available cores)',
        'parttree': 'This flag is required if the number of sequences being '
                    'aligned are larger than 1000000. Disabled by default'},
    output_descriptions={
        'expanded_alignment': 'Alignment containing the provided aligned and '
                              'unaligned sequences.'},
    name='Add sequences to multiple sequence alignment with MAFFT.',
    description='Add new sequences to an existing alignment with MAFFT.',
    citations=[citations['katoh2013mafft']]
)

plugin.methods.register_function(
    function=q2_alignment.mask,
    inputs={'alignment': FeatureData[AlignedSequence]},
    parameters={'max_gap_frequency': Float % Range(0, 1, inclusive_end=True),
                'min_conservation': Float % Range(0, 1, inclusive_end=True)},
    outputs=[('masked_alignment', FeatureData[AlignedSequence])],
    input_descriptions={'alignment': 'The alignment to be masked.'},
    parameter_descriptions={
        'max_gap_frequency': ('The maximum relative frequency of gap '
                              'characters in a column for the column to be '
                              'retained. This relative frequency must be a '
                              'number between 0.0 and 1.0 (inclusive), where '
                              '0.0 retains only those columns without gap '
                              'characters, and 1.0 retains all columns '
                              'regardless of gap character frequency.'),
        'min_conservation': ('The minimum relative frequency '
                             'of at least one non-gap character in a '
                             'column for that column to be retained. This '
                             'relative frequency must be a number between 0.0 '
                             'and 1.0 (inclusive). For example, if a value of '
                             '0.4 is provided, a column will only be retained '
                             'if it contains at least one character that is '
                             'present in at least 40% of the sequences.')
    },
    output_descriptions={'masked_alignment': 'The masked alignment.'},
    name='Positional conservation and gap filtering.',
    description=("Mask (i.e., filter) unconserved and highly gapped "
                 "columns from an alignment. Default min_conservation was "
                 "chosen to reproduce the mask presented in Lane (1991)."),
    citations=[citations['lane1991']]
)

plugin.methods.register_function(
    function=q2_alignment.filter_positions,
    inputs={'alignment': FeatureData[AlignedSequence]},
    parameters={'reference_id': Str,
                'start': Int % Range(1, None),
                'end': Int % Range(1, None)},
    outputs=[('filtered_alignment', FeatureData[AlignedSequence])],
    input_descriptions={'alignment': 'The alignment to filter.'},
    parameter_descriptions={
        'reference_id': 'The identifier of the sequence which the slice'
                        ' positions correspond to.',
        'start': 'The start position (1-based indexing).',
        'end': 'The end position (1-based indexing). The end position '
               'is inclusive.'},
    output_descriptions={
        'filtered_alignment': 'The position-filtered alignment.'},
    name='Filter positions from an alignment',
    description=('Create a subalignment retaining only the specified '
                 'positions.')
)

T = TypeMatch([Sequence, AlignedSequence])

plugin.methods.register_function(
    function=q2_alignment.filter_seqs,
    inputs={'seqs': FeatureData[T]},
    parameters={
        'max_gap_frequency': Float % Range(0.0, 1.0, inclusive_end=True),
        'max_n_frequency': Float % Range(0.0, 1.0, inclusive_end=True),
        'min_length': Int % Range(0, None),
        'max_length': Int % Range(1, None)},
    outputs=[('filtered_seqs', FeatureData[T])],
    input_descriptions={'seqs': 'The sequences to be filtered.'},
    parameter_descriptions={
        'max_gap_frequency': ('The maximum fraction of a sequence that can '
                              'be gaps for the sequence to be retained in '
                              'the output.'),
        'max_n_frequency': ('The maximum fraction of a sequence that can '
                            'be N characters for the sequence to be retained '
                            'in the output.'),
        'min_length': ('The minimum length of a sequence that can be '
                       'retained in the ouput'),
        'max_length': ('The maximum length of a sequence that can be '
                       'retained in the ouput'),
                       },
    output_descriptions={
        'filtered_seqs': 'The sequences that are retained following '
                         'filtering.'},
    name='Filter sequences.',
    description=('Remove sequences from a collection of sequences based on '
                 'characteristics of the sequences.')
)
