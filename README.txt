To install use 'pip install blast_score_ratio'.

Obtain BLAST score ratios (BSRs), for use in comparative genomics and
identifying horizontally transferred genetic material, from fastA files
containing the protein sequences for different organisms.

BSR (Rasko et al, 2006) is obtained by running BLAST using a reference proteome
against one or more other proteomes. The highest BLAST score for each reference
sequence is normalised by dividing by the score for 100% match to the reference
sequence. This analysis can identify shared genetic material in unrelated
strains or species, and find genes unique to a particular strain, for example.

A series of BLAST are performed and objects are created for each reference
sequence containing the results of the analysis. Charts showing relative BSR
in the form of a 2-D graph, histogram and heatmap can be quickly generated.

This program should be run from within the Python environment using
blast_score_ratio.bsr.get_bsr(*args). All functions and classes are fully
documented. The best way to understand how this works is to look at demo.py
for an example project.

Example:
    import blast_score_ratio.bsr as bsr
    bsr.test()

Requires NCBI BLAST+ command line >=2.2.29 application available here:
    ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/
BLAST binaries must be in your computer's path.
Also requires biopython and matplotlib packages.

tested with python v3.6.0, biopython v1.68, matplotlib v2.0.0 on Windows 10
