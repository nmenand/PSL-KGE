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
    data_path, config_path = parse_args(sys.argv)

    # Load data from arguments
    config, data, entity_list = load_data(data_path, config_path)

    #Set the Seed
    seed = config["seed"]
    random.seed(seed)


    # Create splits directory
    current_dir = os.path.dirname(os.path.realpath(__file__))
    dataset_dir = os.path.join(os.path.dirname(current_dir), config["dataset"])
    sub_dir = os.path.join(dataset_dir, "splits")
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

def load_data(data_file, config_file):
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

    data_fd.close()
    config_fd.close()

    return config, data, entity_list

def create_splits(data, entity_list, sub_dir, config):

    # Extract necessary variables to be able to create k splits
    split_num = config["splits"]
    percent_train = config["percent_train"]
    percent_test = round(1 - percent_train, 2)
    train_bound = math.floor(percent_train * len(data))
    false_triple_ratio =  config["false_triples_ratio"]

    for i in range(0, split_num):

    # Lists used to store output
        train = ''
        test = ''
        negative_test = ''
        negative_train = ''
        # Shuffle data to generate random split
        random.shuffle(data)

        #Generate split paths
        train_path, test_path, neg_test_path, neg_train_path = create_split_path(sub_dir, i)

        #Create train split
        for line in range(0,  len(data)):
            choose_split  = random.random()
            if(choose_split >= percent_test):
                train += (data[line][0] + '\t' + data[line][1] + '\t' + data[line][2] + '\n')
                #Generate Negative Triples
                current_negative_triples = [data[line][2]]
                negative_train += generate_negatives(data, line, entity_list, false_triple_ratio, current_negative_triples)
            else:
                test += (data[line][0] + '\t' + data[line][1] + '\t' + data[line][2] + '\n')
                #Generate Negative Triples
                current_negative_triples = [data[line][2]]
                negative_test += generate_negatives(data, line, entity_list, false_triple_ratio, current_negative_triples)

        write_out(train, train_path)
        write_out(negative_train, neg_train_path)
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
