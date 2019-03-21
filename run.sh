#!/bin/bash
out_folder="DiF"
batch_size=1000


./convert_all.sh -i DiF/DiF_v1.csv -o ${out_folder} --image_folder 'full_image' -b ${batch_size}