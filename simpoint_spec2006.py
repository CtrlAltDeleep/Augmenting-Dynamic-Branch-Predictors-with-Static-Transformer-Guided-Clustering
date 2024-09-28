#!/bin/env python
from configs.project.spec2006_workloads import Spec2006TrainBenchmarks, Spec2006TestBenchmarks, Spec2006RefBenchmarks 
import os
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor

# 10M instructions interval length
INTERVAL_LENGTH=10_000_000
SIMPOINT='/home/as8319/simpoints/SimPoint.3.2/bin/simpoint'
MAXK=30
NPROCS=1

SPEC_BASE=/home/as8319/benchmarks/specCPU2006/benchspec/CPU2006/
TYPE=sys.argv[1]
BASE_DIR=sys.argv[2]

def run_simpoint(bname, i):
    print(f'Running {bname}/{i}...')
    base_path = f'{BASE_DIR}/{bname}/{i}'

    with open(f'{base_path}/simpoint_out.txt', 'w') as out_file:
        proc_res = subprocess.run(['zsh', f'{base_path}/build_simpoints.sh'], stdout=out_file, stderr=out_file)

    if proc_res.returncode == 0:
        print(f'{bname}/{i} was successful!')
    else:
        print(f'{bname}/{i} failed!')

if __name__ == '__main__':

    if TYPE == 'train':
        spec2006 = Spec2006TrainBenchmarks(SPEC_BASE)
    elif TYPE == 'test':
        spec2006 = Spec2006TestBenchmarks(SPEC_BASE)
    elif TYPE == 'ref':
        spec2006 = Spec2006RefBenchmarks(SPEC_BASE)
 
    print('Building run scripts')
    # setup scriptsi
    for bname in spec2006.benchmarks:
        exe = spec2006.benchmark_exes[bname]
        for i, (args, stdin) in enumerate(spec2006.benchmarks[bname]):
            run_path   = f'{BASE_DIR}/{bname}/{i}'

            # build simpoint script
            with open(f'{run_path}/build_simpoints.sh', 'w') as fd:
                fd.write(f'cd {run_path}/input/m5out\n')
                fd.write(f'time {SIMPOINT} -loadFVFile simpoint.bb.gz -maxK {MAXK} -saveSimpoints simpoints.txt -saveSimpointWeights simpoint_weights.txt -inputVectorsGzipped\n')

    # start gem5 processes:
    with ThreadPoolExecutor(max_workers=NPROCS) as pool:
        futures = []
        for bname in spec2006.benchmarks:
            for i, (args, stdin) in enumerate(spec2006.benchmarks[bname]):
                f = pool.submit(run_simpoint, bname, i)
                futures.append(f)

