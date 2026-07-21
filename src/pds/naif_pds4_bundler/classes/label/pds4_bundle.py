"""Implementation of the PDS4 version of a label for Bundles.
"""
from pathlib import Path

from .pds4_label import PDS4Label


class BundlePDS4Label(PDS4Label):
    """Class to generate a PDS4 Bundle Label.

    :param setup:  NPB execution Setup object
    :param readme: Readme product
    """

    _mission_reference_type = "bundle_to_investigation"
    _target_reference_type = "bundle_to_target"

    def __init__(self, setup, readme) -> None:
        """Constructor."""
        super().__init__(setup, readme)

        self._template = str(Path(setup.templates_directory)
                             / "template_bundle.xml")

        self.BUNDLE_LID = self.product.bundle.lid
        self.BUNDLE_VID = self.product.bundle.vid

        self.AUTHOR_LIST = setup.author_list
        self.START_TIME = setup.increment_start
        self.STOP_TIME = setup.increment_finish
        self.FILE_NAME = readme.name
        self.DOI = self.setup.doi
        self.BUNDLE_MEMBER_ENTRIES = ""

        eol = self.setup.eol_pds4
        tab = self.setup.xml_tab

        #
        # There might be more than one miscellaneous collection added in
        # an increment (especially if it is the first time that the collection
        # is generated and there have been previous releases.)
        #
        for collection in self.product.bundle.collections:

            if collection.name == 'spice_kernels':

                # TODO: Is "spice_kernels" needed or can it be changed to
                #       "spice_kernel" in order to simplify the code? Open for
                #       discussion.
                coll_name = 'spice_kernel'

            elif collection.name == 'document':
                coll_name = 'document'

            elif collection.name == "miscellaneous":
                coll_name = "miscellaneous" if setup.information_model_float >= 1011001000.0 else "member"

            else:
                raise ValueError(
                    f'NPB bug: the collection name {collection.name} is not '
                    f'supported in PDS4 Bundle Label.')

            self.COLL_NAME = coll_name
            self.COLL_LIDVID = collection.lid + "::" + collection.vid
            self.COLL_STATUS = "Primary" if collection.updated else "Secondary"

            self.BUNDLE_MEMBER_ENTRIES += (
                f"{' ' * tab}<Bundle_Member_Entry>{eol}"
                f"{' ' * 2 * tab}<lidvid_reference>"
                f"{self.COLL_LIDVID}</lidvid_reference>{eol}"
                f"{' ' * 2 * tab}<member_status>"
                f"{self.COLL_STATUS}</member_status>{eol}"
                f"{' ' * 2 * tab}<reference_type>"
                f"bundle_has_{self.COLL_NAME}_collection"
                f"</reference_type>{eol}"
                f"{' ' * tab}</Bundle_Member_Entry>{eol}"
            )

        self.write_label()
