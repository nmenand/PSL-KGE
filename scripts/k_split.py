#!bin/usr/env python3

import os
import sys
import json
import math
import random

# Get command line arguments
# datafile contains all data to be split
def main():

    # Read arguments
    data_file, config_file = parse_args(sys.argv)

    # Load data from arguments
    config, data, entity_list = read_data(data_file, config_file)

    # Create splits directory
    current_dir = os.path.dirname(os.path.realpath(__file__))
    sub_dir = os.path.join(current_dir, "../splits")
    os.mkdir(sub_dir)

    # Generate and write each split
    create_splits(data, entity_list, sub_dir, config)


def parse_args(args):
    if(len(args) != 3):
        print("Usage: gen_splits.sh path_to_data_file path_to_config_file")
        sys.exit(1)

    data_file = args[1]
    config_file = args[2]
    return data_file, config_file

def read_data(data_file, config_file):
    data_fd =  open(data_file, 'r')
    config_fd = open(config_file, 'r')

    config = json.load(config_fd)
    data = []
    entities = set()

    # Read input file into a list of lines and a set of all entities seen
    for line in data_fd:
        data.append(line.strip('\n').split('\t'))
        entities.add(line.strip('\n').split('\t')[2])
    entity_list = list(entities)

    return config, data, entity_list

def create_splits(data, entity_list, sub_dir, config):

    # Extract necessary variables to be able to create k splits
    split_num = config["splits"]
    seed = config["seed"]
    percent_train = config["percent_train"]/100
    percent_test = round(1 - percent_train, 2)
    data_len = len(data)
    train_bound = math.floor(percent_train * data_len)
    false_triple_ratio =  config["false_triples_ratio"]
    random.seed(seed)

    # Lists used to store output
    train = ''
    test = ''
    negative_test = ''
    negative_train = ''

    for i in range(1, split_num+1):
        # Shuffle data to generate random split
        random.shuffle(data)

        #Generate split paths
        train_path, test_path, neg_test_path, neg_train_path = create_split_path(sub_dir, i)

        #Create train split
        for line in range(0, train_bound):
            train += (data[line][0] + '\t' + data[line][1] + '\t' + data[line][2] + '\n')
            #Generate Negative Triples
            current_negative_triples = [data[line][2]]
            negative_train += generate_negatives(data, line, entity_list, false_triple_ratio, current_negative_triples)

        write_out(train, train_path)
        write_out(negative_train, neg_train_path)

        # Create test split
        for line in range(train_bound, data_len):
            test += (data[line][0] + '\t' + data[line][1] + '\t' + data[line][2] + '\n')
            #Generate Negative Triples
            current_negative_triples = [data[line][2]]
            negative_test += generate_negatives(data, line, entity_list, false_triple_ratio, current_negative_triples)

        write_out(test, test_path)
        write_out(negative_test, neg_test_path)

def generate_negatives(data, line, entity_list, false_triple_ratio, current_negative_triples):
    negatives = ''

    #Pick random entities for false triples, while avoiding duplicates
    for _ in range(0, false_triple_ratio):
        negative_entity = random.choices(entity_list)
        #If entity is already in a false triple keep choosing
        while negative_entity[0] in current_negative_triples:
            negative_entity = random.choices(entity_list)
        #Append entity to the list and continue
        current_negative_triples.append(negative_entity[0])
        negatives += (data[line][0] + '\t' + data[line][1] + '\t'+ negative_entity[0] + '\n')
    return negatives

def write_out(data, path):
    path_fd = open(path, 'w+')
    path_fd.write(data)
    path_fd.close()

def create_split_path(sub_dir, split_num):
    #Create split directory
    split_dir  = os.path.join(sub_dir, "split" + str(split_num))
    os.mkdir(split_dir)

    #Generate all sub paths for the split
    train_file = 'split' + str(split_num) + '_' + 'train' + '.txt'
    test_file = 'split' + str(split_num) + '_' + 'test' + '.txt'
    neg_test_file = 'split' + str(split_num) + '_' + 'negative_test' + '.txt'
    neg_train_file = 'split' + str(split_num) + '_' + 'negative_train' + '.txt'
    train_path = os.path.join(split_dir, train_file)
    test_path = os.path.join(split_dir, test_file)
    neg_test_path = os.path.join(split_dir, neg_test_file)
    neg_train_path = os.path.join(split_dir, neg_train_file)

    return train_path, test_path, neg_test_path, neg_train_path

if __name__ == "__main__":
    main()
