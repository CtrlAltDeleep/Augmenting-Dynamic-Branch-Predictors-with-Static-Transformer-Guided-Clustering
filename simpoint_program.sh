#!/bin/bash

GEM5_BASE="/home/as8319/gem5" 

if [[ $4 ]]; then
    echo "Changing to directory '$4'!"
    cd $4
fi

if [[ $5 ]]; then
    ${GEM5_BASE}/build/ARM/gem5.fast ${GEM5_BASE}/configs/example/se.py --simpoint-profile --simpoint-interval $1 --cpu-type=ArmNonCachingSimpleCPU --cmd=$2 -o="$3" --mem-size 8GB --restore-with-cpu=ArmNonCachingSimpleCPU -i $5
else
    ${GEM5_BASE}/build/ARM/gem5.fast ${GEM5_BASE}/configs/example/se.py --simpoint-profile --simpoint-interval $1 --cpu-type=ArmNonCachingSimpleCPU --cmd=$2 -o="$3" --mem-size 8GB --restore-with-cpu=ArmNonCachingSimpleCPU
fi

