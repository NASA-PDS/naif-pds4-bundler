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


class TestDocumentPDS4LabelIntegration:
    """Integration tests for DocumentPDS4Label and the inherited writer."""

    @pytest.fixture()
    def env(self,
            tmp_path: Path,
            mocker) -> tuple[SimpleNamespace, SimpleNamespace, SimpleNamespace, Path, Path]:
        # Create the temporary PDS4 document-label environment used by
        # integration tests: real template, staging product, expected XML label
        # path and setup state.

        # Create isolated directories used by the real writer.
        templates_dir = tmp_path / 'templates'
        staging_dir = tmp_path / 'staging'
        document_dir = staging_dir / 'document'
        work_dir = tmp_path / 'work'
        bundle_dir = tmp_path / 'bundle'

        templates_dir.mkdir()
        document_dir.mkdir(parents=True)
        work_dir.mkdir()
        bundle_dir.mkdir()

        # The template name must match the one selected by DocumentPDS4Label.
        template_path = templates_dir / 'template_product_html_document.xml'
        template_path.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<document>\n'
            '  <file_name>$FILE_NAME</file_name>\n'
            '  <logical_identifier>$PRODUCT_LID</logical_identifier>\n'
            '  <version_id>$PRODUCT_VID</version_id>\n'
            '  <start_date_time>$START_TIME</start_date_time>\n'
            '  <stop_date_time>$STOP_TIME</stop_date_time>\n'
            '</document>\n',
            encoding='utf-8')

        # Context products keep the fake objects close to the real PDS4 label
        # environment used by the inherited writer.
        context_products = [
            {'name': ['MAVEN'],
             'type': ['Mission'],
             'lidvid': 'urn:nasa:pds:context:investigation:mission.maven::1.0'},
            {'name': ['MAVEN'],
             'type': ['Spacecraft'],
             'lidvid': ('urn:nasa:pds:context:instrument_host:'
                        'spacecraft.maven::1.0')},
            {'name': ['Mars'],
             'type': ['Planet'],
             'lidvid': 'urn:nasa:pds:context:target:planet.mars::1.0'}]

        # Build the Setup attributes consumed by DocumentPDS4Label/PDSLabel.
        setup = SimpleNamespace(
            pds_version='4',
            volume_id='maven_0001',
            mission_acronym='maven',
            mission_name='MAVEN',
            mission_start='2014-09-21T00:00:00Z',
            mission_finish='2026-05-04T00:00:00Z',
            observer='MAVEN',
            target='Mars',
            secondary_missions=[],
            secondary_observers=[],
            secondary_targets=[],
            root_dir=str(tmp_path),
            templates_directory=str(templates_dir),
            staging_directory=str(staging_dir),
            working_directory=str(work_dir),
            bundle_directory=str(bundle_dir),
            diff=False,
            xml_model='https://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1F00.sch',
            schema_location='https://pds.nasa.gov/pds4/pds/v1 PDS4_PDS_1F00.xsd',
            information_model='.'.join(['1', '16', '0', '0']),
            information_model_float=1016000000.0,
            logical_identifier='urn:nasa:pds:maven_spice',
            end_of_line='LF',
            eol_pds4='\n',
            xml_tab=1,
            args=SimpleNamespace(silent=True, verbose=False),
            add_file=mocker.Mock())

        # Collection name is used by DocumentPDS4Label before write_label runs.
        collection = SimpleNamespace(
            name='collection_document_inventory_v001.csv',
            bundle=SimpleNamespace(context_products=context_products))

        # The inherited writer creates the XML label next to inventory.path,
        # replacing the product suffix by .xml.
        inventory_path = document_dir / 'spiceds_v001.html'
        inventory_path.write_text('<html>SPICE document</html>\n',
                                  encoding='utf-8')

        # Inventory metadata rendered into the XML template.
        inventory = SimpleNamespace(
            lid='urn:nasa:pds:maven_spice:document:spiceds',
            vid='1.0',
            name='spiceds_v001.html',
            extension='html',
            path=str(inventory_path),
            creation_time='2024-02-01T12:00:00',
            creation_date='2024-02-01',
            size='2048',
            checksum='d41d8cd98f00b204e9800998ecf8427e',
            collection=collection,
            bundle=SimpleNamespace(context_products=context_products))

        # Expected XML label path produced from the staged document product path.
        return (setup, collection, inventory, template_path,
                inventory_path.with_suffix('.xml'))

    def test_label_file_is_created_from_template(
            self,
            env: tuple[SimpleNamespace, SimpleNamespace, SimpleNamespace, Path, Path]) -> None:
        # Render the document XML template with the real inherited writer and
        # compare the generated label with the expected full content.
        setup, collection, inventory, template_path, label_path = env

        label = DocumentPDS4Label(setup, collection, inventory)

        # DocumentPDS4Label must resolve the document-specific template.
        assert label.template == str(template_path)

        # The real writer mutates label.name to the generated XML file path.
        assert Path(label.name) == label_path

        # The real writer creates the XML label beside the document product.
        assert label_path.exists()

        with open(label_path, 'rt', encoding='utf-8', newline='') as label_file:
            written_label = label_file.read()

        # Verify that all placeholders were replaced with DocumentPDS4Label state.
        assert written_label == (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<document>\n'
            '  <file_name>spiceds_v001.html</file_name>\n'
            '  <logical_identifier>'
            'urn:nasa:pds:maven_spice:document:spiceds'
            '</logical_identifier>\n'
            '  <version_id>1.0</version_id>\n'
            '  <start_date_time>2014-09-21T00:00:00Z</start_date_time>\n'
            '  <stop_date_time>2026-05-04T00:00:00Z</stop_date_time>\n'
            '</document>\n')

    def test_add_file_called_with_label_path(
            self,
            env: tuple[SimpleNamespace, SimpleNamespace, SimpleNamespace, Path, Path]) -> None:
        # Verify that the real writer registers the generated document XML label using
        # its staging-relative path.
        setup, collection, inventory, _, label_path = env

        DocumentPDS4Label(setup, collection, inventory)

        # Convert the generated XML label path to the path expected in the file
        # list.
        expected_label_path = str(label_path.relative_to(Path(setup.staging_directory)))

        # The generated XML label must be registered exactly once.
        setup.add_file.assert_called_once_with(expected_label_path)
