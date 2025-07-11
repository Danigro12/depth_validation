import pandas as pd
from Bio import SeqIO
import json
import numpy as np
import sys

# First, don't forget to correct exon number from UCSC, with 'exon_numbered.sh' script (made by Wilson Junior)

# In data/ folder, there is a 'conver_table' file. You can generate it by doing the following:
# Get GTF file from https://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/genes/hg38.ncbiRefSeq.gtf.gz
# Clean the file by doing:
# zcat hg38.ncbiRefSeq.gtf.gz | cut -f 9 > tmp
# awk -F '; ' '{gsub("gene_id ","") ; gsub("transcript_id ","") ; print $1 ";" $2}' tmp > convert_table

_, bed_file_name = sys.argv

#Setting vars
my_dict = {}
#bed_name = "../../data/UCSC_hg38_exome_15padding_corrected_sorted.bed"
bed_name = bed_file_name.strip()
new_name = f"annotated_{bed_name.split('/')[-1].split('\\')[-1]}"

#Inputing bed file
bed_file = pd.read_table(bed_name, sep = '\t',header = None)

#Extracting the transcript ID by regex
bed_file['transcript_id'] = bed_file[3].str.extract(r"^([^.]*)")

#Pegar somente os transcritos MANE. Estão no .bed do UCSC
convert_table = pd.read_table('../../data/convert_table',sep = ';', header = None)

convert_table = convert_table.drop_duplicates()
conjunto_de_transcritos_MANE = set(bed_file['transcript_id'])

# Filtering MANE transcripts
convert_table.iloc[:, 1] = convert_table.iloc[:, 1].str.split('.').str[0]
convert_table = convert_table[convert_table.iloc[:, 1].isin(conjunto_de_transcritos_MANE)]

convert_table.to_csv('../../data/convert_table_MANE', sep=":",encoding='utf-8', header=False, index = False)

#Input data and drop a json file
with open('../../data/convert_table_MANE','r') as input, open('../../data/hg38_UCSC_gene_transcript_id.json' ,'w', encoding='utf-8') as output:
    for linha in input:
        valores = linha.strip().split(':')
        my_dict[valores[1]] = valores[0]
    json.dump(my_dict, output, ensure_ascii=False, indent=4)

# Concat the gene and transcript id
mapped_values = bed_file['transcript_id'].map(my_dict).fillna(bed_file['transcript_id'])

bed_file[3] = np.where(
    mapped_values != bed_file['transcript_id'],  
    mapped_values.str.cat(bed_file[3], sep='.'), 
    bed_file[3]
)

#Removing the last column (transcript_id), that was created to help in concatening
bed_file = bed_file.iloc[:,:-1]

bed_file = bed_file[bed_file.iloc[:,3].notna()]
bed_file[3] = bed_file[3] + "_" + bed_file[0].astype(str) + ":" + bed_file[1].astype(str) + "-" + bed_file[2].astype(str)

bed_file.to_csv(f"../../data/{new_name}", sep= '\t', header = False, index = False)
