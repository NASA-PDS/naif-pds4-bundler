"""Tests for DocumentPDS4Label class."""
from pathlib import Path
from types import SimpleNamespace

import pytest

from pds.naif_pds4_bundler.classes.label.pds4_document import DocumentPDS4Label


class TestDocumentPDS4LabelInit:

    @staticmethod
    def make_document_label_inputs(
            tmp_path: Path,
            collection_name: str = 'collection_document_inventory_v001.csv'
    ) -> tuple[SimpleNamespace, SimpleNamespace, SimpleNamespace]:
        # Build only the attributes consumed directly by DocumentPDS4Label.
        # This keeps the test focused on this constructor and avoids executing
        # unrelated Setup, Collection or Product initialization logic.
        setup = SimpleNamespace(templates_directory=str(tmp_path / 'templates'),
                                mission_start='2014-09-21T00:00:00Z',
                                mission_finish='2026-05-04T00:00:00Z')

        collection = SimpleNamespace(name=collection_name)

        inventory = SimpleNamespace(lid='urn:nasa:pds:maven_spice:document:spiceds',
                                    vid='1.0',
                                    name='spiceds_v001.html')

        return setup, collection, inventory

    def test_init_sets_document_label_state_and_requests_label_write(
            self, mocker, tmp_path: Path) -> None:
        # Verify the successful constructor path: parent initialization,
        # document-label state assignment, template path construction and
        # write_label invocation.

        # Create the minimal objects.
        setup, collection, inventory = self.make_document_label_inputs(tmp_path)

        # This mock allows you to verify that the call is made, but without
        # executing the actual logic of PDSLabel.
        parent_init_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.label.pds4_document.PDSLabel.__init__',
            autospec=True)

        # Mock write_label to verify that label generation is requested without
        # creating files on disk.
        write_label_mock = mocker.patch.object(DocumentPDS4Label, 'write_label',
                                               autospec=True)

        document_label = DocumentPDS4Label(setup, collection, inventory)

        # Verification of the call to the parent.
        parent_init_mock.assert_called_once_with(document_label, setup, inventory)

        # Check that the class stores the same references as those received.
        assert document_label.setup is setup
        assert document_label.collection is collection
        assert document_label.template == str(Path(setup.templates_directory) /
                                              'template_product_html_document.xml')

        # Check the product details.
        assert document_label.PRODUCT_LID == inventory.lid
        assert document_label.PRODUCT_VID == inventory.vid
        assert document_label.START_TIME == setup.mission_start
        assert document_label.STOP_TIME == setup.mission_finish
        assert document_label.FILE_NAME == inventory.name
        assert document_label.name == 'collection_document_inventory_v001.xml'

        # Check that the constructor requests the label to be generated exactly
        # once.
        write_label_mock.assert_called_once_with(document_label)

    def test_write_label_error_is_propagated_after_state_is_prepared(
            self, mocker, tmp_path: Path) -> None:
        # Verify that write_label failures are propagated only after the document-label
        # state required by the writer has been fully prepared.

        # Create the minimal objects.
        setup, collection, inventory = self.make_document_label_inputs(tmp_path)

        parent_init_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.label.pds4_document.PDSLabel.__init__',
            autospec=True)

        # Mock the write_label() to force a fail.
        write_label_mock = mocker.patch.object(DocumentPDS4Label, 'write_label',
                                               autospec=True,
                                               side_effect=RuntimeError('label write failed'))

        # Capture the exception.
        with pytest.raises(RuntimeError, match='label write failed'):
            DocumentPDS4Label(setup, collection, inventory)

        parent_init_mock.assert_called_once()
        write_label_mock.assert_called_once()

        document_label = write_label_mock.call_args.args[0]

        # Check that the parent has been initialised before failing.
        assert document_label.setup is setup
        assert document_label.collection is collection
        assert document_label.template == str(Path(setup.templates_directory) /
                                              'template_product_html_document.xml')

        # Check the status before writing.
        assert document_label.PRODUCT_LID == inventory.lid
        assert document_label.PRODUCT_VID == inventory.vid
        assert document_label.START_TIME == setup.mission_start
        assert document_label.STOP_TIME == setup.mission_finish
        assert document_label.FILE_NAME == inventory.name
        assert document_label.name == 'collection_document_inventory_v001.xml'

    def test_init_currently_truncates_collection_name_at_first_dot(
            self, mocker, tmp_path: Path) -> None:
        # This test document a bug. A valid file name containing more than one
        # dot is truncated at the first dot.

        # Create an object with a valid file name with more than one dot.
        setup, collection, inventory = self.make_document_label_inputs(
            tmp_path, collection_name='collection.document_inventory_v001.csv')

        mocker.patch(
            'pds.naif_pds4_bundler.classes.label.pds4_document.PDSLabel.__init__',
            autospec=True)

        mocker.patch.object(DocumentPDS4Label, 'write_label', autospec=True)

        document_label = DocumentPDS4Label(setup, collection, inventory)

        # Represents the truncated file name because the bug.
        assert document_label.name == 'collection.xml'
