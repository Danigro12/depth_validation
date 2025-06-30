#!/bin/bash

files_path=$1

cat $list_files | xargs -P 4 -I {} bash function_run_mosdepth.sh {}
