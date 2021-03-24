import os
import json
import numpy as np
import pandas as pd
import argparse
from collections import defaultdict


# TODO: Move utils into separate file
"""Start of Utils"""


def defect_codes_to_analyze(category="all"):
    """
    Returns a list of defect codes of a particular defect category that you want to analyze
    The defect codes belonging to different categories
    """
    deposit_codes = [
        "DAE",
        "DAGS",
        "DAR",
        "DAZ",
        "DSV",
        "DSGV",
        "DSC",
        "DSZ",
        "DNF",
        "DNGV",
        "DNZ",
    ]
    deformed_codes = ["DR", "DFBR", "DFBI", "DFC", "DFE", "DTBR", "DTBI"]
    infiltration_codes = [
        "IS",
        "ISB",
        "ISJ",
        "ISC",
        "ISL",
        "IW",
        "IWB",
        "IWC",
        "IWJ",
        "IWL",
        "ID",
        "IDB",
        "IDC",
        "IDJ",
        "IDL",
        "IR",
        "IRB",
        "IRC",
        "IRJ",
        "IRL",
        "IG",
        "IGB",
        "IGC",
        "IGL",
        "IGJ",
    ]
    hole_codes = ["H", "HSV", "HVV"]
    fracture_codes = ["FL", "FC", "FM", "FS", "FH", "FH2", "FH3", "FH4"]
    crack_codes = ["CL", "CC", "CM", "CS", "CH", "CH2", "CH3", "CH4"]
    broken_codes = ["B", "BSV", "BVV"]
    collapse_codes = ["X"]

    tap_codes = [
        "TB",
        "TBI",
        "TBD",
        "TBC",
        "TBA",
        "TF",
        "TFI",
        "TFD",
        "TFC",
        "TFA",
        "TFB",
        "TR",
        "TRI",
        "TRD",
        "TRC",
        "TRA",
        "TRB",
        "TS",
        "TSI",
        "TSD",
        "TSA",
        "TSB",
    ]
    root_codes = [
        "RFB",
        "RFL",
        "RFC",
        "RFJ",
        "RMB",
        "RML",
        "RMC",
        "RMJ",
        "RBB",
        "RBL",
        "RBC",
        "RBJ",
        "RTB",
        "RTL",
        "RTC",
        "RTJ",
    ]
    joint_offset_codes = [
        "JOS",
        "JOM",
        "JOL",
        "JOSD",
        "JOMD",
        "JOLD",
        "JSS",
        "JSM",
        "JSL",
        "JAS",
        "JAM",
        "JAL",
    ]

    defects_all = (
        deposit_codes
        + deformed_codes
        + infiltration_codes
        + hole_codes
        + fracture_codes
        + crack_codes
        + broken_codes
        + root_codes
        + joint_offset_codes
        + collapse_codes
    )
    defects_struct = (
        deformed_codes
        + hole_codes
        + fracture_codes
        + crack_codes
        + broken_codes
        + joint_offset_codes
        + collapse_codes
    )
    defects_operat = root_codes + deposit_codes

    if category == "all":
        return defects_all
    elif category == "structural":
        return defects_struct
    elif category == "operational":
        return defects_operat

    else:
        raise ValueError(
            "Incorrect input. Category should be all, structural, or operational"
        )


"""End of Utils"""


def get_pacp_grade(defect_code):
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
        "B": 4,
        "BSV": 5,
        "BVV": 5,
        "DR": 5,
        "DFBR": 5,
        "DFBI": 5,
        "DFC": 5,
        "DFE": 5,
        "DTBR": 5,
        "DTBI": 5,
        "H": 4,
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
    try:
        return grades[defect_code]
    except ValueError:
        print("Defect code not in dict")


def filter_df_by_defects(df_cond, keep_defects):
    """Delete defects that are not in keep_defects"""
    print(
        f"Total number of inspections to begin with are {format(df_cond['InspectionID'].nunique())}"
    )
    df_cond = df_cond[df_cond["PACP_Code"].isin(keep_defects)]
    print(
        f"Number of inspections with defects under consideration are: {df_cond['InspectionID'].nunique()}"
    )

    return df_cond


def identify_clusters_in_single_inspection(df_cond, cluster_dist_thresh, insp_id):
    """
    Two defects are considered to be in a cluster if they are <=3 feet apart from one another

    Returns empy list if no clusters were identified
    """
    clusters = []
    df_temp = df_cond.copy(deep=True)
    df_temp = df_temp.sort_values(by=["Distance"])

    indices = df_temp.index
    defect_prev, defect_curr = "", ""
    dist_prev, dist_curr = 0, 0
    cluster_curr = []

    for index in indices:
        defect_curr = df_temp.at[index, "PACP_Code"]  # Defect code at current index
        cond_id = df_temp.at[index, "ConditionID"]  # ConditionID at current index
        video_frame = df_temp.at[index, "Counter"]  # Frame at current index

        dist_curr = float(
            df_temp.at[index, "Distance"]
        )  # Distance of defect at current index

        if abs(dist_curr - dist_prev) >= cluster_dist_thresh:
            clusters.append(cluster_curr)
            cluster_curr = []

        cluster_curr.append((insp_id, defect_curr, dist_curr, cond_id, video_frame))

        dist_prev = dist_curr
        defect_prev = defect_curr

    return clusters


def identify_clusters_in_multiple_inspections(df_cond, cluster_dist_thresh):
    clusters = []
    insp_ids = df_cond["InspectionID"].unique()

    # Loop through all inspections
    for insp_id in insp_ids:
        # Get df corresponding to a particular inspection
        df_cond_single_inspection = df_cond[df_cond["InspectionID"] == insp_id]
        # Identify clusters in inspection and add to list of clusters
        clusters.extend(
            identify_clusters_in_single_inspection(
                df_cond_single_inspection, cluster_dist_thresh, insp_id
            )
        )

    # Delete empty clusters
    clusters = list(filter(lambda a: a != [], clusters))
    return clusters


def calc_num_clusters(clusters):
    num_clusters = defaultdict(int)
    for cluster in clusters:
        if len(cluster) >= 1:
            num_clusters[len(cluster)] += 1

    return num_clusters, max_cluster_len


def calc_cluster_severity(cluster, len_thresh=3):
    cluster_length = 0
    grade = 0

    for _, defect_code, _, _, _ in cluster:
        grade += get_pacp_grade(defect_code)

    num_defects = len(cluster)
    cluster_length = (
        cluster[num_defects - 1][2] - cluster[0][2]
    )  # Length is distance of last - first
    if cluster_length < len_thresh:
        cluster_length = len_thresh

    severity = grade / cluster_length
    return severity, grade


def filter_clusters(clusters, num_defects_thresh, severity_thresh):
    """Filter clusters by number of defects and severity"""
    filtered_clusters = [
        cluster
        for cluster in clusters
        if len(cluster) >= num_defects_thresh
        and calc_cluster_severity(cluster)[0] > severity_thresh
    ]
    return filtered_clusters


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--cond_db", help="Path to CSV file containing PACP condition database"
    )
    parser.add_argument(
        "--defect_category", help="Choose between: all, structural, and operational"
    )
    parser.add_argument("--cluster_dist_thresh", help="Cluster threshold distance")
    args = parser.parse_args()
    return args


def ipynb_fake_args(
    cond_db="data/Condition_Databases/Conditions_SAI.csv",
    defect_category="structural",
    cluster_dist_thresh=6.0,
):
    """
    cluster_dist_thresh: maximum distance between 2 defects to consider them in a cluster
    """

    class Args:
        pass

    args = Args()
    args.cond_db = cond_db
    args.defect_category = defect_category
    args.cluster_dist_thresh = cluster_dist_thresh
    return args


def main():
    # main
    is_notebook = True
    if not is_notebook:
        args = parse_args()
    else:
        args = ipynb_fake_args()

    # Read csv containing single or multiple inspections
    df_cond = pd.read_csv(args.cond_db, sep=",")

    # Get list of defect codes to keep
    keep_defects = defect_codes_to_analyze(args.defect_category)

    # Filter the df to only keep particular code
    df_cond = filter_df_by_defects(df_cond, keep_defects)

    # Identify clusters
    clusters = identify_clusters_in_multiple_inspections(
        df_cond, int(args.cluster_dist_thresh)
    )

    filtered_clusters = filter_clusters(
        clusters, num_defects_thresh=3, severity_thresh=1
    )

    # Calculate number of clusters
    num_clusters, max_cluster_len = calc_num_clusters(filtered_clusters)
    print(f"Number of clusters of different sizes is: {num_clusters}")


if __name__ == "__main__":
    main()

"""
Example usage:

python defect_cluster_identifier.py --cond_db "data/PACP_databases/Conditions_SAI.csv" --defect_category "structural" --thresh 3

"""
