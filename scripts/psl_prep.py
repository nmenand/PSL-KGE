#!bin/usr/env python3

import json
import os
import shutil
import sys
	
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

PSL = "psl"
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

ENTITY_1 = 0
ENTITY_2 = 2
RELATION = 1
SIGN = 3

# Writes a list of data to a file
def write_data(data, file_path):
	with open(file_path, 'w+') as out_file:
		# if list of lists
		if isinstance(data[0], list):
			out_file.write('\n'.join(["\t".join(current_list) for current_list in data]))
		# else regular list
		else:
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
# Modifies triple_list to its mapped equivalent
def map_constituents(triple_list):
	entity_map = {}
	relation_map = {}
	entity_count = 0
	relation_count = 0
	for triple in triple_list:
		if not triple[ENTITY_1] in entity_map:
			entity_map[triple[ENTITY_1]] = str(entity_count)
			entity_count += 1
		triple[ENTITY_1] = entity_map[triple[ENTITY_1]]
		if not triple[RELATION] in relation_map:
			relation_map[triple[RELATION]] = str(relation_count)
			relation_count += 1
		triple[RELATION] = relation_map[triple[RELATION]]
		if not triple[ENTITY_2] in entity_map:
			entity_map[triple[ENTITY_2]] = str(entity_count)
			entity_count += 1
		triple[ENTITY_2] = entity_map[triple[ENTITY_2]]

	return entity_map, relation_map

# Helper methods create a list for write_data()
def map_raw_triple(raw_triple, ent_map, rel_map):
	return [ent_map[raw_triple[ENTITY_1]], rel_map[raw_triple[RELATION]], ent_map[raw_triple[ENTITY_2]]]

def get_split_count(splits_dir):
	return len(os.listdir(splits_dir))

# Note: Create PSL rules
def main(dataset_name, dim_num, split_num):
	# PSL-KGE/data
	raw_data_dir = os.path.join(os.path.dirname(BASE_DIR), DATA)
	# PSL-KGE/data/[dataset]
	splits_dir = os.path.join(raw_data_dir, dataset_name)
	# PSL-KGE/[dataset]
	dataset_dir = os.path.join(os.path.dirname(BASE_DIR), dataset_name)
	# PSL-KGE/psl
	psl_dir = os.path.join(os.path.dirname(BASE_DIR), PSL)
	# PSL-KGE/psl/data
	psl_data_dir = os.path.join(psl_dir, DATA)

	full_triple_list = load_helper(os.path.join(dataset_dir, DATA_FILE))

	# Note: full_triple_list is modified to its mapped equivalent after method call
	entity_map, relation_map = map_constituents(full_triple_list)

	# Create or replace(if exists) psl_data_dir
	if os.path.exists(psl_data_dir):
		shutil.rmtree(psl_data_dir)
	os.mkdir(psl_data_dir)

	# Create mapping files
	write_data([[entity_map[entity], entity] for entity in entity_map], os.path.join(psl_data_dir, ENTITY_MAP))
	write_data([[relation_map[relation], relation] for relation in relation_map], os.path.join(psl_data_dir, RELATION_MAP))

	# Create trueblock_obs
	write_data(full_triple_list, os.path.join(psl_data_dir, TRUE_BLOCK))
	
	# Loop through data splits
	for split_num in range(0, split_num):
		cur_split = SPLIT + str(split_num)
		data_split_dir = os.path.join(psl_data_dir, str(split_num))
		raw_split_dir = os.path.join(splits_dir, cur_split)

		# Create or replace data_split dir under psl_data_dir
		if os.path.exists(data_split_dir):
			shutil.rmtree(data_split_dir)
		os.mkdir(data_split_dir)

		# Load triples of current split
		raw_split_triples = load_helper(os.path.join(raw_split_dir, cur_split + TRAIN))
		
		train_triples = []
		neg_train_triples = []

		# Load true and false triples from current split
		# Note: SIGN=0 means false triple
		for triple in raw_split_triples:
			if int(triple[SIGN]):
				train_triples.append(map_raw_triple(triple, entity_map, relation_map))
			else:
				neg_train_triples.append(map_raw_triple(triple, entity_map, relation_map))

		# Create falseblock_obs
		write_data(neg_train_triples, os.path.join(data_split_dir, FALSE_BLOCK))

		# Get all entities and relations in current split. Target files contain only
		# entities and relations present in split_train file.
		target_entity_tracker = {}
		target_relation_tracker = {}
		for triple in train_triples:
			if not triple[ENTITY_1] in target_entity_tracker:
				target_entity_tracker[triple[ENTITY_1]] = None
			if not triple[RELATION] in target_relation_tracker:
				target_relation_tracker[triple[RELATION]] = None
			if not triple[ENTITY_2] in target_entity_tracker:
				target_entity_tracker[triple[ENTITY_2]] = None

		target_entities = [entity for entity in target_entity_tracker]
		target_relations = [relation for relation in target_relation_tracker]

		# Create dimension target files
		for dimension in range(1, dim_num + 1):
			entity_dim_target = os.path.join(data_split_dir, ENTITYDIM + str(dimension) + TARGET)
			relation_dim_target = os.path.join(data_split_dir, RELATIONDIM + str(dimension) + TARGET)
			write_data(target_entities, entity_dim_target)
			write_data(target_relations, relation_dim_target)

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
	split_num = config["splits"]

	return dataset_name, dim_num, split_num

if __name__ == '__main__':
	dataset_name, dim_num, split_num = _load_args(sys.argv)
	main(dataset_name, dim_num, split_num)
