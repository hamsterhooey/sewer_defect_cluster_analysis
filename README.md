# Project Title

Sewer Defect Cluster Analysis

## Project Overview

In most previous studies on sewer deterioration, a single numeric grade is used to represent the condition of a pipe segment. These numeric grades provides insights into the level of deterioration of a pipe, and are thus a handy metric for planning maintenance activities. However, representing pipe deterioration with a single grade, leads to a loss of information, such as the location, density, and co-occurrence of defects – information which, when considered alongside contextual information of the pipe, can be crucial in determining their susceptibility to failure. According to previous studies, the pipe segment on the left and right in the image below, would both be considered to be equally deteriorated.

![alt text](https://github.com/hamsterhooey/sewer_defect_cluster_analysis/blob/master/images/cluster_vs_uniform.png)

However, we believe that pipe b has a higher likelihood of failure because:
(1) the defects, which are in close proximity could propagate and coalesce into more severe defects;
(2) multiple cracks and fractures increase the risk of void formation, due to soil entering the pipe. Voids over pipes are known to create sinkholes; and
(3) the pipe has a higher chance of collapse due to the existence of a localized region of weakness

Thus, this project presents a methodology for assessing pipe condition by considering information about the locations of defects and uses a hybrid approach to (1) identify regions of high defect concentrations in a pipe and (2) identify the co-occurrence characteristics of defects.

Both techniques have been developed to work with sewer inspection databases that are in the NASSCO PACP format (see image below). Since most municipalities in the US adopt the NASSCO PACP format, the methodologies described can be directly applied to existing sewer pipe condition databases.

<p align="center"> 
<img src="https://github.com/hamsterhooey/sewer_defect_cluster_analysis/blob/master/images/sample_pacp.png" width="480">
</p>

### Defect Cluster Identification

Example usage:

```
python defect_cluster_identifier.py --cond_db "data/PACP_databases/Conditions.csv" --defect_category "structural" --thresh 3
```

### Association Rule Mining

Example usage:

```
python association_rule_mining.py --cond_db "data/PACP_databases/Conditions.csv" --defect_category "structural" --min_support 0.001 --min_confidence 0.4
```

Note: the PACP database must be in .csv format. We are currently updating the algorithm to directly read MS Access databases.

## Author

- **Srinath Shiv Kumar** - [hamsterhooey](https://github.com/hamsterhooey)
