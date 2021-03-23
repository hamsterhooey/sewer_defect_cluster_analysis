import os
import json
import numpy as np
import pandas as pd
import argparse
from utils import *


def display_clusters(cluster_metrics):
    (
        max_severity_clusters,
        min_severity_clusters,
        max_severity,
        min_severity,
        avg_severity,
    ) = cluster_metrics
    pass


def calc_severity_cluster(cluster, thresh):
    grades = {
        "JOM": 1,
        "JOL": 2,
        "JOMD": 1,
        "JOLD": 2,
        "JSM": 1,
        "JSL": 2,
        "JAM": 1,
        "JAL": 2,
        "X": 5,
        "BSV": 5,
        "BVV": 5,
        "DR": 5,
        "DFBR": 5,
        "DFBI": 5,
        "DFC": 5,
        "DFE": 5,
        "DTBR": 5,
        "DTBI": 5,
        "HSV": 5,
        "HVV": 5,
        "FL": 3,
        "FC": 2,
        "FM": 4,
        "FS": 3,
        "FH2": 4,
        "FH3": 5,
        "FH4": 5,
        "CL": 2,
        "CC": 1,
        "CM": 3,
        "CS": 2,
        "CH2": 4,
        "CH3": 5,
        "CH4": 5,
    }

    cluster_length = 0
    grade = 0

    for _, def_code, _ in cluster:
        grade += grades[def_code]

    num_defects = len(cluster)
    cluster_length = (
        cluster[num_defects - 1][2] - cluster[0][2]
    )  # Length is distance of last - first
    if cluster_length < thresh:
        cluster_length = thresh

    severity = grade / cluster_length
    return severity


def calc_cluster_metrics(
    clusters, thresh, max_cluster_len
):  # Calculate max, min, and avg severity value for clusters of different lengths

    max_severity_clusters = {i: [] for i in range(3, max_cluster_len + 1)}
    min_severity_clusters = {i: [] for i in range(3, max_cluster_len + 1)}
    max_severity = {i: 0 for i in range(3, max_cluster_len + 1)}
    min_severity = {i: 1000 for i in range(3, max_cluster_len + 1)}
    avg_severity = {i: 0 for i in range(3, max_cluster_len + 1)}

    # Calculating severity scores for clusters or particular lengths
    for cluster_length in range(3, max_cluster_len + 1):

        filtered_clusters = [
            cluster for cluster in clusters if len(cluster) == cluster_length
        ]

        for cluster in filtered_clusters:
            cluster_severity = calc_severity_cluster(cluster, thresh)

            if cluster_severity > max_severity[cluster_length]:
                max_severity[cluster_length] = cluster_severity
                max_severity_clusters[cluster_length] = cluster

            if cluster_severity < min_severity[cluster_length]:
                min_severity[cluster_length] = cluster_severity
                min_severity_clusters[cluster_length] = cluster

            avg_severity[cluster_length] += cluster_severity / len(clusters)

    return {
        "Maximum Severity Clusters": max_severity_clusters,
        "Minimum Severity Clusters": min_severity_clusters,
        "Maximum Cluster Severity": max_severity,
        "Miniimum Cluster Severity": min_severity,
        "Average Cluster Severity": avg_severity,
    }


def calculate_num_clusters(clusters):
    cluster_len = [len(i) for i in clusters]  # List of cluster lengths
    max_cluster_len = max(cluster_len)

    num_clusters = {i: 0 for i in range(1, max_cluster_len + 1)}
    max_length = 0
    for cluster in clusters:
        if len(cluster) >= 1:
            num_clusters[len(cluster)] += 1

    print(f"Number of clusters of different sizes is: {num_clusters}")
    return num_clusters, max_cluster_len


def identify_clusters(df_cond, thresh):
    clusters = []
    insps = df_cond["InspectionID"].unique()

    for insp in insps:

        df_temp = df_cond[df_cond["InspectionID"] == insp]
        df_temp = df_temp.sort_values(by=["Distance"])
        indices = df_temp.index
        defect_prev, defect_curr = "", ""
        dist_prev, dist_curr = 0, 0
        cluster_curr = []

        for index in indices:
            defect_curr = df_temp.at[index, "PACP_Code"]  # Defect code at current index
            dist_curr = float(
                df_temp.at[index, "Distance"]
            )  # Distance of defect at current index

            if abs(dist_curr - dist_prev) < thresh:
                cluster_curr.append((insp, defect_curr, dist_curr))
            else:
                clusters.append(cluster_curr)
                cluster_curr = []
                cluster_curr.append((insp, defect_curr, dist_curr))

            dist_prev = dist_curr
            defect_prev = defect_curr

        clusters.append(cluster_curr)

    # Delete empty clusters
    clusters = list(filter(lambda a: a != [], clusters))
    return clusters


def count_defects(df_cond):
    # List the number of defects
    df_counts = df_cond["PACP_Code"].value_counts()
    print(f"Number of defects in these inspections is:\n{df_counts}")
    # df_counts.to_csv('defect_counts.csv')
    return df_counts


def filter_category(df_cond, keep_defects):
    print(
        f"Total number of inspections to begin with are {format(df_cond['InspectionID'].nunique())}"
    )
    df_cond = delete_rows(df_cond, keep_defects)
    print(
        f"Number of inspections after deletion are: {df_cond['InspectionID'].nunique()}"
    )

    # Calculate the total length of pipe in this dataframe
    length = calculate_length_of_pipeline(df_cond)
    print(f"Length of pipeline is: {length}")
    return df_cond


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--cond_db", help="Path to CSV file containing PACP condition database"
    )
    parser.add_argument(
        "--defect_category", help="Choose between: all, structural, and operational"
    )
    parser.add_argument("--thresh", help="Cluster threshold distance")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    df_cond = pd.read_csv(args.cond_db, sep=",")
    keep_defects = defect_codes_to_analyze(args.defect_category)
    df_cond = filter_category(df_cond, keep_defects)
    df_counts = count_defects(df_cond)
    clusters = identify_clusters(df_cond, int(args.thresh))
    num_clusters, max_cluster_len = calculate_num_clusters(clusters)
    cluster_metrics = calc_cluster_metrics(clusters, int(args.thresh), max_cluster_len)
    filtered_clusters = filter_clusters(clusters)


    # Save cluster metrics as a json
    # with open("cluster_metrics.json", "w") as f:
    #     json.dump(cluster_metrics, f)

    # TODO: Visualize defect cluster metrics
    display_clusters(cluster_metrics)



if __name__ == "__main__":
    main()

"""
Example usage:

python defect_cluster_identifier.py --cond_db "data/PACP_databases/Conditions_Hazen_Sawyer.csv" --defect_category "structural" --thresh 3

"""
