"""Implementation of the Document Collection Class."""
import glob

from .collection import Collection
from ..product import PDS3DocumentProduct


class DocumentCollection(Collection):
    """Class to generate a PDS3 or PDS4 Document Collection.

    :param setup: NPB execution setup object
    :param bundle: Bundle object
    """

    def __init__(self, setup, bundle) -> None:
        """Constructor."""
        if setup.pds_version == "3":
            self.type = "DOCUMENT"
        elif setup.pds_version == "4":
            self.type = "document"

        super().__init__(self.type, setup, bundle)

    def get_pds3_documents(self):
        """Collects the updated PDS3 documents for the increment."""
        for file in glob.glob(
            f"{self.setup.staging_directory}/**/*[.]*", recursive=True
        ):
            if ".txt" in file or ".cat" in file or "aareadme." in file:
                document = PDS3DocumentProduct(self.setup, file)

                if document.new_product:
                    self.add(document)
