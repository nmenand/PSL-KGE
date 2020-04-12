#!bin/usr/env python3

import json
import os
import math
import shutil
import sys
import random

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
MAPE_DIR = os.path.join(os.path.dirname(BASE_DIR), "psl/data/kge/entity_map.txt")
MAPR_DIR = os.path.join(os.path.dirname(BASE_DIR), "psl/data/kge/relation_map.txt")

ENTITY_DIR = os.path.join(os.path.dirname(BASE_DIR), "psl/cli/ENTITYDIM")
RELATION_DIR = os.path.join(os.path.dirname(BASE_DIR), "psl/cli/RELATIONDIM")
TXT = ".txt"

def load_data(config):

    data = []
    entities = set()
    set_of_data = set()

    data_fd =  open(config['data'], 'r')

    # Read input file into a list of lines and a set of all entities seen
    for line in data_fd:
        data.append(line.strip('\n').split('\t'))
        set_of_data.add(tuple(line.strip('\n').split('\t')))
        entities.add(line.strip('\n').split('\t')[2])
    entity_list = list(entities)

    data_fd.close()

    return data, entity_list, set_of_data

def main(config, test_triple):
    data, entity_list, set_of_data = load_data(config)
    (e1, rel, e2) = test_triple
    if test_triple in set_of_data:
        print("Expected Value: 0")
    else:
        print("Expected Value: 1.0")

    entity_mapping = {}
    relation_mapping = {}

    mape = open(MAPE_DIR)
    mapr = open(MAPR_DIR)
    for line in mape:
        entity_mapping[line.strip('\n').split('\t')[1]] = line.strip('\n').split('\t')[0]
    for line in mapr:
        relation_mapping[line.strip('\n').split('\t')[1]] = line.strip('\n').split('\t')[0]
    mape.close()
    mapr.close()
    m_e1 = entity_mapping[e1]
    m_e2 = entity_mapping[e2]
    m_rel = relation_mapping[rel]
    sum = 0

    for dim in range(1,config['dimensions']+1):
        entity_num = {}
        relation_num = {}
        efd = open(ENTITY_DIR + str(dim) + TXT)
        rfd = open(RELATION_DIR + str(dim) + TXT)
        for line in efd:
            entity_num[line.strip('\n').split('\t')[0]] = line.strip('\n').split('\t')[1]
        for line in rfd:
            relation_num[line.strip('\n').split('\t')[0]] = line.strip('\n').split('\t')[1]
        efd.close()
        rfd.close()
        e1_num = entity_num[m_e1]
        e2_num = entity_num[m_e2]
        rel_num = relation_num[m_rel]
        value = float(e1_num) + float(rel_num) - float(e2_num)
        sum += value*value
        print("Dim" + str(dim) +" Actual Value: " + str(value))
    eval = 1 - 1/(3*math.sqrt(config['dimensions'])) * math.sqrt(sum)
    print("TransE Evaluation Function : " + str(eval))
def _load_args(args):
    executable = args.pop(0)
    if len(args) != 4:
        print("USAGE: python3 %s <config.json>" % executable, file = sys.stderr)
        sys.exit(1)

    config_file = args.pop(0)
    with open(config_file, 'r') as config_fd:
        config = json.load(config_fd)
        entity1 = args.pop(0)
        relation = args.pop(0)
        entity2 = args.pop(0)
        triple = (str(entity1), str(relation), str(entity2))

        return config, triple

if __name__ == '__main__':
	config, test_triple = _load_args(sys.argv)
	main(config, test_triple)
