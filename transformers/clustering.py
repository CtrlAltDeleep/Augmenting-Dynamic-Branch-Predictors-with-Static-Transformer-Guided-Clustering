import sys

import networkx as nx
import pickle
import igraph as ig

#from transformer import BranchPredDataset, SEQ_LEN, BRANCH_BITS


def remap_and_log_clusters(clusters, idx2unmaskedbranch, end_branch=None, save_path=None):
    cluster_map = {}  # Dictionary to store mapping between address and cluster numbers
    # Build the cluster map
    for cluster_number, cluster in enumerate(clusters):
        for branch_number in cluster:
            try:
                if idx2unmaskedbranch[branch_number] in cluster_map:
                    print("OVERWRITE CLASH ", idx2unmaskedbranch[branch_number])
                    print(cluster_number)
                cluster_map[idx2unmaskedbranch[branch_number]] = cluster_number
            except Exception as e:
                print("dunno abt idx ", branch_number)
    cluster_map = dict(sorted(cluster_map.items()))
    print(cluster_map)

    cluster_numbers = list(set(cluster_map.values()))

    # Generate color map
    """
        Generate a color map for each unique cluster number.
        """
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'yellow', 'cyan', 'magenta']
    color_map = {}
    for i, cluster_num in enumerate(cluster_numbers):
        color_map[cluster_num] = colors[i % len(colors)]

    """
       Write data to a text file in the specified format.
       """
    with open(save_path, 'w') as f:
        f.write("instruction address\t\tdisassembly\t\tcluster colour\t\tcluster number\n")
        for (address, instruction), cluster_num in cluster_map.items():
            f.write(f"{address}\t\t{instruction}\t\t{color_map[cluster_num]}\t\t{cluster_num}\n")

    return cluster_map


def community_detection_cluster_branches_SLOW(attention_matrix, num_clusters, hard_cluster_number=False):
    # Convert attention matrix to graph
    G = nx.Graph()
    for i in range(len(attention_matrix)):
        for j in range(i + 1, len(attention_matrix)):
            weight = max(attention_matrix[j, i], attention_matrix[i, j])
            if weight > 0:  # add only non-0 edges
                G.add_edge(j, i, weight=weight)

    """
    # Draw the graph
    pos = nx.spring_layout(G, k=100)  # Adjust the 'k' parameter for larger spacing
    nx.draw(G, pos, with_labels=True, node_size=300, font_size=10)  # Decrease node size and font size
    plt.title("Sample NetworkX Graph with Many Nodes")
    plt.show()

    
    # Remove edges with lowest attention until N distinct clusters are obtained
    while nx.number_connected_components(G) < num_clusters:
        min_edge = min(G.edges(data=True), key=lambda x: x[2]['weight'])
        print(min_edge)
        G.remove_edge(*min_edge[:2])
    """
    cluster_cutoff = num_clusters if hard_cluster_number else 1
    clusters = nx.community.greedy_modularity_communities(G, resolution=1, weight='weight', cutoff=cluster_cutoff,
                                                          best_n=num_clusters)

    clusters = list(set(cluster) for cluster in clusters)

    print(clusters)
    return clusters


def fix_dendrogram(graph, cl):
    already_merged = set()
    for merge in cl.merges:
        already_merged.update(merge)

    num_dendrogram_nodes = graph.vcount() + len(cl.merges)
    not_merged_yet = sorted(set(range(num_dendrogram_nodes)) - already_merged)
    if len(not_merged_yet) < 2:
        return

    v1, v2 = not_merged_yet[:2]
    cl._merges.append((v1, v2))
    del not_merged_yet[:2]

    missing_nodes = range(num_dendrogram_nodes,
            num_dendrogram_nodes + len(not_merged_yet))
    cl._merges.extend(zip(not_merged_yet, missing_nodes))
    cl._nmerges = graph.vcount()-1


def community_detection_cluster_branches(attention_matrix, num_clusters, hard_cluster_number=False):
    # Convert attention matrix to graph
    G = ig.Graph.Weighted_Adjacency(attention_matrix, mode=ig.ADJ_MAX)

    # Perform community detection using fast greedy algorithm
    partition = G.community_fastgreedy(weights='weight')
    fix_dendrogram(G, partition) # inplace mutation

    # Extract the community structure
    if hard_cluster_number:
        partition = partition.as_clustering(n=num_clusters)
    else:
        partition = partition.as_clustering()

    # Convert clusters into a tuple of sets
    clusters = tuple(map(set, partition))

    return clusters

if __name__ == '__main__':
    with open('results/global_attention.pkl', 'rb') as f:
        global_attention = pickle.load(f)

    clusters = community_detection_cluster_branches(global_attention, 3, hard_cluster_number=True)
    print(clusters)

    train_data = BranchPredDataset("/Users/avaneesh/Desktop/meng_project_misc/transformer/spec2006/train/gobmk", SEQ_LEN, BRANCH_BITS, True)
    test_data = BranchPredDataset("/Users/avaneesh/Desktop/meng_project_misc/transformer/spec2006/test/gobmk", SEQ_LEN, BRANCH_BITS, train_data.idx2branch, train_data.branch2idx, train_data.branch2unmaskedmapping)

    clusters = remap_and_log_clusters(clusters, test_data.idx2umaskedbranchaddress, save_path='clusters.txt')
