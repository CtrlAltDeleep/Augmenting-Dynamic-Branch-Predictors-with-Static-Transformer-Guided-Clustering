import sys

import numpy as np
import pandas as pd
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

import matplotlib.pyplot as plt
import seaborn as sns

import utils


num_to_keep = 10

def list_to_embed(l):
    l = list(l)
    if len(l) < 5:
        l = (5 - len(l))*[0] + l
    l = np.array(l, dtype=np.uint64).reshape(-1, 1)
    masks = 2**np.arange(64, dtype=np.uint64)
    return np.concatenate(l & masks != 0) + 0    

df = utils.load_data(sys.argv[1])

# Only taken but mispredicted branches
df = df[(df['mispredicted'] == 1) & (df['pred_taken'] == 0)]

# Count all occurences
occurences = df.groupby('inst_rel_addr').size().sort_values().reset_index(name = 'aa')

# Print occurences of best samples
print(occurences[-num_to_keep:])

# Filter only best num_to_keep branches
df = df[df['inst_rel_addr'].isin(occurences[-num_to_keep:]['inst_rel_addr'])]

# embed register state
#df['state'] = df['regs'].apply(lambda x : list_to_embed(list(x.values())))
df['state'] = df['ras'].apply(lambda x : list_to_embed(x))

states = np.array([e for e in df['state']])

print(states.shape)

#pca = PCA(500)
#
#states = pca.fit_transform(states)

tsne = TSNE(verbose = 1, n_jobs=20, metric = 'cityblock')

embeddings = tsne.fit_transform(states)

#plt.scatter(embeddings[:,0], embeddings[:,1], label = df['inst_rel_addr'].to_numpy())
#plt.show()

df2 = pd.DataFrame({'x' : embeddings[:,0], 'y' : embeddings[:, 1], 'name' : df['inst_rel_addr'].to_numpy()})
sns.scatterplot(df2, x='x',y='y',hue='name', legend=False)
plt.show()
