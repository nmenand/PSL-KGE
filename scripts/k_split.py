#!bin/usr/env python3

import copy
import json
import math
import os
import sys
import random

current_dir = os.path.dirname(os.path.realpath(__file__))

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

# Get command line arguments
# datafile contains all data to be split
def main():

    # Read arguments
    config_path = parse_args(sys.argv)

    # Load data from arguments
    config, data, entity_list, set_of_data = load_data(config_path)

    # Set the Seed
    seed = config[SEED]
    random.seed(seed)

    # Create splits directory
    dataset_dir = os.path.join(os.path.dirname(current_dir), config[DATASET])
    raw_splits_dir = os.path.join(os.path.dirname(current_dir), DATAFILE)
    if os.path.isdir(raw_splits_dir) is False:
        os.mkdir(raw_splits_dir)

    sub_dir = os.path.join(raw_splits_dir, config[DATASET])
    if os.path.isdir(sub_dir) is False:
        os.mkdir(sub_dir)

    # Generate and write each split
    create_splits(data, entity_list, set_of_data, sub_dir, config)

def parse_args(args):
    args.pop(0)

    if(len(args) != 1 or ({'h','help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("Usage: python3 gen_splits.py <path_to_config_file>")
        sys.exit(1)

    config_file = args.pop(0)
    return config_file

def load_data(config_file):
    config_fd = open(config_file, 'r')

    config = json.load(config_fd)
    data = []
    entities = set()
    set_of_data = set()

    data_fd =  open(config[DATAFILE], 'r')

    # Read input file into a list of lines and a set of all entities seen
    for line in data_fd:
        line_data = line.strip('\n').split('\t')
        data.append(line_data)
        set_of_data.add(tuple(line_data))
        entities.add(line_data[ENTITY_1])
        entities.add(line_data[ENTITY_2])
    entity_list = list(entities)

    data_fd.close()
    config_fd.close()

    return config, data, entity_list, set_of_data

def create_splits(data, entity_list, set_of_data, sub_dir, config):
    if config[TYPE_SPLIT] == RANDOM:
        random_splits(data, entity_list, set_of_data, sub_dir, config)
    else:
        sys.exit(1)

def random_splits(data, entity_list, set_of_data, sub_dir, config):
    split_num = config[SPLITS]
    percent_train = config[PERCENT_TRAIN]
    percent_test = round(1 - percent_train, 2)
    false_triple_ratio =  config[FALSE_TRIP_RATIO]
    permanent_set_of_data = set_of_data
    for i in range(0, split_num):

    # Lists used to store output
        train = []
        test = []
        # Shuffle data to generate random split
        random.shuffle(data)

        #reset set of data for checking negative triples
        set_of_data = copy.deepcopy(permanent_set_of_data)
        print(len(set_of_data))
        #Generate split paths
        train_path, test_path = create_split_path(sub_dir, i)

        #Create train split
        for line in range(0,  len(data)):
            choose_split  = random.random()
            if(choose_split >= percent_test):
                train.append([data[line][ENTITY_1], data[line][RELATION],  data[line][ENTITY_2], '1'])
                #Generate Negative Triples
                train.extend(generate_negatives(data, line, entity_list, set_of_data, false_triple_ratio))
            else:
                test.append([data[line][ENTITY_1], data[line][RELATION],  data[line][ENTITY_2], '1'])
                #Generate Negative Triples
                test.extend(generate_negatives(data, line, entity_list, set_of_data, false_triple_ratio))

        write_out(train, train_path)
        write_out(test, test_path)

def generate_negatives(data, line, entity_list, set_of_data, false_triple_ratio):
    negatives = []

    #Pick random entities for false triples, while avoiding duplicates
    for _ in range(0, false_triple_ratio):
        negative_entity = random.choice(entity_list)
        #If entity is already in a false triple keep choosing
        while (data[line][ENTITY_1], data[line][RELATION], negative_entity[0]) in set_of_data:
            negative_entity = random.choices(entity_list)

        #Append entity to the list and continue
        set_of_data.add((data[line][ENTITY_1], data[line][RELATION], negative_entity[0]))
        negatives.append([data[line][ENTITY_1], data[line][RELATION], negative_entity[0], '0'])
    return negatives

def write_out(data, file_path):
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

    #Generate all sub paths for the split
    train_file = TRAIN
    test_file = TEST
    train_path = os.path.join(split_dir, train_file)
    test_path = os.path.join(split_dir, test_file)
    return train_path, test_path

if __name__ == "__main__":
    main()
