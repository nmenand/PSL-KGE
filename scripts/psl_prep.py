#!bin/usr/env python3

import os
import shutil
import sys

DATA = "data"
DATA_FILE = "data.txt"
ENTITY_MAP = "entity_map.txt"
RELATION_MAP = "relation_map.txt"
SPLITS = 'splits'

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

def map_write_helper(map_table):
	helper = [map_table[key] + '\t' + key for key in map_table]
	return helper

def main(dataset_name, dim_num):
	current_dir = os.path.dirname(os.path.realpath(__file__))
	dataset_dir = os.path.join(os.path.dirname(current_dir), dataset_name)
	data_dir = os.path.join(dataset_dir, DATA)
	
	full_triple_list = load_helper(os.path.join(dataset_dir, DATA_FILE))
	entity_map, relation_map = map_constituents(full_triple_list)

	# Create or replace(if exists) data_dir
	if os.path.exists(data_dir):
		shutil.rmtree(data_dir)
	os.mkdir(data_dir)

	# Create mapping files under data_dir
	write_data(map_write_helper(entity_map), os.path.join(data_dir, ENTITY_MAP))
	write_data(map_write_helper(relation_map), os.path.join(data_dir, RELATION_MAP))

def _load_args(args):
	executable = args.pop(0)
	if len(args) != 2:
		print("USAGE: python3 %s <dataset_name> <dimension_number>" % executable, file = sys.stderr)
		sys.exit(1)

	dataset_name = args.pop(0)
	dim_num = args.pop(0)

	return dataset_name, dim_num

if __name__ == '__main__':
	print(sys.argv)
	dataset_name, dim_num = _load_args(sys.argv)
	main(dataset_name, dim_num)