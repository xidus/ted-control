#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Version: Sun 1 Sep 2013
#   * Initial build.
#

"""
Control module for running the programs
written for my master's thesis project.

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

"""

import ted
import ted.sdss
import ted.sdss.cas
import ted.sdss.das
import ted.sdss.cutouts
import ted.sdss.cutouts.manage
import ted.sdss.cutouts.plotting
import ted.sdss.cutouts.crossvalidation

from setup_and_parse import setup_and_parse


def load_args():
    arglist = [
        (
            ('-s', '--snlist'),
            dict(type=str, nargs='?', default=None, help='Actions for SNLIST')
        ),
        (
            ('-c', '--cas'),
            dict(type=str, nargs='?', default=None, help='Actions for the CAS')
        ),
        (
            ('-d', '--das'),
            dict(type=str, nargs='?', default=None, help='Actions for the DAS')
        ),
        (
            ('-g', '--gxlist'),
            dict(type=str, nargs='?', default=None, help='Actions for GXLIST')
        ),
        (
            ('-t', '--tlist'),
            dict(type=str, nargs='?', default=None, help='Actions for TLIST')
        ),
        (
            ('-u', '--cut'),
            dict(type=str, nargs='?', default=None, help='Actions for cutout sequences')
        ),
        (
            ('-x', '--exp'),
            dict(type=str, default=None, help='The name of the experiment to run')
        ),
        (
            ('-a', '--action'),
            dict(type=str, default=None, help='Action to perform')
        ),
        (
            ('-q', '--quality'),
            dict(type=int, nargs='+', default=[1, 2, 3])
        ),
    ]
    return setup_and_parse(__doc__, arglist)


def main():

    args = load_args()

    # Temporary hack
    # args.__class__.__contains__ = lambda self, item: False

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

    if args.snlist is not None:

        if 'merge' in args.snlist:

            ted.sdss.merge_sne_lists()

        if 'sql-insert' in args.snlist:

            ted.sdss.sql_fill_table_SNe()

        if 'check-duplicates' in args.snlist:

            ted.sdss.cas.check_snlist()

    # ----------------------------------------------------------------------- #

    """CAS"""

    if args.cas is not None:

        # Clean up?
        if 'clean' in args.cas:

            ted.sdss.cas.field_clean_local_dir()

        if 'get-fields' in args.cas:

            # Just for showing a few datapoints.
            # Incidentally, this call also makes sure that the source candidate files are being merged into one, if not already done.
            df = ted.sdss.load_SNe_candidate_list()
            print df.head(3)
            # df.index = df.SDSS_id

            print '\nQuerying CAS online form (skipping existing files) ...'
            ted.sdss.cas.get_fields()
            # ted.sdss.CAS_get_fields(in_parallel=True, pool_size=10) # Not possible, since CAS online query form limits to 1 request per second.

            print 'get-fields: Done ...'

        if 'get-fields-force' in args.cas:

            print '\nQuerying CAS online form (force-mode) ...'
            ted.sdss.cas.get_fields(skip_if_exists=False)
            # ted.sdss.CAS_get_fields(in_parallel=True, pool_size=10) # Not possible, since CAS online query form limits to 1 request per second.

            print 'get-fields-forced: Done ...'

        if 'csv-fields-gather' in args.cas:

            # Build a single list of alle the unique fields that cover any of the candidate supernovae.
            print 'csv-fields-gather: Creating unique field list ...'
            # Keep invalid frames (negative or having ~ zero RA extent) for now,
            # but this is a big problem, when coding up the analysis,
            # since I need to manually exclude these every time.
            ted.sdss.cas.create_unique_field_list()

        if 'csv-fields-filter-invalid' in args.cas:

            print 'csv-fields-filter-invalid: Filtering invalid fields from unique field list ...'
            ted.sdss.cas.filter_invalid_from_unique_field_list()

        if 'csv-fields-nrecords' in args.cas:

            # Count how many fields that cover each candidate.
            print 'csv-fields-nrecords: Counting field records for each supernova ...'
            ted.sdss.cas.count_field_records()

        if 'csv-fields-nrecords-q' in args.cas:

            print 'csv-fields-nrecords-q: Counting field records for each supernova ...'
            ted.sdss.cas.count_field_records_by_quality()

    # ----------------------------------------------------------------------- #

    """GALAXIES"""

    if args.gxlist is not None:

        if 'get-galaxies' in args.gxlist:

            ted.sdss.cas.get_galaxies()

        if 'create-galaxy-list' in args.gxlist:

            ted.sdss.cas.create_galaxy_list()

    # ----------------------------------------------------------------------- #

    """TRAINING and TEST data set (TLIST)"""

    if args.tlist is not None:

        if 'build' in args.tlist:

            ted.sdss.cas.build_tlist()

        if 'build-sample' in args.tlist:

            ted.sdss.cas.build_tlist_sample()

        if 'check' in args.tlist:

            """For each entry in `tlist.csv`,
            find out how many fields cover it."""
            ted.sdss.cas.check_tlist()

    # ----------------------------------------------------------------------- #

    """DAS"""

    if args.das is not None:

        if 'get-some' in args.das:

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

        if 'get-all' in args.das:

            print 'Getting all of the frames from the DAS ...'

            print '\nBuilding unique list of URIs to download from DAS ...'
            ted.sdss.das.export_fpC_URIs()

            # ted.sdss.DAS_download_fields(in_parallel=True, pool_size=10)
            ted.sdss.das.download_fields_from_list(pool_size=20)
            # ted.sdss.DAS_download_fields()

        if 'check-field-list' in args.das:

            print 'Assuming that all frames have been downloaded,'
            print 'excluded from fields.csv entries for which frames do not work.'

            # ted.sdss.das.check_field_list()
            ted.sdss.das.check_field_list(do_get_frames=False)

    # ----------------------------------------------------------------------- #

    """CUTOUTS"""

    if args.cut is not None:

        if 'create-raw' in args.cut:

            ted.sdss.cutouts.create_cutout_data()

        if 'create-fp2q' in args.cut:

            ted.sdss.cutouts.create_cutout_original_to_field_quality_dict()

        if 'create-c2q' in args.cut:

            ted.sdss.cutouts.create_cutout2quality_mapping()

        if 'remove-unwanted' in args.cut:

            ted.sdss.cutouts.manage.remove_unwanted_data()

        if 'remove-flags' in args.cut:

            ted.sdss.cutouts.manage.remove_flags()

        if 'tlist-log-plot' in args.cut:

            ted.sdss.cutouts.plotting.plot_tlist_log()

    # ----------------------------------------------------------------------- #

    """EXPERIMENTS"""

    if args.exp is not None:

        print args.exp
        print args.action
        print args.quality

        ekw = dict(exp=args.exp, quality=args.quality)

        if args.action == 'cv':

           ted.sdss.cutouts.crossvalidation.cv(**ekw)

        elif args.action == 'plot':

           ted.sdss.cutouts.crossvalidation.plot(**ekw)

        elif args.action == 'plot-all':

           ted.sdss.cutouts.crossvalidation.plot_all(exp=args.exp)

        elif args.action == 'analyse':

           ted.sdss.cutouts.crossvalidation.analyse(**ekw)


    # ----------------------------------------------------------------------- #

    """DONE"""

    print 'main.py: Done ...'


if __name__ == '__main__':
    raise SystemExit(main())
