#!bin/usr/env python3

import json
import os
import math
import shutil
import sys
import random

ENTITY_MAP =  "psl/data/kge/entity_map.txt"
RELATION_MAP =  "psl/data/kge/relation_map.txt"
ENTITY_DIM = "psl/cli/inferred-predicates/ENTITYDIM"
RELATION_DIM = "psl/cli/inferred-predicates/RELATIONDIM"
PSL_DATA_DIR = "psl/data/kge/"
TRUEBLOCK_DIR = "/eval/trueblock_obs.txt"
FALSEBLOCK_DIR = "/eval/falseblock_obs.txt"
POS_OUTPUT_DIR = "positive_evaluated_triples.txt"
NEG_OUTPUT_DIR = "negative_evaluated_triples.txt"

TXT = ".txt"
DATA = "data"
DIMENSIONS = "dimensions"
MAP_INPUT = "map_input"
TEST_FILE = "/test.txt"
DATASET = "dataset"

SPLIT_NO = "0"

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
MAPE_DIR = os.path.join(os.path.dirname(BASE_DIR), ENTITY_MAP)
MAPR_DIR = os.path.join(os.path.dirname(BASE_DIR), RELATION_MAP)

ENTITY_DIR = os.path.join(os.path.dirname(BASE_DIR), ENTITY_DIM)
RELATION_DIR = os.path.join(os.path.dirname(BASE_DIR), RELATION_DIM)
DATA_DIR = os.path.dirname(BASE_DIR)

def load_mappings(file_name, key, value):
    map = {}
    map_file = open(file_name)
    for line in map_file:
        map[line.strip('\n').split('\t')[key]] = line.strip('\n').split('\t')[value]
    map_file.close()
    return map

def write_data(data, file_path):
	with open(file_path, 'w+') as out_file:
		# if list of lists
		if isinstance(data[0], list):
			out_file.write('\n'.join(["\t".join(current_list) for current_list in data]))
		# else regular list
		else:
			out_file.write('\n'.join(data))

def eval_triple(mapped_e1 , mapped_e2, mapped_rel, dimensions, ent_embeddings, rel_embeddings):
    sum = 0
    for dim in range(1, dimensions+1):
        try:
            e1_num = ent_embeddings[dim-1][mapped_e1]
            e2_num = ent_embeddings[dim-1][mapped_e2]
            rel_num = rel_embeddings[dim-1][mapped_rel]
        except Exception:
            e1_num = 1
            e2_num = 1
            rel_num = 0
        value = float(e1_num) + float(rel_num) - float(e2_num)

        sum += value*value
    return math.sqrt(sum)

# ent_list is a list mapped entities where each entity is of type string
def link_prediction(ent_embeddings, rel_embeddings, ent_list, mapped_e1, mapped_rel, mapped_e2):
    original_triple = (mapped_e1, mapped_rel, mapped_e2)
    ranking_list = []
    dimensions = len(ent_embeddings)
    for ent in ent_list:
        corrupted_e1 = ent
        score = eval_triple(corrupted_e1, mapped_e2, mapped_rel, dimensions, ent_embeddings, rel_embeddings)
        ranking_list.append((score, corrupted_e1))
    ranking_list.sort(key=lambda x: x[0], reverse=True)
    return ranking_list

def load_data(config):
    data = []
    entities = set()
    set_of_data = set()

    data_fd =  open(config[DATA], 'r')

    # Read input file into a list of lines and a set of all entities seen
    for line in data_fd:
        data.append(line.strip('\n').split('\t'))
        set_of_data.add(tuple(line.strip('\n').split('\t')))
        entities.add(line.strip('\n').split('\t')[2])
    entity_list = list(entities)

    data_fd.close()
    return data, entity_list, set_of_data

def test_all(config, entity_mapping, relation_mapping):
    TRUE_DIR = os.path.join(DATA_DIR, PSL_DATA_DIR + SPLIT_NO + TRUEBLOCK_DIR)
    FALSE_DIR = os.path.join(DATA_DIR, PSL_DATA_DIR + SPLIT_NO + FALSEBLOCK_DIR)

    dimensions = config[DIMENSIONS]
    pos_sum = 0

    trip_fd = open(TRUE_DIR)
    triples = []
    eval_data = []
    for line in trip_fd:
        triples.append(line.strip('\n').split('\t'))
    trip_fd.close()

    ent_embeddings = []
    rel_embeddings = []
    for dim in range(1, dimensions+1):
        ent_embeddings.append(load_mappings(ENTITY_DIR + str(dim) + TXT, 0, 1))
        rel_embeddings.append(load_mappings(RELATION_DIR + str(dim) + TXT, 0, 1))

    for triple in triples:
        mapped_e1 = triple[0]
        mapped_e2 = triple[2]
        mapped_rel = triple[1]

        eval = eval_triple(mapped_e1 , mapped_e2, mapped_rel, dimensions, ent_embeddings, rel_embeddings)
        pos_sum+= eval
        triple.append(str(eval))
        eval_data.append(triple)

    write_data(eval_data, POS_OUTPUT_DIR)
    print("Positive triples total sum is: " +str(pos_sum))
    print("Positive triples average is: " +str(pos_sum/len(triples)) + "\n")

    trip_fd = open(FALSE_DIR)
    triples = []
    eval_data = []
    neg_sum = 0
    for line in trip_fd:
        triples.append(line.strip('\n').split('\t'))
    trip_fd.close()

    for triple in triples:
        mapped_e1 = triple[0]
        mapped_e2 = triple[2]
        mapped_rel = triple[1]

        eval = eval_triple(mapped_e1 , mapped_e2, mapped_rel, dimensions, ent_embeddings, rel_embeddings)
        neg_sum += eval
        triple.append(str(eval))
        eval_data.append(triple)
    write_data(eval_data, NEG_OUTPUT_DIR)
    print("Negative triples total sum is: " +str(neg_sum))
    print("Negative triples average is: " +str(neg_sum/len(triples)))

def main(config, test_triple):

    data, entity_list, set_of_data = load_data(config)
    (e1, rel, e2) = test_triple
    dimensions = config[DIMENSIONS]

    if test_triple in set_of_data:
        print("Valid Triple")
    else:
        print("Corrupted Triple")

    if(config[MAP_INPUT] == 1):
        entity_mapping = load_mappings(MAPE_DIR, 1, 0)
        relation_mapping = load_mappings(MAPR_DIR, 1, 0)

        mapped_e1 = entity_mapping[e1]
        mapped_e2 = entity_mapping[e2]
        mapped_rel = relation_mapping[rel]
    else:
        mapped_e1 = e1
        mapped_e2 = e2
        mapped_rel = rel

    # Get entity and relation embeddings for each dimension
    ent_embeddings = []
    rel_embeddings = []

    # ent_embeddings is a list of dictionaries
    for dim in range(1, dimensions+1):
        ent_embeddings.append(load_mappings(ENTITY_DIR + str(dim) + TXT, 0, 1))
        rel_embeddings.append(load_mappings(RELATION_DIR + str(dim) + TXT, 0, 1))

    eval = eval_triple(mapped_e1 , mapped_e2, mapped_rel, dimensions, ent_embeddings, rel_embeddings)
    print("TransE Evaluation Function : " + str(eval) + "\n")

    test_all(config, entity_mapping, relation_mapping)

def _load_args(args):
    executable = args.pop(0)
    if len(args) != 4 or ({'h','help'} & {arg.lower().strip().replace('-', '') for arg in args}):
        print("USAGE: python3 %s <config.json> original_entity1 original_relation original_entity2" % executable, file = sys.stderr)
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
