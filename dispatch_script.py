#!/bin/env python

import argparse
import subprocess
import glob
import os
import time

def parse_args():
    parser = argparse.ArgumentParser(prog='Dispatch Gem5 Workload Emulations',
                        description='Start processes for each workload in a benchmark suite')
    parser.add_argument(
        '--base-dir',
        type=str,
        required=True
    )

    parser.add_argument(
        '--script',
        type=str,
        required=True
    )
    
    parser.add_argument(
        '--use-tmux',
        default=False,
        action='store_true'
    )
    
    parser.add_argument(
        '--use-subprocs',
        default=False,
        action='store_true'
    )
    
    parser.add_argument(
        '--use-hpc-array',
        default=False,
        action='store_true'
    )
    
    parser.add_argument(
        '--idx',
        type=int,
        default=None
    )

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    scripts = sorted(glob.glob(f'{args.base_dir}/**/{args.script}', recursive=True))
    if args.use_tmux:
        print('Creating tmux sessions...', flush=True)
        # start gem5 processes:
        for script in scripts:
            i     = os.path.dirname(script)
            bname = os.path.dirname(i)
            i     = os.path.basename(i)
            bname = os.path.basename(bname)
            os.system(f'tmux new-session -d -s {bname}_{i} "bash {script}"')
    elif args.use_subprocs:
        print('Starting child processes...', flush=True)

        child_procs = []
        for script in scripts:
            i     = os.path.dirname(script)
            bname = os.path.dirname(i)
            i     = os.path.basename(i)
            bname = os.path.basename(bname)
            child_procs.append((subprocess.Popen(
                ['bash', script], 
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL), bname, i))
        
        print('Waiting for child processes to finish...', flush=True)

        polls = [p.poll() for p,_,_ in child_procs]

        while any([p is None for p in polls]):
            print('#########################################')
            for p, bname, i in child_procs:
                if p.poll() is None:
                    status_str = 'running'
                elif p.poll() == 0:
                    status_str = 'finished'
                else:
                    status_str = 'error'
                print(f'{bname}/{i}: {status_str}')
            print('', flush=True)
            # Sleep 5 mins
            time.sleep(60 * 5)

            polls = [p.poll() for p,_,_ in child_procs]

        print('Done building traces!', flush=True)
    elif args.use_hpc_array:
        subprocess.run(['bash', scripts[args.idx]])
    else:
        raise RuntimeError("Unsupported dispatch type")

