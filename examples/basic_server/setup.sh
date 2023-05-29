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

# # Add labels
textflow label create -p 1 -l "Category A" -v "CAT_A"
textflow label create -p 1 -l "Category B" -v "CAT_B"
textflow label create -p 1 -l "Category C" -v "CAT_C"
textflow label create -p 1 -l "Category D" -v "CAT_D"

# # Add documents
# textflow document upload -p 1 -i documents.json

# create user named admin
# for this example we use simple password
textflow user create -u admin -p admin@123

# # assign user to project 1
textflow user assign -u admin -p 1 -r admin
