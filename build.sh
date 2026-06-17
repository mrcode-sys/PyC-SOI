#!/bin/bash

# Cores para deixar o terminal bonito e legível
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NO_COLOR='\033[0m'

echo -e "${BLUE}[PyC-SOI] Preparing the environment...${NO_COLOR}"

echo "Checking directory structure..."
mkdir -p lib data core src_c

echo -e "Compiling the math engine (${BLUE}src_c/category_grouper.c${NO_COLOR})..."

gcc -shared -o lib/category_grouper_lib.so -fPIC src_c/agrupador.c -lm -O3 -march=native

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[Success] The lib/category_grouper_lib.so library is generated${NO_COLOR}"
    echo -e "${BLUE}Installing python libraries${NO_COLOR}..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo -e "The environment is ready. To run, use: ${GREEN}python main.py${NO_COLOR}"
    else
        echo -e "${RED}[Error] Error instaling python libraries. Check python and pip.${NO_COLOR}"
        exit 1
    fi
else
    echo -e "${RED}[Error] Error compiling C code. Check GCC.${NO_COLOR}"
    exit 1
fi
