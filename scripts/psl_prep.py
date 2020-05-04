#!bin/usr/env python3

import json
import os
import shutil
import sys

from rule_generation import generate_rules

PSL = "psl"
DATA = "data"
CLI = "cli"
KGE = "kge"
DATA_FILE = "data.txt"
ENTITY_MAP = "entity_map.txt"
RELATION_MAP = "relation_map.txt"
TRAIN = "train.txt"
TEST = "test.txt"
VALID = "valid.txt"
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

ENTITY_1 = 0
ENTITY_2 = 2
RELATION = 1
SIGN = 3

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
RAW_DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), DATA)
PSL_DIR = os.path.join(os.path.dirname(BASE_DIR), PSL)
PSL_DATA_DIR = os.path.join(PSL_DIR, DATA)
CLI_DIR = os.path.join(PSL_DIR, CLI)
DATA_KGE_DIR = os.path.join(PSL_DATA_DIR, KGE)

def main(dataset_name, dim_num, split_num):
    dataset_splits_dir = os.path.join(RAW_DATA_DIR, dataset_name)

    entity_map, relation_map = load_mappings(dataset_splits_dir)
    makedir(DATA_KGE_DIR)

    # Loop through data splits
    for split_num in range(0, split_num):
        mapped_split_dir = os.path.join(DATA_KGE_DIR, str(split_num))
        raw_split_dir = os.path.join(dataset_splits_dir, str(split_num))
        split_eval_dir = os.path.join(mapped_split_dir, EVAL)
        split_learn_dir = os.path.join(mapped_split_dir, LEARN)

        # Create/replace directories
        makedir(mapped_split_dir)
        makedir(split_eval_dir)
        makedir(split_learn_dir)

        # Separate positive and negative triples from train file
        mapped_pos_train_triples, mapped_neg_train_triples = separate_triples(raw_split_dir, TRAIN, entity_map, relation_map)

        # Create trueblock_obs & falseblock_obs
        write_data(mapped_pos_train_triples, os.path.join(split_eval_dir, TRUE_BLOCK))
        write_data(mapped_neg_train_triples, os.path.join(split_eval_dir, FALSE_BLOCK))

        # Separate positive and negative triples from the validation file
        mapped_pos_valid_triples, mapped_neg_valid_triples = separate_triples(raw_split_dir, VALID, entity_map, relation_map)

        # Create trueblock_obs & falseblock_obs
        write_data(mapped_pos_valid_triples, os.path.join(split_learn_dir, TRUE_BLOCK))
        write_data(mapped_neg_valid_triples, os.path.join(split_learn_dir, FALSE_BLOCK))

        # Target files contain only entities and relations present in current split
        create_target_files(mapped_pos_train_triples, split_eval_dir)
        create_target_files(mapped_pos_valid_triples, split_learn_dir)

        # Generate and write rules
        psl_rules_target = os.path.join(CLI_DIR, RULES_PSL)
        psl_predicates_target = os.path.join(CLI_DIR, DATA_PSL)
        rules, predicates = generate_rules(dim_num)
        write_data(rules, psl_rules_target)
        write_data(predicates, psl_predicates_target)

# Separates triples into true and false group and maps them
def separate_triples(raw_split_dir, file_name, entity_map, relation_map):
    triple_list = load_helper(os.path.join(raw_split_dir, file_name))

    true_triples = []
    false_triples = []
    for triple in triple_list:
        if int(triple[SIGN]):
            true_triples.append(map_raw_triple(triple, entity_map, relation_map))
        else:
            false_triples.append(map_raw_triple(triple, entity_map, relation_map))
    return true_triples, false_triples

# Creates and writes observation files for each dimension
def create_target_files(mapped_triple_list, split_eval_dir):
    target_entities = set()
    target_relations = set()

    # Get all entities and relations in training split
    for triple in mapped_triple_list:
        if not triple[ENTITY_1] in target_entities:
            target_entities.add(triple[ENTITY_1])
        if not triple[ENTITY_2] in target_entities:
            target_entities.add(triple[ENTITY_2])
        if not triple[RELATION] in target_relations:
            target_relations.add(triple[RELATION])

    target_entities = list(target_entities)
    target_relations = list(target_relations)

    # Create target files for each dimension
    for dimension in range(1, dim_num + 1):
        entity_dim_target_file = os.path.join(split_eval_dir, ENTITYDIM + str(dimension) + TARGET)
        relation_dim_target_file = os.path.join(split_eval_dir, RELATIONDIM + str(dimension) + TARGET)
        write_data(target_entities, entity_dim_target_file)
        write_data(target_relations, relation_dim_target_file)

# Writes a list of data to a file
def write_data(data, file_path):
    with open(file_path, 'w+') as out_file:
        # if list is empty
        if not data:
            return
        # if list of lists
        elif isinstance(data[0], list):
            out_file.write('\n'.join(["\t".join(current_list) for current_list in data]))
        # else regular list
        else:
            out_file.write('\n'.join(data))

# Return list of triples from filename
def load_helper(data_file):
    helper = []
    with open(data_file, 'r') as file_ptr:
        for line in file_ptr:
            helper.append(line.strip('\n').split('\t'))

    return helper

# TODO write better function
def load_mappings(dataset_splits_dir):
    ent_map_list = load_helper(os.path.join(dataset_splits_dir, ENTITY_MAP))
    rel_map_list = load_helper(os.path.join(dataset_splits_dir, RELATION_MAP))
    ent_map = {}
    rel_map = {}
    for line in ent_map_list:
        ent_map[line[1]] = line[0]
    for line in rel_map_list:
        rel_map[line[1]] = line[0]
    return ent_map, rel_map

def makedir(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)

# Helper methods create a list for write_data()
def map_raw_triple(raw_triple, ent_map, rel_map):
    return [ent_map[raw_triple[ENTITY_1]], rel_map[raw_triple[RELATION]], ent_map[raw_triple[ENTITY_2]]]

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
