#!bin/usr/env python3

import copy
import json
import math
import os
import sys
import random

RANDOM = "random"
SPLIT = 'split'

SEED = 'seed'
SPLITS = 'splits'
DATASET = 'dataset'
DATAFILE = 'data'
PERCENT_TRAIN = 'percent_train'
FALSE_TRIP_RATIO = 'false_triples_ratio'
TYPE_SPLIT = 'type_split'

TRAIN = 'train.txt'
TEST =  'test.txt'

ENTITY_1 = 0
ENTITY_2 = 2
RELATION = 1

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
RAW_SPLITS_DIR = os.path.join(os.path.dirname(CURRENT_DIR), DATAFILE)

def main():

    # Read arguments
    config_path = parse_args(sys.argv)

    # Load data from arguments
    config, data, set_of_data = load_data(config_path)

    # Set the Seed
    seed = config[SEED]
    random.seed(seed)

    # Create splits directory
    dataset_dir = os.path.join(os.path.dirname(CURRENT_DIR), config[DATASET])
    if os.path.isdir(RAW_SPLITS_DIR) is False:
        os.mkdir(RAW_SPLITS_DIR)

    # Create a directory for the specific dataset
    sub_dir = os.path.join(RAW_SPLITS_DIR, config[DATASET])
    if os.path.isdir(sub_dir) is False:
        os.mkdir(sub_dir)

    # Generate and write each split
    create_splits(data, set_of_data, sub_dir, config)

# Check and return arguments
def parse_args(args):
    args.pop(0)

    if(len(args) != 1 or ({'h','help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("Usage: python3 gen_splits.py <path_to_config_file>")
        sys.exit(1)

    config_file = args.pop(0)
    return config_file

# Returns Config and the dataset as a list of
# lists and a set used for checking negative data
def load_data(config_file):
    config_fd = open(config_file, 'r')

    config = json.load(config_fd)
    config_fd.close()
    data = []
    set_of_data = set()

    data_fd =  open(config[DATAFILE], 'r')

    # Read input file into a list of lines and a set of all entities seen
    for line in data_fd:
        line_data = line.strip('\n').split('\t')
        data.append(line_data)
        set_of_data.add(tuple(line_data))

    data_fd.close()

    return config, data, set_of_data

def create_splits(data, set_of_data, sub_dir, config):
    if config[TYPE_SPLIT] == RANDOM:
        random_splits(data, set_of_data, sub_dir, config)
    else:
        sys.exit(1)

def random_splits(data, set_of_data, sub_dir, config):

    # Settings used for splitting the data
    split_num = config[SPLITS]
    percent_train = config[PERCENT_TRAIN]
    false_triple_ratio =  config[FALSE_TRIP_RATIO]

    # Copy of valid triples used to allow each split to creat
    permanent_set_of_data = set_of_data
    for i in range(0, split_num):

        # Lists used to store output
        train = []
        test = []

        # Set of entities unique to each split
        test_entities = set()
        train_entities = set()

        #reset set of data for checking negative triples
        set_of_data = copy.deepcopy(permanent_set_of_data)

        #Generate split paths
        train_path, test_path = create_split_path(sub_dir, i)

        # Split each line into a train or test file
        for line in range(0,  len(data)):
            choose_split  = random.random()

            # Assigns a triple by comparing the random value to the percent
            # of data to be assigned to the training split
            if(choose_split <= percent_train):
                train.append([data[line][ENTITY_1], data[line][RELATION],  data[line][ENTITY_2], '1'])
                # Add the entities in the triple to the set of
                # entities used in negative triple generation
                train_entities.add(data[line][ENTITY_1])
                train_entities.add(data[line][ENTITY_2])
            else:
                test.append([data[line][ENTITY_1], data[line][RELATION],  data[line][ENTITY_2], '1'])
                # Add the entities in the triple to the set of
                # entities used in negative triple generation
                test_entities.add(data[line][ENTITY_1])
                test_entities.add(data[line][ENTITY_2])

        # Generate negative test and train triples and add them to the list of triples
        train.extend(generate_negatives(train, list(train_entities), set_of_data, false_triple_ratio))
        test.extend(generate_negatives(test, list(test_entities), set_of_data, false_triple_ratio))

        write_list(train, train_path)
        write_list(test, test_path)

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

def write_list(data, file_path):
    with open(file_path, 'w+') as out_file:
        # if list of lists
        if isinstance(data[0], list):
            out_file.write('\n'.join(["\t".join(current_list) for current_list in data]))
        # else regular list
        else:
            out_file.write('\n'.join(data))

def create_split_path(sub_dir, split_num):
    #Create split directory
    split_dir  = os.path.join(sub_dir, str(split_num))
    isdir = os.path.isdir(split_dir)
    if isdir is False:
        os.mkdir(split_dir)

    #Generate train and test paths for the split
    train_path = os.path.join(split_dir, TRAIN)
    test_path = os.path.join(split_dir, TEST)
    return train_path, test_path

if __name__ == "__main__":
    main()
