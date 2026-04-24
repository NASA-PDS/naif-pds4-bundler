"""Tests for DocumentCollection — one test class per method.
"""
from unittest.mock import MagicMock, patch

import pytest

from pds.naif_pds4_bundler.classes.collection.collection_docs import DocumentCollection


# ---------------------------------------------------------------------------
# Patch targets — the names as they exist inside the module under test
# ---------------------------------------------------------------------------

_PDS3_PRODUCT_CLS = "pds.naif_pds4_bundler.classes.collection.collection_docs.PDS3DocumentProduct"
_GLOB             = "pds.naif_pds4_bundler.classes.collection.collection_docs.glob.glob"


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def make_setup(pds_version="4", staging_directory="/fake/staging"):
    return MagicMock(
        pds_version=pds_version,
        staging_directory=staging_directory
    )


# ---------------------------------------------------------------------------
# TestDocumentCollectionInit
# ---------------------------------------------------------------------------

class TestDocumentCollectionInit:
    """Tests for DocumentCollection.__init__."""

    @pytest.mark.parametrize("pds_version, kind", [
        ('3', 'DOCUMENT'),
        ('4', 'document')
    ])
    def test_init_sets_type(self, pds_version, kind):
        """pds_version == '3' must set self.type = 'DOCUMENT'."""
        obj = DocumentCollection(make_setup(pds_version=pds_version), MagicMock())
        assert obj.type == kind
        assert obj.name == kind

    @pytest.mark.parametrize("pds_version", ['3', '4'])
    def test_super_receives_setup_and_bundle(self, pds_version):
        """setup and bundle must be forwarded to super().__init__ unchanged."""
        setup  = make_setup(pds_version=pds_version)
        bundle = MagicMock()
        obj = DocumentCollection(setup, bundle)
        assert obj.setup  is setup
        assert obj.bundle is bundle

    def test_neither_pds3_nor_pds4_raises_attribute_error(self):
        """If pds_version is neither '3' nor '4', self.type is never assigned
        and the super().__init__ call raises AttributeError."""
        with pytest.raises(AttributeError):
            DocumentCollection(make_setup(pds_version="99"), MagicMock())


# ---------------------------------------------------------------------------
# TestGetPds3Documents
# ---------------------------------------------------------------------------

class TestDocumentCollectionGetPds3Documents:
    """Tests for DocumentCollection.get_pds3_documents."""

    TXT_FILE    = "/fake/staging/docs/readme.txt"
    CAT_FILE    = "/fake/staging/docs/voldesc.cat"
    README_FILE = "/fake/staging/aareadme.txt"   # matches "aareadme."
    OTHER_FILE  = "/fake/staging/docs/image.png"

    # ---- construction helper ----

    @staticmethod
    def _make_instance(staging_dir="/fake/staging", pds_version="3"):
        """Return a DocumentCollection with collaborators patched."""
        return DocumentCollection(
            make_setup(pds_version=pds_version, staging_directory=staging_dir),
            MagicMock())

    @staticmethod
    def _run(obj, glob_files, new_product=True):
        """Drive get_pds3_documents with a controlled glob result and product mock."""
        mock_doc = MagicMock()
        mock_doc.new_product = new_product

        with patch(_GLOB, return_value=glob_files), \
             patch(_PDS3_PRODUCT_CLS, return_value=mock_doc) as mock_cls:
            obj.get_pds3_documents()

        return mock_doc, mock_cls

    def test_no_files_no_products_added(self):
        """glob returns no files"""
        obj = self._make_instance()
        self._run(obj, glob_files=[])
        assert obj.product == []
        assert obj.updated is False

    @pytest.mark.parametrize("files, length, updated", [
        ([TXT_FILE], 1, True),
        ([CAT_FILE], 1, True),
        ([README_FILE], 1, True),
        ([OTHER_FILE], 0, False)
    ])
    def test_new_product_true_is_added(self, files, length, updated):
        obj = self._make_instance()
        self._run(obj, files, new_product=True)
        assert len(obj.product) == length
        assert obj.updated is updated

    @pytest.mark.parametrize("files", [TXT_FILE, CAT_FILE, README_FILE, OTHER_FILE])
    def test_new_product_false_not_added(self, files):
        obj = self._make_instance()
        self._run(obj, files, new_product=False)
        assert obj.product == []
        assert obj.updated is False

    # ---- PDS3DocumentProduct instantiated with correct args ----

    def test_product_constructed_with_setup_and_file(self):
        obj = self._make_instance(staging_dir="/fake/staging")
        _, mock_cls = self._run(obj, [self.TXT_FILE], new_product=True)
        mock_cls.assert_called_once_with(obj.setup, self.TXT_FILE)

    # ---- multiple files: only qualifying new products are added ----

    def test_mixed_files_only_qualifying_new_products_added(self):
        """Of four files: txt (new=True) and aareadme (new=True) are added;
        cat (new=False) and png (non-qualifying) are not."""
        obj = self._make_instance()

        files = [self.TXT_FILE, self.CAT_FILE, self.README_FILE, self.OTHER_FILE]

        def _product_factory(_, filepath):
            m = MagicMock()
            m.new_product = filepath in (self.TXT_FILE, self.README_FILE)
            return m

        with patch(_GLOB, return_value=files), \
             patch(_PDS3_PRODUCT_CLS, side_effect=_product_factory):
            obj.get_pds3_documents()

        assert len(obj.product) == 2

    # ---- glob called with the correct recursive pattern ----

    def test_glob_called_with_correct_pattern(self):
        obj = self._make_instance(staging_dir="/my/staging")
        with patch(_GLOB, return_value=[]) as mock_glob:
            obj.get_pds3_documents()
        mock_glob.assert_called_once_with(
            "/my/staging/**/*[.]*", recursive=True
        )
