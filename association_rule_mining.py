import pandas as pd
import argparse
from utils import *
from defect_cluster_identifier import identify_clusters, filter_category


def calculate_co_matrix(clusters, keep_defects):  # Co occurrence matrix
    co_matrix = []

    for cluster in clusters:
        row = np.zeros(len(keep_defects))
        for _, defect, _ in cluster:
            defect_index = keep_defects.index(defect)
            row[defect_index] = 1
        co_matrix.append(row)

    return co_matrix


def count_pairs(x, y, co_matrix):  # Count number of occurrences of X and Y
    count_x, count_y, count_xy = 0, 0, 0
    for row in co_matrix:
        if row[x] == 1 and row[y] == 1.0:
            count_xy += 1
        if row[x] == 1.0:
            count_x += 1
        if row[y] == 1.0:
            count_y += 1

    return count_x, count_y, count_xy


def support_confidence_xy(x, y, co_matrix):  # Calculate support and confidence of X ---> Y
    count_x, count_y, count_xy = count_pairs(x, y, co_matrix)
    support_xy = count_xy / len(co_matrix)
    support_x = count_x / len(co_matrix)
    support_y = count_y / len(co_matrix)
    if count_x == 0 or count_y == 0 or count_xy == 0:
        confidence_xy = 0
    else:
        confidence_xy = count_xy / count_x
    return support_x, support_y, support_xy, confidence_xy


def mine_rules(co_matrix, keep_defects, min_support, min_confidence):
    rules = []
    for x in range(0, len(keep_defects)):
        for y in range(0, len(keep_defects)):
            if x != y:
                support_x, support_y, support_xy, confidence_xy = support_confidence_xy(x, y, co_matrix)
                if support_xy > min_support and confidence_xy > min_confidence:
                    lift_xy = support_xy / (support_x * support_y)
                    rules.append([keep_defects[x], keep_defects[y], support_xy, confidence_xy, lift_xy])

    return rules


def display_rules(rules):
    print('Interesting Association Rules Found')
    for rule in rules:
        if rule[4] > 1.5:
            print(rule)


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--cond_db", help="Path to CSV file containing PACP condition database")
    parser.add_argument("--defect_category", help="Choose between: all, structural, and operational")
    parser.add_argument("--min_support", help="Minimum support of rules")
    parser.add_argument("--min_confidence", help="Minimum confidence of rules")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    df_cond = pd.read_csv(args.cond_db, sep=',')
    keep_defects = defect_codes_to_analyze(args.defect_category)
    df_cond = filter_category(df_cond, keep_defects)

    clusters = identify_clusters(df_cond, 1000)  # Modify this function and use thresh = 1000
    co_matrix = calculate_co_matrix(clusters, keep_defects)

    rules = mine_rules(co_matrix, keep_defects, float(args.min_support), float(args.min_confidence))
    display_rules(rules)


if __name__ == "__main__":
    main()

"""
Example usage:

python association_rule_mining.py --cond_db "data/PACP_databases/Conditions_Hazen_Sawyer.csv" --defect_category "structural" --min_support 0.001 --min_confidence 0.4

"""
