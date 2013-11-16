#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Version: Sun 1 Sep 2013
#   Initial build.
#

import sys

import ted
import ted.sdss


def sql_fill_table_SNe():
    """Inserts records from the SNe lists into an SQLite3 db."""

    import os
    import sqlite3

    import numpy as np
    import pandas as pd

    def col_count(df):
        # names = ['SDSS_id', 'SN_type', 'IAUC_id', 'redshift', 'Peak_MJD']
        # tests = ['', '', '', np.nan, np.nan]
        names = ['SN_type', 'IAUC_id', 'redshift', 'Peak_MJD']
        tests = ['', '', np.nan, np.nan]
        counts = [(df_right[name].values != test).sum() for name, test in zip(names, tests)]
        print ('{: >10s} ' * len(names)).format(*names)
        print ('{: >10d} ' * len(names)).format(*counts)
        print ''

    _path_data_small = ted.paths['data']['small']['path']
    fn_snlist_sdss_org = os.path.join(_path_data_small, 'snlist_confirmed.csv')
    fn_snlist_SNII_upd = os.path.join(_path_data_small, 'SDSS-II-SNe.csv')

    ofn_snlists_merged = os.path.join(_path_data_small, 'snlist_merged_flagged.csv')
    ofn_sqlite_skyml = os.path.join(_path_data_small, 'skyml.sqlite')

    _path_sql = ted.paths['sql']['path']
    fn_create_table_sne = os.path.join(_path_sql, 'skyml_create_table_SNe.sql')

    def snid_sortable(SDSS_id):
        _id = int(SDSS_id[2:])
        # print SDSS_id, _id
        return 'SN{:0>5d}'.format(_id)

    s2valornan = lambda s: s or np.nan
    conv = dict(SDSS_id=snid_sortable, Ra=ted.sdss.ra2deg, Dec=ted.sdss.dec2deg,
        redshift=s2valornan, Peak_MJD=s2valornan)
    df_left = pd.read_csv(fn_snlist_sdss_org, sep=';', converters=conv)
    df_right = pd.read_csv(fn_snlist_SNII_upd, sep=';', converters=conv)
    # df_left = pd.read_csv(fn_snlist_sdss_org, sep=';', converters=conv, index_col='SDSS_id')
    # df_right = pd.read_csv(fn_snlist_SNII_upd, sep=';', converters=conv, index_col='SDSS_id')

    SDSS_id_left = list(df_left.SDSS_id)
    SDSS_id_right = list(df_right.SDSS_id)
    SDSS_ids = np.array(SDSS_id_left + SDSS_id_right)
    SNids = np.unique(SDSS_ids)
    SNids.sort()

    columns = list(df_left.columns)
    # print columns
    # raise SystemExit
    ncols = len(columns) - 1
    df = pd.DataFrame(columns=columns)
    print df.describe()
    tests = [''] * 2 + [np.nan] * 4
    # raise SystemExit

    for SNid in SNids:
        # print SNid,
        lix = (df_left.SDSS_id == SNid)
        rix = (df_right.SDSS_id == SNid)
        ls = lix.sum()
        rs = rix.sum()

        # First, do both sides have the SDSS_id?
        # If not, just add the given one to the DataFrame.
        if ls and rs:
            # print 'is a duplicate ...'
            row_left = df_left[lix]
            row_right = df_right[rix]
            values = row_left.copy()
            # print values.values[0, 0], values.shape
            # raise SystemExit
            test_left = [(row_left[col].values[0] != test) for col, test in zip(columns, tests)]
            test_right = [(row_right[col].values[0] != test) for col, test in zip(columns, tests)]
            for i in range(1, ncols):

                col = columns[i]

                if test_left[i] and test_right[i]:
                    # Both have valid values
                    # Choose the value from the newest list
                    values.values[0, i] = row_right.values[0, i]

                elif test_right[i]:
                    values.values[0, i] = row_right.values[0, i]

                else:
                    values.values[0, i] = row_left.values[0, i]

            df = df.append(values)

        elif rs:
            # print 'is unique (right) ...'
            df = df.append(df_right[rix])

        elif ls:
            # print 'is unique (left) ...'
            df = df.append(df_left[lix])

    df.sort_index(by='SDSS_id', ascending=True)
    # print df.head(10)
    # raise SystemExit

    # ---

    # print df_left.head(10)
    # raise SystemExit

    # df = pd.merge(df_left, df_right, on=['SDSS_id'], sort=True)
    # col_count(df_right)
    # df = pd.merge(df_left, df_right, how='outer', sort=True)
    # col_count(df)

    # from IPython import embed
    # embed()

    # df = df.sort_index(by='SDSS_id', ascending=True)
    # df = pd.merge(df_left, df_right, how='outer')
    # df = pd.concat([df_left, df_right], join='outer', join_axes=[''], ignore_index=True, verify_integrity=True)
    # df = df_left.combine_first(df_right)
    # df_left.update(df_right)
    # df = df_left

    # col_count(df_right)
    # df_right.update(df_left)
    # col_count(df_right)
    # df = df_right

    # df = df.sort_index(by='SDSS_id', ascending=True)
    # df = pd.merge(df_left, df_right, on=df_left.columns.values, sort=True)
    # df = pd.concat([df_left, df_right], join='outer', ignore_index=True, verify_integrity=True)
    # df = df.sort_index(by='SDSS_id', ascending=True)

    # print df.head(10)
    # raise SystemExit

    # Check if confirmed by IAUC, i.e. that it has an ID.
    confirmed = (df['IAUC_id'].values != np.nan)
    flags = np.zeros_like(df['IAUC_id'].values).astype(str)
    flags[confirmed] = 'C'
    flags[~confirmed] = ''
    df['Flag'] = flags

    print 'Confirmed SNe (has IAUC ID):', confirmed.sum()
    print 'Internally confirmed SNe:', (~confirmed).sum()

    df.to_csv(ofn_snlists_merged, sep=';', index=False, header=True)

    # # Read SQL
    with open(fn_create_table_sne, 'r') as fsock:
        sql_create_table_sne = fsock.read()

    # Connect to database file
    with sqlite3.connect(ofn_sqlite_skyml) as con:
        cur = con.cursor()
        cur.execute('DROP TABLE IF EXISTS Supernovae')
        cur.execute(sql_create_table_sne)
        # from IPython import embed
        # embed()
        sql_insert = '''\
INSERT INTO Supernovae
    (SDSS_id, SN_type, IAUC_id, Ra, Dec, redshift, Peak_MJD, Flag)
    VALUES
    (?, ?, ?, ?, ?, ?, ?, ?)
'''
        # cur.executemany(sql_insert, df.values)
        for i, row in enumerate(df.values):
            # print i
            cur.execute(sql_insert, row)
        # con.commit()
        # df.to_sql(name='Supernovae', con=con, if_exists='replace')


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

    """Clean up?
    """

    # asdf

    """Foundation

    * Creating the list of coordinates for which to obtain overlapping
      image frames.

    * Create database files that will contain easily accessible metadata.

    """

    if 0:
        sql_fill_table_SNe()

    """Data gathering


    """

    if 0:

        # Just for showing a few datapoints.
        df = ted.sdss.load_SNe()
        print df.head(3)
        # df.index = df.SDSS_id

        print '\nQuerying CAS online form ...'
        ted.sdss.CAS_get_fields()
        # ted.sdss.CAS_get_fields(in_parallel=True, pool_size=10) # Not possible, since CAS online query form limits to 1 request per second.

        print '\nBuilding unique list of URIs to download from DAS ...'
        ted.sdss.DAS_export_fpC_URIs()

        # Then call external script to organise the downloaded data
        # and prepare them for preliminary statistical analysis.
        import os

        exec_prefix = '/home/joachim/ku/msc/work/code'
        scripts = (
            'make_fpC_unique_csv.sh',
        )

        for fname_script in scripts:
            cmd = os.path.join(exec_prefix, fname_script)
            print 'executing:', cmd
            os.system(cmd)

    if 0:
        # ted.sdss.DAS_download_fields(in_parallel=True, pool_size=10)
        ted.sdss.DAS_download_fields_from_list(pool_size=20)
        # ted.sdss.DAS_download_fields()

    if 0:
        ted.sdss.CAS_get_galaxies()


if __name__ == '__main__':
    main(*sys.argv[1:])
