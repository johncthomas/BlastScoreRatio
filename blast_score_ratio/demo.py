from blast_score_ratio.bsr import get_bsr
import matplotlib.pyplot as plt
import inspect, os

package_path = os.path.dirname(
    inspect.getfile(inspect.currentframe())  # gets string of .py path
)

print("""
*****************************************************************************
Test the installation of blast_score_ratio and demonstrate functionality.
Edit this file ({}/demo.py) to view the commands being run.
*****************************************************************************

""".format(package_path))

paff = os.path.join(package_path + '/Examples/')

# get BSR results, a BSR_RecordSet
bsr_results = get_bsr(
    work_path=paff,
    job_name='Test',
    reference_fasta = paff+'example_A.faa',
    comparison_fastas = [ paff+'example_B.faa',
                          paff+'example_C.faa',
                          paff+'example_D.faa' ],
    # Order here should match comparison_fastas above. Used to obtain strain
    # specific data using index number or string
    strain_names = ['Strain A', 'Strain B', 'Strain C', 'Strain D'],
    force_redo = True
)


# the results object contains information about the test, for example, the names of
# all files created by get_bsr()
print(bsr_results.files)

# you can do 2 kinds of plots directly from the results object
fig, ax = bsr_results.plot_2d((3, 1)) # fig, ax objects are returned
# you can do things with the plots using matplotlib
plt.annotate('Common to strains A & D,\nnot strain B', xy = (0.95, 0.03), xytext = (0.6, 0.2),
             arrowprops=dict(facecolor='black', shrink=0.05))
plt.show()

bsr_results.plot_2d(('Strain B', 'Strain C')) # Can also specify strains by names
plt.show()

# By default the histogram includes all strains
bsr_results.histogram()
plt.show()

# Heat map.
# supplying a groups mapping orders the heatmap by difference between mean bsr for each group
# Groups does not include reference strain
bsr_results.heatmap(groups=[0,0,1])
plt.show()

# Demonstration of identifying shared genes in strains A & D
print('\n\n\t\tBSR SCORES')
print('B\t\tC\t\tD\t\tRecord Title')

hgt_recs = []
for rec in bsr_results.bsr_records:
    # get the BSR scores for each comparison strain
    B, C, D = rec.bsr[1:]
    # find BSR scores that are higher in strain D, and above an arbitary threshold of 0.6
    if D > B and D > C and D > 0.6:
        hgt_recs.append(rec)
        print(f'{B:.3f}\t{C:.3f}\t{D:.3f}\t{rec.ref_title}')

# Identify proteins unique to strain A
print('\t')
for rec in bsr_results.bsr_records:
    B, C, D = rec.bsr[1:]
    if B < 0.6 and C < 0.6 and D < 0.6:
        print(f'{B:.3f}\t{C:.3f}\t{D:.3f}\t{rec.ref_title}')

# each record object contains info about the reference sequence and hit sequences,
# including FastA titles, amino acid sequence, BLAST scores
# All are stored as lists in a set order
hgt_protein = hgt_recs[0]
print(hgt_protein.strain_names)
print(hgt_protein.blast_scores)
print(hgt_protein.record_num) # This gives the order the sequences are found in the reference FastA

print("""

*****************************************************************************
Test complete.
Edit this file ({}/demo.py) to view the commands being run.
*****************************************************************************
""".format(package_path))
