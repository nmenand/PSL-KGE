#!bin/usr/env python3

import json
import os
import shutil
import sys

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

PSL = "psl"
DATA = "data"
CLI  = "cli"
KGE = "kge"
DATA_FILE = "data.txt"
ENTITY_MAP = "entity_map.txt"
RELATION_MAP = "relation_map.txt"
SPLITS = "splits"
SPLIT = "split"
TRAIN = "train.txt"
TEST = "test.txt"
NEG_TRAIN = "_negative_train.txt"
TRUE_BLOCK = "trueblock_obs.txt"
FALSE_BLOCK = "falseblock_obs.txt"
ENTITYDIM = "entitydim"
RELATIONDIM = "relationdim"
TARGET = "_target.txt"
RULES_PSL = "kge.psl"
DATA_PSL = "kge.data"
EVAL = "eval"
LEARN = "learn"

ENTITY1_RULE = "1.0: EntityDim"
RELATION_RULE = "(e1) + RelationDim"
ENTITY2_RULE = "(r1) - EntityDim"
TRUE_RULE = "(e2) + 0*TrueBlock(e1, r1, e2) = 0"
FALSE_RULE2 = "(e2) + 0*FalseBlock(e1, r1, e2) >= 1\n"

PREDICATES = "predicates:"
FALSEBLOCK = "\tFalseBlock/3: closed"
TRUEBLOCK = "\tTrueBlock/3: closed\n"
OPEN = "/1: open"
OBSERVATIONS = "observations:"
TARGETS = "targets:"
PREDICATE_PATH = ": ../data/kge/0/eval/"
TRUEPATH = "\tFalseBlock: ../kge/data/0/eval/falseblock_obs.txt\n"
FALSEPATH = "\tTrueBlock: ../kge/data/0/eval/trueblock_obs.txt"
ENTITY_RULE = "EntityDim"
RELATION_RULE_DIM = "RelationDim"

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

#Create PSL rules
def generate_rules(num_dimensions):
	rule_output = []
	for dim in range(1, num_dimensions+1):
		rule_output.append(ENTITY1_RULE + str(dim) + RELATION_RULE + str(dim) + ENTITY2_RULE+ str(dim) + TRUE_RULE)
		rule_output.append(ENTITY1_RULE + str(dim) + RELATION_RULE + str(dim) + ENTITY2_RULE+ str(dim) + FALSE_RULE2)

	predicate_output = []

	predicate_output.append(PREDICATES)
	for dim in range(1, num_dimensions+1):
		predicate_output.append("\t" + ENTITY_RULE + str(dim) + OPEN)
		predicate_output.append("\t" + RELATION_RULE_DIM + str(dim) + OPEN)
	predicate_output.append(FALSEBLOCK)
	predicate_output.append(TRUEBLOCK)

	predicate_output.append(OBSERVATIONS)
	predicate_output.append(FALSEPATH)
	predicate_output.append(TRUEPATH)

	predicate_output.append(TARGETS)
	for dim in range(1, num_dimensions+1):
		predicate_output.append("\t" + ENTITY_RULE + str(dim) + PREDICATE_PATH + ENTITYDIM + str(dim)+ TARGET)
		predicate_output.append("\t" + RELATION_RULE_DIM + str(dim) + PREDICATE_PATH + RELATIONDIM + str(dim)+ TARGET)

	return rule_output, predicate_output

def makedir(directory):
	if os.path.exists(directory):
		shutil.rmtree(directory)
	os.mkdir(directory)

# Helper methods create a list for write_data()
def map_raw_triple(raw_triple, ent_map, rel_map):
	return [ent_map[raw_triple[ENTITY_1]], rel_map[raw_triple[RELATION]], ent_map[raw_triple[ENTITY_2]]]

# Return positive and negative triples in separate lists
# Note: SIGN=0 means false triple
def separate_triples(all_triples, entity_map, relation_map):
	true_triples = []
	false_triples = []
	for triple in all_triples:
		if int(triple[SIGN]):
			true_triples.append(map_raw_triple(triple, entity_map, relation_map))
		else:
			false_triples.append(map_raw_triple(triple, entity_map, relation_map))
	return true_triples, false_triples

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
	# PSL-KGE/psl/cli
	cli_dir = os.path.join(psl_dir, CLI)
	# PSL-KGE/psl/data/KGE
	data_kge_dir = os.path.join(psl_data_dir, KGE)

	full_triple_list = load_helper(os.path.join(dataset_dir, DATA_FILE))

	# Note: full_triple_list is modified to its mapped equivalent after method call
	entity_map, relation_map = map_constituents(full_triple_list)

	# Create or replace(if exists) psl_data_dir
	makedir(psl_data_dir)

	makedir(data_kge_dir)

	# Create mapping files
	write_data([[entity_map[entity], entity] for entity in entity_map], os.path.join(data_kge_dir, ENTITY_MAP))
	write_data([[relation_map[relation], relation] for relation in relation_map], os.path.join(data_kge_dir, RELATION_MAP))

	# Loop through data splits
	for split_num in range(0, split_num):
		cur_split =  str(split_num)
		data_split_dir = os.path.join(data_kge_dir, str(split_num))
		raw_split_dir = os.path.join(splits_dir, cur_split)
		split_eval_dir = os.path.join(data_split_dir, EVAL)
		split_learn_dir = os.path.join(data_split_dir, LEARN)

		# Create or replace data_split dir under data_kge_dir
		makedir(data_split_dir)
		makedir(split_eval_dir)
		makedir(split_learn_dir)

		# Load train triples & test triples of current split
		raw_split_train_triples = load_helper(os.path.join(raw_split_dir, TRAIN))

		train_triples, neg_train_triples = separate_triples(raw_split_train_triples, entity_map, relation_map)

		# Create trueblock_obs & falseblock for eval
		write_data(full_triple_list, os.path.join(split_eval_dir, TRUE_BLOCK))
		write_data(neg_train_triples, os.path.join(split_eval_dir, FALSE_BLOCK))

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
			entity_dim_target = os.path.join(split_eval_dir, ENTITYDIM + str(dimension) + TARGET)
			relation_dim_target = os.path.join(split_eval_dir, RELATIONDIM + str(dimension) + TARGET)
			write_data(target_entities, entity_dim_target)
			write_data(target_relations, relation_dim_target)

		# Generate and write rules
		psl_rules_target = os.path.join(cli_dir, RULES_PSL)
		psl_predicates_target = os.path.join(cli_dir, DATA_PSL)
		rules, predicates = generate_rules(dim_num)
		write_data(rules, psl_rules_target)
		write_data(predicates, psl_predicates_target)


def _load_args(args):
	executable = args.pop(0)
	if (len(args) != 1 or ({'h','help'} & {arg.lower().strip().replace('-', '') for arg in args})):
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
