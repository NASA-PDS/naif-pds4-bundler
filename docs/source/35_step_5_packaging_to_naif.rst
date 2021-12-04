Step 5: Packaging and Delivering the Archive to the NAIF Node
=============================================================

If the project archive plan calls for delivery of the SPICE archive to
the NAIF Node of the PDS, the data set producer can do it in two ways:

   1. If the volume of the data to be delivered is relatively small
      (under 2 GB), either the whole data set or only the files that
      were updated or added in the last release can be packaged into
      a ``.tar`` file, which is then made available to NAIF staff.
      The tar file should contain the whole data set directory tree
      starting at the ``<sc>_spice`` level (where ``<sc>`` is the
      mission acronym.)

      For example, to make a ``.tar`` file containing the whole MAVEN
      archive, the following commands can be used (to first change
      to the final archive area and then to "tar" the whole archive
      directory tree)::

        $ cd /ftp/pub/naif/pds/pds4/maven
        $ tar -cvf maven_release_26.tar maven_spice

      To make a ``.tar`` file containing only additions and changes
      to the MAVEN archive from the latest release, the following
      commands can be used (to first change to the final archive area
      and then to ``tar`` all files included in the file list file)::

        $ cd /ftp/pub/naif/pds/pds4/maven
        $ tar cBf maven_release_26.tar -T /home/naif/maven/pds/working/maven_release_26.file_list

   2. If the volume of the data to be delivered is large (greater
      than 2 GB), NAIF staff should be given access to the final
      archive area (or a copy of it), which NAIF staff will mirror
      using either ``wget`` or ``scp`` tools (depending on the kind
      of access that was provided).

      The kind of access to be given to NAIF staff is up to the data provider.
      Any of the following ways is acceptable:

         * putting ``.tar`` file(s) or a copy of the final data set tree
           on an anonymous public FTP server or a public Web server

         * putting ``.tar`` file(s) or a copy of the final data set tree
           on a password-protected FTP server or a Web server. In this
           case NAIF staff should be provided with an account and
           password.

         * putting ``.tar`` file(s) or a copy of the final data set tree
           on a UNIX workstation, providing NAIF staff with an account on
           this workstation, and setting file permissions allowing read
           access to the data.

Providing the NPB Configuration File, Release Plan, Kernel List, and any other
NPB execution by-products to NAIF is recommended. You can do so by providing
them along with the ``.tar`` file or as an attachment to the email to
communicate the delivery to NAIF.
