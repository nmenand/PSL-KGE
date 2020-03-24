#!bin/usr/env python3

#NOTE: Not finshed 

import os
import sys

# Takes in name of dataset to create model out of
dataset_name = sys.argv[1]

# Create data subdirectory
current_dir = os.path.dirname(os.path.realpath(__file__))
dataset_dir = os.path.join(current_dir, "../"+dataset_name)
data_file = os.path.join(dataset_dir, "data.txt")
data_dir = os.path.join(current_dir, "../"+dataset_name + "_data")
os.mkdir(data_dir)

# Entity and mapping files
entity_map_file = os.path.join(data_dir, "entity_map.txt")
relation_map_file = os.path.join(data_dir, "relation_map.txt")

# Extract relations and entities into two tables
# Assume triples in dataset have form: entity, relation, entity
with open(data_file) as df:
	# Entity and relation hash tables
	ht_relation = {}
	ht_entity = {}
	for line in df:
		# Note: What value should be placed in table?
		triple = line.strip('\n').split('\t')
		if not triple[1] in ht_relation:
			ht_relation[triple[1]] = 1
		if not triple[0] in ht_entity:
			ht_entity[triple[0]] = 1
		if not triple[2] in ht_entity:
			ht_entity[triple[2]] = 1

# Create mapping files and place them into data_dir
with open(entity_map_file, 'w+') as em, open(relation_map_file, 'w+') as rm:
	num = 0
	for ent in ht_entity:
		em.write(str(num) + '\t' + ent + '\n')
		num += 1
	num = 0
	for rel in ht_relation:
		rm.write(str(num) + '\t' + rel + '\n')
		num += 1

# Positive and Negative triple files
false_block_obs_file = os.path.join(data_dir, "false_block_obs.txt")
true_block_obs_file = os.path.join(data_dir, "true_block_obs.txt")

# Create observation files and place them into data_dir












