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
blast_score_ratio.bsr.get_bsr(*args). See get_bsr.__doc__ for usage
instructions. See demo.py for an example project flow and the
the bsr module for more information.

Requires NCBI BLAST command line application available here:
    ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/
BLAST binaries must be in your computer's path.
Also requires biopython and matplotlib packages.

tested with python v3.6.0, biopython v1.68, matplotlib v2.0.0 on Windows 10
