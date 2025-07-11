#!/bin/bash

# Script to run MOSDEPTH -----------------------------------------------------------

# Var ------------------------------------------------------------------------------
input_list="$1"
md_results_paths="$2"
input_crai="$input_list.crai"
input_file="$(basename $input_list)"
bed_file="${3:-"/mnt/ssd/MegaBOLT_scheduler/reference/db/db_BED/annotated_UCSC_hg38_exome_15padding_corrected_sorted.bed"}"
sample_name=$(basename "$input_list" | awk -F '.' '{print $1}')
output_dir="md_out_$sample_name"
mosdepth_bin="/mnt/ssd/MegaBOLT_scheduler/bin/mosdepth"
hg38_ref="/mnt/ssd/MegaBOLT_scheduler/reference/Homo_sapiens_assembly38.fasta"
origin_path=$(dirname $input_list)
tempdir="temp_$sample_name"

mkdir -p "$output_dir"

# Log ------------------------------------------------------------------------------

LOG_FILE="$output_dir/md_${sample_name}.log"
exec > >(tee -a "$LOG_FILE") 2>&1

# Verificações ---------------------------------------------------------------------
if [ ! -f "$input_list" ]; then
    echo "Erro: Arquivo $input_list não encontrado!" >&2
    exit 1
fi

if [ ! -f "$bed_file" ]; then
    echo "Erro: Arquivo BED $bed_file não encontrado!" >&2
    exit 1
fi

# Execution ------------------------------------------------------------------------
echo -e "\n$(date)"
echo -e "\nProcessando arquivo: $sample_name"
echo "Bed file: $(basename "$bed_file")"
echo

# Cria diretório temporário e copia arquivos
mkdir -p $tempdir
rsync -avp --progress $input_list $input_crai $tempdir

# Verifica se há arquivos no tempdir
if [ -z "$(ls -A $tempdir)" ]; then
    echo "Erro: Nenhum arquivo foi copiado para tempdir!" >&2
    exit 1
fi

# Executa mosdepth (assumindo que há apenas 1 arquivo BAM/CRAM no tempdir)
input_cram=$(find $tempdir -type f -iname "$input_file")

if [ -z "$input_cram" ]; then
    echo "Erro: Nenhum arquivo BAM/CRAM encontrado em tempdir!" >&2
    exit 1
fi

$mosdepth_bin -t 10 --by "$bed_file" --thresholds 0,1,10,20,30,100 -f $hg38_ref "md_$sample_name" "$input_cram"

mv md_"$sample_name"* $output_dir

echo "Copiando para origem: $origin_path"
mkdir -p $origin_path/mosdepth_out
mv $output_dir/* $origin_path/mosdepth_out

find $origin_path/mosdepth_out -type f -iname "*.thresholds.bed.gz" | xargs realpath >> $md_results_paths

rm -r $tempdir
rm -r $output_dir

echo "Terminada a análise do arquivo: $sample_name">&1
echo "$(date)" >&1
