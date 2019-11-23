#!/bin/bash
python3 generateMutants.py testProgram.py mutantLibrary.txt
python3 insertMutants.py mutantLibrary.txt
python3 simulateMutants.py mutantLibrary.txt
rm -r __pycache__
echo -e "\nFINAL MUTANT LIBRARY:\n\n$(<mutantLibrary.txt)"