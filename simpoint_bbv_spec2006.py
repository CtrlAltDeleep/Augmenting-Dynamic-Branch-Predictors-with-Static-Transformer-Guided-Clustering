#!/bin/env python
from configs.project.spec2006_workloads import Spec2006TrainBenchmarks, Spec2006TestBenchmarks, Spec2006RefBenchmarks 
import os
import sys
import time
import subprocess

# 10M instructions interval length
INTERVAL_LENGTH=10_000_000

GEM5_DIR='/home/as8319/gem5'
SPEC_BASE='/home/as8319/benchmarks/specCPU2006/benchspec/CPU2006'
VENV='/home/as8319/venv'
TYPE=sys.argv[1]
BASE_DIR=sys.argv[2]

USE_TMUX=False

if __name__ == '__main__':
    
    if TYPE == 'train':
        spec2006 = Spec2006TrainBenchmarks(SPEC_BASE)
    elif TYPE == 'test':
        spec2006 = Spec2006TestBenchmarks(SPEC_BASE)
    elif TYPE == 'ref':
        spec2006 = Spec2006RefBenchmarks(SPEC_BASE)

    print('Copying files...', flush=True)

    # setup dirs
    for bname in spec2006.benchmarks:
        os.mkdir(f'{BASE_DIR}/{bname}')
        exe = spec2006.benchmark_exes[bname]
        for i, (args, stdin) in enumerate(spec2006.benchmarks[bname]):
            run_path   = f'{BASE_DIR}/{bname}/{i}'
            bench_path = f'{spec2006.benchmark_dirs[bname]}/data/{TYPE}/input' 

            os.mkdir(run_path)
            os.system(f'cp -r {bench_path} {run_path}/input')

            # build run script
            with open(f'{run_path}/build_simpoint_bbvs.sh', 'w') as fd:
                fd.write(f"source {VENV}/bin/activate\n")
                fd.write(f'time {GEM5_DIR}/simpoint_program.sh {INTERVAL_LENGTH} {exe} \'{" ".join(args)}\' {run_path}/input')
                if stdin is not None:
                    fd.write(f' {stdin}')
                fd.write(f' > >(tee {run_path}/bbv_out.txt) 2> >(tee {run_path}/bbv_err.txt >&2)\n')

                if USE_TMUX:
                    fd.write('zsh\n')

