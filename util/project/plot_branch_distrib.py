import numpy as np
import matplotlib.pyplot as plt
import utils
import sys
import seaborn as sns

df = utils.load_data(sys.argv[1], 100)

mispred_rate = df.groupby('inst_rel_addr')['mispredicted'].mean().reset_index(name='mispredict rate').sort_values('mispredict rate')

sns.barplot(x="mispredict rate", y="inst_rel_addr", data=mispred_rate)

plt.show()
