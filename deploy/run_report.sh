#!/bin/bash

# Verifica se o argumento foi fornecido
if [ "$#" -ne 1 ]; then
    echo "Uso: $0 <arquivo_lista.txt>"
    exit 1
fi

# Atribui o argumento a variável
arquivo_lista="$1"

# Obtém o diretório do arquivo de lista
diretorio_saida=$(dirname "$arquivo_lista")

# Verifica se o arquivo de lista existe
if [ ! -f "$arquivo_lista" ]; then
    echo "Erro: Arquivo $arquivo_lista não encontrado!"
    exit 1
fi

# Executa o script Python passando o arquivo de lista como argumento
python3 gerar_report.py "$arquivo_lista"

# Verifica se o arquivo de saída foi criado e move para o diretório do arquivo de lista
if [ -f "mosdepth_validation.xlsx" ]; then
    mv "mosdepth_validation.xlsx" "$diretorio_saida/"
    echo "Arquivo mosdepth_validation.xlsx movido para $diretorio_saida/"
else
    echo "Erro: Arquivo mosdepth_validation.xlsx não foi gerado!"
    exit 1
fi

echo "Processamento concluído com sucesso!"
exit 0
