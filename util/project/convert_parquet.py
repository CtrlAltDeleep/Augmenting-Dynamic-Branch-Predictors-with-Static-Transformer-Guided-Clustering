#!/bin/env python

import sys
import os
import time
import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import csv
    
def tick_loader(t):
    return int(t.strip()[:-1])

def hex_loader(t):
    return int(t, 16) if t else None

def array_loader(t):
    return t[1:-1].split(',')

def dict_loader(t):
    t = t[1:-1].split(',')
    t = [e.split('=') for e in t]
    return { e[0] : e[1] for e  in t }

converters = {'tick' : tick_loader, 'inst_addr' : hex_loader, 
              'pred_addr' : hex_loader, 'jump_addr' : hex_loader, 'ras' : array_loader, 'regs' : dict_loader, 'alloc_context' : hex_loader }

dtypes = {'mispredicted' : bool, 'pred_taken' : bool, 'virtual' : bool, 'return' : bool, 'call' : bool}

# aarc64 registers
regs =['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r12', 'sp', 'fp', 'lr']

parquet_schema = pa.schema([
    ('tick', pa.uint64(), False),
    ('disassembly', pa.string(), False),
    ('inst_addr', pa.uint64(), False),
    ('inst_rel_addr', pa.string(), False),
    ('pred_addr', pa.uint64(), False),
    ('pred_rel_addr', pa.string(), False),
    ('jump_addr', pa.uint64(), False),
    ('jump_rel_addr', pa.string(), False),
    ('pred_taken', pa.bool_(), False),
    ('mispredicted', pa.bool_(), False),
    ('ras', pa.list_(pa.uint64()), False),
    ('regs', pa.struct([pa.field(r, pa.uint64()) for r in regs]), False),
    ('virtual', pa.bool_(), False),
    ('return', pa.bool_(), False),
    ('call', pa.bool_(), False),
    ('taken', pa.bool_(), False),
    ('ras_rel', pa.list_(pa.string()), False),
    ('alloc_context', pa.uint64(), True)
])

def convert_to_parquet(inputfile, outputfile=None, chunksize=1000000, memory_map=True, verbose=False): 
 
    if outputfile is None:
        outputfile = os.path.splitext(inputfile)[0]+'.parquet'
    
    chunks = pd.read_csv(inputfile, converters=converters, header=0, chunksize=chunksize, dtype=dtypes, memory_map=memory_map) 
    
    parquet_writer = pq.ParquetWriter(outputfile, parquet_schema)

    for i, chunk in enumerate(chunks):
   
        t1 = time.time()
        # Post process chunk 
        ras = chunk['ras'].apply(lambda x : np.array([np.uint64(int(e,16)) for e in x[::2] if e != '']))
        rel_ras = chunk['ras'].apply(lambda x : [str(e) for e in x[1::2]])
    
        chunk['ras'] = ras
        chunk['ras_rel'] = rel_ras

        # parsing the regs as ints
        chunk['regs'] = chunk['regs'].apply(lambda x : { k : np.uint64(int(v,16)) for k,v in x.items()})
        
        chunk['taken'] = (chunk['mispredicted'] & ~chunk['pred_taken']) | (~chunk['mispredicted'] & chunk['pred_taken'])

        # Save parquet
        # Write CSV chunk to the parquet file
        table = pa.Table.from_pandas(chunk, schema=parquet_schema)
        parquet_writer.write_table(table)        
        
        if verbose:
            print(f'Chunk {i}: {chunksize / (time.time() - t1):.2f} rows/s')
    
    parquet_writer.close()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.stdin.isatty():
            convert_to_parquet(sys.argv[1], memory_map='fifo' not in sys.argv[1])
        else:
            convert_to_parquet(sys.stdin, sys.argv[1], memory_map=False)
    elif len(sys.argv) == 3:
        convert_to_parquet(sys.argv[1], sys.argv[2], memory_map='fifo' not in sys.argv[1])
    else:
        raise RuntimeError('2 or 3 arguments required')
