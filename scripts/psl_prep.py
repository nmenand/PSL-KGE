#!bin/usr/env python3

import json
import os
import shutil
import sys

DATA = "data"
DATA_FILE = "data.txt"
ENTITY_MAP = "entity_map.txt"
RELATION_MAP = "relation_map.txt"
SPLITS = "splits"
SPLIT = "split"
TRAIN = "_train.txt"
NEG_TRAIN = "_negative_train.txt"
TRUE_BLOCK = "trueblock_obs.txt"
FALSE_BLOCK = "falseblock_obs.txt"
ENTITYDIM = "entitydim"
RELATIONDIM = "relationdim"
TARGET = "_target.txt"

# Writes a list of data to a file
def write_data(data, file_path):
	with open(file_path, 'w+') as out_file:
		out_file.write('\n'.join(data))

# Return list of triples from filename
def load_helper(data_file):
	helper = []
	with open(data_file, 'r') as file_ptr:
		for line in file_ptr:
			triple = line.strip('\n').split('\t')
			helper.append(triple)

	return helper

# Map entities and relations to integers
def map_constituents(triple_list):
	entity_map = {}
	relation_map = {}
	entity_count = 0
	relation_count = 0
	for triple in triple_list:
		if not triple[0] in entity_map:
			entity_map[triple[0]] = str(entity_count)
			entity_count += 1
		if not triple[1] in relation_map:
			relation_map[triple[1]] = str(relation_count)
			relation_count += 1
		if not triple[2] in entity_map:
			entity_map[triple[2]] = str(entity_count)
			entity_count += 1
	return entity_map, relation_map

# Helper methods create a list for write_data()
def map_write_helper(map_table):
	helper = [map_table[key] + '\t' + key for key in map_table]
	return helper

def block_write_helper(triple_list, ent_map, rel_map):
	helper = [ent_map[triple[0]] + '\t' + rel_map[triple[1]] + '\t' + ent_map[triple[2]] for triple in triple_list]
	return helper

def target_write_helper(block_table, map_table):
	helper = [map_table[key] for key in block_table]
	return helper

def get_split_count(splits_dir):
	return len(os.listdir(splits_dir))

# Note: Create PSL rules
def main(dataset_name, dim_num):
	current_dir = os.path.dirname(os.path.realpath(__file__))
	dataset_dir = os.path.join(os.path.dirname(current_dir), dataset_name)
	data_dir = os.path.join(dataset_dir, DATA)
	splits_dir = os.path.join(dataset_dir, SPLITS)

	full_triple_list = load_helper(os.path.join(dataset_dir, DATA_FILE))
	entity_map, relation_map = map_constituents(full_triple_list)

	# Create or replace(if exists) data_dir
	if os.path.exists(data_dir):
		shutil.rmtree(data_dir)
	os.mkdir(data_dir)

	# Create mapping files
	write_data(map_write_helper(entity_map), os.path.join(data_dir, ENTITY_MAP))
	write_data(map_write_helper(relation_map), os.path.join(data_dir, RELATION_MAP))

	# Create trueblock_obs
	write_data(block_write_helper(full_triple_list, entity_map, relation_map),
		os.path.join(data_dir, TRUE_BLOCK))

	# Todo: Get split count from config file
	for split_num in range(0, get_split_count(splits_dir)):
		cur_split = SPLIT + str(split_num)
		data_split_dir = os.path.join(data_dir, cur_split)
		raw_split_dir = os.path.join(dataset_dir, SPLITS, cur_split)

		# Create or replace data_split dir under data_dir
		if os.path.exists(data_split_dir):
			shutil.rmtree(data_split_dir)
		os.mkdir(data_split_dir)

		# Load train triples of current split
		train_triples = load_helper(os.path.join(raw_split_dir, cur_split + TRAIN))
		# Load neg train triples of current split
		neg_train_triples = load_helper(os.path.join(raw_split_dir, cur_split + NEG_TRAIN))

		# Create falseblock_obs
		write_data(block_write_helper(neg_train_triples, entity_map, relation_map),
			os.path.join(data_split_dir, FALSE_BLOCK))

		# Get all entities and relations in current split. Target files contain only
		# entities and relations present in split_train file.
		# Note: Don't actually need map_consituents() since
		# trueblock_entities and trueblock relations serve only as record elements in train_triples
		trueblock_entities, trueblock_relations = map_constituents(train_triples)

		# Create dimension target files
		for dimension in range(1, dim_num + 1):
			entity_dim_target = os.path.join(data_split_dir, ENTITYDIM + str(dimension) + TARGET)
			relation_dim_target = os.path.join(data_split_dir, RELATIONDIM + str(dimension) + TARGET)

			write_data(target_write_helper(trueblock_entities, entity_map), entity_dim_target)
			write_data(target_write_helper(trueblock_relations, relation_map), relation_dim_target)

def _load_args(args):
	executable = args.pop(0)
	if len(args) != 1:
		print("USAGE: python3 %s <config.json>" % executable, file = sys.stderr)
		sys.exit(1)

	config_file = args.pop(0)
	with open(config_file, 'r') as config_fd:
		config = json.load(config_fd)

	dataset_name = config["dataset"]
	dim_num = config["dimensions"]

	return dataset_name, dim_num

if __name__ == '__main__':
	dataset_name, dim_num = _load_args(sys.argv)
	main(dataset_name, dim_num)
