from dataclasses import dataclass
from typing import List, Optional
from .workload_util import BenchmarkArgs, BenchmarkSuite

class Spec2006RefBenchmarks(BenchmarkSuite):

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
                BenchmarkArgs(['-I./lib', 'checkspam.pl', '2500', '5', '25', '11', '150', '1', '1', '1', '1']),
                BenchmarkArgs(['-I./lib', 'diffmail.pl', '4', '800', '10', '17', '19', '300']), 
                BenchmarkArgs(['-I./lib', 'splitmail.pl', '1600', '12', '26', '16', '4500'])
            ],
            'bzip2' : [
                BenchmarkArgs(['input.source', '280']),
                BenchmarkArgs(['chicken.jpg', '30']),
                BenchmarkArgs(['liberty.jpg', '30']),
                BenchmarkArgs(['input.program', '280']),
                BenchmarkArgs(['text.html', '280']),
                BenchmarkArgs(['input.combined', '200']),
            ],
            'gcc' : [
                BenchmarkArgs(['166.i', '-o', '166.i']), 
                BenchmarkArgs(['200.i', '-o', '200.i']), 
                BenchmarkArgs(['cp-decl.i', '-o', 'cp-decl.i']), 
                BenchmarkArgs(['c-typeck.i', '-o', 'c-typeck.i']), 
                BenchmarkArgs(['expr2.i', '-o', 'expr2.i']), 
                BenchmarkArgs(['expr.i', '-o', 'expr.i']), 
                BenchmarkArgs(['g23.i', '-o', 'g23.i']), 
                BenchmarkArgs(['s04.i', '-o', 's04.i']), 
                BenchmarkArgs(['scilab.i', '-o', 'scilab.i']), 
            ],
            'mcf' : [
                BenchmarkArgs(['inp.in'])
            ],
            'gobmk' : [
                BenchmarkArgs(['--quiet' , '--mode' , 'gtp'], '13x13.tst'),
                BenchmarkArgs(['--quiet' , '--mode' , 'gtp'], 'nngs.tst'),
                BenchmarkArgs(['--quiet' , '--mode' , 'gtp'], 'score2.tst'),
                BenchmarkArgs(['--quiet' , '--mode' , 'gtp'], 'trevorc.tst'),
                BenchmarkArgs(['--quiet' , '--mode' , 'gtp'], 'trevord.tst'),
            ],
            'hmmer' : [
               BenchmarkArgs(['nph3.hmm', 'swiss41']),
               BenchmarkArgs(['--fixed', '0', '--mean', '500', '--num', '500000', '--sd', '350', '--seed', '0', 'retro.hmm']) 
            ],
            'sjeng' : [
               BenchmarkArgs(['ref.txt']) 
            ],
            'libquantum' : [
                BenchmarkArgs(['1397', '8'])
            ],
            'h264ref' : [
                BenchmarkArgs(['-d', 'foreman_ref_encoder_baseline.cfg']),
                BenchmarkArgs(['-d', 'foreman_ref_encoder_main.cfg']),
                BenchmarkArgs(['-d', 'sss_encoder_main.cfg']),
            ],
            'omnetpp' : [
                BenchmarkArgs(['omnetpp.ini'])
            ],
            'astar' : [
                BenchmarkArgs(['BigLakes2048.cfg']),
                BenchmarkArgs(['rivers.cfg']),
            ],
            'xalancbmk' : [
                BenchmarkArgs(['t5.xml', 'xalanc.xsl'])
            ]
        }

    def get_workload_spec(self, name: str, idx: int) -> (str, BenchmarkArgs):
        return (self.benchmark_exes[name], self.benchmarks[name][idx])

    def get_benchmark_names(self) -> List[str]:
       return self.benchmarks.keys() 
    
    def get_num_workloads(self) -> int:
        return sum([len(b) for b in self.benchmarks.values()])
