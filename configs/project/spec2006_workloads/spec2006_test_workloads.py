from dataclasses import dataclass
from typing import List, Optional
from .workload_util import BenchmarkArgs, BenchmarkSuite

class Spec2006TestBenchmarks(BenchmarkSuite):

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
                BenchmarkArgs(['-I.', '-I./lib', 'array.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'exists_sub.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'do.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'ord.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'cmp.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'redef.pl']),
                BenchmarkArgs(['-I.', '-I./lib', 'study.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'loopctl.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'args.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'my.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'concat.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'bop.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'join.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'rs.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'delete.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'attrs.pl']),
                BenchmarkArgs(['-I.', '-I./lib', 'defins.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'pack.pl']),
                BenchmarkArgs(['-I.', '-I./lib', 'int.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'sleep.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'wantarray.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'bless.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'index.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'range.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'auto.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'comp_term.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'die.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'base_term.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'lex.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'tr.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'exp.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'push.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'sub_lval.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'chars.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'undef.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'eval.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'test.pl']),
                BenchmarkArgs(['-I.', '-I./lib', 'regexp_noamp.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'regexp.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'cmdopt.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'makerand.pl']),
                BenchmarkArgs(['-I.', '-I./lib', 'vec.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'splice.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'fh.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'bproto.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'decl.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'base_pat.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'subst_amp.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'ref.pl']),
                BenchmarkArgs(['-I.', '-I./lib', 'if.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'chop.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'oct.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'op_cond.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'base_cond.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'lop.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'method.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'unshift.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'append.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'hashwarn.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'package.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'gv.pl']),
                BenchmarkArgs(['-I.', '-I./lib', 'repeat.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'reverse.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'each.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'quotemeta.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'grep.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'inc.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'subst.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'sort.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'subst_wamp.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'context.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'pos.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'length.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'nothr5005.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'op_pat.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'regmesg.pl']),
                BenchmarkArgs(['-I.', '-I./lib', 'recurse.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'override.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'list.t']),
                BenchmarkArgs(['-I.', '-I./lib', 'arith.t']),
            ],
            'bzip2' : [
                BenchmarkArgs(['input.program', '5']),
                BenchmarkArgs(['dryer.jpg', '2']),
            ],
            'gcc' : [
                BenchmarkArgs(['cccp.i', '-o', 'cccp.s'])
            ],
            'mcf' : [
                BenchmarkArgs(['inp.in'])
            ],
            'gobmk' : [
                BenchmarkArgs(['--quiet' , '--mode' , 'gtp'], 'cutstone.tst'),
                BenchmarkArgs(['--quiet' , '--mode' , 'gtp'], 'dniwog.tst'),
                BenchmarkArgs(['--quiet' , '--mode' , 'gtp'], 'capture.tst'),
                BenchmarkArgs(['--quiet' , '--mode' , 'gtp'], 'connection_rot.tst'),
                BenchmarkArgs(['--quiet' , '--mode' , 'gtp'], 'connect_rot.tst'),
                BenchmarkArgs(['--quiet' , '--mode' , 'gtp'], 'connect.tst'),
                BenchmarkArgs(['--quiet' , '--mode' , 'gtp'], 'connection.tst'),
            ],
            'hmmer' : [
               BenchmarkArgs(["--fixed", "0", "--mean", "325", "--num", "45000", "--sd", "200", "--seed", "0", "bombesin.hmm"]) 
            ],
            'sjeng' : [
               BenchmarkArgs(['test.txt']) 
            ],
            'libquantum' : [
                BenchmarkArgs(['33', '5'])
            ],
            'h264ref' : [
                BenchmarkArgs(['-d', 'foreman_test_encoder_baseline.cfg'])
            ],
            'omnetpp' : [
                BenchmarkArgs(['omnetpp.ini'])
            ],
            'astar' : [
                BenchmarkArgs(['lake.cfg']),
            ],
            'xalancbmk' : [
                BenchmarkArgs(['test.xml', 'xalanc.xsl'])
            ]
        }

    def get_workload_spec(self, name: str, idx: int) -> (str, BenchmarkArgs):
        return (self.benchmark_exes[name], self.benchmarks[name][idx])

    def get_benchmark_names(self) -> List[str]:
       return self.benchmarks.keys() 
    
    def get_num_workloads(self) -> int:
        return sum([len(b) for b in self.benchmarks.values()])
