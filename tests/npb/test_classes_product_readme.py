"""Unit tests for the ReadmeProduct class.
"""
import logging
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, mock_open, patch

import pytest

from pds.naif_pds4_bundler.classes.product.product_readme import ReadmeProduct

# ---------------------------------------------------------------------------
# Patch target: every name imported into product_readme is patched here so the
# real Product registration, label generation and filesystem helpers never run.
# ---------------------------------------------------------------------------
MOD = 'pds.naif_pds4_bundler.classes.product.product_readme'


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

def make_setup(tmp_path, readme=None, silent=True, verbose=False):
    """Return a minimal mock Setup object for ReadmeProduct tests.

    :param tmp_path:  pytest ``tmp_path`` fixture used to build real directories
    :param readme:    value for ``setup.readme`` (dict). Defaults to an empty
                      dict, i.e. no ``'input'`` key, which forces the template
                      generation branch in ``_write_product``.
    :param silent:    value for ``setup.args.silent``
    :param verbose:   value for ``setup.args.verbose``
    :return:          configured ``MagicMock`` acting as the Setup object
    """
    setup = MagicMock()
    # Real directories so 'self.path = staging + os.sep + name' is usable.
    setup.staging_directory = str(tmp_path / 'staging')
    setup.bundle_directory = str(tmp_path / 'bundle')
    setup.templates_directory = str(tmp_path / 'templates')
    setup.working_directory = str(tmp_path / 'work')
    setup.mission_acronym = 'insight'
    setup.spice_name = 'INSIGHT'
    setup.eol = '\r\n'
    setup.eol_pds4 = '\n'
    setup.readme = {} if readme is None else readme
    setup.args = SimpleNamespace(silent=silent, verbose=verbose)
    return setup


def make_bundle(name='bundle_insight_spice_v001.xml', vid='1.0'):
    """Return a minimal mock Bundle object.

    :param name: bundle file name used for the final label path
    :param vid:  bundle version id copied onto the product
    :return:     configured ``MagicMock`` acting as the Bundle object
    """
    bundle = MagicMock()
    bundle.name = name
    bundle.vid = vid
    return bundle


def build_product(setup, bundle):
    """Construct a ``ReadmeProduct`` with the heavy collaborators mocked.

    ``Product.__init__`` and ``BundlePDS4Label`` are always patched so no
    registration or labelling happens. ``md5`` is patched to a stable value.
    ``_write_product`` is also patched out, isolating the constructor logic
    from file generation.

    :param setup:  mock Setup object
    :param bundle: mock Bundle object
    :return:       tuple ``(product, mocks_dict)``
    """
    with patch(f'{MOD}.Product.__init__', return_value=None) as m_init, \
         patch(f'{MOD}.BundlePDS4Label') as m_label, \
         patch(f'{MOD}.md5', return_value='d' * 32) as m_md5, \
         patch.object(ReadmeProduct, '_write_product') as m_write:
        product = ReadmeProduct(setup, bundle)
        mocks = {'init': m_init, 'label': m_label, 'md5': m_md5, 'write': m_write}
        return product, mocks


# ===========================================================================
# ReadmeProduct.__init__
# ===========================================================================

class TestReadmeProductInit:
    """Tests for ``ReadmeProduct.__init__``."""

    def test_init_generates_product_when_no_existing_readme(self, tmp_path):
        # When no readme exists in the final area the "generate" branch is taken:
        # _write_product is invoked, new_product is True, the bundle checksum is
        # set from md5, and constructor-owned attributes are initialised.
        setup = make_setup(tmp_path)
        bundle = make_bundle(vid='2.0')

        product, mocks = build_product(setup, bundle)

        # The generation branch was taken.
        mocks['write'].assert_called_once()
        assert product.new_product is True

        # The bundle checksum is taken from md5() applied to the staging path.
        assert bundle.checksum == 'd' * 32
        mocks['md5'].assert_called_once()

        # Constructor-owned attributes are initialised correctly.
        assert product.name == 'readme.txt'
        assert product.bundle is bundle
        assert product.setup is setup
        assert product.vid == '2.0'
        # collection is a SimpleNamespace with an empty name attribute.
        assert product.collection.name == ''

        # The base Product constructor and the bundle label are invoked once each.
        mocks['init'].assert_called_once()
        mocks['label'].assert_called_once_with(setup, product)

    def test_init_final_path_points_to_bundle_name(self, tmp_path):
        # After construction self.path is rewritten to staging + bundle.name so
        # the label uses the bundle file name rather than readme.txt.
        setup = make_setup(tmp_path)
        bundle = make_bundle(name='bundle_insight_spice_v003.xml')

        product, _ = build_product(setup, bundle)

        expected = setup.staging_directory + os.sep + 'bundle_insight_spice_v003.xml'
        assert product.path == expected

    def test_init_reuses_existing_readme_in_final_area(self, tmp_path):
        # When a readme already exists in the final (bundle) area:
        # _write_product is NOT called, new_product is False, no md5 is computed
        # and self.path is still rewritten to staging + bundle.name for the label.
        # The final (bundle) area is expected to be:
        #    bundle_dir / mission_acronym + "_spice"
        final_dir = Path(tmp_path) / 'bundle' / 'insight_spice'
        final_dir.mkdir(parents=True)
        (final_dir / 'readme.txt').write_text('existing', encoding='utf-8')

        setup = make_setup(tmp_path)
        bundle = make_bundle()

        product, mocks = build_product(setup, bundle)

        # Generation branch was skipped.
        mocks['write'].assert_not_called()
        assert product.new_product is False

        # No checksum was computed because the product was not regenerated.
        mocks['md5'].assert_not_called()

        # Final path is still rewritten to the bundle name for the label.
        expected = setup.staging_directory + os.sep + bundle.name
        assert product.path == expected
        mocks['label'].assert_called_once_with(setup, product)

    def test_init_logs_existing_readme_message(self, tmp_path, caplog):
        # The "already exists" path logs the corresponding info message.
        final_dir = Path(tmp_path) / 'bundle' / 'insight_spice'
        final_dir.mkdir(parents=True)
        (final_dir / 'readme.txt').write_text('existing', encoding='utf-8')

        setup = make_setup(tmp_path)
        bundle = make_bundle()

        with caplog.at_level(logging.INFO):
            build_product(setup, bundle)

        expected = [
            (logging.INFO, '-- Readme file already exists in final area.'),
            (logging.INFO, ''),
            (logging.INFO, '-- Generating bundle label...')]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected

    def test_init_logs_generating_readme_messages(self, tmp_path, caplog):
        # The "generate" path logs the generation notice and the label notice.
        setup = make_setup(tmp_path)
        bundle = make_bundle()

        with caplog.at_level(logging.INFO):
            build_product(setup, bundle)

        expected = [
            (logging.INFO, '-- Generating readme file...'),
            (logging.INFO, ''),
            (logging.INFO, '-- Generating bundle label...')]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]

        assert messages == expected


# ===========================================================================
# ReadmeProduct._write_product
# ===========================================================================

class TestReadmeProductWriteProduct:
    """Tests for ``ReadmeProduct._write_product``."""

    @staticmethod
    def _make_obj(setup, path: str) -> ReadmeProduct:
        # Build a bare ReadmeProduct with only the attributes _write_product
        # needs. __init__ is bypassed via __new__ so the method can be exercised
        # in isolation without triggering the full construction sequence.
        obj = ReadmeProduct.__new__(ReadmeProduct)
        obj.setup = setup
        obj.path = path
        return obj

    # ------------------------------------------------------------------
    # Branch: readme provided via configuration ('input') and it exists
    # ------------------------------------------------------------------

    def test_write_product_copies_input_when_provided_and_exists(self, tmp_path):
        # When setup.readme['input'] points to an existing file it is copied to
        # self.path via shutil.copy; handle_npb_error is not called.
        input_file = tmp_path / 'provided_readme.txt'
        input_file.write_text('provided', encoding='utf-8')

        setup = make_setup(tmp_path, readme={'input': str(input_file)})
        # self.path does not exist yet so the copy branch is entered.
        obj = self._make_obj(setup, str(tmp_path / 'staging' / 'readme.txt'))

        with patch(f'{MOD}.shutil.copy') as m_copy, \
                patch(f'{MOD}.handle_npb_error') as m_err:
            obj._write_product()

        m_copy.assert_called_once_with(str(input_file), obj.path)
        m_err.assert_not_called()

    # ------------------------------------------------------------------
    # Branch: readme provided via configuration but the file is missing
    # ------------------------------------------------------------------

    def test_write_product_errors_when_input_file_missing(self, tmp_path):
        # When setup.readme['input'] points to a non-existent file,
        # handle_npb_error is called with the appropriate message and shutil.copy
        # is never invoked.
        missing = str(tmp_path / 'does_not_exist.txt')
        setup = make_setup(tmp_path, readme={'input': missing})
        obj = self._make_obj(setup, str(tmp_path / 'staging' / 'readme.txt'))

        with patch(f'{MOD}.shutil.copy') as m_copy, \
                patch(f'{MOD}.handle_npb_error') as m_err:
            obj._write_product()

        m_copy.assert_not_called()
        m_err.assert_called_once_with(
            'Readme file provided via configuration does not exist.')

    # ------------------------------------------------------------------
    # Branch: template generation (no 'input' key in setup.readme)
    # ------------------------------------------------------------------

    def test_write_product_generates_from_template_all_substitutions(self, tmp_path):
        # Without a configured input the readme is rendered from the template.
        # Every substitution branch is exercised in a single template:
        # $SPICE_NAME, $UNDERLINE, $OVERVIEW, $COGNISANT_AUTHORITY and a plain
        # (else) line. add_carriage_return is patched to the identity function so
        # the assertions can match the raw rendered content.
        templates = tmp_path / 'templates'
        templates.mkdir()
        template = templates / 'template_readme.txt'
        template.write_text('$SPICE_NAME\n'
                            '$UNDERLINE\n'
                            'Plain line\n'
                            '$OVERVIEW\n'
                            '$COGNISANT_AUTHORITY\n', encoding='utf-8')

        staging = tmp_path / 'staging'
        staging.mkdir()
        out_path = staging / 'readme.txt'

        setup = make_setup(tmp_path,
                           readme={'overview': 'Line A\nLine B',
                                   'cognisant_authority': 'Authority X'})
        setup.templates_directory = str(templates)
        obj = self._make_obj(setup, str(out_path))

        with patch(f'{MOD}.add_carriage_return',
                   side_effect=lambda line, eol, s: line):
            obj._write_product()

        content = out_path.read_text(encoding='utf-8')

        assert content == ('INSIGHT\n'
                           '=======\n'
                           'Plain line\n'
                           '   Line A\n'
                           '   Line B\n'
                           '   Authority X\n')

    @pytest.mark.parametrize('eol_pds4, eol, expected', [
        ('\n', '\n', 'INSIGHT\n   Body\n'),
        ('\r\n', '\r\n', 'INSIGHT\r\n   Body\r\n'),
        # TODO: BUG; mixed values expose the inconsistency:
        #       $SPICE_NAME/$UNDERLINE use setup.eol_pds4 while
        #       $OVERVIEW/$COGNISANT_AUTHORITY and plain lines use setup.eol. If
        #       the production code is unified to one EOL this test must be
        #       updated accordingly.
        pytest.param('\n', '\r\n', 'INSIGHT\n   Body\n',
                     marks=pytest.mark.xfail(
                         reason='mixed EOL bug - see TODO in product_readme.py',
                         strict=True))])
    def test_write_product_forwards_correct_eols_to_add_carriage_return(
            self, tmp_path, eol_pds4, eol, expected):
        # add_carriage_return must be called with eol_pds4 for the $SPICE_NAME
        # branch and with eol for the $OVERVIEW branch; both values are asserted.
        real_open = open
        templates = tmp_path / 'templates'
        templates.mkdir()
        with real_open(templates / 'template_readme.txt', 'w', encoding='utf-8',
                       newline='') as f:
            f.write('$SPICE_NAME\n$OVERVIEW\n')
        staging = tmp_path / 'staging'
        staging.mkdir()
        out_path = staging / 'readme.txt'

        setup = make_setup(tmp_path, readme={'overview': 'Body'})
        setup.templates_directory = str(templates)
        setup.eol_pds4 = eol_pds4
        setup.eol = eol
        obj = self._make_obj(setup, str(out_path))

        with patch('builtins.open',
                   lambda *a, **kw: real_open(*a, **{**kw, 'newline': ''})), \
                patch(f'{MOD}.add_carriage_return',
                      side_effect=lambda line, eol_value, s: line.rstrip('\n') + eol_value):
            obj._write_product()

        with real_open(out_path, encoding='utf-8', newline='') as f:
            content = f.read()

        assert content == expected

    def test_write_product_skips_writing_when_output_already_exists(self, tmp_path):
        # If self.path already exists on disk neither the copy branch nor the
        # template generation branch is entered; the file content is unchanged.
        # This covers the fall-through of both conditions in _write_product.
        staging = tmp_path / 'staging'
        staging.mkdir()
        out_path = staging / 'readme.txt'
        out_path.write_text('already here', encoding='utf-8')

        setup = make_setup(tmp_path, readme={})
        obj = self._make_obj(setup, str(out_path))

        with patch('builtins.open', mock_open()) as m_open, \
                patch(f'{MOD}.shutil.copy') as m_copy:
            obj._write_product()

        m_open.assert_not_called()
        m_copy.assert_not_called()
        assert out_path.read_text(encoding='utf-8') == 'already here'

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def test_write_product_logs_created_message(self, tmp_path, caplog):
        # _write_product always logs "Created readme file." regardless of which
        # branch was taken; the file already exists so no generation work runs.
        staging = tmp_path / 'staging'
        staging.mkdir()
        out_path = staging / 'readme.txt'
        out_path.write_text('x', encoding='utf-8')

        setup = make_setup(tmp_path, readme={})
        obj = self._make_obj(setup, str(out_path))

        with caplog.at_level(logging.INFO):
            obj._write_product()

        expected = [
            (logging.INFO, '-- Created readme file.')]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected

    # ------------------------------------------------------------------
    # Print branch
    # ------------------------------------------------------------------

    @pytest.mark.parametrize('silent, verbose, expected_out', [
        (False, False, '   * Created readme file.\n'),  # only this prints
        (True, False, ''),
        (False, True, ''),
        (True, True, '')])
    def test_write_product_prints_only_when_not_silent_and_not_verbose(
            self, tmp_path, capsys, silent, verbose, expected_out):
        # The console notice is printed only when both args.silent and
        # args.verbose are False; the expected stdout content is itself
        # parametrized so the test body contains a single, unconditional assert.
        staging = tmp_path / 'staging'
        staging.mkdir()
        out_path = staging / 'readme.txt'
        out_path.write_text('x', encoding='utf-8')

        setup = make_setup(tmp_path, readme={}, silent=silent, verbose=verbose)
        obj = self._make_obj(setup, str(out_path))

        obj._write_product()

        captured = capsys.readouterr()
        assert captured.out == expected_out
