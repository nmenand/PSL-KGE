#!bin/usr/env python3
from statistics import median
from math import fabs

SCORE_INDEX = 0
# Returns the L1 and L2 norms centered around 0
def eval_triple(mapped_e1 , mapped_e2, mapped_rel, dimensions, ent_embeddings, rel_embeddings, _fabs = fabs):
    L1_norm = 0
    for dim in range(1, dimensions+1):
        try:
            e1_num = ent_embeddings[dim-1][mapped_e1]
            e2_num = ent_embeddings[dim-1][mapped_e2]
            rel_num = rel_embeddings[dim-1][mapped_rel]
            L1_norm += _fabs(e1_num + rel_num - e2_num)
        except KeyError:
            return -1
    return L1_norm

# generate rankings
def generate_link_ranking(ent_embeddings, rel_embeddings, num_entities, mapped_e1, mapped_rel, mapped_e2, set_of_data):
    rank = 1
    dimensions = len(ent_embeddings)
    # Keep track of evaluated triples as to not compute them twice
    valid_triple_score = eval_triple(mapped_e1, mapped_e2, mapped_rel, dimensions, ent_embeddings, rel_embeddings)
    if valid_triple_score != -1:
        for corrupted_ent in range(0,num_entities):
            # Corrupt head
            if (corrupted_ent, mapped_rel, mapped_e2) not in set_of_data:
                score = eval_triple(corrupted_ent, mapped_e2, mapped_rel, dimensions, ent_embeddings, rel_embeddings)
                if score != -1:
                    if score < valid_triple_score:
                        rank+=1
            # Corrupt tail
            if (mapped_e1, mapped_rel, corrupted_ent) not in set_of_data:
                score = eval_triple(mapped_e1, corrupted_ent, mapped_rel, dimensions, ent_embeddings, rel_embeddings)
                if score != -1:
                    if score < valid_triple_score:
                        rank+=1
        return rank
    return -1

def predict_links(ent_embeddings, rel_embeddings, num_entities, test_list, set_of_data, rel_list):
    list_of_ranks = []
    total_reciprocal_rank = 0
    hits_at_1 = 0
    hits_at_3 = 0
    hits_at_5 = 0
    hits_at_10 = 0
    num_skipped = 0
    for (e1, rel, e2) in test_list:
        curr_rank = generate_link_ranking(ent_embeddings, rel_embeddings, num_entities, e1, rel, e2, set_of_data)
        if curr_rank != -1:
            #curr_rank = rank #eval_link_ranking(set_of_data, (e1, rel, e2), ranking_list)
            list_of_ranks.append(curr_rank)
            total_reciprocal_rank += 1/curr_rank

            if(curr_rank <= 1):
                hits_at_1 += 1
            if(curr_rank <= 3):
                hits_at_3 += 1
            if(curr_rank <= 5):
                hits_at_5 += 1
            if(curr_rank <= 10):
                hits_at_10 += 1
        else:
            num_skipped += 1

    mean = sum(list_of_ranks)/len(list_of_ranks)
    mrr = (total_reciprocal_rank/len(list_of_ranks))
    med = median(list_of_ranks)

    print("Mean Rank: " + str(mean))
    print("MRR: " + str(mrr))
    print("Median Rank: " + str(med))
    print("Hits at 1: " + str(hits_at_1))
    print("Hits at 3: " + str(hits_at_3))
    print("Hits at 5: " + str(hits_at_5))
    print("Hits at 10: " + str(hits_at_10))
    print("Triples evaluated: " + str(len(list_of_ranks)))
    print("Triples Not evaluated: " + str(num_skipped))
    return mean, mrr, med, hits_at_1, hits_at_3, hits_at_5, hits_at_10
