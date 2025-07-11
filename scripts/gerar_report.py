import pandas as pd
import numpy as np
import openpyxl
import json
from Bio import SeqIO
import sys
import os

#Variables
path_list = sys.argv[1]
coberturas = [x.strip() for x in sys.argv[2].split(',')]
path_to_file = []

#Dicionário com os dataframes para cada cobertura
tabela_final = {}
for cobertura in coberturas:
    tabela_final[f'classification{cobertura}'] = pd.DataFrame()
    tabela_final[f'scores{cobertura}'] = pd.DataFrame()

#Parsing input files
with open(path_list,'r') as input:
    parse_lines = input.readlines()
    for line in parse_lines:
        path_to_file.append(line.strip())

def importar_dataset(path_to_file):
    file_name = path_to_file.strip().split('\\')[-1]
    file_name = file_name.replace(".thresholds.bed.gz", "")

    #Importing Mosdepth Output and selecting its columns
    mosdepth_output = pd.read_table(path_to_file, sep='\t', compression = 'gzip')
    cols = ['#chrom', 'start', 'end', 'region', '0X'] + [f'{c}X' for c in coberturas]
    mosdepth_output = mosdepth_output.loc[:, cols]
    #Extract Gene Name by regex
    mosdepth_output['gene_name'] = mosdepth_output['region'].str.extract(r"^([^.]*)")

    #Setting validation column, to see 30x and 20x depth of which exon
    mosdepth_output[f'score{cobertura}_{file_name}'] = mosdepth_output[f'{cobertura}X'] - mosdepth_output['0X']

    gene_size = mosdepth_output.groupby('gene_name', as_index=False)['0X'].agg('sum')

    #Aggregation of values from which exon, to get depth 30x by gene
    df_agrupado = mosdepth_output.groupby('gene_name', as_index=False)[f'score30_{file_name}'].agg('sum')
    df_agrupado[f'{file_name}'] = df_agrupado[f'score_{file_name}'].apply(
        lambda x: 'OK' if x == 0 else ('OUT' if x < 0 else np.nan))  # Changed NA to np.nan

    df_agrupado[f'score_{file_name}'] = (df_agrupado[f'score_{file_name}'].astype(str) + "/" + gene_size['0X'].astype(str))

    # Building the dict with dataframes
    if len(tabela_final['classification']) == 0:
        tabela_final['classification'] = df_agrupado[['gene_name', f'{file_name}']] 
    else:
        tabela_final['classification'] = pd.merge(
            tabela_final['classification'],
            df_agrupado[['gene_name', f'{file_name}']],  
            on="gene_name",
            how="left"
        )
    
    if len(tabela_final['scores']) == 0:
        tabela_final['scores'] = df_agrupado[['gene_name', f'score_{file_name}']]  
    else:
        tabela_final['scores'] = pd.merge(
            tabela_final['scores'],
            df_agrupado[['gene_name', f'score_{file_name}']],  
            on="gene_name",
            how="left"
        )

for file in path_to_file:
    importar_dataset(file)

with pd.ExcelWriter('mosdepth_validation.xlsx', engine = 'openpyxl') as writer:
    for nome_aba, df in tabela_final.items():
        df.to_excel(writer,sheet_name=nome_aba,index=False)
