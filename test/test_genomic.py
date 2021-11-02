import pytest
import sys
import os
import glob
import distutils.util
from pathlib import Path
import unittest
import pytest
import conftest

build_dir = "build/lib.%s-%s" % (distutils.util.get_platform(), sys.version[0:3])

sys.path.insert(0, os.path.join(os.getcwd(), build_dir))
import HTSeq


data_folder = conftest.get_data_folder()


class TestGenomicArray(unittest.TestCase):
    def test_init(self):
        # Autoallocation
        ga = HTSeq.GenomicArray("auto")

        # Infinite length chromosomes
        ga = HTSeq.GenomicArray(['1', '2'])

        # Fixed chromosomes
        ga = HTSeq.GenomicArray({
            '1': 5898,
            '2': 4876,
        })

        # Store: ndarray
        ga = HTSeq.GenomicArray({
            '1': 5898,
            '2': 4876,
            },
            storage='ndarray',
        )

        # Store: memmap
        ga = HTSeq.GenomicArray({
            '1': 5898,
            '2': 4876,
            },
            storage='memmap',
            memmap_dir='.',
        )

    def test_steps(self):
        for storage in ['step', 'ndarray']:
            ga = HTSeq.GenomicArray({
                '1': 5898,
                '2': 4876,
                },
                storage=storage,
            )
            steps = ga.steps()
            steps_exp = [
                (HTSeq.GenomicInterval('1', 0, 5898, strand='+'), 0),
                (HTSeq.GenomicInterval('1', 0, 5898, strand='-'), 0),
                (HTSeq.GenomicInterval('2', 0, 4876, strand='+'), 0),
                (HTSeq.GenomicInterval('2', 0, 4876, strand='-'), 0),
            ]
            for step, step_exp in zip(steps, steps_exp):
                self.assertEqual(step, step_exp)

    def test_bedgraph(self):
        def compare_bedgraph_line(line1, line2):
            fields1 = line1.split()
            fields2 = line2.split()
            # Chromosome
            self.assertEqual(fields1[0], fields2[0])
            # Start-end
            self.assertEqual(int(fields1[1]), int(fields2[1]))
            self.assertEqual(int(fields1[2]), int(fields2[2]))
            # Value
            self.assertEqual(float(fields1[3]), float(fields2[3]))

        ga = HTSeq.GenomicArray.from_bedgraph_file(
            data_folder+'example_bedgraph.bedgraph',
            strand='.',
        )
        steps = []
        for iv, value in ga.steps():
            steps.append((iv.chrom, iv.start, iv.end, value))

        steps_exp = [
            ('chr19', 49302000, 49302300, -1.0),
            ('chr19', 49302300, 49302600, -0.75),
            ('chr19', 49302600, 49302900, -0.50),
            ('chr19', 49302900, 49303200, -0.25),
            ('chr19', 49303200, 49303500, 0.0),
            ('chr19', 49303500, 49303800, 0.25),
            ('chr19', 49303800, 49304100, 0.50),
            ('chr19', 49304100, 49304400, 0.75),
            ('chr19', 49304400, 49304700, 1.00),
        ]
        self.assertEqual(steps, steps_exp)

        ga.write_bedgraph_file(
            'test_output.bedgraph',
            track_options='name="BedGraph Format" description="BedGraph format" visibility=full color=200,100,0 altColor=0,100,200 priority=20',
            separator=' ',
        )
        with open(data_folder+'example_bedgraph.bedgraph') as f1, \
             open('test_output.bedgraph') as f2:
            header_found = False
            for line1, line2 in zip(f1, f2):
                if not header_found:
                    self.assertEqual(line1, line2)
                else:
                    compare_bedgraph_line(line1, line2)
                if 'track type' in line1:
                    header_found = True


if __name__ == '__main__':

    suite = TestGenomicArray()
    suite.test_init()
