import csv
import sys
import logging
import os
import ConfigParser
import itertools
import argparse
import string
import gzip
import ConfigParser
import shutil
from collections import *
import numpy as np
import pandas as pd

import pypeliner
import pypeliner.managed as mgd

import citup

if __name__ == '__main__':

    argparser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    pypeliner.app.add_arguments(argparser)

    argparser.add_argument('input_freqs',
                           help='Input Mutation Frequencies')

    argparser.add_argument('output_solution',
                           help='Output Solution Tree')

    argparser.add_argument('output_all_trees',
                           help='Output For All Trees')

    argparser.add_argument('--min_nodes', type=int, default=1,
                           help='Output For All Trees')

    argparser.add_argument('--max_nodes', type=int, default=8,
                           help='Output For All Trees')

    argparser.add_argument('--max_children_per_node', type=int, default=100,
                           help='Output For All Trees')

    args = vars(argparser.parse_args())

    pyp = pypeliner.app.Pypeline([citup], args)

    citup_bin_directory = os.path.join(os.path.dirname(citup.__file__))
    citup_iter_tool = os.path.join(citup_bin_directory, 'citupiter')

    lowmem = {'mem':1,'ncpu':1}

    pyp.sch.transform('create_trees', (), lowmem,
        citup.create_trees,
        mgd.TempOutputObj('trees', 'tree'),
        int(args['min_nodes']),
        int(args['max_nodes']),
        int(args['max_children_per_node']))
    
    pyp.sch.commandline('run_citup', ('tree',), lowmem, 
        citup_iter_tool,
        mgd.TempInputObj('trees', 'tree').prop('unlabeled_tree_string'),
        mgd.InputFile(args['input_freqs']),
        mgd.TempOutputFile('results', 'tree'))

    pyp.sch.transform('select_optimal_tree', (), lowmem,
        citup.select_optimal_tree,
        None,
        mgd.InputFile(args['input_freqs']),
        mgd.TempInputObj('trees', 'tree'),
        mgd.TempInputFile('results', 'tree'),
        mgd.OutputFile(args['output_solution']), 
        mgd.OutputFile(args['output_all_trees']))

    pyp.run()

