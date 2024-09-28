#!/bin/bash

# Iterate through directories in the train folder
for benchmark_dir in /rds/general/user/ad2820/home/meng_project_misc/transformer/spec2006/train/*/; do
    # Extract benchmark name from directory path
    benchmark=$(basename "$benchmark_dir")

    # Generate script for each benchmark
    script_name="job_${benchmark}_small_seq.sh"
    echo "#!/bin/bash" > "$script_name"
    echo "#PBS -l select=1:ncpus=6:mem=100gb:ngpus=1:gpu_type=RTX6000" >> "$script_name"
    echo "#PBS -l walltime=72:00:00" >> "$script_name"
    echo "#PBS -N ${benchmark}_small_seq" >> "$script_name"
    echo "" >> "$script_name"
    echo "cd \$PBS_O_WORKDIR" >> "$script_name"
    echo "" >> "$script_name"
    echo "module load anaconda3/personal" >> "$script_name"
    echo "source activate pytorch_env" >> "$script_name"
    echo "" >> "$script_name"
    echo "python3 -c \"import torch;print(torch.cuda.is_available())\"" >> "$script_name"
    echo "python3 transformer_small_seq.py /rds/general/user/ad2820/home/meng_project_misc/transformer/spec2006/train/${benchmark} /rds/general/user/ad2820/home/meng_project_misc/transformer/spec2006/test/${benchmark} 3" >> "$script_name"
    
    # Make the script executable
    chmod +x "$script_name"
done

