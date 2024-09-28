#!/bin/bash

# Define gem5 paths and options
gem5_path="/home/ctrlaltdeleep/gem5/build/ARM/gem5.fast"
gem5_script="/home/ctrlaltdeleep/gem5/configs/example/se.py"
gem5_debug_flags="--debug-flags=Coloured,BranchTrace"
gem5_options="--cpu-type=DerivO3CPU --caches --l2cache --mem-size 20GB --restore-with-cpu=AtomicSimpleCPU"


# Define input directories
input_dirs=(
    "/home/ctrlaltdeleep/gem5/spec2006/benchspec/CPU2006/401.bzip2"
    "/home/ctrlaltdeleep/gem5/spec2006/benchspec/CPU2006/403.gcc"
    "/home/ctrlaltdeleep/gem5/spec2006/benchspec/CPU2006/445.gobmk"
    "/home/ctrlaltdeleep/gem5/spec2006/benchspec/CPU2006/456.hmmer"
    "/home/ctrlaltdeleep/gem5/spec2006/benchspec/CPU2006/458.sjeng"
    "/home/ctrlaltdeleep/gem5/spec2006/benchspec/CPU2006/464.h264ref"
    "/home/ctrlaltdeleep/gem5/spec2006/benchspec/CPU2006/471.omnetpp"
    "/home/ctrlaltdeleep/gem5/spec2006/benchspec/CPU2006/483.xalancbmk"
    "/home/ctrlaltdeleep/gem5/spec2006/benchspec/CPU2006/473.astar"
    "/home/ctrlaltdeleep/gem5/spec2006/benchspec/CPU2006/462.libquantum"
    "/home/ctrlaltdeleep/gem5/spec2006/benchspec/CPU2006/429.mcf"
)

output_base="/home/ctrlaltdeleep/out_new_indexing/"
output_base_small="/home/ctrlaltdeleep/out_new_indexing_small_transformer_window/"

# Array of values for colourBits
colour_values=(0 2)
# Array of values for localColourBits
local_colour_values=(0 1)

# Get the number of CPUs available
num_cpus=$(($(nproc) - 5))

index=0
# Iterate through gem5 benchmark result directories
for benchmark_dir in /home/ctrlaltdeleep/gem5/results_*; do
    # Extract benchmark name from directory
    benchmark_name=$(basename "$benchmark_dir" | sed -E 's/.*_([^_]+)$/\1/') 

    if [[ "$n" -eq 0 && "$benchmark_dir" == *"small"* ]]; then
        continue
    fi

    # Update source code file with benchmark-specific path
    sed -i "s|readFileContents(\"/home/ctrlaltdeleep/gem5/.*/clusters.txt\");|readFileContents(\"$benchmark_dir/clusters.txt\");|g" /home/ctrlaltdeleep/gem5/src/cpu/pred/colour_tournament.cc
    sed -i "s|readFileContents(\"/home/ctrlaltdeleep/gem5/.*/takeness_based_clusters.txt\");|readFileContents(\"$benchmark_dir/takeness_based_clusters.txt\");|g" /home/ctrlaltdeleep/gem5/src/cpu/pred/colour_tournament.cc

    # Loop through each value for colourBits
    for n in "${colour_values[@]}"; do
        # Loop through each value for localColourBits
        for m in "${local_colour_values[@]}"; do
            # Rewrite the Python file with new bp colour parameters
            sed -i "s/colourBits = Param.Unsigned([0-9]*, \"Bits for colour information\")/colourBits = Param.Unsigned(${n}, \"Bits for colour information\")/g" /home/ctrlaltdeleep/gem5/src/cpu/pred/BranchPredictor.py
            sed -i "s/localColourBits = Param.Unsigned([0-9]*, \"Bits for local colour information\")/localColourBits = Param.Unsigned(${m}, \"Bits for local colour information\")/g" /home/ctrlaltdeleep/gem5/src/cpu/pred/BranchPredictor.py

            # Build gem5
            cd /home/ctrlaltdeleep/gem5/
            scons -j"${num_cpus}" build/ARM/gem5.fast

            input_dir=""
            for dir in "${input_dirs[@]}"; do
                if [[ "$dir" == *"$benchmark_name"* ]]; then
                    input_dir="$dir"
                    break
                fi
            done

            # Get benchmark-specific options and test files
            options_files=("${benchmark_args[$benchmark_name]}")

            # Change to the input directory
            cd "${input_dir}/data/test/input/"

            # Get benchmark-specific options and test files
            case $benchmark_name in
                'bzip2')
                    options=("input.program 5" "dryer.jpg 2")
                    test_files=("")
                    ;;
                'gcc')
                    options=("cccp.i -o cccp.s")
                    test_files=("")
                    ;;
                'mcf')
                    options=("inp.in")
                    test_files=("")
                    ;;
                'gobmk')
                    options=("--quiet --mode gtp")
                    test_files=("cutstone.tst" "dniwog.tst" "capture.tst" "connection_rot.tst" "connect_rot.tst" "connect.tst" "connection.tst")
                    ;;
                'hmmer')
                    options=("--fixed 0 --mean 325 --num 45000 --sd 200 --seed 0 bombesin.hmm")
                    test_files=("")
                    ;;
                'sjeng')
                    options=("test.txt")
                    test_files=("")
                    ;;
                'libquantum')
                    options=("33 5")
                    test_files=("")
                    ;;
                'h264ref')
                    options=("-d foreman_test_encoder_baseline.cfg")
                    test_files=("")
                    ;;
                'omnetpp')
                    options=("omnetpp.ini")
                    test_files=("")
                    ;;
                'astar')
                    options=("lake.cfg")
                    test_files=("")
                    ;;
                'xalancbmk')
                    options=("test.xml xalanc.xsl")
                    test_files=("")
                    ;;
                'perlbench')
                    options=(
                        " -I. -I./lib array.t"
                        " -I. -I./lib exists_sub.t"
                        " -I. -I./lib do.t"
                        " -I. -I./lib ord.t"
                        " -I. -I./lib cmp.t"
                        " -I. -I./lib redef.pl"
                        " -I. -I./lib study.t"
                        " -I. -I./lib loopctl.t"
                        " -I. -I./lib args.t"
                        " -I. -I./lib my.t"
                        " -I. -I./lib concat.t"
                        " -I. -I./lib bop.t"
                        " -I. -I./lib join.t"
                        " -I. -I./lib rs.t"
                        " -I. -I./lib delete.t"
                        " -I. -I./lib attrs.pl"
                        " -I. -I./lib defins.t"
                        " -I. -I./lib pack.pl"
                        " -I. -I./lib int.t"
                        " -I. -I./lib sleep.t"
                        " -I. -I./lib wantarray.t"
                        " -I. -I./lib bless.t"
                        " -I. -I./lib index.t"
                        " -I. -I./lib range.t"
                        " -I. -I./lib auto.t"
                        " -I. -I./lib comp_term.t"
                        " -I. -I./lib die.t"
                        " -I. -I./lib base_term.t"
                        " -I. -I./lib lex.t"
                        " -I. -I./lib tr.t"
                        " -I. -I./lib exp.t"
                        " -I. -I./lib push.t"
                        " -I. -I./lib sub_lval.t"
                        " -I. -I./lib chars.t"
                        " -I. -I./lib undef.t"
                        " -I. -I./lib eval.t"
                        " -I. -I./lib test.pl"
                        " -I. -I./lib regexp_noamp.t"
                        " -I. -I./lib regexp.t"
                        " -I. -I./lib cmdopt.t"
                        " -I. -I./lib makerand.pl"
                        " -I. -I./lib vec.t"
                        " -I. -I./lib splice.t"
                        " -I. -I./lib fh.t"
                        " -I. -I./lib bproto.t"
                        " -I. -I./lib decl.t"
                        " -I. -I./lib base_pat.t"
                        " -I. -I./lib subst_amp.t"
                        " -I. -I./lib ref.pl"
                        " -I. -I./lib if.t"
                        " -I. -I./lib chop.t"
                        " -I. -I./lib oct.t"
                        " -I. -I./lib op_cond.t"
                        " -I. -I./lib base_cond.t"
                        " -I. -I./lib lop.t"
                        " -I. -I./lib method.t"
                        " -I. -I./lib unshift.t"
                        " -I. -I./lib append.t"
                        " -I. -I./lib hashwarn.t"
                        " -I. -I./lib package.t"
                        " -I. -I./lib gv.pl"
                        " -I. -I./lib repeat.t"
                        " -I. -I./lib reverse.t"
                        " -I. -I./lib each.t"
                        " -I. -I./lib quotemeta.t"
                        " -I. -I./lib grep.t"
                        " -I. -I./lib inc.t"
                        " -I. -I./lib subst.t"
                        " -I. -I./lib sort.t"
                        " -I. -I./lib subst_wamp.t"
                        " -I. -I./lib context.t"
                        " -I. -I./lib pos.t"
                        " -I. -I./lib length.t"
                        " -I. -I./lib nothr5005.t"
                        " -I. -I./lib op_pat.t"
                        " -I. -I./lib regmesg.pl"
                        " -I. -I./lib recurse.t"
                        " -I. -I./lib override.t"
                        " -I. -I./lib list.t"
                        " -I. -I./lib arith.t"
                    )
                    test_files=("")
                    ;;
                *)
                    echo "Unknown benchmark: $benchmark_name"
                    ;;
            esac

            options_index=0
            # Loop over all test files in the input directory
            for options in "${options[@]}"; do
                for test_file in "${test_files[@]}"; do
                    if [[ "$test_file" == *.tst ]]; then
                        filename=$(basename "$test_file" .tst) # Extract filename without extension
                    else
                        filename=$(basename "$test_file")
                    fi

                    # Calculate the output directory name
                    if [[ $benchmark_dir == *"small"* ]]; then
                        output_base_used="$output_base_small"
                    else
                        output_base_used="$output_base"
                    fi

                    output_dir="${output_base_used}${benchmark_name}/${n}BitsGlobal_${m}BitsLocal/m5out_${options_index}_${filename}"

                    mkdir -p "${output_dir}"
                    
                    if [[ "$test_file" == *.tst ]]; then
                        # Run gem5 simulation in the background with a different output directory for each file
                        taskset -c $((index % num_cpus)) "${gem5_path}" -d "${output_dir}" \
                        "${gem5_script}" ${gem5_options} --cmd="${input_dir}/${benchmark_name}" -o "${options}" -i "${test_file}" > "${output_dir}/out.txt" &
                    else
                        # Run gem5 simulation in the background with a different output directory for each file
                        taskset -c $((index % num_cpus)) "${gem5_path}" -d "${output_dir}" \
                        "${gem5_script}" ${gem5_options} --cmd="${input_dir}/${benchmark_name}" -o "${options}" > "${output_dir}/out.txt" &
                    fi
                    
                    threshold=$((num_cpus * 2))

                    if [ $index -ge $threshold ]; then
                        sleep 0h
                        index=0
                    fi

                    # Increment index for the next CPU
                    index=$((index + 1))

                    options_index=$((options_index + 1))
                done
            done
        done
    done
done

# Wait for all background processes to finish
wait