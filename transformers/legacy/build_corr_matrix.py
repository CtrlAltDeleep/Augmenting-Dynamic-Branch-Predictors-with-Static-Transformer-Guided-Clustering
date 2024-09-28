from transformer import BranchPredDataset, TransformerModel, build_targets
from transformer import SEQ_LEN, EMBED_DIM, NHEAD, NUM_ENC_LAYERS, NUM_DEC_LAYERS, DIM_FF, BRANCH_BITS
import torch
import polars as pl
import numpy as np
from tqdm import trange
import sys
import math
import matplotlib.pyplot as plt
import seaborn as sns

BATCH_SIZE = 32
SET_SIZE = 10

if __name__ == '__main__': 
    if torch.cuda.is_available():
        device = torch.device('cuda')
    elif torch.backends.mps.is_available():
        device = torch.device('mps')
    else:
        device = torch.device('cpu')
    print(f'Using device: {device}')

    # Load data
    df_train = pl.scan_parquet(sys.argv[1])
    df_train = df_train.select([pl.col('inst_addr'), pl.col('taken').cast(pl.Int32)]).collect()

    train_data = BranchPredDataset(df_train, SEQ_LEN, BRANCH_BITS)

    # Load model
    model = TransformerModel(train_data.num_unique_branches(), SEQ_LEN, EMBED_DIM, NHEAD, NUM_ENC_LAYERS, NUM_DEC_LAYERS, DIM_FF)
    model.load_state_dict(torch.load(sys.argv[2]))
    model = model.to(device)
    model.eval()

    # Setup test data
    inst_addrs = np.array(df_train['inst_addr'])

    if BRANCH_BITS is not None:
        inst_addrs = np.bitwise_and(inst_addrs, (1 << BRANCH_BITS) - 1).astype(np.int32)

    branch_idxs = np.array([train_data.branch2idx[b] for b in inst_addrs])
 
    branch_correlations = np.zeros((len(train_data.branch2idx), len(train_data.branch2idx)), dtype=np.uint32)

    with trange(SEQ_LEN, len(inst_addrs), BATCH_SIZE) as test_iter, torch.no_grad():

        for i in test_iter:
            start_idx = i
            end_idx   = min(len(inst_addrs), i+BATCH_SIZE)

            # each entry in a batch contains SEQ_LEN branches: j+1-SEQ_LEN, j+2-SEQ_LEN,...,j
            # these are indexes in the branch trace
            idxs = np.array([np.arange(j+1-SEQ_LEN,j+1) for j in range(start_idx, end_idx)])
            # index into the trace to get the branch indexes i.e. the branch ids
            batch_branches = torch.tensor(branch_idxs[idxs], dtype=torch.int32, device=device)
            
            # compute attention weigths for every sequence
            attention_weights = model.compute_src_attention(batch_branches)

            # only keep attention weights for the last  branch
            attention_weights = attention_weights[:, -1, :]
            # sort weights and keep the highest ones
            sort_idxs = torch.argsort(attention_weights, dim=1, descending=True)
            correlated_branch_idx = sort_idxs[:, :SET_SIZE].cpu().numpy()

            # get the indexes of the branches with the highest correlation
            correlations = np.take_along_axis(branch_idxs[idxs], correlated_branch_idx, axis=1)

            # increment correlation counters
            for j, corr in enumerate(correlations):
                b_idx = i + j
                branch_correlations[branch_idxs[b_idx], corr] += 1

    np.save(sys.argv[3], branch_correlations, False)

