import os
import re
import pandas as pd

# Define the base directory
base_dir = "/home/ctrlaltdeleep/out_new_indexing"

# Initialize an empty DataFrame to store the results
results = []

# Iterate through each benchmark directory
for benchmark in os.listdir(base_dir):
    benchmark_dir = os.path.join(base_dir, benchmark)
    if os.path.isdir(benchmark_dir):
        # Iterate through each configuration directory
        for config in os.listdir(benchmark_dir):
            config_dir = os.path.join(benchmark_dir, config)
            if os.path.isdir(config_dir):
                # Iterate through each subtest directory
                for subtest in os.listdir(config_dir):
                    subtest_dir = os.path.join(config_dir, subtest)
                    if os.path.isdir(subtest_dir):
                        # Read the stats.txt file and extract all stats
                        stats_file = os.path.join(subtest_dir, "stats.txt")
                        if os.path.isfile(stats_file) and os.path.getsize(stats_file) > 0:
                            with open(stats_file, "r") as f:
                                stats_content = f.read()
                                # Define patterns to match
                                patterns = {
                                    "branch_mispredicts": r"system\.cpu\.commit\.branchMispredicts\s+(\d+)",
                                    "lookups": r"system\.cpu\.branchPred\.lookups\s+(\d+)",
                                    "local_used": r"system\.cpu\.branchPred\.localUsed\s+(\d+)",
                                    "global_uncoloured_used": r"system\.cpu\.branchPred\.globalUncolouredUsed\s+(\d+)",
                                    "global_uncoloured_used_on_coloured": r"system\.cpu\.branchPred\.globalUncolouredUsedOnColouredBranch\s+(\d+)",
                                    "global_coloured_used": r"system\.cpu\.branchPred\.globalColouredUsed\s+(\d+)"
                                }
                                extracted_values = {}
                                for key, pattern in patterns.items():
                                    match = re.search(pattern, stats_content)
                                    if match:
                                        extracted_values[key] = int(match.group(1))
                                # Check if all required values are extracted
                                if all(value is not None for value in extracted_values.values()):
                                    # Perform calculations and append the results to the list
                                    mispredicts = extracted_values["branch_mispredicts"]
                                    lookups = extracted_values["lookups"]
                                    result = (mispredicts / lookups) * 100
                                    results.append([benchmark, config, subtest, mispredicts, lookups, result,
                                                    extracted_values["local_used"], extracted_values["global_uncoloured_used"],
                                                    extracted_values["global_uncoloured_used_on_coloured"],
                                                    extracted_values["global_coloured_used"]])

# Create a DataFrame from the results list
results_df = pd.DataFrame(results, columns=["Benchmark", "Configuration", "Subtest", "Mispredicts", "Lookups", 
                                             "Result", "LocalUsed", "GlobalUncolouredUsed", 
                                             "GlobalUncolouredUsedOnColoured", "GlobalColouredUsed"])

# Write the DataFrame to a CSV file
results_df.to_csv("test_results.csv", index=False)

