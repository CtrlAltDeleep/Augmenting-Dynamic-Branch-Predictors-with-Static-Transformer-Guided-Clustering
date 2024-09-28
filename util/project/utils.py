import pandas as pd
import numpy as np
import time

def load_data(path, nrows=None):

    def tick_loader(t):
        return int(t.strip()[:-1], 16)

    def hex_loader(t):
        return int(t, 16)

    def array_loader(t):
        t = t[1:-1]
        return t.split(',')
    
    def dict_loader(t):
        t = t[1:-1].split(',')
        t = [e.split('=') for e in t]
        return { e[0] : e[1] for e  in t }
    
    converters = {'tick' : tick_loader, 'inst_addr' : hex_loader, 
                  'pred_addr' : hex_loader, 'ras' : array_loader, 'regs' : dict_loader }

    t1 = time.time()
    df =  pd.read_csv(path, converters=converters, header=0, nrows = nrows)
    
    print(f'Loading the trace took {time.time() - t1} seconds')
    
    t1 = time.time()    
    # Post processing
    
    # absolute and relative RAS addresses
    ras = df['ras'].apply(lambda x : [int(e,16) for e in x[::2] if e != ''])
    rel_ras = df['ras'].apply(lambda x : np.array([str(e) for e in x[1::2]]))

    df['ras'] = ras
    df['ras_rel'] = rel_ras

    # parsing the regs as ints
    df['regs'] = df['regs'].apply(lambda x : { k : int(v,16) for k,v in x.items()})
    
    df['taken'] = (df['mispredicted'] & ~df['pred_taken']) | (~df['mispredicted'] & df['pred_taken'])
    
    print(f'Post processing took {time.time() - t1} seconds')
 
    return df
