
# TED control-script

A module to interface with the tools provided by my codebase for my master's thesis project.

# About

This module was made as part of my master's thesis project.

It calls functions within a Python package that I call [Transient-Event Detector (TED)](https://github.com/xidus/ted).

# Requirements

The script runs in Python 2.7.6+, but not in Python 3+.

It depends on a argument-parsing module that I have written, called [`setup_and_parse`](https://github.com/xidus/setup_and_parse).

# Running the code

The module is meant to be called directly from the command line.

(Examples might show up here. Otherwise, look through the code and see what it does.)


# Running the entire pipeline

## Data acquisition

### Supernovae candidates

Merge the two lists if they have not been merged

    $ main.py --snlist merge

Drop duplicates

    $ main.py --snlist check-duplicates


### SDSS Catalogue Archive Server (CAS)

#### Fields

Query database and save results for each supernova coordinate in separate file.

    $ main.py --cas get-fields

Create a single file with all the unique and sorted results from the above query.

    $ main.py --cas csv-fields-gather

    $ main.py --cas csv-fields-filter-invalid

#### Galaxies

To do the following steps requires that the galaxy catalogue has been downloaded from CasJobs using the SQL query in the sdss folder of the repository for TED. 

    $ main.py --gxlist create-galaxy-list

### SDSS Data Archive Server (DAS)

Download only frames from the list of fields obetained above.

    $ main.py --das get-all

Assuming that all frames have been downloaded,
exclude from `fields.csv` entries for which frames do not work (non-loadable by `astropy.io.fits` module).

    $ main.py --das check-field-list

Now the data are ready for pre-processing.


## Data reduction


### Training and test data set (TLIST)

Combine coordinates from `snlist` with coordinates from `gxlist`.

    $ main.py --tlist build

### Cutout sequences

    $ main.py --cut build

    $ main.py --cut create-raw

This was not initially done, when creating the cutout sequences, but in order to select only cutouts with certain qualities a mapping between each cutout and its quality based on the original frame from which it came has to be created.

First create the mapping between the field and the frame from which the cutout was created.

    $ main.py --cut create-fp2q

Then create the mapping from the cutout to the frame from which the cutout was created.

    $ main.py --cut create-c2q

## Experiments

### ANY

Run experiment for the chosen algorithm using all possible quality combinations the cutout frames.

    $ main.py --exp any --action cv analyse --quality 1
    $ main.py --exp any --action cv analyse --quality 2
    $ main.py --exp any --action cv analyse --quality 3
    $ main.py --exp any --action cv analyse --quality 1 2
    $ main.py --exp any --action cv analyse --quality 1 3
    $ main.py --exp any --action cv analyse --quality 2 3
    $ main.py --exp any --action cv analyse --quality 1 2 3

Plot the results

    $ main.py --exp any --action plot_all

### MANY

Run experiment for the chosen algorithm using all possible quality combinations the cutout frames.

    $ main.py --exp many --action cv analyse --quality 1
    $ main.py --exp many --action cv analyse --quality 2
    $ main.py --exp many --action cv analyse --quality 3
    $ main.py --exp many --action cv analyse --quality 1 2
    $ main.py --exp many --action cv analyse --quality 1 3
    $ main.py --exp many --action cv analyse --quality 2 3
    $ main.py --exp many --action cv analyse --quality 1 2 3

Plot the results

    $ main.py --exp many --action plot_all

### MANYC

Run experiment for the chosen algorithm using all possible quality combinations the cutout frames.

    $ main.py --exp manyc --action cv analyse --quality 1
    $ main.py --exp manyc --action cv analyse --quality 2
    $ main.py --exp manyc --action cv analyse --quality 3
    $ main.py --exp manyc --action cv analyse --quality 1 2
    $ main.py --exp manyc --action cv analyse --quality 1 3
    $ main.py --exp manyc --action cv analyse --quality 2 3
    $ main.py --exp manyc --action cv analyse --quality 1 2 3

Plot the results

    $ main.py --exp manyc --action plot_all

---
