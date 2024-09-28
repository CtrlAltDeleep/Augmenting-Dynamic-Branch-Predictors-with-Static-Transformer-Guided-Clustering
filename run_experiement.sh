#!/bin/bash

GEM5_BASE="/home/ctrlaltdeleep/gem5" 

FIFO_NAME=".fifo_${RANDOM}"
while [ -f ${GEM5_BASE}/m5out/${FIFO_NAME} ]; do
FIFO_NAME=".fifo_${RANDOM}"
done


echo "Using FIFO ${FIFO_NAME}"

mkfifo "${GEM5_BASE}/m5out/${FIFO_NAME}"

trap 'echo "SIGINT received, cleaning up!"; rm -f "${GEM5_BASE}/m5out/${FIFO_NAME}" "${GEM5_BASE}/m5out/$2"' INT

if [[ $4 ]]; then
    echo "Changing to directory '$4'!"
    cd $4
fi

if [ -z "$3" ]; then
    ${GEM5_BASE}/build/ARM/gem5.opt --debug-flags=BranchTrace --debug-start=0 --debug-file=${FIFO_NAME} -d ${GEM5_BASE}/m5out ${GEM5_BASE}/configs/project/arm.py --exp $1 &
else
    ${GEM5_BASE}/build/ARM/gem5.opt --debug-flags=BranchTrace --debug-start=0 --debug-file=${FIFO_NAME} -d ${GEM5_BASE}/m5out ${GEM5_BASE}/configs/project/arm.py --exp $1 < $3 &
fi

${GEM5_BASE}/util/project/convert_parquet.py "${GEM5_BASE}/m5out/${FIFO_NAME}" "${GEM5_BASE}/m5out/$2" <&-

rm -f "${GEM5_BASE}/m5out/${FIFO_NAME}"

