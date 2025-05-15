import pandas as pd
import numpy as np
import openpyxl
import json
from Bio import SeqIO
import sys
import os

#Input
path_to_file = sys.argv[1]

#Setting Variables
#path_to_file = "C:\\Users\\daniel.nigro\\Desktop\\depth_validation\\data\\sample.thresholds.bed"
file_name = path_to_file.strip().split('\\')[-1]
file_name = file_name.replace(".thresholds.bed","")
stats = {}

#Importing Mosdepth Output and selecting its columns
mosdepth_output = pd.read_table(path_to_file, sep= '\t')
mosdepth_output = mosdepth_output.loc[:,['#chrom','start','end','region','0X','30X']]

#Extract Gene Name by regex
mosdepth_output['gene_name'] = mosdepth_output['region'].str.extract(r"^([^.]*)")

#Setting validation column, to see x30 depth of which exon
mosdepth_output['validation'] = mosdepth_output['30X'] - mosdepth_output['0X']

#Aggregation of values from which exon, to get depth by gene
df_agrupado = mosdepth_output.groupby('gene_name', as_index=False)['validation'].agg('sum')
df_agrupado[f'{file_name}'] = df_agrupado['validation'].apply(lambda x: 'OK' if x == 0 else ('OUT' if x < 0 else NA))

#df_agrupado[f'#{file_name}'] = df_agrupado['validation'].abs()
#print(df_agrupado)
df_agrupado[['gene_name',f'{file_name}']].to_csv(f"{file_name}.dv",sep='\t',encoding='utf-8',index=False)
