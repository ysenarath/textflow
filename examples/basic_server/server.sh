#!/bin/bash

# Initialize environment
export PYTHONPATH=PYTHONPATH:`pwd`/../..
source ../../venv/bin/activate

rm database.sqlite config.json

# Create project
python -m textflow project create -t "sequence_labeling" -n "Named Entity Recognition"

# Add labels
python -m textflow label create -p 1 -l "Category A" -v "CAT_A"
python -m textflow label create -p 1 -l "Category B" -v "CAT_B"
python -m textflow label create -p 1 -l "Category C" -v "CAT_C"
python -m textflow label create -p 1 -l "Category D" -v "CAT_D"

# Add documents
python -m textflow document upload -p 1 -i documents.json

# create user named admin
# for this example we use simple password
python -m textflow user create -u admin -p admin@123

# assign user to project
python -m textflow user assign -u admin -p 1

# now run the project using __main__.sh
python app.py

