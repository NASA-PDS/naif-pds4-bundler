Step-by-Step Summary
====================

This section provides a brief step-by-step summary of the process for
creating a new archive and for adding another release to an existing
archive. Please augment the checklists below with any additional steps
needed for your SPICE archive.


Steps for Creating a New Archive
--------------------------------

   * identify kinds of kernels to be archived

   * setup work area and collect kernels under it; write scripts for
     collecting kernels if more than one archive release is expected

   * merge kernels if needed; write merging scripts if more than one
     archive release is expected

   * verify internal comments and add comments as needed; write
     scripts for adding comments to kernels if more than one archive
     release is expected

   * validate final kernels; write validating scripts if more than
     one archive release is expected

   * add or modify extra files -- Meta-kernels, ORBNUM files, etc.

   * Obtain a DOI for the archive

   * if needed, create the release plan for new release

   * write SPICEDS file, using files from an existing SPICE archive as
     the starting point

   * setup workspace for the new archive

   * install NPB

   * write the NPB configuration file

   * run NPB

   * run validate tool to verify the archive

   * move the files from the final area to the public area

   * notify your archiving authority and/or NAIF


Steps for Adding Data To an Existing Archive
--------------------------------------------

   * identify new kernels to be added to the archive

   * collect kernels under kernel area(s)

   * merge/subset kernels if needed

   * verify internal comments and add comments as needed

   * validate final kernels

   * add or modify extra files -- Meta-kernels, ORBNUM files, etc.

   * if needed, create the release plan for new release

   * check and, if needed, update the SPICEDS file

   * check and, if needed, update the NPB configuration file

   * run NPB

   * run validate tool to verify the archive

   * move the files from the final area to the public area

   * notify your archiving authority and/or NAIF
