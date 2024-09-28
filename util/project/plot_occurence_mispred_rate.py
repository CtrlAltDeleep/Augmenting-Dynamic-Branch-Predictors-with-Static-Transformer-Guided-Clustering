import pandas as pd
import altair as alt
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import utils

df = utils.load_data(sys.argv[1])

mispred_rate = df.groupby('inst_rel_addr')['mispredicted'].mean().reset_index(name='misprediction rate')
counts       = df.groupby('inst_rel_addr').size().map(lambda x : np.log10(x)).reset_index(name='occurences')
mr_counts = mispred_rate.merge(counts, on='inst_rel_addr')

sns.scatterplot(data = mr_counts, y = 'occurences', x = 'misprediction rate')
plt.show()

