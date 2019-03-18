#!/bin/bash

HELP(){
    echo "usage: ./convert_image.sh [-s START_LINE] -n CONVERT_NUM -i|--input INPUT_CSV -o|--output OUTPUT_FILE --image IMAGE_FOLDER"
    exit 0
}

# Path settings
DIF_HOME="DiF/"
CSV_FILE="DiF_v1.csv"

# Download number default settings
START_LINE=1
CONVERT_NUM=10000

# Download folder settings
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            HELP
        ;;
        -s)
            shift;
            START_LINE=$1
            shift
        ;;
        -n)
            shift;
            CONVERT_NUM=$1
            shift;
        ;;
        --home)
            shift;
            DIF_HOME=$1
            IMAGE_FOLDER=${DIF_HOME}/'images'
            FACE_FOLDER=${DIF_HOME}/'cropped'
        ;;
        --image)
            shift;
            IMAGE_FOLDER=$1
            break
        ;;
        -o|--output)
            shift;
            FACE_FOLDER=$1
            shift;
        ;;
        -i|--input)
            shift;
            INPUT_PATH=$1
            shift;
        ;;

        *)
            INPUT_PATH=$1
            shift;
        ;;
    esac
done

if [[ -z ${IMAGE_FOLDER} ]]; then echo "missing image folder"; HELP ;fi
if [[ -z ${INPUT_PATH} ]]; then echo "missing input folder"; HELP ;fi
if [[ -z ${FACE_FOLDER} ]]; then echo "missing face folder"; HELP ;fi


# Download format settings
IMAGE_FILENAME(){
	echo $1 | cut -f 5- -d'/' # $1=url
}
FACE_FILENAME(){
	printf '%s-%02d.jpg' $1 $2  # $1=id $2=crop_id
}

# face augmentation settings
CROP_ID_ANGLES="1,10\n2,20\n3,-10\n4,-20\n"

# program option parsing
# folder existence pre-check
if [[ ! -d ${IMAGE_FOLDER} ]]; then mkdir ${IMAGE_FOLDER}; fi
if [[ ! -d ${FACE_FOLDER} ]]; then mkdir ${FACE_FOLDER}; fi

# read CSV_FILE
export IFS=','
cat ${INPUT_PATH} | tail -n +${START_LINE} |head -n ${CONVERT_NUM} | while read id url img_w img_h box_x1 box_y1 box_x2 box_y2 meta_params
do
	# 68 face points with x,y pairs, so 136 columns
	dlib_points=`echo ${meta_params} | head -n 136`
	face_w=$((${box_x2} - ${box_x1}))
	face_h=$((${box_y2} - ${box_y1}))

	# print info
	printf "%s: %-65s %5.1f %5.1f %5.1f %5.1f\n" ${id} ${url} ${box_x1} ${box_x2} ${box_y1} ${box_y2}

	# download image
	image_path=${IMAGE_FOLDER}/`IMAGE_FILENAME ${url}`
	if [[ ! -f ${image_path} ]]; then
		wget -q -O ${image_path} ${url}
	fi

	# crop image and resize to 128x128
	face_path=${FACE_FOLDER}/`FACE_FILENAME ${id} 0`
	if [[ ! -f ${face_path} ]]; then
		magick ${image_path} -crop ${face_w}x${face_h}+${box_x1}+${box_y1} -resize 128x128\! ${face_path}
	fi

	# face augmentation
	printf "1,10\n2,20\n3,-10\n4,-20\n" | while read crop_id angle
	do
		crop_path=${FACE_FOLDER}/`FACE_FILENAME ${id} ${crop_id}`
		if [[ ! -f ${crop_path} ]]; then
			magick convert ${face_path} -distort SRT ${angle} ${crop_path}
		fi
	done
done
