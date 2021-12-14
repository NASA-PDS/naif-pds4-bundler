Step 3: Running NAIF PDS4 Bundler
=================================

Once you have reached this step, the hard work is done. From here onwards the
process should take full advantage of NPB and should be mostly automatic.

Run NPB from the command line
-----------------------------

If you are in a hurry run NPB as follows: open your favorite
terminal application and with coherence with respect to the workspace that you
have defined for NPB, execute the following command::

   $ naif-pds4-bundler <path_to_file>/<sc>_release_??.xml -p <path_to_file>/<sc>_release_??.plan -l -v

where

   * ``<path_to_file>`` is the relative or absolute path to the corresponding
     file
   * ``<sc>`` is the mission acronym
   * ``??`` is the two digit archive release version

For example::

   $ naif-pds4-bundler maven_release_26.xml -p maven_release_26.plan -l -v

This will run NPB using the configuration file that you have just written or
updated for the files specified in the archive release plan (``-p PLAN``), will
generate a log file with the following file name: ``<sc>_release_??.log``
(``-l``) and will run with verbosity (``-v``). This is the recommended
way to run NPB, but is not the only one. Explanations for all the options to run
NPB are provided in Section
:ref:`source/43_using_npb:Running NPB from the command line`.

We recommend you to always generate a log of your run (``-l``) and in general,
and especially for the first times that you use NPB, we recommend you to prompt
the log in the screen as well (``-v``). If it is the first time you are using
the configuration file, it might be a good idea to test the generation of the
kernel list (``-f list``) and then to inspect the release products in the
staging area before pushing them to the bundle area (``-f staging``).

We **do not** recommend you to bypass the final validation (``-f bundle``),
to use a kernel list as your input (instead of a release plan with
``-kerlist KERLIST``) or to run NPB silently (``-s``), unless you are
experienced with its usage and you have a strong reason to do so.


Interactive step for Meta-kernels
---------------------------------

If the Meta-kernel(s) are being generated automatically, which means that
you have provided a a ``<mk>`` section in the configuration file and that you
have set the nested element ``<interrupt_to_update>`` to ``True``, NPB will pause
its execution for each generated MK, before the MK is labelled and will give you
the opportunity to edit the MK at your will. NPB will either let you use
a text editor of your choice or it can also try to run ``vi`` for you. The
message that you will see is similar to::

   INFO    : -- Meta-kernel generated.
       * The meta-kernel might need to be updated. You can:
           - Type "vi" and press ENTER to edit the file with the VI text editor.
           - Edit the file with your favorite edit and press ENTER and continue.
           - Press ENTER to continue.
         MK path: /staging/insight_spice/spice_kernels/mk/insight_v08.tm
   >> Type 'vi' and/or press ENTER to continue...


More information is provided in :ref:`source/31_step_1_preparing_data:Preparing Meta-kernels`
and :ref:`source/42_npb_configuration_file:Meta-kernel`.


Understanding NPB prompting and logging
---------------------------------------

We have recommended you to run NPB in verbose mode (``-v --verbose``) and to
generate the run log (``-l --log``). If you do so, NPB will provide you either
on the screen or in the log a structured and comprehensive step-by-step
explanation of the run with ``INFO``, ``WARNING``, indicators at the beginning
of each line. If the run has not been successful, you will see an ``ERROR``
indicator and the execution will stop.

Please pay attention to the lines with a ``WARNING``, try to understand their
meaning and whether if it is something that you expected from the execution or
not. If you do not understand its meaning or it was expected, there might be
something fishy about your input data or your configuration file.

Here's an example of a ``WARNING`` message in the log::

   INFO    : Step 4 - Load LSK, PCK, FK and SCLK kernels
   INFO    : -------------------------------------------
   INFO    :
   INFO    : -- LSK     loaded: ['/kernels/lsk/naif0012.tls']
   WARNING : -- PCK not found.
   WARNING : -- FK not found.
   INFO    : -- SCLK(s) loaded: ['/kernels/sclk/NSY_SCLKSCET.00019.tsc']


What if something goes wrong?
-----------------------------

You're covered. NPB has an argument: ``-c CLEAR --clear CLEAR``, that allows you
to clear the resulting products of a run from your workspace.

After you run NPB (successfully or not) one of the by-products that NPB
generates is the **File List**. This File List is the value that is provided to
this argument. For example::

   $ naif-pds4-bundler maven_release_26.xml -c working/maven_release_26.file_list -v

By default, using this argument will stop the execution when the workspace
has been cleared.


Processing large binary kernels
-------------------------------

When working with large binary kernels (CKs, SPKs, DSKs or PCKs) obtaining
the md5 sum hash (checksum, required by the products' labels) of each file can
take a large amount of time. In order to avoid re-calculating
checksums NPB can be instructed to look for the **checksum registry file(s)**
in the ``working_directory``, these files are automatically generated by NPB based on
the checksums that it calculates during its execution, they have ``*.checksum``
extension, e.g., ``maven_release_26.checksum``. In order to instruct NPB to use
these checksums you need to use the argument ``-s --checksum``.

Note that NPB will use all the checksum registry files available in the
``working_directory``.

If the argument is provided but the file is not present, NPB will look in the
``staging_directory`` for labels generated in previous runs and extract the
checksum from them.

We know from experience that this feature can save you a lot of time, but at
the same time it must be managed carefully and you must always be aware
whether if the checksum registry files in the working directory and/or the
labeled products in the staging area are adequate.


Until you get it right
----------------------

It is hard to get NPB to work on the first try, especially for the first
release of the archive or after a major update of the configuration file. Most
likely you will need to try several times before you get it right. That is why
we do not recommend you to set the ``bundle_directory`` to the final destination
of the archive but rather an intermediate destination before pushing the
incremented archive to the public (or to the relevant organisation.)

A good idea is to stop NPB's execution before the generated files are copied
from the staging directory to the bundle directory. You can do so by setting
the argument: ``-f FAUCET --faucet FAUCET`` to ``staging``. More information
about this argument is provided in the section
:ref:`source/43_using_npb:Optional Arguments Description`.
