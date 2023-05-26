#!/bin/bash

# Initialize environment
# python -m venv venv
# source ./venv/bin/activate

# pip install <path to textflow source>
# pip install ../../.

which python

# How to install redis from source?
# ---------------------------------

# https://redis.io/docs/getting-started/installation/install-redis-from-source/

# >>
# wget https://download.redis.io/redis-stable.tar.gz
# tar -xzvf redis-stable.tar.gz
# rm redis-stable.tar.gz
# cd redis-stable
# make
# cd ..
# >>

# Clean the existing db
rm database.sqlite config.json

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --

# Create project
textflow project create -n "Named Entity Recognition"

textflow task create -p 1 -t "span-categorization"

# Add labels
textflow label create -p 1 -l "Category A" -v "CAT_A"
textflow label create -p 1 -l "Category B" -v "CAT_B"
textflow label create -p 1 -l "Category C" -v "CAT_C"
textflow label create -p 1 -l "Category D" -v "CAT_D"

# Add documents
# textflow document upload -p 1 -i documents.json

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --

# Create project
textflow project create -n "Sentiment Analysis"

textflow task create -p 2 -t "text-classification"

# Add labels
textflow label create -p 2 -l "Negative" -v "CAT_NEGATIVE" -o 0 -c "red"
textflow label create -p 2 -l "Neutral" -v "CAT_NEUTRAL" -o 1 -c "orange"
textflow label create -p 2 -l "Positive" -v "CAT_POSITIVE" -o 2 -c "green"

# Add documents
# textflow document upload -p 2 -i documents.json

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --

# create user named admin
# for this example we use simple password
textflow user create -u admin -p admin@123
textflow user create -u guest1 -p guest1@123
textflow user create -u guest2 -p guest2@123
textflow user create -u guest3 -p guest3@123

# assign user to project 1
textflow user assign -u admin -p 1 -r admin
textflow user assign -u guest1 -p 1 -r manager
textflow user assign -u guest2 -p 1
textflow user assign -u guest3 -p 1

# assign user to project 2
textflow user assign -u admin -p 2 -r admin
textflow user assign -u guest1 -p 2 -r manager
textflow user assign -u guest2 -p 2
textflow user assign -u guest3 -p 2

# now run the project using __main__.sh
# python app.py
# python -m gunicorn  -w 4 'app:create_app()'