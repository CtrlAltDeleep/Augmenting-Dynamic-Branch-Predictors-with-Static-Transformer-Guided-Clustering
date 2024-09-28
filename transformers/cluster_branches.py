import numpy as np
import polars as pl
import torch
from transformer import BranchPredDataset, TransformerModel
from transformer import SEQ_LEN, EMBED_DIM, NHEAD, NUM_ENC_LAYERS, NUM_DEC_LAYERS, DIM_FF, BRANCH_BITS
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import random
from sklearn.manifold import TSNE

if __name__ == '__main__': 

    device = torch.device('cpu')

    df_train = pl.scan_parquet(sys.argv[1])
    df_train = df_train.select([pl.col('inst_addr'), pl.col('taken').cast(pl.Int32)]).collect()
    
    df_test = pl.scan_parquet(sys.argv[2])
    df_test = df_test.select([pl.col('inst_addr'), pl.col('taken').cast(pl.Int32), pl.col('inst_rel_addr')]).collect()

    train_data = BranchPredDataset(df_train, SEQ_LEN, BRANCH_BITS)
    
    model = TransformerModel(train_data.num_unique_branches(), SEQ_LEN, EMBED_DIM, NHEAD, NUM_ENC_LAYERS, NUM_DEC_LAYERS, DIM_FF)
    model.load_state_dict(torch.load(sys.argv[3], map_location=torch.device('cpu')))
    model = model.to(device)

    with torch.no_grad():
        embeddings = model.src_embeddings(torch.arange(0, train_data.num_unique_branches(), device=device))
        in_proj_weight = model.state_dict()['transformer.encoder.layers.0.self_attn.in_proj_weight']
        in_proj_bias   = model.state_dict()['transformer.encoder.layers.0.self_attn.in_proj_bias']
   
        q, k, v = torch.nn.functional._in_projection_packed(embeddings, embeddings, embeddings, in_proj_weight, in_proj_bias)


    qk = (torch.nn.functional.softmax(q @ k.T, dim = 1)).cpu().numpy()

    X_embedded = TSNE().fit_transform(qk)
    
    plt.scatter(X_embedded[:,0], X_embedded[:,1])
    plt.show()

    
