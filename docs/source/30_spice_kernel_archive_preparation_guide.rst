**************************************
SPICE Kernel Archive Preparation Guide
**************************************

Process Overview
================

The process of preparing a SPICE archive includes the following steps:

    1. collecting and preparing the data

    2. preparing the NAIF PDS4 Bundler setup 

    3. running NAIF PDS4 Bundler

    4. checking the result and finishing up

    5. if needed, packaging and delivering the data set to NAIF

Each of these steps is described in a separate section below.


.. toctree::
   :maxdepth: 1

   31_step_1_preparing_data
   32_step_2_npb_setup
   33_step_3_running_npb
   


Step-by-Step Summary
====================

   This section provides a brief step-by-step summary of the process for
   creating a new archive and for adding another release to an existing
   archive. Please augment the checklists below with any additional steps
   needed for your SPICE archive.


Steps for Creating a New Archive
--------------------------------

       --   identify kinds of kernels to be archived

       --   setup work area and collect kernels under it; write scripts for
            collecting kernels if more than one archive release is expected

       --   merge kernels if needed; write merging scripts if more than one
            archive release is expected

       --   verify internal comments and add comments as needed; write
            scripts for adding comments to kernels if more than one archive
            release is expected

       --   validate final kernels; write validating scripts if more than
            one archive release is expected

       --   make or collect extra files -- meta-kernels, ORBNUM files, etc.

       --   obtain mission, instrument host, and references catalog files
            from the responsible project person/team

       --   write ``spiceds.cat'' and ``data/*/*info.txt'' files to
            document kernels, using files from an existing SPICE archive as
            the starting point

       --   write all other required catalog and text files using files
            from an existing SPICE archive as the starting point

       --   setup staging area for the new archive

       --   setup archiving scripts and utilities used by scripts on the
            workstation that contains the staging area; change hard-coded
            locations in the scripts as needed; add directory in which
            scripts/tools are located to the system path

       --   copy kernels, value-added, and meta-information files to the
            staging area

       --   create the MAKLABEL template file

       --   create the kernel list file

       --   generate labels

       --   generate index files; move ``index.*'' files to ``index''
            directory

       --   check that all binary kernels are in BIG-IEEE format and all
            text kernels are in UNIX format (<LF>-terminated lines);
            convert those that aren't to the right format using BINGO

       --   run ``check_everything.csh''

       --   make a list of files to which <CR>s should be added and add
            <CR>s to them

       --   copy the data set to the final archive area; move ``dsindex.*''
            to the directory above the volume root

       --   check all meta-kernels using BRIEF

       --   run ``mkpdssum.pl'' to generate the checksum table and label

       --   run VTool and/or Online Volume Validation tool to verify the
            archive

       --   remove <CR>s from the staging area meta-information files to
            which they were added


Steps for Adding Data To an Existing Archive
--------------------------------------------

   * identify new kernels to be added to the archive

   * collect kernels under kernel area(s)

   * merge/subset kernels if needed

   * verify internal comments and add comments as needed

   * validate final kernels

   * add or modify extra files -- meta-kernels, ORBNUM files, etc.

   * if needed, create the kernel plan file for new release

   * check and, if needed, update ``spiceds_v???.html``

   * check and, if needed, update the NPB configuration file

   * run NPB

   * run validate tool to verify the archive

   * move the files from the final area to the public area

   * notify your archiving authority and/or NAIF