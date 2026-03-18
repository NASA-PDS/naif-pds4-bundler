"""Implementation of the PDS4 version of a label for Bundles.
"""
from .label import PDSLabel


class BundlePDS4Label(PDSLabel):
    """PDS Label child class to generate a PDS4 Bundle Label.

    :param setup: NPB execution Setup object
    :param readme: Readme product
    """

    def __init__(self, setup: object, readme: object) -> object:
        """Constructor."""
        PDSLabel.__init__(self, setup, readme)

        self.template = f"{setup.templates_directory}/template_bundle.xml"

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
            if collection.name == "spice_kernels":
                self.COLL_NAME = "spice_kernel"
                self.COLL_LIDVID = collection.lid + "::" + collection.vid
                if collection.updated:
                    self.COLL_STATUS = "Primary"
                else:
                    self.COLL_STATUS = "Secondary"
            if collection.name == "miscellaneous":
                if setup.information_model_float >= 1011001000.0:
                    self.COLL_NAME = "miscellaneous"
                else:
                    self.COLL_NAME = "member"
                self.COLL_LIDVID = collection.lid + "::" + collection.vid
                if collection.updated:
                    self.COLL_STATUS = "Primary"
                else:
                    self.COLL_STATUS = "Secondary"
            if collection.name == "document":
                self.COLL_NAME = "document"
                self.COLL_LIDVID = collection.lid + "::" + collection.vid
                if collection.updated:
                    self.COLL_STATUS = "Primary"
                else:
                    self.COLL_STATUS = "Secondary"

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

    def get_mission_reference_type(self):
        """Get mission reference type.

        :return: Literally ``bundle_to_investigation``
        :rtype: str
        """
        return "bundle_to_investigation"

    def get_target_reference_type(self):
        """Get target reference type.

        :return: Literally ``bundle_to_target``
        :rtype: str
        """
        return "bundle_to_target"
