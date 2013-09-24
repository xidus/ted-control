#!/bin/bash

# PATHS
DATA_SMALL=/home/joachim/ku/msc/work/data
DATA_BIG=/home/joachim/projects/data/msc
SCRIPTS=/home/joachim/ku/msc/work/code

# Clean up first, since the file is only appended to in the following
rm $DATA_SMALL/fpC_all.txt

# Build one big file with all the results
cat $DATA_BIG/CAS_fields/*.csv >> $DATA_SMALL/fpC_all.txt

# Sort and remove duplicates
cat $DATA_SMALL/fpC_all.txt | sort | uniq > $DATA_SMALL/fpC_all_uniq.csv

# Move last line (with the CSV headers) to the top
$SCRIPTS/correct_fpC_all_uniq.py

# ---

# Count the number of records found for each coordinate
wc -l $DATA_BIG/CAS_fields/*.csv > $DATA_SMALL/nrecords.dat
sed '$d' < $DATA_SMALL/nrecords.dat > tempfile
mv $DATA_SMALL/nrecords.dat $DATA_SMALL/nrecords.dat.old
mv tempfile $DATA_SMALL/nrecords.dat

