#!/bin/bash

# Author: Yasas Senarath

# Initialize environment
python -m venv venv
source ./venv/bin/activate

# pip install <path to textflow source>
pip install ../../.

# Clean the existing db
rm database.sqlite config.json

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --

# Create project
textflow project create -t "sequence_labeling" -n "Named Entity Recognition"

# Add labels
textflow label create -p 1 -l "Category A" -v "CAT_A"
textflow label create -p 1 -l "Category B" -v "CAT_B"
textflow label create -p 1 -l "Category C" -v "CAT_C"
textflow label create -p 1 -l "Category D" -v "CAT_D"

# Add documents
textflow document upload -p 1 -i documents.json

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --

# Create project
python -m textflow project create -t "classification" -n "Sentiment Analysis"

# Add labels
textflow label create -p 2 -l "Negative" -v "CAT_NEGATIVE"
textflow label create -p 2 -l "Neutral" -v "CAT_NEUTRAL"
textflow label create -p 2 -l "Positive" -v "CAT_POSITIVE"

# Add documents
textflow document upload -p 2 -i documents.json

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --

# create user named admin
# for this example we use simple password
textflow user create -u admin -p admin@123
textflow user create -u guest1 -p guest1@123
textflow user create -u guest2 -p guest2@123
textflow user create -u guest3 -p guest3@123

# assign user to project 1
textflow user assign -u admin -p 1 -r admin
textflow user assign -u guest1 -p 1
textflow user assign -u guest2 -p 1
textflow user assign -u guest3 -p 1

# assign user to project 2
textflow user assign -u admin -p 2 -r admin
textflow user assign -u guest1 -p 2
textflow user assign -u guest2 -p 2
textflow user assign -u guest3 -p 2

# now run the project using __main__.sh
python app.py
