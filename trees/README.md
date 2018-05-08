### General Information ###

SCIP uses the .vbc file extension to write its search trees. The generation of .vbc files
can be turned on by setting the parameter "visual/vbcfilename". The files contain
information about the tree structure, the branched variables, the order in which the
nodes were created, their primal bounds as well as their type (solved, infeasible,
repropagated, etc.). For memory purposes, it may be helpful to compress .vbc files. The
script ../instancegen/compressvbc.py parses a single .vbc file and creates a compressed
version of it as .abc file. These can then be used for sampling in ../sampling/main.py.
Further scripts in ../auc/ calculate the mean absolute percentage error for a given set
of estimates for an instance.


### Information about the instances ###

|Instance Name          |        Total Nodes      |      auc p_k-online      |       auc p_k-uniform     |
|-----------------------|-------------------------|--------------------------|---------------------------|
|bc                     |        15991            |      59.19               |       11.94               |
|bienst1                |        14847            |      21.88               |       2.89                |
|dfn-gwin-UUM           |        19659            |      29.59               |       5.04                |
|mine-90-10             |        32691            |      43.55               |       231.56              |
|neos-1324574           |        37157            |      28.61               |       25.95               |
|neos-1396125           |        11637            |      41.68               |       41.84               |
|neos-693347            |        16115            |      181.98              |       15189.75            |
|ns1702808              |        38725            |      30.62               |       39.09               |
|nsrand-ipx             |        78035            |      39.34               |       17.0                |
|reblock67              |        60689            |      37.04               |       22.69               |
|rococoC10-001000       |        125945           |      42.53               |       11.72               |
|rout                   |        14615            |      28.88               |       1367.19             |
|stein45                |        40695            |      21.55               |       1.2                 |
|timtab1                |        52439            |      48.81               |       2.65                |
|uct-subprob            |        56103            |      24.15               |       1.86                |
|wachplan               |        47937            |      39.27               |       8.14                |
