#!/bin/bash

PRINTHELP(){
    echo "usage: convert_all.sh --input INPUT_CSV [--image_folder IMG_FOLDER_NAME] [-b BATCH_SIZE] [-l LIMIT] OUT_PATH"
    exit $1
}


while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            PRINTHELP 0;
        ;;
        -i|--input)
            shift;CSV_FILE_PATH=$1;shift
        ;;
        -o|--output)
            shift;OUT_PATH=$1;shift
        ;;
        --image_folder)
            shift;FULL_IMAGE_DIR=$1;shift
        ;;
        -b|--batch_size)
            shift;BATCH_SIZE=$1;shift
        ;;
        -l|--limit)
            shift;LIMIT=$1;shift
        ;;
        *)
            OUT_PATH=$1;
            break
    esac
done


if [[ -z ${CSV_FILE_PATH} ]]; then echo "input csv path not given"; PRINTHELP 1; fi
if [[ -z ${OUT_PATH} ]]; then echo "output path not given"; PRINTHELP 2; fi
if [[ -z ${FULL_IMAGE_DIR} ]]; then FULL_IMAGE_DIR='full_image'; fi
if [[ -z ${BATCH_SIZE} ]]; then BATCH_SIZE=10000; fi
if [[ -z ${LIMIT} ]]; then LIMIT=`wc -l ${CSV_FILE_PATH} | awk '{print $1}'`; fi


BATCH_NAME(){
    printf "%05d" $1
}


BATCH_ID=1
COUNTER=1


while [[ ${LIMIT} -gt ${COUNTER} ]]
do
    out_dir=${OUT_PATH}/`BATCH_NAME ${BATCH_ID}`
    image_dir=${out_dir}/${FULL_IMAGE_DIR}
    if [[ ! -d ${out_dir} ]]; then mkdir -p ${out_dir};fi
    if [[ ! -d ${image_dir} ]]; then mkdir -p ${image_dir};fi
    python3 convert_points.py -s ${COUNTER} -n ${BATCH_SIZE} -i ${CSV_FILE_PATH} -o ${out_dir}
    ./convert_image.sh -s ${COUNTER} -n ${BATCH_SIZE} -i ${CSV_FILE_PATH} -o ${out_dir} --image ${image_dir}
    COUNTER=$((${COUNTER}+${BATCH_SIZE}))
    BATCH_ID=$((${BATCH_ID}+1))
done