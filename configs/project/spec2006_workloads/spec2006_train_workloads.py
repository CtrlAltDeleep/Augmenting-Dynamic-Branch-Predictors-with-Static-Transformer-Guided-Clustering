from dataclasses import dataclass
from typing import List, Optional
from .workload_util import BenchmarkArgs, BenchmarkSuite

class Spec2006TrainBenchmarks(BenchmarkSuite):

    def __init__(self, spec_base):
        
        self.benchmark_dirs = {
            'perlbench'  : spec_base + '/400.perlbench',
            'bzip2'      : spec_base + '/401.bzip2',
            'gcc'        : spec_base + '/403.gcc',
            'mcf'        : spec_base + '/429.mcf',
            'gobmk'      : spec_base + '/445.gobmk',
            'hmmer'      : spec_base + '/456.hmmer',
            'sjeng'      : spec_base + '/458.sjeng',
            'libquantum' : spec_base + '/462.libquantum',
            'h264ref'    : spec_base + '/464.h264ref',
            'omnetpp'    : spec_base + '/471.omnetpp',
            'astar'      : spec_base + '/473.astar',
            'xalancbmk'  : spec_base + '/483.xalancbmk',
        }

        self.benchmark_exes = { k : f'{v}/{k}' for k,v in self.benchmark_dirs.items() }

        self.benchmarks = {
            'perlbench' : [
                BenchmarkArgs(['-I./lib', 'perfect.pl', 'b', '3']),
                BenchmarkArgs(['-I./lib', 'scrabbl.pl', 'scrabbl.in']), 
                BenchmarkArgs(['-I./lib', 'suns.pl'])
            ],
            'bzip2' : [
                BenchmarkArgs(['input.program', '10']),
                BenchmarkArgs(['byoudoin.jpg', '5']),
                BenchmarkArgs(['input.combined','80'])
            ],
            'gcc' : [
                BenchmarkArgs(['integrate.i', '-o', 'integrate.s'])     
            ],
            'mcf' : [
                BenchmarkArgs(['inp.in'])
            ],
            'gobmk' : [
                BenchmarkArgs(['--quiet' , '--mode' , 'gtp'], 'arb.tst'),
                BenchmarkArgs(['--quiet' , '--mode' , 'gtp'], 'arend.tst'),
                BenchmarkArgs(['--quiet' , '--mode' , 'gtp'], 'atari_atari.tst'),
                BenchmarkArgs(['--quiet' , '--mode' , 'gtp'], 'blunder.tst'),
                BenchmarkArgs(['--quiet' , '--mode' , 'gtp'], 'buzco.tst'),
                BenchmarkArgs(['--quiet' , '--mode' , 'gtp'], 'nicklas2.tst'),
                BenchmarkArgs(['--quiet' , '--mode' , 'gtp'], 'nicklas4.tst')
            ],
            'hmmer' : [
               BenchmarkArgs(['--fixed', '0', '--mean', '425', '--num', '85000', '--sd', '300', '--seed', '0', 'leng100.hmm']) 
            ],
            'sjeng' : [
               BenchmarkArgs(['train.txt']) 
            ],
            'libquantum' : [
                BenchmarkArgs(['143', '25'])
            ],
            'h264ref' : [
                BenchmarkArgs(['-d', 'foreman_train_encoder_baseline.cfg'])
            ],
            'omnetpp' : [
                BenchmarkArgs(['omnetpp.ini'])
            ],
            'astar' : [
                BenchmarkArgs(['BigLakes1024.cfg']),
                BenchmarkArgs(['rivers1.cfg']),
            ],
            'xalancbmk' : [
                BenchmarkArgs(['allbooks.xml', 'xalanc.xsl'])
            ]
        }

    def get_workload_spec(self, name: str, idx: int) -> (str, BenchmarkArgs):
        return (self.benchmark_exes[name], self.benchmarks[name][idx])

    def get_benchmark_names(self) -> List[str]:
       return self.benchmarks.keys() 
    
    def get_num_workloads(self) -> int:
        return sum([len(b) for b in self.benchmarks.values()])
