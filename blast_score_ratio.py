__author__ = 'JCThomas'

from Bio.Blast import NCBIXML
from Bio.Blast.Applications import NcbiblastpCommandline as blastp
from Bio import SeqIO
import pickle, os
from statistics import mean
import matplotlib.pyplot as plt

"""Get BLAST Score Ratios (BSR; as described in Rasko et al (2006) doi:10.1186/1471-2105-6-2)
for a reference proteome compared to other proteomes.

get_bsr() is the main function, see it's documentation for use. A 
BSR_RecordSet containing BSR_Record objects are produced."""


# PAM is more accurate for closely related sequences (which is what we are intested in.
# Scoring matrices used to generate reference scores without invoking BLAST
# Turns out BLAST doesn't support PAM10.
MATRICES = dict(
    PAM30 = {'A': 6, 'B': 6, 'C': 10, 'D': 8, 'E': 8, 'F': 9, 'G': 6, 'H': 9, 'I': 8, 'J': 6, 'K': 7, 'L': 7, 'M': 11,
     'N': 8, 'P': 8, 'Q': 8, 'R': 8, 'S': 6, 'T': 7, 'V': 7, 'W': 13, 'X': -1, 'Y': 10, 'Z': 6},
)
MATRIX = 'PAM30'

class BSR_RecordSet:
    """Class for holding and working with BSR results. Generated by get_bsr().

    The indicies of strain/species specific info in lists in this and the
        held BSR_Record all match and are made explicit in the strain_names
        attribute.

    Contains methods to generate plots: plot_2d, histogram, heatmap. When
        specifying strains in plotting methods you can use indicies or strings
        that match the given strain names.

    Attributes:
        strain_names (iter[str]): Names of strains.  The indicies of
            strain/species specific info in all related objects should match
            the order given here, with the ref fasta at index 0.
        bsr_records (list): BSR_Record obj created by get_bsr(). BSR values
            held in record.bsr[strain_index]. See BSR_Record documentation for
            more info.
        ref_fasta (str): Path to the reference FastA file.
        comparison_fastas (iter[str]): Paths of comparison FastA files.
        files (iter[str]): path of files generated by get_bsr().

    All attributes are set by get_bsr()
    """

    def __init__(self, job_title, bsr_records, ref_fasta, comparison_fastas,
                 strain_names, files):
        self.job_title = job_title
        # get a list of records in the order they were created
        if type(bsr_records) is dict:
            self.bsr_records = sorted(bsr_records.values(), key = lambda x: x.record_num)
        else:
            self.bsr_records = bsr_records
        self.ref_fasta = ref_fasta
        self.comparison_fastas = comparison_fastas
        self.strain_names = strain_names
        self.files = files
        self.group = None
        self.sort_func = None


    def plot_2d(self, strains, axes = None, plt_kwargs = None):
        """
        Generate a 2-dimensional plot showing the relative BSR for 2
            specified strains (indicies or strings).

        Arguments:
            strains (iter[str or int]): The two strains that will have their
                bsr plotted. The first will be plotted on the X-axis.
            axes (plt.axes.Axes), optional: If supplied will be used for
                plotting and returned. Otherwise a Figure and Axes object
                will be created and returned.
            plt_kwargs (dict), optional: passed to plt.plot() when plotting the
                markers.
        """

        str_i, str_j = self.get_strains(strains)

        data = self.bsr_records

        fig, ax, plt_kwargs = self._deal_with_plot_stuff(
            axes, plt_kwargs, {'color':'b', 'marker':'o', 'markersize':6}
        )

        # if axes is None:
        #     fig, ax = plt.subplots(1,1,figsize = (8,8))
        # else:
        #     ax = axes
        #
        #
        # if plt_kwargs is None:
        #     plt_kwargs = { 'markersize':6}
        # elif 'markersize' not in plt_kwargs:
        #     plt_kwargs['markersize'] = 6
        for match in data:
            strx, stry = match.bsr[str_i], match.bsr[str_j]

            ax.plot(strx,stry, **plt_kwargs)

        ax.plot((0, 1), (0, 1), 'k-')
        ax.set_ylim(0, 1)
        ax.set_xlim(0, 1)
        ax.set_xlabel(self.strain_names[str_i])
        ax.set_ylabel(self.strain_names[str_j])

        if axes is None:
            return fig, ax
        else:
            return ax

    def get_strains(self, strains = None):
        """Get the index for strain data in .bsr_records so that strain specific
        bsr, scores etc can be retrieved.

        return list of index ints for strain when given strain names as
            strings. Return an int when given a single string."""
        if strains is None:
            return list(range(1, len(self.strain_names)))
        if type(strains) is str:
            return self.strain_names.index(strains)
        else:
            _strains = []
            for strain in strains:
                if type(strain) is not int:
                    strain = self.strain_names.index(strain)
                _strains.append(strain)

            return _strains


    def histogram(self, strains = None, axes = None,  plt_kwargs = None):
        """
        Generate a histogram of the distribution of BSR for specified
            strains.

        Arguments:
            strains (list[str or int]), optional: The strains that will be
                included in the histogram. Ordering effects the results seen.
                Default: Plots all strains
            axes (plt.axes.Axes), optional: If supplied will be used for
                plotting and returned. Otherwise a Figure and Axes object
                will be created and returned.
            plt_kwargs (dict), optional: passed to plt.hist().
        """
        strains = self.get_strains(strains)

        matches = self.bsr_records
        x_data = [[] for _ in strains]
        for match in matches:
            for hist_i, str_i in enumerate(strains):
                x_data[hist_i].append(match.bsr[str_i])

        fig, ax, plt_kwargs = self._deal_with_plot_stuff(
            axes, plt_kwargs, {'label':[self.strain_names[i] for i in strains]}
        )

        plt.hist(x_data,  **plt_kwargs)
        plt.legend(loc = 'upper left')
        plt.xlabel('BSR')
        plt.ylabel('Count')

        return fig, ax


    def get_bsr_array(self, strains = None):
        """Retruns nested list len(strains) columns by len(ref fasta) rows"""
        strains = self.get_strains(strains)
        #bsr = [[] for _ in strains]
        bsr = []
        for rec in self.bsr_records:
            bsr.append(
                [rec.bsr[strn] for strn in strains]
            )

            #
            # for ordered, strain in enumerate(strains):
            #     bsr[ordered].append(rec.bsr[strain])

        return bsr


    def heatmap(self, strains = None, axes = None, plt_kwargs = None,
                n = None, groups = None, width = 5):
        """
        Generate a heat map of BSR for specified strains.

        Arguments:
            strains (iter[str or int]), optional: The strains that will be
                included in the histogram. Ordering effects the results seen.
                Default: Plots all strains
            axes (plt.axes.Axes), optional: If supplied will be used for
                plotting and returned. Otherwise a Figure and Axes object
                will be created and returned.
            plt_kwargs (dict), optional: passed to plt.hist().
            n (int), optional: Number of CDS to be included.
            groups (iter[bool]), optional: Split strains into two groups
                using a mask. The positive difference in mean BSR between the
                two groups will be used to order the CDS shown in the heat map
                with highest difference at the top. By default CDS shown in
                the same order as they were obtained.
            width (int), optional: Specifies the width of pixels, relative to
                their height. Default: 5.
        """
        # Some ordering and option to limit it to the top X
        bsr = self.get_bsr_array(strains)
        strains = self.get_strains(strains)
        if groups:
            # Get the difference in scores between the postive group and negative
            def sorter(bsrs):

                return mean([s for i, s in enumerate(bsrs) if groups[i]]) - \
                    mean([s for i, s in enumerate(bsrs) if not groups[i]])
            bsr.sort(key = sorter, reverse=True)

        fig, ax, plt_kwargs = self._deal_with_plot_stuff(
            axes, plt_kwargs,
            dict(cmap = 'cool',
                 extent=(0, len(strains) * width, 0, len(bsr)) )
        )
        ax.imshow( bsr[:n], **plt_kwargs )
                  #aspect = 'auto')

        # The relationship between ax specific x values and the extent is
        # weird, and the autoticks are unrelated to the number of columns
        xmin, xmax = ax.get_xlim()
        tick_sz = xmax/len(strains)
        xticks = [i*tick_sz+0.5*tick_sz for i in range(len(strains))]
        strain_labs = [self.strain_names[i] for i in strains]
        # Position xticks depending on width
        ax.set_xticks(
            xticks
        )
        ax.set_yticklabels([])

        ax.set_xticklabels(
            strain_labs,
            rotation = 'vertical'
        )
        fig.tight_layout()
        if axes is None:
            return fig, ax
        else:
            return ax


    def _deal_with_plot_stuff(self, axes, user_kwargs, set_kwargs = None):
        """Parse args for plotting funcs. Get (fig, ax, kwargs).
        Fig = None if axes = None."""
        if axes is None:
            fig, ax = plt.subplots(1,1)
        else:
            ax = axes
            fig = None

        if user_kwargs is None:
            kwargs = {}
        if set_kwargs:
            for kw, v in set_kwargs.items():
                if kw not in kwargs:
                    kwargs[kw] = v

        return fig, ax, kwargs

    def __repr__(self):
        return '<BSR_RecordSet: {}. {} records>'.format(
            self.job_title, len(self.bsr_records)
        )

class BSR_Record:
    """
    Stores details of protein sequences and BSR etc. BSR_Record.bsr and
        similar stored as lists with the reference at i = 0.

    If iterated through returns a tuple of (fasta_title, aa_seq, blast_score,
        bsr) for each strain.

    Attributes:
        bsr (list[float]): Blast Score Ratios of strains. Reference strain at
            i = 0, always has the value of 1.0.
        aa_seqs (list[str]): Amino acid sequences of the reference strain
            and highest scoring sequences in the comparison strains.
        blast_scores (list[int]): BLAST scores used to generate BSR.
        fasta_titles (list[str]): FastA titles for reference sequence and
            highest scoring sequences from comparison fastas
        record_num (int): Reflects order the Record was generated in. The first
            CDS in the reference FastA will have record_num == 0 and record_num
            will match the record's position in BSR_RecordSet.bsr_records.

    Methods:
        get_query(strain_index): Returns (fasta_title, aa_seq, blast_score,
            bsr)
    """
    def __init__(self, ref_title, ref_seq, ref_strain_name, ref_score = None,
                 record_num = None): #ref_loc = None):
        # ref_* are details of the organism to which all others are compared
        # hit_* are the comparees, listed in order of comparison, hit_seqs[2]
        # matches up to bsr[2], hit_titles[2] etc.

        self.ref_title = ref_title
        self.ref_seq = ref_seq
        self.ref_score = ref_score
        #self.ref_loc = ref_loc
        self.fasta_titles = [ref_title] # The fastA description of the best hit for the ref seq
        self.aa_seqs = [ref_seq]
        self.blast_scores = [ref_score]
        self.bsr = [1]
        self.record_num = record_num
        self._index = 0 # used by __next__
        # Note that the reference strain goes first so the index won't match the other lists here
        self.strain_names = [ref_strain_name]
        # IPRScan details will be implimented elsewhere
        self.iprs_details = None
        # .nt_loci is not set in this module, but is used elsewhere. Places are saved with None
        self.nt_loci = [None]


    def get_query(self, i):
        return (self.fasta_titles[i], self.aa_seqs[i], self.blast_scores[i], self.bsr[i])

    def add_hit(self, title, score, seq, strain_name):
        self.fasta_titles.append(title)
        self.aa_seqs.append(seq) # A space is saved for the seq if None
        self.blast_scores.append(score)
        bsr = score/self.ref_score
        self.bsr.append(bsr)
        self.strain_names.append(strain_name)
        self.nt_loci.append(None)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            val = self.get_query(self._index)
            self._index+=1
            return val
        except IndexError:
            raise StopIteration()

    def __repr__(self):
        bsr_string = ' '.join('{:.2}'.format(score) for score in self.bsr[1:])
        return '<BSR_Record #{}. {}, BSRs: {}>'.format(
            self.record_num, self.ref_title, bsr_string
        )


def get_initial_BSR_Records_with_ref_scores(ref_fasta, strain_name):
    """
    Creates BSR records with reference BLAST score for each
    protein sequence given in ref_fasta. Ref_fasta should be a string
    giving the fastA file path.

    Returns a dictionary of records and the concatonated AA string, containing
    all protine sequences in the ref_fasta. This should be saved somewhere.
    """

    print('Making BSR records from this file:', ref_fasta)

    # First make concatonated fastA file (aka proteome fasta) and match obj with position of sequence recorded

    # The object to be returned. Dict uses the ref fastA description as key
    matches = {}
    # For printing updates
    counter = 0

    for gene_num, rec in enumerate(SeqIO.parse(ref_fasta,'fasta')):
        counter+=1

        try:
            refscore = sum([ MATRICES[MATRIX][aa] for aa in str(rec.seq).upper() ])

        except KeyError as e:
            print('\n')
            print(rec.description)
            print(str(rec.seq))
            raise e

        prot_comp = BSR_Record(rec.description,
                               rec.seq,
                               strain_name,
                               refscore,
                               record_num=gene_num
                               #(loc, loc+len(rec.seq))
                               )
        #amino_acid_seqs.append(str(rec.seq))
        #loc+=len(rec.seq)

        # GenemarkS uses '\t' in fasta descriptions, biopython BLAST records
        # truncate at the tab messing up later steps. No doubt other escape sequences will mess this up too.
        match_title = rec.description.split('\t')[0]
        matches[match_title] = prot_comp
        if counter % 100 == 0:
            print(counter, '... ', end = '')

    print(counter, 'BSR record objects created')
    return matches#, concat_aa

# # Testing above function 18.03.17, passed, the origional fastA can be reproduced from the attributes of the BSR_Records
# faa = seq_paff+'zz.faa'
# matches, aa_string = get_initial_BSR_Records_with_ref_scores(faa)
# for m in matches.values():
#     start, stop = m.ref_loc
#     print(m.ref_title)
#     # Get the substring from the concat AA seq
#     s = aa_string[start:stop]
#     print(s)
#     assert s == m.ref_seq
# raise EOFError

def get_bsr_for_strain(bsr_records, blast_results_path, strain_name):
    """Give a bunch of BSR_Record {'match_key':BSR_Record, ...}
    and a blast results filepath. BSR etc. updated in the Match.
    Dict of BSR_Record returned as provided.

    BLAST records should have the FASTA title as alignment.hit_def
    """

    print('Getting BSR from this blast results file:', blast_results_path)

    record_count = 0
    records_with_hits = 0

    for record in NCBIXML.parse(open(blast_results_path)):
        if record.alignments:
            records_with_hits+=1
            #Take the best hit for each query sequence
            hsps = record.alignments[0].hsps[0]
            sbjct_descrpt = record.alignments[0].hit_def
            sbjct_seq = ''.join([nt for nt in hsps.sbjct if nt != '-'])
            best_score = hsps.score
            #query_score = record.alignments[0].hsps[0].score
            query_descrpt = record.query

            if query_descrpt in bsr_records:
                bsr_records[query_descrpt].add_hit(sbjct_descrpt, best_score, sbjct_seq,strain_name)
            else:
                print(query_descrpt, 'not found in bsr_records, this shouldnt happen but can result from weirdly formated FastA record descriptions.')
                raise KeyError
        # If this didn't hit in the subject genome we still want to create an
        # empty placeholder in the match record
        else:
            bsr_records[record.query].add_hit('', 0, None, strain_name)
        if record_count %100 == 0:
            print(record_count, '... ', sep='', end='')
        record_count+=1

    print('Of {} reference sequences, {} had hits in the primary proteome.'.format(record_count,records_with_hits ))

    return bsr_records


def _do_next_step_pickle(fn, func, args = None, kwargs = None, force_redo = False):
    """
    If force_redo is False, checks if a pickled results file exists.
        Returns it if it does. If it doesn't or, force_redo  is True, performs
        func(*args, **kwargs), pickles the returned object using path fn and
        returns the object."""
    if not os.path.isfile(fn) or force_redo:

        if kwargs and args:
            output = func(*args, **kwargs)
        elif args:
            output = func(*args)
        elif kwargs:
            output = func(**kwargs)
        else:
            output = func()
        with open(fn, 'wb') as f:
            pickle.dump(output, f)
            print('file saved: ', fn)

    else:
        with open(fn, 'rb') as f:
            output = pickle.load(f)
            print('File loaded:', fn)
    return output


def get_bsr(work_path, job_name, reference_fasta, comparison_fastas,
            strain_names, force_redo = False):
    """Return a BSR_RecordSet containing BSR_Record objects with
    the results of a BSR analysis.

    Args:
        work_path (str): The path were generated files will be saved to.
        job_name (str): Prefix used for all generated file names, and stored
            in the returned BSR_Record
        reference_fasta (str): Path of the FastA file used as the reference
        comparison_fastas (iter[str]): List or tuple of paths to FastA files
            for which BSR will be generated.
        strain_names (iter[str]): Strain/species names of organisms in the
            analysis. Used when generating graphs and optionally to obtain
            data of that strain.
        force_redo (bool): If True the analysis will be performed from the
            start, overwriting any files in the workpath. Defaults to False.

    Returns:
        BSR_RecordSet: see documentation for this object for more info

    A series of blastp are performed using the reference_fasta as the query
        against the comparison_fastas. Files archiving the process are created
        and saved to disc using pickle. If the process is interupted then it
        can be continued by running the same command.
    """
    assert len(comparison_fastas) == len(strain_names)-1
    created_files = []
    # Create (or load) the initial BSR_records from the prime fasta
    fprefix = work_path+job_name
    init_bsr_records_fn = fprefix+' - ref BSR records.pickle'

    bsr_records = _do_next_step_pickle(
        init_bsr_records_fn,
        get_initial_BSR_Records_with_ref_scores,
        (reference_fasta, strain_names[0]), # Don't forget to pass *args as tuple
        force_redo=force_redo
    )
    created_files.append(init_bsr_records_fn)
    # Go through each proteome to be compared to the reference and get BSR.
    if type(comparison_fastas) is not list:
        comparison_fastas = [comparison_fastas]
    comparison_num = 0
    for comparee_index, subject_fasta in enumerate(comparison_fastas):
        comparison_num +=1
        # Get a blast of every reference sequences against the comparison proteome
        blast_results_path = fprefix + ' - BLAST ref vs ' + os.path.split(subject_fasta)[1] + '.xml'
        created_files.append(blast_results_path)
        if not os.path.isfile(blast_results_path) or force_redo:
            blast_query = blastp(query = reference_fasta,
                                 subject = subject_fasta,
                                 remote = False,
                                 outfmt = 5,
                                 max_hsps = 1,
                                 matrix = MATRIX,
                                 comp_based_stats = "0")
            # run the blast
            blast_results = blast_query()

            with open(blast_results_path, 'w') as f:
                f.write(blast_results[0])
                print('BLAST results file saved:', blast_results_path)

        bsr_records_path = fprefix+' - {} of {} BSR calculated.pickle'.format(
            comparison_num, len(comparison_fastas)
        )
        created_files.append(bsr_records_path)
        bsr_records = _do_next_step_pickle(
            bsr_records_path,
            get_bsr_for_strain,
            (bsr_records, blast_results_path, strain_names[comparee_index+1]),
            force_redo = force_redo
        )

    final_results_path = fprefix+' - complete BSR results.pickle'
    created_files.append(final_results_path)
    final_results = BSR_RecordSet(job_name, bsr_records, reference_fasta, comparison_fastas, strain_names, created_files)
    fn = work_path+job_name+' - Final record set.pickle'
    with open(fn, 'wb') as f:
        pickle.dump(final_results, f)
        print('File saved:', fn)

    return final_results

def test():
    print('Running demo.py')
    import demo
    print("\n\nHopefully it didn't crash")

# def run_from_command_line_not_implimented():
#     parser = argparse.ArgumentParser(
#         description="""Obtain Blast Score Ratios of protein sequences to identify potentially
#         conserved or horizontally transferred genes.""")
#     # work_path, job_name, primary_fasta: str, comparison_fastas, strain_names, force_redo = False
#     parser.add_argument('--job-name',
#                         help = 'String to be used as prefix for all generated files')
#     parser.add_argument('--work-path',
#                         help = 'Path were all generated files will be stored')
#     parser.add_argument('--primary',
#                         help = 'FastA file containing the primary sequences from which BSR will be generated')
#



#todo: integrate with IPRS, maybe add or recieve details from IPRS results table
#todo support BLOSSUM
#todo: sort func in RecordSet




# if __name__ == '__main__':



