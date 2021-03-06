Working Example
===============

This section provides a working example for the user to be able to exercise
NPB's execution before using it to generate an actual archive. This section
assumes that NPB is properly installed as indicated in :ref:`41_npb_installation:NPB Installation`
and that you have the package available in the user's computer. We will assume that
its location is ``~/naif-pds4-bundler/`` and that NPB can executed with the
command ``naif-pds4-bundler``.


Setup the workspace
-------------------

We will generate an increment of the INSIGHT archive. The first step is to
define our workspace, we will do so by creating the adequate directory
structure as follows::

    cd ~/
    mkdir insight
    mkdir insight/working
    mkdir insight/staging
    mkdir insight/bundle
    mkdir insight/kernels
    mkdir insight/kernels/sclk
    mkdir insight/kernels/ck

The next step is to copy the "current" version of the INSIGHT SPICE Kernel
(version 7). This is provided as test data with NPB::

    cp -pr naif-pds4-bundler/tests/naif_pds4_bundler/data/insight/insight_spice insight/bundle/

Now we copy the kernels that we will include in the archive increment (that will
be version 8)::

   cp -p naif-pds4-bundler/tests/naif_pds4_bundler/data/kernels/sclk/NSY_SCLKSCET.00019.tsc insight/kernels/sclk/nsy_sclkscet_00019.tsc
   cp -p naif-pds4-bundler/tests/naif_pds4_bundler/data/kernels/ck/insight_ida_enc_200829_201220_v1.bc insight/kernels/ck/
   cp -p naif-pds4-bundler/tests/naif_pds4_bundler/data/kernels/ck/insight_ida_pot_200829_201220_v1.bc insight/kernels/ck/

The next step is to write the archive release plan that indicates the SPICE
kernels that we want to archive. We will also include the meta-kernel in the
release plan -- it will be automatically generated by NPB and therefore
we do not need to provide it. The release plan can be generated as follows::

   {ls -1 insight/kernels/sclk; ls -1 insight/kernels/ck} > insight/working/insight_release_08.plan

The next step is to setup the NPB configuration file appropriately. The starting
point will be the configuration file provided for INSIGHT in the NPB test data::

   cp naif-pds4-bundler/tests/naif_pds4_bundler/config/insight.xml insight/working/insight_release_v08.xml


Prepare the Configuration File
------------------------------

We will now need to modify the configuration file to adapt it to our workspace.
In order to do so open the file with a text editor and do the replacements
indicated hereunder::

   vi insight/working/insight_release_v08.xml

Because we are not providing an updated SPICEDS file, remove the following line::

   <spiceds>../data/spiceds_insight.html</spiceds>

Replace::

   <sclk>NSY_SCLKSCET.[0-9][0-9][0-9][0-9][0-9].tsc</sclk>

with::

   <sclk>nsy_sclkscet_[0-9][0-9][0-9][0-9][0-9].tsc</sclk>

Given that we do not need to map the SCLK kernel name -- we already copied the
file with the update name.

Replace::

   <bundle_directory>insight</bundle_directory>

with::

   <bundle_directory>bundle</bundle_directory>


Finally, replace::

   <interrupt_to_update>True</interrupt_to_update>

with::

   <interrupt_to_update>False</interrupt_to_update>

This will prevent NPB from pausing the process to update the automatically
generated meta-kernel.


Run NPB
-------

We are ready to run NPB and to generate the archive increment. To do so change
the directory to ``insight`` and then run NPB::

   cd insight
   naif-pds4-bundler working/insight_release_v08.xml -p working/insight_release_08.plan -l

You should see something similar to this in your screen (minor differences can
happen due to the usage of different versions of NPB)::

   naif-pds4-bundler-1.2.0 for InSight Mars Lander Mission
   =======================================================
   -- Executed on MT-308302 at 2022-05-13 16:17:39
   -- Setup the archive generation.
   -- Kernel List generation.
   -- Check kernel list products.
   -- All products checks have succeeded.
   -- Bundle/data set structure generation at staging area.
   -- Load LSK, PCK, FK and SCLK kernels.
   -- SPICE kernel collection/data processing.
      * Created spice_kernels/sclk/nsy_sclkscet_00019.xml.
      * Created spice_kernels/ck/insight_ida_enc_200829_201220_v1.xml.
      * Created spice_kernels/ck/insight_ida_pot_200829_201220_v1.xml.
   -- Generation of meta-kernel(s).
   -- Determine archive increment start and finish times.
   -- Validate SPICE kernel collection generation.
   -- Generation of spice_kernels collection.
      * Created /spice_kernels/collection_spice_kernels_inventory_v008.csv.
      * Created spice_kernels/collection_spice_kernels_v008.xml.
   -- Processing spiceds file.
   -- Generation of miscellaneous collection.
   -- Generate checksum file.
      * Created miscellaneous/checksum/checksum_v001.xml.
      * Created /miscellaneous/collection_miscellaneous_inventory_v001.csv.
      * Created miscellaneous/collection_miscellaneous_v001.xml.
   -- Generate checksum file.
      * Created miscellaneous/checksum/checksum_v002.xml.
      * Created /miscellaneous/collection_miscellaneous_inventory_v002.csv.
      * Created miscellaneous/collection_miscellaneous_v002.xml.
   -- Generate checksum file.
      * Created miscellaneous/checksum/checksum_v003.xml.
      * Created /miscellaneous/collection_miscellaneous_inventory_v003.csv.
      * Created miscellaneous/collection_miscellaneous_v003.xml.
   -- Generate checksum file.
      * Created miscellaneous/checksum/checksum_v004.xml.
      * Created /miscellaneous/collection_miscellaneous_inventory_v004.csv.
      * Created miscellaneous/collection_miscellaneous_v004.xml.
   -- Generate checksum file.
      * Created miscellaneous/checksum/checksum_v005.xml.
      * Created /miscellaneous/collection_miscellaneous_inventory_v005.csv.
      * Created miscellaneous/collection_miscellaneous_v005.xml.
   -- Generate checksum file.
      * Created miscellaneous/checksum/checksum_v006.xml.
      * Created /miscellaneous/collection_miscellaneous_inventory_v006.csv.
      * Created miscellaneous/collection_miscellaneous_v006.xml.
   -- Generate checksum file.
      * Created miscellaneous/checksum/checksum_v007.xml.
      * Created /miscellaneous/collection_miscellaneous_inventory_v007.csv.
      * Created miscellaneous/collection_miscellaneous_v007.xml.
   -- Generate checksum file.
      * Created /miscellaneous/collection_miscellaneous_inventory_v008.csv.
      * Created miscellaneous/collection_miscellaneous_v008.xml.
   -- Generation of bundle products.
      * Created bundle_insight_spice_v008.xml.
      * Created miscellaneous/checksum/checksum_v008.xml.
   -- Recap files in staging area.
   -- Copy files to the bundle area.
   -- Validate bundle history with checksum files.
   Execution finished at 2022-05-13 16:17:40


Checking the Results
--------------------

NPB has been executed successfully. The result can be checked by inspecting the
run by-products that are under the ``working`` directory::

   PDS4_PDS_1500.sch
   PDS4_PDS_1500.xsd
   insight_release_08.checksum
   insight_release_08.file_list
   insight_release_08.kernel_list
   insight_release_08.log
   insight_release_08.validate_config
