"""Unit tests for the SpicedsProduct class."""
import logging
import os
from unittest.mock import MagicMock, patch

import pytest

from pds.naif_pds4_bundler.classes.product.product_spiceds import SpicedsProduct

# Module path used as the anchor for every patch target.
_MODULE = 'pds.naif_pds4_bundler.classes.product.product_spiceds'


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

def make_setup(spiceds='/input/spiceds.html', increment=False, diff=False,
               staging_directory='/staging', bundle_directory='/bundle',
               working_directory='/work', root_dir='/root',
               mission_acronym='insight',
               logical_identifier='urn:nasa:pds:insight_spice',
               eol_pds4='\r\n'):
    """Return a minimal mock Setup object for SpicedsProduct tests.
    """
    setup = MagicMock()
    setup.spiceds = spiceds
    setup.increment = increment
    setup.diff = diff
    setup.staging_directory = staging_directory
    setup.bundle_directory = bundle_directory
    setup.working_directory = working_directory
    setup.root_dir = root_dir
    setup.mission_acronym = mission_acronym
    setup.logical_identifier = logical_identifier
    setup.eol_pds4 = eol_pds4
    return setup


def make_collection(name='document'):
    """Return a minimal mock collection object"""
    collection = MagicMock()
    collection.name = name
    return collection


def make_spiceds_without_init(**attrs):
    """Build a SpicedsProduct bypassing ``__init__``.

    The single-method test classes (``_check_cr``, ``_check_product``,
    ``_compare``) only need a few attributes on the instance, so constructing
    via ``__new__`` keeps each test focused on the method under test and avoids
    dragging the whole constructor in.
    """
    product = SpicedsProduct.__new__(SpicedsProduct)
    for key, value in attrs.items():
        setattr(product, key, value)
    return product


def base_init_patches():
    """Return a fresh list of context managers isolating ``__init__``.

    Every constructor test that reaches the 'spiceds provided' tail needs the
    same external collaborators stubbed: the file copy into staging, the CR
    normalisation, the product self-check, the optional comparison, the base
    ``Product.__init__`` and the PDS4 label. A fresh list per call keeps the
    patch objects single-use.
    """
    return [
        patch(f'{_MODULE}.shutil.copy2'),
        patch.object(SpicedsProduct, '_check_cr'),
        patch.object(SpicedsProduct, '_check_product', return_value=True),
        patch.object(SpicedsProduct, '_compare'),
        patch(f'{_MODULE}.Product.__init__', return_value=None),
        patch(f'{_MODULE}.DocumentPDS4Label', return_value=MagicMock())]


# ---------------------------------------------------------------------------
# __init__  (also exercises set_product_lid and set_product_vid)
# ---------------------------------------------------------------------------

class TestSpicedsProductInit:
    """Tests for __init__, set_product_lid and set_product_vid. The latter two
    are trivial setters invoked only from the constructor, so per the brief
    they are verified through the lid/vid attributes __init__ leaves behind
    rather than in isolation."""

    def test_init_no_increment_with_spiceds_provided(self):
        # Common first-release path: no increment and a 'spiceds' provided.
        # Drives the whole tail of the constructor and pins down the derived
        # name/path/lid/vid plus the ordering side effects (copy, CR check,
        # product check, label).
        setup = make_setup(increment=False, diff=False)
        collection = make_collection(name='document')

        with base_init_patches()[0] as copy2, \
                base_init_patches()[1] as check_cr, \
                base_init_patches()[2] as check_product, \
                base_init_patches()[3] as compare, \
                base_init_patches()[4] as base_init, \
                base_init_patches()[5] as label:
            product = SpicedsProduct(setup, collection)

        # Version 1 because there is no previous increment.
        assert product.version == 1
        assert product.latest_spiceds == ''

        # Name and staging path are derived from version + collection name.
        assert product.name == 'spiceds_v001.html'
        assert product.path == os.path.join('/staging', 'document',
                                            'spiceds_v001.html')

        # set_product_lid / set_product_vid results (lower-cased LID, '<v>.0').
        assert product.lid == 'urn:nasa:pds:insight_spice:document:spiceds'
        assert product.vid == '1.0'

        # self.mission is the whole setup object.
        assert product.mission is setup

        # new_product stays True and the constructor finished the happy path.
        assert product.new_product is True
        assert product.generated is True

        # External collaborators were invoked exactly as expected.
        copy2.assert_called_once_with('/input/spiceds.html', product.path)
        check_cr.assert_called_once_with()
        check_product.assert_called_once_with()
        base_init.assert_called_once()

        # diff is False so _compare must be skipped, but the label is built.
        compare.assert_not_called()
        label.assert_called_once_with(setup, collection, product)

    def test_init_runs_compare_when_diff_enabled(self):
        # When setup.diff is truthy and the product is generated, _compare runs
        # before the label is built.
        setup = make_setup(increment=False, diff=True)
        collection = make_collection()

        patches = base_init_patches()
        with patches[0], patches[1], \
                patches[2], patches[3] as compare, \
                patches[4], patches[5] as label:
            product = SpicedsProduct(setup, collection)

        compare.assert_called_once_with()
        label.assert_called_once()
        assert product.generated is True

    def test_init_skips_label_when_not_generated(self):
        # When _check_product returns False the product is not generated, so
        # neither the comparison nor the label run.
        setup = make_setup(increment=False, diff=True)
        collection = make_collection()

        patches = base_init_patches()
        with patches[0], patches[1], \
                patch.object(SpicedsProduct, '_check_product', return_value=False), \
                patches[3] as compare, patches[4], \
                patches[5] as label:
            product = SpicedsProduct(setup, collection)

        # Not generated => neither the comparison nor the label run.
        assert product.generated is False
        compare.assert_not_called()
        label.assert_not_called()

    def test_init_increment_with_previous_version_and_new_spiceds(self):
        # Increment + previous 'spiceds' files + a new 'spiceds' provided. glob
        # returns out-of-order versions; the constructor must sort them, pick the
        # highest, store it as latest_spiceds/latest_version and bump version by
        # one. Because a new 'spiceds' is also provided it continues to the staging
        # tail rather than early-returning.
        setup = make_setup(increment=True, spiceds='/input/spiceds.html')
        collection = make_collection(name='document')

        previous = [
            '/bundle/insight_spice/document/spiceds_v001.html',
            '/bundle/insight_spice/document/spiceds_v003.html',
            '/bundle/insight_spice/document/spiceds_v002.html']

        patches = base_init_patches()
        with patch(f'{_MODULE}.glob.glob', return_value=list(previous)) as glob_mock, \
                patches[0] as copy2, patches[1], patches[2], \
                patches[3], patches[4], patches[5]:
            product = SpicedsProduct(setup, collection)

        # The search path is bundle/<acronym>_spice/<collection>.
        expected_glob = os.path.join(
            '/bundle', 'insight_spice', 'document', 'spiceds_v*.html')
        glob_mock.assert_called_once_with(expected_glob)

        # Highest version after sorting is v003 -> new version is 4.
        assert product.latest_version == '003'
        assert product.latest_spiceds.endswith('spiceds_v003.html')
        assert product.version == 4
        assert product.name == 'spiceds_v004.html'
        assert product.vid == '4.0'
        copy2.assert_called_once()

    def test_init_increment_previous_version_no_new_spiceds_early_returns(self):
        # Increment + previous version + NO new spiceds. The constructor sets
        # generated = False and returns before deriving name/path/lid, so those
        # attributes must be absent.
        setup = make_setup(increment=True, spiceds='')
        collection = make_collection()

        with patch(f'{_MODULE}.glob.glob',
                   return_value=['/bundle/insight_spice/document/spiceds_v005.html']):
            product = SpicedsProduct(setup, collection)

        assert product.version == 6
        assert product.latest_version == '005'
        assert product.generated is False

        # Early return happened before the staging tail.
        assert not hasattr(product, 'name')
        assert not hasattr(product, 'lid')

    def test_init_increment_no_previous_with_spiceds_provided(self):
        # Increment but glob finds nothing, yet a spiceds is provided. The
        # empty-list [-1] raises IndexError -> the except branch sets version 1
        # and empty latest_spiceds; handle_npb_error must NOT fire because a
        # spiceds was supplied.
        setup = make_setup(increment=True, spiceds='/input/spiceds.html')
        collection = make_collection()

        patches = base_init_patches()
        with patch(f'{_MODULE}.glob.glob', return_value=[]), \
                patch(f'{_MODULE}.handle_npb_error') as npb_error, \
                patches[0], patches[1], patches[2], \
                patches[3], patches[4], patches[5]:
            product = SpicedsProduct(setup, collection)

        npb_error.assert_not_called()
        assert product.version == 1
        assert product.latest_spiceds == ''
        assert product.name == 'spiceds_v001.html'

    def test_init_increment_no_previous_no_spiceds_calls_handle_error(self):
        # Increment, no previous version AND no 'spiceds' -> handle_npb_error.

        # TODO: BUG, handle_npb_error is annotated NoReturn, so the constructor
        #       assumes it never returns. However, the code does not enforce
        #       this structurally: if handle_npb_error were to return, execution
        #       would fall through to shutil.copy2(spiceds='', ...) and raise
        #       FileNotFoundError instead of the intended npb error message.
        setup = make_setup(increment=True, spiceds='')
        collection = make_collection()

        with patch(f'{_MODULE}.glob.glob', return_value=[]), \
                patch(f'{_MODULE}.handle_npb_error',
                      side_effect=SystemExit) as npb_error:
            with pytest.raises(SystemExit):
                SpicedsProduct(setup, collection)

        npb_error.assert_called_once()

    def test_init_no_increment_no_spiceds_calls_handle_error(self):
        # No increment and no spiceds -> handle_npb_error on the else branch.
        setup = make_setup(increment=False, spiceds='')
        collection = make_collection()

        with patch(f'{_MODULE}.handle_npb_error',
                   side_effect=SystemExit) as npb_error:
            with pytest.raises(SystemExit):
                SpicedsProduct(setup, collection)

        npb_error.assert_called_once()

    def test_init_missing_spiceds_attribute_treated_as_empty(self):
        # If accessing setup.spiceds raises, the constructor's try/except
        # BaseException must swallow it and treat 'spiceds' as empty, behaving
        # exactly like spiceds='' (here on the no-increment else branch). A mock
        # with the attribute deleted makes access raise AttributeError.
        setup = make_setup(increment=False)
        del setup.spiceds
        collection = make_collection()

        with patch(f'{_MODULE}.handle_npb_error',
                   side_effect=SystemExit) as npb_error:
            with pytest.raises(SystemExit):
                SpicedsProduct(setup, collection)

        npb_error.assert_called_once()


# ---------------------------------------------------------------------------
# _check_cr
# ---------------------------------------------------------------------------

class TestSpicedsProductCheckCr:
    """ Tests for _check_cr, which normalises line endings via a temporary
    file."""

    # TODO: BUG, the temporary filename is built from date.today() formatted
    #       with '%H:%M:%S.%f'. A date object has no time component, so the
    #       suffix is always '00:00:00.000000' and the temp name is NOT unique
    #       across runs on the same day.

    def _make_product(self, tmp_path, content, eol_pds4='\r\n'):
        # Helper: create a product whose path points to a real file on disk.
        spiceds_path = tmp_path / 'spiceds_v001.html'
        spiceds_path.write_text(content, encoding='utf-8', newline='')
        setup = make_setup(eol_pds4=eol_pds4)
        return make_spiceds_without_init(path=str(spiceds_path), setup=setup), \
            spiceds_path

    def test_check_cr_no_change_removes_temporary_file(self, tmp_path):
        # When add_carriage_return is a no-op, filecmp reports temp == original,
        # so the temporary copy is removed and the original is preserved.
        # TODO: BUG; date.today() uses strftime with time directives
        #       (%H:%M:%S.%f) but date has no time component, so the suffix is
        #       always '00:00:00.000000'. Colons are illegal in filenames on
        #       Windows, so date is patched here to return a colon-free suffix
        #       until the bug is fixed.
        product, spiceds_path = self._make_product(tmp_path, 'line1\nline2\n')

        # add_carriage_return returns each line verbatim. Because the class
        # opens the file in text mode, only LF content round-trips byte-for-byte
        # (CRLF would be normalised to LF on read), so filecmp reports equality.
        mock_date = MagicMock()
        mock_date.strftime.return_value = '2026-06-29T000000.000000'

        with patch(f'{_MODULE}.date') as date_mock, \
                patch(f'{_MODULE}.add_carriage_return',
                      side_effect=lambda line, eol, setup: line):
            date_mock.today.return_value = mock_date
            product._check_cr()

        leftovers = [p for p in tmp_path.iterdir() if p.name != spiceds_path.name]
        assert leftovers == []

    def test_check_cr_adds_cr_and_moves_temporary_over_original(self, tmp_path, caplog):
        # When CRs are added, the temp file differs from the original, so it is
        # moved over the original and the addition is logged. add_carriage_return
        # is simulated via a lambda that turns every LF into CRLF.
        product, spiceds_path = self._make_product(tmp_path, 'line1\nline2\n')

        mock_date = MagicMock()
        mock_date.strftime.return_value = '2026-06-29T000000.000000'
        with patch(f'{_MODULE}.date') as date_mock, \
                patch(f'{_MODULE}.add_carriage_return',
                      side_effect=lambda line, eol, setup: line.replace('\n', '\r\n')):
            date_mock.today.return_value = mock_date
            with caplog.at_level(logging.INFO):
                product._check_cr()

        leftovers = [p for p in tmp_path.iterdir() if p.name != spiceds_path.name]
        assert leftovers == []

        expected = [
            (logging.INFO, '-- Carriage Return has been added to lines in the spiceds file.')]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected

    def test_check_cr_passes_eol_and_setup_to_helper(self, tmp_path):
        # Each line is forwarded to add_carriage_return with the configured
        # eol_pds4 and the setup object.
        product, _ = self._make_product(tmp_path, 'a\nb\n', eol_pds4='\r\n')

        mock_date = MagicMock()
        mock_date.strftime.return_value = '2026-06-29T000000.000000'
        with patch(f'{_MODULE}.date') as date_mock, \
                patch(f'{_MODULE}.add_carriage_return',
                      side_effect=lambda line, eol, setup: line) as helper:
            date_mock.today.return_value = mock_date
            product._check_cr()

        # Two lines -> two calls, each with the configured eol and setup object.
        assert helper.call_count == 2
        for call_args in helper.call_args_list:
            assert call_args.args[1] == '\r\n'
            assert call_args.args[2] is product.setup


# ---------------------------------------------------------------------------
# _check_product
# ---------------------------------------------------------------------------

class TestSpicedsProductCheckProduct:
    """Tests for _check_product, which returns whether the product must be built."""

    def test_check_product_returns_true_when_no_latest(self):
        # With no previous spiceds, the product always needs generating.
        product = make_spiceds_without_init(latest_spiceds='', path='/ignored')
        assert product._check_product() is True

    def test_check_product_true_on_substantive_difference(self, tmp_path):
        # A real content difference (not just a 'Last update' line) forces
        # regeneration and must not delete the current product.
        current = tmp_path / 'spiceds_v002.html'
        latest = tmp_path / 'spiceds_v001.html'
        current.write_text('Intro\nBrand new paragraph\n', encoding='utf-8')
        latest.write_text('Intro\nOld paragraph\n', encoding='utf-8')

        product = make_spiceds_without_init(
            latest_spiceds=str(latest), path=str(current))

        assert product._check_product() is True

        # A substantive change must NOT delete the current product.
        assert current.exists()

    @pytest.mark.parametrize('current_text, latest_text', [
        ('Intro\nBody\n', 'Intro\nBody\n'),
        ('Intro\nLast update 2024\nBody\n', 'Intro\nLast update 2023\nBody\n')])
    def test_check_product_false_when_only_trivial_changes(
            self, tmp_path, current_text, latest_text, caplog):
        # Identical content, or only a 'Last update' line differing, means no
        # regeneration: the method returns False, removes the staged current
        # product and logs a warning.
        current = tmp_path / 'spiceds_v002.html'
        latest = tmp_path / 'spiceds_v001.html'
        current.write_text(current_text, encoding='utf-8')
        latest.write_text(latest_text, encoding='utf-8')

        product = make_spiceds_without_init(
            latest_spiceds=str(latest), path=str(current))

        with caplog.at_level(logging.INFO):
            result = product._check_product()

        assert result is False

        # The staged product is deleted when it does not need updating.
        assert not current.exists()

        expected = [
            (logging.WARNING, '-- spiceds document does not need to be updated.'),
            (logging.WARNING, ''),
        ]
        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected


# ---------------------------------------------------------------------------
# _compare
# ---------------------------------------------------------------------------

class TestSpicedsProductCompare:
    """Tests for _compare, which diffs the product against a reference
    'spiceds'."""

    def test_compare_uses_latest_previous_increment(self, tmp_path):
        # When previous-increment spiceds exist, the highest sorted one is used
        # as the fromfile and the product path as the tofile.
        setup = make_setup(diff=True)
        product = make_spiceds_without_init(
            setup=setup, name='spiceds_v004.html', path='/staging/spiceds_v004.html')

        found = [
            '/bundle/insight_spice/document/spiceds_v001.html',
            '/bundle/insight_spice/document/spiceds_v003.html',
            '/bundle/insight_spice/document/spiceds_v002.html']

        with patch(f'{_MODULE}.glob.glob', return_value=list(found)) as glob_mock, \
                patch(f'{_MODULE}.compare_files') as compare_files:
            product._compare()

        # The glob targets the bundle document directory
        expected_glob = '/bundle/insight_spice/document/spiceds_v*.html'
        glob_mock.assert_called_once_with(expected_glob)

        # fromfile is the highest sorted match; tofile is the product path.
        compare_files.assert_called_once_with(
            '/bundle/insight_spice/document/spiceds_v003.html',
            '/staging/spiceds_v004.html', '/work', True)

    def test_compare_falls_back_to_insight_example(self, tmp_path, caplog):
        # With no previous increment (empty glob -> IndexError), _compare falls
        # back to the bundled InSight sample and logs the fallback.

        # TODO: BUG, _compare builds val_spd_path and the InSight fallback path
        #       with hardcoded '/' separators via f-strings, unlike __init__
        #       which uses os.sep. On Windows these forward-slash paths still
        #       work with the glob/open APIs but are inconsistent with the rest
        #       of the class.
        setup = make_setup(diff=True)
        product = make_spiceds_without_init(
            setup=setup, name='spiceds_v001.html', path='/staging/spiceds_v001.html')

        # Empty glob -> [-1] raises IndexError -> fallback branch.
        with patch(f'{_MODULE}.glob.glob', return_value=[]), \
                patch(f'{_MODULE}.compare_files') as compare_files:
            with caplog.at_level(logging.INFO):
                product._compare()

        expected_from = '/root/data/insight_spice/document/spiceds_v002.html'
        compare_files.assert_called_once_with(
            expected_from, '/staging/spiceds_v001.html', '/work', True)

        expected = [
            (logging.WARNING, '-- No other version of spiceds_v001.html has been found.'),
            (logging.WARNING, '-- Comparing with default InSight example.'),
            (logging.INFO, '')]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected
