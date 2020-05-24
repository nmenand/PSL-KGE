## COUPLED RULE CONSTANTS ##
#TRUE_RULE_WEIGHT = "5.0"
FALSE_RULE_WEIGHT = "1.0"
ENTITY1_RULE = ": EntityDim"
RELATION_RULE = "(e1) + RelationDim"
ENTITY2_RULE = "(r1) - EntityDim"
TRUE_RULE = "(e2) + 0*TrueBlock(e1, r1, e2) = 0"
FALSE_RULE2 = "(e2) + 0*FalseBlock(e1, r1, e2) >= 1\n"
ENTITYDIM = "entitydim"

## DECOUPLED RULE CONSTANTS ##
WEIGHT_1 = "0.5: "
SMOOTHER = " ^2"

PREDICATES = "predicates:"
FALSEBLOCK = "   FalseBlock/3: closed"
TRUEBLOCK = "   TrueBlock/3: closed\n"
OPEN = "/1: open"
OBSERVATIONS = "observations:"
TARGETS = "targets:"
PREDICATE_PATH = ": ../data/kge/0/eval/"
TRUEPATH = "   FalseBlock: ../data/kge/0/eval/falseblock_obs.txt\n"
FALSEPATH = "   TrueBlock: ../data/kge/0/eval/trueblock_obs.txt"
ENTITY_RULE = "EntityDim"
RELATION_RULE_DIM = "RelationDim"
TARGET = "_target.txt"
RELATIONDIM = "relationdim"


# Create PSL rules
def generate_rules(num_dimensions, rule_type, neg_triple_ratio):
    if rule_type == "decoupled":
        rule_output = []
        for dim in range(1, num_dimensions+1):
            rule_output.append(str(float(neg_triple_ratio)) + ENTITY1_RULE + str(dim) + RELATION_RULE + str(dim) + ENTITY2_RULE+ str(dim) + TRUE_RULE)
            rule_output.append(FALSE_RULE_WEIGHT + ENTITY1_RULE + str(dim) + RELATION_RULE + str(dim) + ENTITY2_RULE+ str(dim) + FALSE_RULE2)
    elif rule_type == "coupled":
        rule_output = []
        for dim in range(1, num_dimensions+1):
            rule_output.append(WEIGHT_1 + "!EntityDim" + str(dim) + "(e1)" + SMOOTHER)
        for dim in range(1, num_dimensions+1):
            rule_output.append(WEIGHT_1 + "!RelationDim" + str(dim) + "(e1)" + SMOOTHER)
        rule_output.append("\n")
        # Add rule weight
        rule_helper = ""
        for dim in range(1, num_dimensions+1):
            rule_helper += ("EntityDim" + str(dim) + "(e1)" + " + " + "RelationDim" + str(dim) + "(r1)" + " - " + "EntityDim" + str(dim) + "(e2) + ")
        rule_output.append("50.0: " + rule_helper + "0*TrueBlock(e1, r1, e2) = 0 ^2\n")
        rule_output.append("10.0: " + rule_helper + "0*FalseBlock(e1, r1, e2) = " + str(neg_triple_ratio) + " ^2\n")
        rule_helper = ""
        for dim in range(1, num_dimensions+1):
            if dim == num_dimensions:
                rule_helper += "EntityDim" + str(dim) + "(e1)"
            else:
                rule_helper += "EntityDim" + str(dim) + "(e1)" + " + "
        rule_output.append("25.0: " + rule_helper + " = 1 ^2\n")

    predicate_output = []

    predicate_output.append(PREDICATES)
    for dim in range(1, num_dimensions+1):
        predicate_output.append("   " + ENTITY_RULE + str(dim) + OPEN)
        predicate_output.append("   " + RELATION_RULE_DIM + str(dim) + OPEN)
    predicate_output.append(FALSEBLOCK)
    predicate_output.append(TRUEBLOCK)

    predicate_output.append(OBSERVATIONS)
    predicate_output.append(FALSEPATH)
    predicate_output.append(TRUEPATH)

    predicate_output.append(TARGETS)
    for dim in range(1, num_dimensions+1):
        predicate_output.append("   " + ENTITY_RULE + str(dim) + PREDICATE_PATH + ENTITYDIM + str(dim)+ TARGET)
        predicate_output.append("   " + RELATION_RULE_DIM + str(dim) + PREDICATE_PATH + RELATIONDIM + str(dim)+ TARGET)

    return rule_output, predicate_output
