#!/bin/bash

files_path=$1
report_name=$2
output_dir=$3

if [ -z "$files_path" ] || [ -z "$report_name" ] || [ -z "$output_dir" ]; then
    echo "Usage: $0 <files_path> <report_name> <output_dir>"
    exit 1
fi

output_tmp="md_results_$report_name.txt"

touch $output_tmp

cat $files_path | xargs -P 4 -I {} bash function_run_mosdepth.sh {} $output_tmp

date
echo "All mosdepth jobs completed successfully."
python3 gerar_report.py $output_tmp $report_name

mv md_report_$report_name.xlsx $output_dir
rm $output_tmp
date
echo "Report generated: $report_name.xlsx"

