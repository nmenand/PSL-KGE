#!bin/usr/env python3

import copy
import json
import os
import shutil
import sys
import random

RANDOM = "random"
SPLIT = 'split'

SEED = 'seed'
SPLITS = 'splits'
DATASET = 'dataset'
DATAFILE = 'data'
PERCENT_TRAIN = 'percent_train'
PERCENT_VALID = 'percent_valid'
FALSE_TRIP_RATIO = 'false_triples_ratio'
TYPE_SPLIT = 'type_split'
ENTITY_MAP = "entity_map.txt"
RELATION_MAP = "relation_map.txt"

TRAIN = 'train.txt'
TEST = 'test.txt'
VALID = 'valid.txt'

ENTITY_1 = 0
ENTITY_2 = 2
RELATION = 1

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
RAW_SPLITS_DIR = os.path.join(os.path.dirname(CURRENT_DIR), DATAFILE)

def main():

    # Load data from arguments
    config, data, set_of_data = load_data(sys.argv)

    # Set the Seed
    seed = config[SEED]
    random.seed(seed)

    # Create splits directory
    if os.path.isdir(RAW_SPLITS_DIR) is False:
        os.mkdir(RAW_SPLITS_DIR)

    # Create a directory for the specific dataset
    sub_dir = os.path.join(RAW_SPLITS_DIR, config[DATASET])
    # Delete previous dataset raw splits if they exist.
    if os.path.exists(sub_dir):
        shutil.rmtree(sub_dir)
    os.mkdir(sub_dir)

    create_mapping_files(data, sub_dir)

    # Generate and write each split
    create_splits(data, set_of_data, sub_dir, config)

def load_data(args):
    args.pop(0)
    if(len(args) != 1 or ({'h','help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("Usage: python3 gen_splits.py <path_to_config_file>")
        sys.exit(1)

    config_file = args.pop(0)
    with open(config_file, 'r') as config_fd:
        config = json.load(config_fd)

    data = []
    set_of_data = set()
    with open(config[DATAFILE], 'r') as data_fd:
        # Read input file into a list of lists and a set of all entities seen
        for line in data_fd:
            line_data = line.strip('\n').split('\t')
            data.append(line_data)
            set_of_data.add(tuple(line_data))

    return config, data, set_of_data

# Create mapping files and return entity map and relation map
def create_mapping_files(all_triples, sub_dir):
    ent_mapping, rel_mapping = map_constituents(all_triples)
    # Key = raw_ent/raw_rel
    # Val = mapping
    # Writes the list of mappings in the form [raw_value,mapping]
    write_data([[ent_mapping[entity], entity] for entity in ent_mapping], os.path.join(sub_dir, ENTITY_MAP))
    write_data([[rel_mapping[relation], relation] for relation in rel_mapping], os.path.join(sub_dir, RELATION_MAP))

# Map entities and relations to integers
def map_constituents(triple_list):
    entity_map = {}
    relation_map = {}
    entity_count = 0
    relation_count = 0
    for triple in triple_list:
        if not triple[ENTITY_1] in entity_map:
            entity_map[triple[ENTITY_1]] = str(entity_count)
            entity_count += 1
        if not triple[RELATION] in relation_map:
            relation_map[triple[RELATION]] = str(relation_count)
            relation_count += 1
        if not triple[ENTITY_2] in entity_map:
            entity_map[triple[ENTITY_2]] = str(entity_count)
            entity_count += 1

    return entity_map, relation_map

def create_splits(data, set_of_data, sub_dir, config):
    if config[TYPE_SPLIT] == RANDOM:
        random_splits(data, set_of_data, sub_dir, config)
    else:
        sys.exit(1)

def random_splits(data, set_of_data, sub_dir, config):

    # Settings used for splitting the data
    split_num = config[SPLITS]
    percent_train = config[PERCENT_TRAIN]
    percent_valid = config[PERCENT_VALID]
    false_triple_ratio = config[FALSE_TRIP_RATIO]

    # Copy of valid triples used to allow each split to creat
    permanent_set_of_data = set_of_data
    for i in range(0, split_num):

        # Lists used to store output
        train = []
        test = []
        valid = []

        # Set of entities unique to each split
        test_entities = set()
        train_entities = set()
        valid_entities = set()

        # Reset set of data for checking negative triples
        set_of_data = copy.deepcopy(permanent_set_of_data)

        # Generate split paths
        train_path, test_path, valid_path = create_split_path(sub_dir, i)

        # Split each line into a train or test file
        for line in range(0,  len(data)):
            choose_split = random.random()

            # Assigns a triple by comparing the random value to the percent
            # of data to be assigned to the training split
            if(choose_split <= percent_train):
                train.append([data[line][ENTITY_1], data[line][RELATION], data[line][ENTITY_2], '1'])
                # Add the entities in the triple to the set of entities seen,
                # which are used for negative triple generation
                train_entities.update([data[line][ENTITY_1], data[line][ENTITY_2]])
            elif(choose_split <= (percent_train + percent_valid)):
                valid.append([data[line][ENTITY_1], data[line][RELATION], data[line][ENTITY_2], '1'])
                # Add the entities in the triple to the set of entities seen,
                # which are used for negative triple generation
                valid_entities.update([data[line][ENTITY_1], data[line][ENTITY_2]])
            else:
                test.append([data[line][ENTITY_1], data[line][RELATION], data[line][ENTITY_2], '1'])
                # Add the entities in the triple to the set of
                # entities used in negative triple generation
                test_entities.update([data[line][ENTITY_1], data[line][ENTITY_2]])

        # Generate negative test and train triples and add them to the list of triples
        train.extend(generate_negatives(train, list(train_entities), set_of_data, false_triple_ratio))
        test.extend(generate_negatives(test, list(test_entities), set_of_data, false_triple_ratio))
        valid.extend(generate_negatives(valid, list(valid_entities), set_of_data, false_triple_ratio))

        write_data(train, train_path)
        write_data(test, test_path)
        write_data(valid, valid_path)

# Generates false triples, while avoiding duplicates
def generate_negatives(data, entity_list, set_of_data, false_triple_ratio):
    negatives = []

    # Generate a negative triple for each element in the list
    for line in data:
        # Repeat for the ratio of negative triples to positive ones
        for _ in range(0, false_triple_ratio):

            # Select a random entity from the list of entities
            negative_entity = random.choice(entity_list)

            # If the new triple is either valid or has already been created,
            # pick a new negative entity
            while (line[ENTITY_1], line[RELATION], negative_entity) in set_of_data:
                negative_entity = random.choice(entity_list)

            # Add the new triple to the set to avoid duplicates in the same split
            set_of_data.add((line[ENTITY_1], line[RELATION], negative_entity))

            # Append triple to the list of negative data
            negatives.append([line[ENTITY_1], line[RELATION], negative_entity, '0'])
    return negatives

def write_data(data, file_path):
    with open(file_path, 'w+') as out_file:
        # if list is empty
        if not data:
            return
        # if list of lists
        if isinstance(data[0], list):
            out_file.write('\n'.join(["\t".join(current_list) for current_list in data]))
        # else regular list
        else:
            out_file.write('\n'.join(data))

def create_split_path(sub_dir, split_num):
    # Create split directory
    split_dir = os.path.join(sub_dir, str(split_num))
    # Todo: split dir is replaced in main. Is this check unecessary?
    if os.path.isdir(split_dir) is False:
        os.mkdir(split_dir)

    # Generate train and test paths for the split
    train_path = os.path.join(split_dir, TRAIN)
    test_path = os.path.join(split_dir, TEST)
    valid_path = os.path.join(split_dir, VALID)

    return train_path, test_path, valid_path

if __name__ == "__main__":
    main()
