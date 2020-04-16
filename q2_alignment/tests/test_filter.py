# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import skbio
import numpy as np
import unittest

from q2_alignment._filter import _most_conserved
from q2_alignment import mask, filter_seqs, filter_positions


class MostConservedTests(unittest.TestCase):

    def test_basic(self):
        frequencies = [{'A': 1/3, '-': 2/3}, {'G': 1.0}, {'A': 2/3, 'C': 1/3}]
        actual = _most_conserved(frequencies, skbio.DNA)
        expected = [1.0, 1.0, 2./3.]
        self.assertEqual(actual, expected)

        frequencies = [{'A': 1/4, '-': 3/4}, {'G': 1.0}, {'A': 1/2, 'C': 1/2},
                       {'A': 1/4, 'C': 1/4, 'G': 1/4, 'T': 1/4}]
        actual = _most_conserved(frequencies, skbio.DNA)
        expected = [1.0, 1.0, 0.5, 0.25]
        self.assertEqual(actual, expected)

    def test_N(self):
        frequencies = [{'A': 1/3, '-': 2/3}, {'G': 1.0}, {'A': 2/3, 'N': 1/3}]
        actual = _most_conserved(frequencies, skbio.DNA)
        expected = [1.0, 1.0, 2./3.]
        self.assertEqual(actual, expected)

    def test_unknown_gap_mode(self):
        frequencies = [{'A': 1/3, '-': 2/3}, {'G': 1.0}, {'A': 2/3, 'C': 1/3}]
        with self.assertRaises(ValueError):
            _most_conserved(frequencies, skbio.DNA, gap_mode='not-real')

    def test_all_gap(self):
        frequencies = [{'-': 1.0}]
        actual = _most_conserved(frequencies, skbio.DNA)
        expected = [0.0]
        self.assertEqual(actual, expected)

    def test_empty(self):
        frequencies = []
        actual = _most_conserved(frequencies, skbio.DNA)
        expected = []
        self.assertEqual(actual, expected)


class MaskTests(unittest.TestCase):

    def test_basic(self):
        alignment = skbio.TabularMSA(
            [skbio.DNA('AGA', metadata={'id': 'seq1', 'description': ''}),
             skbio.DNA('-GA', metadata={'id': 'seq2', 'description': ''}),
             skbio.DNA('-GC', metadata={'id': 'seq3', 'description': ''})]
        )

        actual = mask(alignment, max_gap_frequency=0.05, min_conservation=0.30)

        expected = skbio.TabularMSA(
            [skbio.DNA('GA', metadata={'id': 'seq1', 'description': ''}),
             skbio.DNA('GA', metadata={'id': 'seq2', 'description': ''}),
             skbio.DNA('GC', metadata={'id': 'seq3', 'description': ''})]
        )

        self.assertEqual(actual, expected)

    def test_gap_boundaries(self):
        alignment1 = skbio.TabularMSA(
            [skbio.DNA('-', metadata={'id': 'seq1', 'description': ''}),
             skbio.DNA('-', metadata={'id': 'seq2', 'description': ''}),
             skbio.DNA('-', metadata={'id': 'seq3', 'description': ''})]
        )
        alignment2 = skbio.TabularMSA(
            [skbio.DNA('A', metadata={'id': 'seq1', 'description': ''}),
             skbio.DNA('A', metadata={'id': 'seq2', 'description': ''}),
             skbio.DNA('A', metadata={'id': 'seq3', 'description': ''})]
        )

        actual = mask(alignment1, max_gap_frequency=1.0, min_conservation=0.0)
        self.assertEqual(actual, alignment1)

        actual = mask(alignment2, max_gap_frequency=0.0, min_conservation=0.0)
        self.assertEqual(actual, alignment2)

    def test_error_on_empty_alignment_gap_boundary(self):
        alignment1 = skbio.TabularMSA(
            [skbio.DNA('A', metadata={'id': 'seq1', 'description': ''}),
             skbio.DNA('-', metadata={'id': 'seq2', 'description': ''}),
             skbio.DNA('-', metadata={'id': 'seq3', 'description': ''})]
        )

        self.assertRaisesRegex(ValueError,
                               " 0.00% of positions were retained by the gap",
                               mask, alignment1, max_gap_frequency=0.1,
                               min_conservation=0.0)

    def test_conservation_boundaries(self):
        alignment1 = skbio.TabularMSA(
            [skbio.DNA('A', metadata={'id': 'seq1', 'description': ''}),
             skbio.DNA('A', metadata={'id': 'seq2', 'description': ''}),
             skbio.DNA('A', metadata={'id': 'seq3', 'description': ''})])
        alignment2 = skbio.TabularMSA(
            [skbio.DNA('-', metadata={'id': 'seq1', 'description': ''}),
             skbio.DNA('-', metadata={'id': 'seq2', 'description': ''}),
             skbio.DNA('-', metadata={'id': 'seq3', 'description': ''})])

        actual = mask(alignment1, max_gap_frequency=1.0, min_conservation=1.0)
        self.assertEqual(actual, alignment1)

        actual = mask(alignment2, max_gap_frequency=1.0, min_conservation=0.0)
        self.assertEqual(actual, alignment2)

    def test_error_on_empty_alignment_conservation_boundary(self):
        alignment1 = skbio.TabularMSA(
            [skbio.DNA('A', metadata={'id': 'seq1', 'description': ''}),
             skbio.DNA('C', metadata={'id': 'seq2', 'description': ''}),
             skbio.DNA('G', metadata={'id': 'seq3', 'description': ''})])

        self.assertRaisesRegex(ValueError,
                               " 0.00% of positions were retained by the con",
                               mask, alignment1, max_gap_frequency=1.0,
                               min_conservation=0.5)

    def test_invalid_gap_threshold(self):
        alignment = skbio.TabularMSA(
            [skbio.DNA('-', metadata={'id': 'seq1', 'description': ''}),
             skbio.DNA('-', metadata={'id': 'seq2', 'description': ''}),
             skbio.DNA('-', metadata={'id': 'seq3', 'description': ''})]
        )
        eps = np.finfo(float).eps
        with self.assertRaises(ValueError):
            mask(alignment, max_gap_frequency=0.0 - eps)
        with self.assertRaises(ValueError):
            mask(alignment, max_gap_frequency=1.0 + eps)

    def test_invalid_conservation_threshold(self):
        alignment = skbio.TabularMSA(
            [skbio.DNA('-', metadata={'id': 'seq1', 'description': ''}),
             skbio.DNA('-', metadata={'id': 'seq2', 'description': ''}),
             skbio.DNA('-', metadata={'id': 'seq3', 'description': ''})]
        )
        eps = np.finfo(float).eps
        with self.assertRaises(ValueError):
            mask(alignment, min_conservation=0.0 - eps)
        with self.assertRaises(ValueError):
            mask(alignment, min_conservation=1.0 + eps)

    def test_empty_input(self):
        alignment = skbio.TabularMSA(
            [skbio.DNA('', metadata={'id': 'seq1', 'description': ''}),
             skbio.DNA('', metadata={'id': 'seq2', 'description': ''}),
             skbio.DNA('', metadata={'id': 'seq3', 'description': ''})]
            )
        with self.assertRaises(ValueError):
            mask(alignment)

        alignment = skbio.TabularMSA([])
        with self.assertRaises(ValueError):
            mask(alignment)

class FilterPositionsTests(unittest.TestCase):

    def test_retain_full_reference(self):
        alignment = skbio.TabularMSA(
            [skbio.DNA('CCA-T-AGA', metadata={'id': 's1', 'description': ''}),
             skbio.DNA('T---T-ATA', metadata={'id': 's2', 'description': ''}),
             skbio.DNA('---GTTATA', metadata={'id': 's3', 'description': ''})]
        )
        obs = filter_positions(alignment, 's1', 1, 7)
        self.assertEqual(obs, alignment)
        obs = filter_positions(alignment, 's2', 1, 5)
        self.assertEqual(obs, alignment)
        obs = filter_positions(alignment, 's3', 1, 6)
        exp = skbio.TabularMSA(
            [skbio.DNA('-T-AGA', metadata={'id': 's1', 'description': ''}),
             skbio.DNA('-T-ATA', metadata={'id': 's2', 'description': ''}),
             skbio.DNA('GTTATA', metadata={'id': 's3', 'description': ''})]
        )
        self.assertEqual(obs, exp)