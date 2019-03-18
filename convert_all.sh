#!/bin/bash

FILE_NUM_PER_FOLDER=10000
CSV_FILE_PATH='DiF/DiF_v1.csv'
FULL_IMAGE_PATH='DiF/images'
LINE_NUM=`wc -l ${CSV_FILE_PATH} | awk '{print $1}'`


SUBSET_NAME(){
    printf "%05d" $1
}


SUBSET_ID_COUNTER=1
LINE_NUM_COUNTER=1


while [[ ${LINE_NUM} -gt ${LINE_NUM_COUNTER} ]]
do
    out_dir=`SUBSET_NAME ${LINE_NUM_COUNTER}`
    python3 convert_points.py -s ${LINE_NUM_COUNTER} -n ${FILE_NUM_PER_FOLDER} -i ${CSV_FILE_PATH} -o ${out_dir}
    ./convert_image.sh -s ${LINE_NUM_COUNTER} -n ${FILE_NUM_PER_FOLDER} -i ${CSV_FILE_PATH} -o ${out_dir} --image ${FULL_IMAGE_PATH}
    LINE_NUM=$((${LINE_NUM}+${FILE_NUM_PER_FOLDER}))
    SUBSET_ID_COUNTER=$((${SUBSET_ID_COUNTER}+1))
done