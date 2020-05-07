#!bin/usr/env python3

import json
import os
import sys

from link_prediction import predict_links

ENTITY_DIM = "psl/cli/inferred-predicates/ENTITYDIM"
RELATION_DIM = "psl/cli/inferred-predicates/RELATIONDIM"
PSL_DATA_DIR = "psl/data/kge/"
ENTITY_DIR = ""
TRUEBLOCK_DIR = "/learn/trueblock_obs.txt"
TRAINBLOCK_DIR = "/eval/trueblock_obs.txt"
FALSEBLOCK_DIR = "/learn/falseblock_obs.txt"
POS_OUTPUT_DIR = "positive_evaluated_triples.txt"
NEG_OUTPUT_DIR = "negative_evaluated_triples.txt"

TXT = ".txt"
DIMENSIONS = "dimensions"
SPLIT_NO = "0"

ENTITY_1 = 0
RELATION = 1
ENTITY_2 = 2
# 0 for L1 Norm 1 for L2 norm
NORM_TYPE = 0

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

ENTITY_DIR = os.path.join(os.path.dirname(BASE_DIR), ENTITY_DIM)
RELATION_DIR = os.path.join(os.path.dirname(BASE_DIR), RELATION_DIM)
DATA_DIR = os.path.dirname(BASE_DIR)
TRUE_DIR = os.path.join(DATA_DIR, PSL_DATA_DIR + SPLIT_NO + TRUEBLOCK_DIR)
REST_OF_DATA_DIR = os.path.join(DATA_DIR, PSL_DATA_DIR + SPLIT_NO + TRAINBLOCK_DIR)
FALSE_DIR = os.path.join(DATA_DIR, PSL_DATA_DIR + SPLIT_NO + FALSEBLOCK_DIR)

def load_embeddings(file_name, key, value):
    mapping = {}
    with open(file_name) as map_file:
        for line in map_file:
            mapping[line.strip('\n').split('\t')[key]] = line.strip('\n').split('\t')[value]
    return mapping

def write_data(data, file_path):
    with open(file_path, 'w+') as out_file:
        if data:
            # if list of lists
            if isinstance(data[0], list):
                out_file.write('\n'.join(["\t".join(current_list) for current_list in data]))
                # else regular list
            else:
                out_file.write('\n'.join(data))

def load_data(config):
    data = []
    entities = set()
    set_of_data = set()

    TRUE_DIR = os.path.join(DATA_DIR, PSL_DATA_DIR + SPLIT_NO + TRUEBLOCK_DIR)
    REST_OF_DATA_DIR = os.path.join(DATA_DIR, PSL_DATA_DIR + SPLIT_NO + TRAINBLOCK_DIR)
    FALSE_DIR = os.path.join(DATA_DIR, PSL_DATA_DIR + SPLIT_NO + FALSEBLOCK_DIR)
    with open(TRUE_DIR, 'r') as data_fd:
        # Read input file into a list of lines and a set of all entities seen
        for line in data_fd:
            line_data = line.strip('\n').split('\t')
            data.append(line_data)
            set_of_data.add(tuple(line_data))
            entities.update([line_data[0], line_data[2]])
    with open(REST_OF_DATA_DIR, 'r') as data_fd:
        for line in data_fd:
            line_data = line.strip('\n').split('\t')
            set_of_data.add(tuple(line_data))
            entities.update([line_data[0], line_data[2]])

    entity_list = list(entities)

    return data, entity_list, set_of_data

# Returns the L1 and L2 norms centered around 0
def eval_triple(mapped_e1 , mapped_e2, mapped_rel, dimensions, ent_embeddings, rel_embeddings):
    L1_norm = 0
    L2_norm = 0
    for dim in range(1, dimensions+1):
        try:
            e1_num = float(ent_embeddings[dim-1][mapped_e1])
            e2_num = float(ent_embeddings[dim-1][mapped_e2])
            rel_num = float(rel_embeddings[dim-1][mapped_rel])
            value = e1_num + rel_num - e2_num
            L2_norm += value**2
            L1_norm += abs(value)
        except:
            # Catch key errors if unseen ent/rel
            return None, None
    return L1_norm, L2_norm**(0.5)

def eval_list(dimensions, triples, ent_embeddings, rel_embeddings):
    total_sum = 0
    total_energy = 0
    for triple in triples:
        mapped_e1 = triple[ENTITY_1]
        mapped_e2 = triple[ENTITY_2]
        mapped_rel = triple[RELATION]

        L1_norm, L2_norm = eval_triple(mapped_e1 , mapped_e2, mapped_rel, dimensions, ent_embeddings, rel_embeddings)
        if L1_norm is not None:
            triple.append(str(L1_norm))
            total_sum += L1_norm/dimensions
            total_energy += L2_norm
    return total_sum, total_energy

def test_all(dimensions, ent_embeddings, rel_embeddings):

    triples = []
    with open(TRUE_DIR, 'r') as trip_fd:
        for line in trip_fd:
            triples.append(line.strip('\n').split('\t'))

    pos_sum, pos_energy = eval_list(dimensions, triples, ent_embeddings, rel_embeddings)

    write_data(triples, POS_OUTPUT_DIR)
    print("Positive triples total sum is: " + str(pos_sum))
    print("Positive triples L1 is: " + str(pos_sum/len(triples)))
    print("Positive triples L2 is: " + str(pos_energy/len(triples)) + "\n")

    triples = []
    with open(FALSE_DIR, 'r') as trip_fd:
        for line in trip_fd:
            triples.append(line.strip('\n').split('\t'))
    if(len(triples) > 0):
        neg_sum, neg_energy = eval_list(dimensions, triples, ent_embeddings, rel_embeddings)

        write_data(triples, NEG_OUTPUT_DIR)
        print("Negative triples total sum is: " + str(neg_sum))
        print("Negative triples L1 is: " + str(neg_sum/len(triples)))
        print("Negative triples L2 is: " + str(neg_energy/len(triples)) + "\n")

def main(config):

    data, entity_list, set_of_data = load_data(config)
    dimensions = config[DIMENSIONS]

    ent_embeddings = []
    rel_embeddings = []
    for dim in range(1, dimensions+1):
        ent_embeddings.append(load_embeddings(ENTITY_DIR + str(dim) + TXT, 0, 1))
        rel_embeddings.append(load_embeddings(RELATION_DIR + str(dim) + TXT, 0, 1))

    test_all(dimensions, ent_embeddings, rel_embeddings)

    predict_links(ent_embeddings, rel_embeddings, entity_list, data[0:5000], set_of_data)

def _load_args(args):
    executable = args.pop(0)
    if (len(args) != 1 or ({'h','help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 %s <config.json> original_entity1 original_relation original_entity2" % executable, file = sys.stderr)
        sys.exit(1)

    config_file = args.pop(0)
    with open(config_file, 'r') as config_fd:
        config = json.load(config_fd)
    return config

if __name__ == '__main__':
    config = _load_args(sys.argv)
    main(config)
