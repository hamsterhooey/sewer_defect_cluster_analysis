import os
import numpy as np
import pandas as pd

"""
Helper functions
"""


def delete_rows(df_cond, keep_defects):
    """
    Delete rows where the defects that we want to consider are not present
    """
    df_cond = df_cond[df_cond['PACP_Code'].isin(keep_defects)]
    return df_cond


def delete_inspections_with_no_defects(df_cond, defects):
    """
    Delete those inspections where there aren't any defects at all.
    By defects we mean fractures, cracks, etc. Not tap and manhole
    """
    insp_ids = np.unique(list(df_cond['InspectionID']))

    keep_ids = []  # Inspection IDs that we want to keep

    for insp_id in insp_ids:
        df_temp = df_cond[(df_cond['InspectionID'] == insp_id)]
        if df_temp['PACP_Code'].isin(defects).sum() > 0:
            keep_ids.append(insp_id)

    return df_cond[df_cond['InspectionID'].isin(keep_ids)]


def calculate_length_of_pipeline(df_cond):
    # Find total length of pipeline
    insps = df_cond['InspectionID'].unique()
    length = 0.0
    for insp in insps:
        df_temp = df_cond[df_cond['InspectionID'] == insp]
        length += df_temp['Distance'].max()
    return length


def defect_codes_to_analyze(category='all'):
    """
    Returns a list of defect codes of a particular defect category that you want to analyze
    The defect codes belonging to different categories
    """
    deposit_codes = ['DAE', 'DAGS', 'DAR', 'DAZ', 'DSV', 'DSGV', 'DSC', 'DSZ', 'DNF', 'DNGV', 'DNZ']
    deformed_codes = ['DR', 'DFBR', 'DFBI', 'DFC', 'DFE', 'DTBR', 'DTBI']
    infiltration_codes = ['IS', 'ISB', 'ISJ', 'ISC', 'ISL', 'IW', 'IWB', 'IWC', 'IWJ', 'IWL', 'ID', 'IDB', 'IDC', 'IDJ', 'IDL', 'IR', 'IRB', 'IRC', 'IRJ', 'IRL', 'IG', 'IGB', 'IGC', 'IGL', 'IGJ']
    hole_codes = ['HSV', 'HVV']
    fracture_codes = ['FL', 'FC', 'FM', 'FS', 'FH', 'FH2', 'FH3', 'FH4']
    crack_codes = ['CL', 'CC', 'CM', 'CS', 'CH', 'CH2', 'CH3', 'CH4']
    broken_codes = ['BSV', 'BVV']
    collapse_codes = ['X']

    tap_codes = ['TB', 'TBI', 'TBD', 'TBC', 'TBA', 'TF', 'TFI', 'TFD', 'TFC', 'TFA', 'TFB', 'TR', 'TRI', 'TRD', 'TRC', 'TRA', 'TRB', 'TS', 'TSI', 'TSD', 'TSA', 'TSB']
    root_codes = ['RFB', 'RFL', 'RFC', 'RFJ', 'RMB', 'RML', 'RMC', 'RMJ', 'RBB', 'RBL', 'RBC', 'RBJ', 'RTB', 'RTL', 'RTC', 'RTJ']
    joint_offset_codes = ['JOS', 'JOM', 'JOL', 'JOSD', 'JOMD', 'JOLD', 'JSS', 'JSM', 'JSL', 'JAS', 'JAM', 'JAL']

    defects_all = deposit_codes + deformed_codes + infiltration_codes + hole_codes + fracture_codes + crack_codes + broken_codes + root_codes + joint_offset_codes + collapse_codes
    defects_struct = deformed_codes + hole_codes + fracture_codes + crack_codes + broken_codes + joint_offset_codes + collapse_codes
    defects_operat = root_codes + deposit_codes

    if category == 'all':
        return defects_all
    elif category == 'structural':
        return defects_struct
    elif category == 'operational':
        return defects_operat

    else:
        raise ValueError('Incorrect input. Category should be all, structural, or operational')


def main():
    df_cond = pd.read_csv('data/PACP_databases/Conditions_Hazen_Sawyer.csv', sep=',')
    keep_defects = defect_codes_to_analyze('structural')

    print(f"Total number of inspections to begin with are {format(df_cond['InspectionID'].nunique())}")
    df_cond = delete_rows(df_cond, keep_defects)
    df_cond = delete_inspections_with_no_defects(df_cond, keep_defects)
    print(f"Number of inspections after deletion are: {df_cond['InspectionID'].nunique()}")


if __name__ == "__main__":
    main()
