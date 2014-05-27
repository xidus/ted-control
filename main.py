#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Version: Sun 1 Sep 2013
#   * Initial build.
#

import sys

import ted
import ted.sdss
import ted.sdss.cas
import ted.sdss.das
import ted.sdss.cutouts
import ted.sdss.cutouts.manage
import ted.sdss.cutouts.plotting
import ted.sdss.cutouts.crossvalidation


def main(*args):
    """
    The main controller for running the
    programs written for this thesis project.

    Parameters
    ----------
    args : list
        contains words whose order is independent
        from their use in this function.

        If a word whose presence is checked for *is* present,
        some action is performed. But only in the order in
        which it is placed in the script.

    To do
    -----
    Make script check whether some procedure has been performed,
    before a procedure that depends on this being so is performed.

    One way to do it could be to update a log file which can be cleared
    if there is a need for starting over from the top. This would only
    be a deletion of records of the steps having been performed so far,
    and not the data that were generated as a consequence of running
    those procedures. Each of the procedures may or may not check if
    any given data already exist and redo or skip creating those data
    unless specifically being forced to.

    Returns
    -------
    None

    """

    # CAS
    # query database and save results for each supernova coordinate in separate file.
    #   loading the candidate list
    #       merges the two lists if they have not been merged
    #           Error thrown if source lists do not exists. If so, reate manually.
    #
    # Path 1)
    #   create a single file with all the unique and sorted results from the above query.
    #   If all data are to be downloaded, use function that uses this list. Otherwise use the function that lets you download frames for selected supernovae.
    #   run function that ceates a file with number of records found for each individual candidate.
    #   Run data analysis on all the data
    #
    # Path 2)
    #   Download only frames for given candidates
    #   The function which does this, checks if the given file exists before downloading it (since more than one candidate may be within the region covered by a given found field.)
    #   Now the data are ready for analysis. The notebook with this initial trial an error thing should work.

    """Foundation

    * Creating the list of coordinates for which to obtain overlapping
      image frames.

    * Create database files that will contain easily accessible metadata.

    """

    if 'snlist-merge' in args:

        ted.sdss.merge_sne_lists()

    if 'snlist-sql-insert' in args:

        ted.sdss.sql_fill_table_SNe()

    if 'snlist-check-duplicates' in args:

        ted.sdss.cas.check_snlist()

    # ----------------------------------------------------------------------- #

    """CAS"""

    # Clean up?
    if 'cas-clean' in args:

        ted.sdss.cas.field_clean_local_dir()

    if 'cas-get-fields' in args:

        # Just for showing a few datapoints.
        # Incidentally, this call also makes sure that the source candidate files are being merged into one, if not already done.
        df = ted.sdss.load_SNe_candidate_list()
        print df.head(3)
        # df.index = df.SDSS_id

        print '\nQuerying CAS online form (skipping existing files) ...'
        ted.sdss.cas.get_fields()
        # ted.sdss.CAS_get_fields(in_parallel=True, pool_size=10) # Not possible, since CAS online query form limits to 1 request per second.

        print 'cas-get-fields: Done ...'

    if 'cas-get-fields-force' in args:

        print '\nQuerying CAS online form (force-mode) ...'
        ted.sdss.cas.get_fields(skip_if_exists=False)
        # ted.sdss.CAS_get_fields(in_parallel=True, pool_size=10) # Not possible, since CAS online query form limits to 1 request per second.

        print 'cas-get-fields-forced: Done ...'

    if 'cas-csv-fields-gather' in args:

        # Build a single list of alle the unique fields that cover any of the candidate supernovae.
        print 'cas-csv-fields-gather: Creating unique field list ...'
        # Keep invalid frames (negative or having ~ zero RA extent) for now,
        # but this is a big problem, when coding up the analysis,
        # since I need to manually exclude these every time.
        ted.sdss.cas.create_unique_field_list()

    if 'cas-csv-fields-filter-invalid' in args:

        print 'cas-csv-fields-filter-invalid: Filtering invalid fields from unique field list ...'
        ted.sdss.cas.filter_invalid_from_unique_field_list()

    if 'cas-csv-fields-nrecords' in args:

        # Count how many fields that cover each candidate.
        print 'cas-csv-fields-nrecords: Counting field records for each supernova ...'
        ted.sdss.cas.count_field_records()

    if 'cas-csv-fields-nrecords-q' in args:

        print 'cas-csv-fields-nrecords-q: Counting field records for each supernova ...'
        ted.sdss.cas.count_field_records_by_quality()

    # ----------------------------------------------------------------------- #

    """GALAXIES"""

    if 'cas-get-galaxies' in args:

        ted.sdss.cas.get_galaxies()

    if 'cas-create-galaxy-list' in args:

        ted.sdss.cas.create_galaxy_list()

    if 'cas-build-tlist' in args:

        ted.sdss.cas.build_tlist()

    if 'cas-build-tlist-sample' in args:

        ted.sdss.cas.build_tlist_sample()

    if 'cas-check-tlist' in args:

        """For each entry in `tlist.csv`, find out how many fields cover it."""
        ted.sdss.cas.check_tlist()

    # ----------------------------------------------------------------------- #

    """DAS"""

    if 'das-get-some' in args:

        print 'Getting only some of the frames from the DAS for testing ...'
        # Select slice of SNe candidates to download frames for.
        # A single function gets a single FITS file, and it is called when downloading both all or some of the frames.
        #   it should
        #       * check if the file exists
        #       * copy the file structure of the DAS ,when saving the files locally.
        #   should it
        #       * update a database table of downloaded frames?
        #           or would this be better done with a general file checking script which uses a database table of all the frames, and checks each file one by one to see if it was downloade, and, if not, try to download it, if an attempt has not already been made and the HTTP status code made it clear that it would not be available. Compile a list of non-downloadable frames and send it to the SDSS collaboration.
        #
        # ted.sdss.das.download_frames_by_sn(bix=0, eix=5, frame_type='fpC', filt='r', pool_size=10)
        ted.sdss.das.download_frames_by_sn(bix=5, eix=10, frame_type='fpC', filt='r', pool_size=10)

    if 'das-get-all' in args:

        print 'Getting all of the frames from the DAS ...'

        print '\nBuilding unique list of URIs to download from DAS ...'
        ted.sdss.das.export_fpC_URIs()

        # ted.sdss.DAS_download_fields(in_parallel=True, pool_size=10)
        ted.sdss.das.download_fields_from_list(pool_size=20)
        # ted.sdss.DAS_download_fields()

    if 'das-check-field-list' in args:

        print 'Assuming that all frames have been downloaded,'
        print 'excluded from fields.csv entries for which frames do not work.'

        # ted.sdss.das.check_field_list()
        ted.sdss.das.check_field_list(do_get_frames=False)


    # ----------------------------------------------------------------------- #

    """CUTOUTS"""

    if 'cut-create-raw' in args:

        ted.sdss.cutouts.create_cutout_data()

    if 'cut-create-fp2q' in args:

        ted.sdss.cutouts.create_cutout_original_to_field_quality_dict()

    if 'cut-create-c2q' in args:

        ted.sdss.cutouts.create_cutout2quality_mapping()

    if 'cut-remove-unwanted' in args:

        ted.sdss.cutouts.manage.remove_unwanted_data()

    if 'cut-remove-flags' in args:

        ted.sdss.cutouts.manage.remove_flags()

    if 'cut-tlist-log-plot' in args:

        ted.sdss.cutouts.plotting.plot_tlist_log()

    # ANY

    if 'cut-cv-any' in args:

        if 'q1' in args:

            ted.sdss.cutouts.crossvalidation.cv(exp='any', quality=[1])

        elif 'q2' in args:

            ted.sdss.cutouts.crossvalidation.cv(exp='any', quality=[2])

        elif 'q3' in args:

            ted.sdss.cutouts.crossvalidation.cv(exp='any', quality=[3])

        elif 'q12' in args:

            ted.sdss.cutouts.crossvalidation.cv(exp='any', quality=[1, 2])

        elif 'q23' in args:

            ted.sdss.cutouts.crossvalidation.cv(exp='any', quality=[2, 3])

        elif 'q13' in args:

            ted.sdss.cutouts.crossvalidation.cv(exp='any', quality=[1, 3])

        elif 'q123' in args:

            ted.sdss.cutouts.crossvalidation.cv(exp='any', quality=[1, 2, 3])

        else:

            ted.sdss.cutouts.crossvalidation.cv(exp='any')

    if 'cut-cv-any-all' in args:

        qualities = [
            [1],
            [2],
            [3],
            [1, 2],
            [2, 3],
            [1, 3],
            [1, 2, 3],
        ]

        for quality in qualities:
            print quality
            ted.sdss.cutouts.crossvalidation.cv(exp='any', quality=quality)

    if 'cut-cv-any-plot' in args:

        if 'q1' in args:

            ted.sdss.cutouts.crossvalidation.plot(exp='any', quality=[1])

        elif 'q2' in args:

            ted.sdss.cutouts.crossvalidation.plot(exp='any', quality=[2])

        elif 'q3' in args:

            ted.sdss.cutouts.crossvalidation.plot(exp='any', quality=[3])

        elif 'q12' in args:

            ted.sdss.cutouts.crossvalidation.plot(exp='any', quality=[1, 2])

        elif 'q23' in args:

            ted.sdss.cutouts.crossvalidation.plot(exp='any', quality=[2, 3])

        elif 'q13' in args:

            ted.sdss.cutouts.crossvalidation.plot(exp='any', quality=[1, 3])

        elif 'q123' in args:

            ted.sdss.cutouts.crossvalidation.plot(exp='any', quality=[1, 2, 3])

        else:

            ted.sdss.cutouts.crossvalidation.plot(exp='any')

    if 'cut-cv-any-analyse-all' in args:

        qualities = [
            [1],
            [2],
            [3],
            [1, 2],
            [2, 3],
            [1, 3],
            [1, 2, 3],
        ]

        for quality in qualities:
            print quality
            # ted.sdss.cutouts.crossvalidation.analyse(exp='any', quality=quality)


    # BASELINE

    if 'cut-cv-baseline-all' in args:

        """
        I need all the qualities, i.e. different number of labels,
        to account for the accuracy of a given model.
        """
        qualities = [
            [1],
            [2],
            [3],
            [1, 2],
            [2, 3],
            [1, 3],
            [1, 2, 3],
        ]
        experiments = ['blr', 'bla', 'bln']

        for exp in experiments:
            print exp
            for quality in qualities:
                print quality
                ted.sdss.cutouts.crossvalidation.cv(exp=exp, quality=quality)

    if 'cut-cv-baseline-plot-all' in args:

        qualities = [
            [1],
            [2],
            [3],
            [1, 2],
            [2, 3],
            [1, 3],
            [1, 2, 3],
        ]
        experiments = ['blr', 'bla', 'bln']

        for exp in experiments:
            print exp
            for quality in qualities:
                print quality
                ted.sdss.cutouts.crossvalidation.plot(exp=exp, quality=quality)


    if 'cut-cv-baseline-analyse-all' in args:

        qualities = [
            [1],
            [2],
            [3],
            [1, 2],
            [2, 3],
            [1, 3],
            [1, 2, 3],
        ]
        experiments = ['blr', 'bla', 'bln']

        for exp in experiments:
            print exp
            for quality in qualities:
                print quality
                ted.sdss.cutouts.crossvalidation.analyse(exp=exp, quality=quality)


    # MANY

    if 'cut-cv-many' in args:

        if 'q1' in args:

            ted.sdss.cutouts.crossvalidation.cv(exp='many', quality=[1])

        elif 'q2' in args:

            ted.sdss.cutouts.crossvalidation.cv(exp='many', quality=[2])

        elif 'q3' in args:

            ted.sdss.cutouts.crossvalidation.cv(exp='many', quality=[3])

        elif 'q12' in args:

            ted.sdss.cutouts.crossvalidation.cv(exp='many', quality=[1, 2])

        elif 'q23' in args:

            ted.sdss.cutouts.crossvalidation.cv(exp='many', quality=[2, 3])

        elif 'q13' in args:

            ted.sdss.cutouts.crossvalidation.cv(exp='many', quality=[1, 3])

        elif 'q123' in args:

            ted.sdss.cutouts.crossvalidation.cv(exp='many', quality=[1, 2, 3])

    if 'cut-cv-many-all' in args:

        qualities = [
            [1],
            [2],
            [3],
            [1, 2],
            [2, 3],
            [1, 3],
            [1, 2, 3],
        ]

        for quality in qualities:
            print quality
            ted.sdss.cutouts.crossvalidation.cv(exp='many', quality=quality)

    if 'cut-cv-many-analyse-all' in args:

        qualities = [
            [1],
            [2],
            [3],
            [1, 2],
            [2, 3],
            [1, 3],
            [1, 2, 3],
        ]

        for quality in qualities:
            print quality
            ted.sdss.cutouts.crossvalidation.analyse(exp='many', quality=quality)

    if 'cut-cv-many-plot-all' in args:

        qualities = [
            [1],
            [2],
            [3],
            [1, 2],
            [2, 3],
            [1, 3],
            [1, 2, 3],
        ]

        for quality in qualities:
            print quality
            ted.sdss.cutouts.crossvalidation.plot(exp='many', quality=quality)




    # ----------------------------------------------------------------------- #

    """DONE"""

    print 'main.py: Done ...'


if __name__ == '__main__':
    main(*sys.argv[1:])
