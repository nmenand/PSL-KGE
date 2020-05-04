#!bin/usr/env python3
import statistics

# 0 for L1 norm, 1 for L2 norm
NORM_TYPE = 0

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
            return None, None
    return L1_norm, L2_norm**(0.5)

# generate rankings
def generate_link_ranking(ent_embeddings, rel_embeddings, ent_list, mapped_e1, mapped_rel, mapped_e2):
    ranking_list = []
    dimensions = len(ent_embeddings)
    valid_triple_score = eval_triple(mapped_e1, mapped_e2, mapped_rel, dimensions, ent_embeddings, rel_embeddings)
    for ent in ent_list:
        corrupted_ent = ent
        score = eval_triple(corrupted_ent, mapped_e2, mapped_rel, dimensions, ent_embeddings, rel_embeddings)
        if score != (None, None):
            ranking_list.append((score, corrupted_ent, mapped_rel, mapped_e2))

        score = eval_triple(mapped_e1, corrupted_ent, mapped_rel, dimensions, ent_embeddings, rel_embeddings)
        if score != (None, None):
            ranking_list.append((score, mapped_e1, mapped_rel, corrupted_ent))
    ranking_list.sort(key=lambda x: x[0], reverse=True)
    return ranking_list, valid_triple_score

def eval_link_ranking(set_of_positive_data, target_triple_score, ranking_list):
    rank = 1
    for (value, entity1, relation, entity2) in ranking_list:
        if (entity1, relation, entity2) not in set_of_positive_data:
            if float(value[NORM_TYPE]) < target_triple_score[NORM_TYPE]:
                rank += 1
    return rank

def predict_links(ent_embeddings, rel_embeddings, ent_list, test_list, set_of_data):
    list_of_ranks = []
    total_reciprocal_rank = 0
    hits_at_1 = 0
    hits_at_3 = 0
    hits_at_5 = 0
    hits_at_10 = 0
    num_skipped = 0

    for (e1, rel, e2) in test_list:
        ranking_list, curr_triple_score = generate_link_ranking(ent_embeddings, rel_embeddings, ent_list, e1, rel, e2)
        if curr_triple_score != (None, None):
            curr_rank = eval_link_ranking(set_of_data, curr_triple_score, ranking_list)
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
    mrr = str(total_reciprocal_rank/len(list_of_ranks))
    median = statistics.median(list_of_ranks)

    print("Mean Rank: " + str(mean))
    print("MRR: " + str(mrr))
    print("Median Rank: " + str(median))
    print("Hits at 1: " + str(hits_at_1))
    print("Hits at 3: " + str(hits_at_3))
    print("Hits at 5: " + str(hits_at_5))
    print("Hits at 10: " + str(hits_at_10))
    print("Triples evaluated: " + str(len(list_of_ranks)))
    print("Triples Not evaluated: " + str(num_skipped))
    return mean, mrr, median, hits_at_1, hits_at_3, hits_at_5, hits_at_10
