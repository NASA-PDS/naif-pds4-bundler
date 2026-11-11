"""Implementation of the PDS4 SPICE Kernels Collection Class."""
from __future__ import annotations
import glob
import logging
import os

import spiceypy
from spiceypy.utils.exceptions import SpiceyPyError

from .collection import Collection
from ..exceptions import NPBError
from ...utils import archive_subdirectory
from ...utils import et_to_date
from ...utils import extension_to_type
from ...utils import FILE_READ_ERRORS


class SpiceKernelsCollection(Collection):
    """Class to generate a PDS4 SPICE Kernels Collection.

    :param setup:   NPB execution setup object
    :param bundle:  Bundle object
    :param kernels: Kernel List object

    The ``increment_start`` and ``increment_finish`` attributes only exist once
    :meth:`set_increment_times` has run.
    """

    def __init__(self, setup, bundle, kernels) -> None:
        """Constructor."""
        self.bundle = bundle
        self.list = kernels
        self.type = "spice_kernels"
        """Collection type (`str`)."""

        if setup.pds_version == "4":
            self.start_time = setup.mission_start
            self.stop_time = setup.mission_finish

        super().__init__(self.type, setup, bundle)

    def determine_meta_kernels(self):
        """Determine the name of the Meta-kernel(s) to be generated.

        :return: Dictionary of meta-kernels to be generated. The keys list the
                 meta-kernels and the values whether if they are provided by the
                 user or not.
        :rtype: dictionary.
        """
        #
        # First check if a meta-kernel has been provided via configuration by
        # the user. If so, only the provided meta-kernels will be taken into
        # account (there is no hybrid possibility but NPB provides a warning
        # message if more meta-kernels are expected).
        #
        meta_kernels = self._mk_from_config()

        #
        # Second we check if meta-kernels are indicated with the kernel list.
        # Note that if kernels are provided as input, the ones present in the
        # kernel list are ignored.
        #
        # It is assumed that these kernels will be in the kernels_directory,
        # under the mk subdirectory.
        #
        meta_kernels = meta_kernels or self._mk_from_kernel_list()

        #
        # If no meta-kernels are provided as inputs or in the kernel list,
        #
        if not meta_kernels:
            if self.setup.args.faucet == "labels":
                logging.info(
                    "-- No meta-kernel provided as input in the plan in labeling mode."
                )
            else:
                logging.info(
                    "-- No meta-kernel provided in the kernel list or via configuration."
                )

            #
            # NPB will try to determine if a meta-kernel can be generated
            # only using the information from the configuration file.
            #
            meta_kernels = self._mk_synthesized_from_template()

        if not meta_kernels:
            logging.info("")
            logging.warning("-- No Meta-kernel will be generated.")
        else:
            self._assert_mks_absent(meta_kernels)

        return meta_kernels

    def _mk_from_config(self) -> dict:
        """Take the meta-kernels provided via the ``mk_inputs`` configuration.

        When given, only these meta-kernels are used: there is no hybrid with
        the kernel list. Nothing is taken in labeling mode.

        :return: Provided meta-kernels as keys, all with value ``True``. Empty
                 if the configuration provides none.
        :raises NPBError: If a provided meta-kernel file does not exist.
        """
        meta_kernels = {}
        if (not hasattr(self.setup, "mk_inputs")
                or self.setup.args.faucet == "labels"):
            return meta_kernels

        if "file" not in self.setup.mk_inputs:
            logging.warning("-- Configuration item mk_inputs is empty.")
            return meta_kernels

        mks = self.setup.mk_inputs["file"]
        if not isinstance(mks, list):
            mks = [mks]
        for mk in mks:
            if not os.path.exists(mk):
                logging.info("")
                raise NPBError(
                    f"Meta-kernel provided via"
                    f" configuration"
                    f" does not exist: {mk}")
            meta_kernels[mk] = True

        return meta_kernels

    def _mk_from_kernel_list(self) -> dict:
        """Take the meta-kernels listed in the kernel list.

        Those present under ``mk`` in one of the kernels directories are
        returned by path with value ``True``. The rest are returned by name
        with value ``False``, to be generated.

        :return: Meta-kernels from the kernel list, empty if it has none.
        """
        meta_kernels = {}
        for kernel in self.list.kernel_list:
            if ".tm" not in kernel:
                continue

            for kernel_dir in self.setup.kernels_directory:
                path = f"{kernel_dir}/mk/{kernel}"
                if os.path.exists(path):
                    meta_kernels[path] = True
                    break
            # The loop ended without a break: no kernels directory has it.
            else:
                logging.info(
                    '-- %s not provided as input in kernels directory.',
                    kernel)
                meta_kernels[kernel] = False

        return meta_kernels

    def _mk_synthesized_from_template(self) -> dict:
        """Build the meta-kernel name from the ``mk`` configuration template.

        This only works if the bundle has one meta-kernel and the only pattern
        in its name is ``VERSION``, and only when the collection has products.
        The first version is used. A meta-kernel already in the bundle is not
        generated again.

        :return: The meta-kernel name with value ``False`` (to be generated),
                 or empty if it cannot or need not be generated.
        """
        if not (hasattr(self.setup, "mk")
                and self.product
                and self.setup.args.faucet != "labels"):
            return {}

        if not self._is_single_version_only_mk_template(self.setup.mk):
            return {}

        version_length = int(
            self.setup.mk[0]["name"][0]["pattern"]["@length"])
        meta_kernel = self.setup.mk[0]["@name"].replace(
            "$VERSION", "1".zfill(version_length))
        existing_path = f"{self.setup.bundle_directory}/{self.setup.mission_acronym}_spice/spice_kernels/mk/{meta_kernel}"
        if os.path.exists(existing_path):
            return {}

        return {meta_kernel: False}

    @staticmethod
    def _is_single_version_only_mk_template(mk: list) -> bool:
        """Tell if the ``mk`` configuration is a single, version-only template.

        That means one meta-kernel whose name has a single pattern, and that
        pattern is ``VERSION``. Only then can the meta-kernel name be built
        from the configuration alone.

        The configuration is parsed from XML, so a single ``pattern`` element
        is a dictionary with its ``#text`` and ``@length``, which is why
        ``len(pattern) == 2`` identifies one pattern. Two ``pattern`` elements
        come as a list, which also has length 2, so the ``isinstance`` check
        is what rules that case out.

        :param mk: ``mk`` item of the configuration, a list of meta-kernels.
        :return: ``True`` for a single meta-kernel named with only ``VERSION``.
        """
        if not (len(mk) == 1
                and len(mk[0]["name"]) == 1
                and len(mk[0]["name"][0]) == 1):
            return False

        pattern = mk[0]["name"][0]["pattern"]
        return (len(pattern) == 2
                and not isinstance(pattern, list)
                and pattern["#text"] == "VERSION")

    def _assert_mks_absent(self, mks: dict) -> None:
        """Stop the execution if any of the meta-kernels is already archived.

        :param mks: Meta-kernels to check; only the keys (names) are used.
        :raises NPBError: If any of them is already in the archive.
        """
        for meta_kernel in sorted(mks):
            if self.setup.pds_version == "4":
                existing_path = f"{self.setup.bundle_directory}/{self.setup.mission_acronym}_spice/spice_kernels/mk/{meta_kernel}"
            else:
                existing_path = f"{self.setup.bundle_directory}/{self.setup.volume_id}/extras/mk/{meta_kernel}"
            if os.path.exists(existing_path):
                raise NPBError(f"MK already exists in the archive: {existing_path}")

    def set_increment_times(self) -> None:
        """Determine the archive increment start and finish times.

        This is done based on the identification of the coverage of a given
        SPK or CK kernel. Alternatively it can be provided as a parameter of the
        execution. The determined times are stored in ``increment_start`` and
        ``increment_finish``.
        """
        increment_start = ""
        increment_finish = ""
        #
        # The increment start and finish times are to be set with the MK.
        # This is the first step taken.
        #
        # Match the pattern with the kernels in the meta-kernel.
        #
        try:
            increment_starts = []
            increment_finishs = []
            for prod in self.product:
                if hasattr(prod, "mk_sets_coverage"):
                    if prod.mk_sets_coverage:
                        increment_starts.append(prod.start_time)
                        increment_finishs.append(prod.stop_time)

                        logging.info(
                            '-- Using MK: %s to determine increment coverage.',
                            prod.name)

            increment_start = min(increment_starts)
            increment_finish = max(increment_finishs)

        # min()/max() raise ValueError when no MK sets the increment coverage
        # (both lists are empty), or TypeError if the collected start/stop times
        # are of incompatible types (e.g. None or mixed str/datetime);
        # prod.start_time/stop_time access raises AttributeError if a matched
        # product lacks the coverage attributes.
        except (ValueError, AttributeError, TypeError):
            #
            # If no MKs are provided in the increment. First check if an
            # increment stop time has been provided as an input
            # parameter.
            #
            logging.warning("-- No Meta-kernels found to determine increment times.")

            if hasattr(self.setup, "increment_start"):

                logging.info(
                    '   Increment stop time set to: %s as provided from '
                    'configuration file', self.setup.increment_start)

                increment_start = self.setup.increment_start

            if hasattr(self.setup, "increment_finish"):

                logging.info(
                    '   Increment finish time set to: %s as provided from '
                    'configuration file', self.setup.increment_finish
                )

                increment_finish = self.setup.increment_finish

            #
            # The alternative is to set the increment stop time to the
            # end time of the mission.
            #
            if not increment_start:
                increment_start = self.setup.mission_start

                logging.warning(
                    '-- No increment start time provided via configuration. '
                    'Mission start time will be used:')
                logging.warning('   %s', increment_start)

            if not increment_finish:
                increment_finish = self.setup.mission_finish

                logging.warning(
                    '-- No increment finish time provided via configuration. '
                    'Mission stop time will be used:')
                logging.warning('   %s', increment_finish)

        #
        # We check the coverage with the previous increment.
        #
        try:
            #
            # The first alternative option is to set the time to the time of
            # the previous increment since we might be generating an increment
            # that does not extend the coverage.
            #
            bundles = glob.glob(
                self.setup.bundle_directory
                + os.sep
                + self.setup.mission_acronym
                + "_spice"
                + os.sep
                + f"bundle_{self.setup.mission_acronym}"
                f"_spice_v*"
            )
            bundles.sort()

            prev_increment_start = None
            prev_increment_finish = None
            with open(bundles[-1], "r", encoding='utf-8') as b:
                for line in b:
                    if "<start_date_time>" in line:
                        prev_increment_start = line.split(">")[-2].split("<")[0]
                    if "<stop_date_time>" in line:
                        prev_increment_finish = line.split(">")[-2].split("<")[0]

            #
            # Provide different logging level depending on the times'
            # combination.
            #
            logging.info('-- Previous bundle increment interval is:')
            logging.info('   %s - %s', prev_increment_start, prev_increment_finish)

            #
            # Correct the increment interval with previous interval if
            # required.
            #
            if prev_increment_start < increment_start:
                increment_start = prev_increment_start
                logging.info("-- Increment start corrected from previous bundle.")
            elif prev_increment_start > increment_start:
                logging.warning("-- Increment start from previous bundle not used.")

            if prev_increment_finish > increment_finish:
                increment_finish = prev_increment_finish
                logging.warning("-- Increment finish corrected form previous bundle.")

        # bundles[-1] raises IndexError with no matching glob; a matched label
        # missing the start/stop tags leaves prev_increment_start or _finish as
        # None, so comparing it below raises TypeError; open() raises OSError if
        # the file can't be read, or UnicodeDecodeError if it isn't valid UTF-8
        # (opened with encoding='utf-8').
        except (IndexError, TypeError, *FILE_READ_ERRORS):
            logging.warning("-- Previous bundle not found.")

        #
        # Check the format of the previous bundle and correct it. The 'Z' is
        # removed from the UTC string since it is not supported until the
        # SPICE Toolkit N0067.
        #
        try:
            (increment_start, increment_finish) = et_to_date(
                spiceypy.utc2et(increment_start[:-1]),
                spiceypy.utc2et(increment_finish[:-1]),
                self.setup.date_format,
            )

        # spiceypy.utc2et() raises SpiceyPyError when no LSK is loaded.
        except SpiceyPyError:
            logging.warning(
                "-- A leapseconds kernel (LSK) has not been loaded. "
                "Increment start/finish times will not be corrected."
            )

        logging.info('-- Increment interval for collection and bundle set to:')
        logging.info('   %s - %s', increment_start, increment_finish)
        logging.info('')

        self.increment_finish = increment_finish
        self.increment_start = increment_start

    def validate(self) -> None:
        """Validate the SPICE Kernels collection.

        The SPICE Kernels collection validation performs the following checks:

           * check that all the kernels from the kernel list are present
           * check that all the kernels have been labeled
           * display the key elements of the labels for the user to do a visual
             inspection. The key elements are: ``logical_identifier``, ``version_id``,
             ``title``, ``description``, ``start_date_time``, ``stop_date_time``,
             ``file_name``, ``file_size``, ``md5_checksum``, ``object_length``,
             ``kernel_type``, and ``encoding_type``.
        """
        #
        # Check that all the kernels from the list are present
        #
        logging.info("-- Checking that all the kernels from list are present...")

        # Staging folder of each kind of product for the PDS version. Each one
        # starts and ends with a separator, so it can sit between the staging
        # directory and the product name. Orbnum files and meta-kernels are one
        # level deeper, in "orbnum" and "mk"; for the kernels, the type folder
        # is added in the checks below.
        pds_version = self.setup.pds_version
        ker_dir = os.sep + archive_subdirectory("kernel", pds_version) + os.sep
        orbnum_dir = (
            os.sep + archive_subdirectory("orbnum", pds_version)
            + os.sep + "orbnum" + os.sep
        )
        mk_dir = (
            os.sep + archive_subdirectory("mk", pds_version)
            + os.sep + "mk" + os.sep
        )

        # PDS3 labels have the .lbl extension and PDS4 labels the .xml one.
        if pds_version == "3":
            lbl_ext = ".lbl"

        else:
            lbl_ext = ".xml"

        non_present_products = []
        for product in self.list.kernel_list:
            if (
                not os.path.exists(
                    self.setup.staging_directory
                    + ker_dir
                    + extension_to_type(product)
                    + os.sep
                    + product
                )
                and not os.path.exists(
                    self.setup.staging_directory + orbnum_dir + product
                )
                and not os.path.exists(self.setup.staging_directory + mk_dir + product)
            ):
                non_present_products.append(product)

        if non_present_products:
            logging.error("-- The following products from the list are not present:")
            for product in non_present_products:
                logging.error('   %s', product)

            # Report all missing products before terminating so the user can
            # address every gap in a single run.
            raise NPBError("Some products from the list are not present.")

        else:
            logging.info("   OK")
        logging.info("")

        #
        # Check that all the kernels have been labeled.
        #
        logging.info("-- Checking that all the kernels have been labeled...")

        non_labeled_products = []
        for product in self.product:
            # PDS3 meta-kernels (.tm) are not labeled; all other products in
            # both PDS versions must have both a kernel file and a label file.
            if (
                not (self.setup.pds_version == "3" and ".tm" in product.name)
                and (
                    not os.path.exists(
                        self.setup.staging_directory
                        + ker_dir
                        + product.type
                        + os.sep
                        + product.name
                    )
                    or not os.path.exists(
                        self.setup.staging_directory
                        + ker_dir
                        + product.type
                        + os.sep
                        + product.name.split(".")[0]
                        + lbl_ext
                    )
                )
            ):
                non_labeled_products.append(product.name)

        if non_labeled_products:
            logging.error("-- The following products have not been labeled:")
            for product in non_labeled_products:
                logging.error('   %s', product)

            # PDS3 labeling is not yet implemented; termination is deferred
            # until it is. For PDS4, all products must be labeled.
            if self.setup.pds_version == "4":
                raise NPBError("Some products have not been labeled.")

        else:
            logging.info("   OK")

        #
        # Exit the method if no products are present in collection
        #
        if not self.product:
            return

        #
        # Display the key elements of the labels for the user to do a visual
        # check. The key elements are: logical_identifier, version_id, title,
        # description, start_date_time, stop_date_time, file_name, file_size,
        # md5_checksum, object_length, kernel_type, and encoding_type.
        #
        if self.setup.pds_version == "4":
            elements = [
                "logical_identifier",
                "version_id",
                "title",
                "description",
                "start_date_time",
                "stop_date_time",
                "file_name",
                "file_size",
                "md5_checksum",
                "object_length",
                "kernel_type",
                "encoding_type",
            ]
        else:
            elements = [
                "RECORD_TYPE",
                "RECORD_BYTES",
                "SPICE_KERNEL",
                "DESCRIPTION",
            ]

        elements_dict = dict.fromkeys(elements)

        #TODO: Possible bug: when executed in PDS3 mode, self.product may have (?)
        #      a metakernel. In PDS3, metakernels are not labeled, but this loop
        #      will attempt to open the label for reading, causing a
        #      FileNotFoundError exception.
        for product in self.product:
            with open(product.label.name, "r", encoding='utf-8') as p:
                for line in p:
                    for element in elements:
                        if element in line:
                            if not elements_dict[element]:
                                elements_dict[element] = [line.strip()]
                            else:
                                elements_dict[element].append(line.strip())

        logging.info("")
        logging.info("-- Providing relevant fields of labels for visual inspection.")
        logging.info("")
        for key in elements_dict.keys():
            for element in elements_dict[key]:
                logging.info('   %s', element)
            logging.info('')
        logging.info('')
