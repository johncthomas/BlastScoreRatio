# BlastScoreRatio
Obtain BLAST score ratios (BSR) of amino acid sequences between two or more FastA 
files. Useful for identifying horizontally transferred material.

BSR (Rasko et al, 2006) are obtained by running BLAST using a reference proteome
against one or more other proteomes. The highest BLAST score for each reference
sequence is normalised by dividing by the maximum score for that sequence. This analysis can identify shared genetic material in unrelated
strains or species, and find genes unique to a particular strain, for example.

It should be run from within the Python environment using
blast_score_ratio.bsr.get_bsr(*args)

A series of BLAST searches are performed and objects are created for each reference
sequence containing the results of the analysis. Charts can be quickly generated showing relative BSR
in the form of a 2-D graph, histogram and heatmap .

See demo.py for examples and the function/class documentation of the bsr
module for more information.

Requires NCBI BLAST command line application, available here:
    ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/

Also requires biopython and matplotlib packages.

