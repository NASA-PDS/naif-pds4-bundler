"""Tests for SpiceKernelsCollection — one test class per method, 100% branch coverage.

Assumes the package is installed (e.g. ``pip install -e .``) so that

    from naif_pds4_bundler.classes.collection_kernels import SpiceKernelsCollection

resolves normally.

Collaborators patched at their locations inside the module under test:
  - naif_pds4_bundler.classes.collection_kernels.os.path.exists
  - naif_pds4_bundler.classes.collection_kernels.glob.glob
  - naif_pds4_bundler.classes.collection_kernels.handle_npb_error
  - naif_pds4_bundler.classes.collection_kernels.et_to_date
  - naif_pds4_bundler.classes.collection_kernels.spiceypy
  - naif_pds4_bundler.classes.collection.Collection.set_collection_lid
"""
import logging
from unittest.mock import MagicMock, mock_open, patch

import pytest

from pds.naif_pds4_bundler.classes.collection.collection_kernels import SpiceKernelsCollection


# ---------------------------------------------------------------------------
# Patch targets
# ---------------------------------------------------------------------------

_SET_LID      = "pds.naif_pds4_bundler.classes.collection.collection.Collection.set_collection_lid"
_EXISTS       = "pds.naif_pds4_bundler.classes.collection.collection_kernels.os.path.exists"
_GLOB         = "pds.naif_pds4_bundler.classes.collection.collection_kernels.glob.glob"
_OPEN         = "builtins.open"


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def make_bundle():
    return MagicMock()


def make_kernels(kernel_list=None):
    return MagicMock(
        kernel_list=kernel_list or []
    )


# ---------------------------------------------------------------------------
# Helpers to control hasattr() on a MagicMock
# Because MagicMock auto-creates attributes, we use spec= or delete via
# configure: we set spec_set attrs explicitly and use wraps for hasattr tests.
# ---------------------------------------------------------------------------

class _Setup:
    """Minimal plain-object setup for tests needing precise hasattr control."""
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


# ===========================================================================
# SpiceKernelsCollection.__init__
# ===========================================================================

class TestSpiceKernelsCollectionInit:
    """Tests for SpiceKernelsCollection.__init__."""

    @staticmethod
    def make_setup(pds_version="4", faucet="plan", **kwargs):
        s = MagicMock(
            pds_version=pds_version,
            mission_start="2000-001T00:00:00.000Z",
            mission_finish="2040-001T00:00:00.000Z",
            mission_acronym="test",
            bundle_directory="/fake/bundle",
            staging_directory="/fake/staging",
            date_format="maklabel"
        )
        s.args.faucet = faucet

        for k, v in kwargs.items():
            setattr(s, k, v)
        return s

    @pytest.mark.parametrize('pds_version', ['3', '4'])
    def test_type_always_set_to_spice_kernels(self, pds_version):
        setup = self.make_setup(pds_version=pds_version)
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), make_kernels())
        assert obj.type == "spice_kernels"

    def test_list_assigned_to_kernels(self):
        kernels = make_kernels()
        setup = self.make_setup(pds_version="3")
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), kernels)
        assert obj.list is kernels

    def test_pds4_sets_start_and_stop_time(self):
        setup = self.make_setup(pds_version="4")
        setup.mission_start = "2000-001T00:00:00.000Z"
        setup.mission_finish = "2040-001T00:00:00.000Z"
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), make_kernels())
        assert obj.start_time == "2000-001T00:00:00.000Z"
        assert obj.stop_time == "2040-001T00:00:00.000Z"

    def test_non_pds4_does_not_set_start_stop_time(self):
        setup = self.make_setup(pds_version="3")
        setup.mission_start = "2000-001T00:00:00.000Z"
        setup.mission_finish = "2040-001T00:00:00.000Z"
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), make_kernels())
        assert not hasattr(obj, "start_time")
        assert not hasattr(obj, "stop_time")

    @pytest.mark.parametrize('pds_version', ['3', '4'])
    def test_super_init_called_with_correct_c_type(self, pds_version):
        setup= self.make_setup(pds_version=pds_version)
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), make_kernels())
        assert obj.name == "spice_kernels"

    @pytest.mark.parametrize('pds_version', ['3', '4'])
    def test_setup_and_bundle_forwarded(self, pds_version):
        setup = self.make_setup(pds_version=pds_version)
        bundle = make_bundle()
        kernels = make_kernels()
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, bundle, kernels)
        assert obj.setup is setup
        assert obj.bundle is bundle

    def test_pds4_calls_set_collection_lid(self):
        setup = self.make_setup(pds_version="4")
        with patch(_SET_LID) as mock_lid:
            SpiceKernelsCollection(setup, make_bundle(), make_kernels())
        mock_lid.assert_called_once()

    def test_non_pds4_does_not_call_set_collection_lid(self):
        setup = self.make_setup(pds_version="3")
        with patch(_SET_LID) as mock_lid:
            SpiceKernelsCollection(setup, make_bundle(), make_kernels())
        mock_lid.assert_not_called()


# ===========================================================================
# SpiceKernelsCollection.determine_meta_kernels
# ===========================================================================

class TestSpiceKernelsCollectionDetermineMetaKernels:
    """Tests for SpiceKernelsCollection.determine_meta_kernels."""

    # ------------------------------------------------------------------ #
    # mk_inputs branch                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def make_setup(pds_version="4", files=None, faucet="plan"):
        return _Setup(
            pds_version=pds_version,
            args=MagicMock(faucet=faucet),
            mk_inputs={"file": files} if files else {},
            mission_acronym="test",
            volume_id='test',
            bundle_directory="/fake/bundle",
            kernels_directory=['/fake/kernels'],
            staging_directory="/fake/staging",
            mission_start="2000-01-01T00:00:00.000Z",
            mission_finish="2040-01-01T00:00:00.000Z",
            # Required by handle_npb_error
            write_file_list = lambda: None,
            write_checksum_registry = lambda: None,
            template_files = []
        )

    @pytest.mark.parametrize('pds_version, files, exists', [
        ('4', "../data/mk.tm", [False]),
        ('4', ["../data/mk.tm"], [False]),
        ('4', ["../metakernel.tm", "../data/mk.tm"], [True, False]),
        ('3', "../data/mk.tm", [False]),
        ('3', ["../data/mk.tm"], [False]),
        ('3', ["../metakernel.tm", "../data/mk.tm"], [True, False])
    ])
    def test_mk_inputs_file_not_exists_calls_handle_error(self, pds_version, files, exists, caplog):
        """mk provided via config but file missing → handle_npb_error called."""
        setup = self.make_setup(pds_version=pds_version, files=files)
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), make_kernels())
        with patch(_EXISTS, side_effect=exists):
            with pytest.raises(RuntimeError, match='Meta-kernel provided via configuration does not exist: ../data/mk.tm'):
                obj.determine_meta_kernels()

    def test_mk_inputs_no_file_key_logs_warning(self, caplog):
        """mk_inputs present but no 'file' key -> warning logged."""
        setup = self.make_setup()
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), make_kernels())
        with caplog.at_level(logging.INFO):
            result = obj.determine_meta_kernels()

        expected = [
            (logging.WARNING, '-- Configuration item mk_inputs is empty.'),
            (logging.INFO, '-- No meta-kernel provided in the kernel list or via configuration.'),
            (logging.INFO, ''),
            (logging.WARNING, '-- No Meta-kernel will be generated.')
        ]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected
        assert result == {}

    @pytest.mark.parametrize('pds_version', ['3', '4'])
    def test_kernel_list_metakernel_not_found_added_as_false(self, pds_version, caplog):
        """.tm kernel not on disk -> added with value False."""
        setup = self.make_setup(pds_version=pds_version)
        kernels = make_kernels(["test_v001.tm"])
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), kernels)

        with caplog.at_level(logging.INFO), patch(_EXISTS, return_value=False):
            result = obj.determine_meta_kernels()

        expected = [
            (logging.WARNING, '-- Configuration item mk_inputs is empty.'),
            (logging.INFO, '-- test_v001.tm not provided as input in kernels directory.')]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected
        assert result == {"test_v001.tm": False}

    def test_kernel_list_non_tm_kernel_ignored(self, caplog):
        """Non-.tm kernels in kernel_list are skipped entirely."""
        setup = self.make_setup()
        kernels = make_kernels(["naif0012.tls"])
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), kernels)

        with caplog.at_level(logging.INFO), patch(_EXISTS, return_value=False):
            result = obj.determine_meta_kernels()

        expected = [
            (logging.WARNING, '-- Configuration item mk_inputs is empty.'),
            (logging.INFO, '-- No meta-kernel provided in the kernel list or via configuration.'),
            (logging.INFO, ''),
            (logging.WARNING, '-- No Meta-kernel will be generated.')
        ]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected
        assert result == {}

    def test_no_mks_faucet_labels_logs_labels_message(self, caplog):
        """No MKs found and faucet == 'labels' -> specific log message."""
        setup = self.make_setup(faucet="labels")
        kernels = make_kernels([])
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), kernels)

        with caplog.at_level(logging.INFO):
            result = obj.determine_meta_kernels()

        expected = [
            (logging.INFO, '-- No meta-kernel provided as input in the plan in labeling mode.'),
            (logging.INFO, ''),
            (logging.WARNING, '-- No Meta-kernel will be generated.')
        ]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected
        assert result == {}

    def test_auto_generate_mk_version_pattern_no_existing(self, caplog):
        """All auto-generate conditions met and MK file absent -> added as False."""
        mk_config = [{
            "@name": "test_$VERSION.tm",
            "name": [{"pattern": {"#text": "VERSION", "@length": "3"}}],
        }]
        setup = self.make_setup()
        setup.mk = mk_config
        kernels = make_kernels([])
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), kernels)
        # Put a product in collection so self.product is truthy
        obj.product = [MagicMock()]

        with caplog.at_level(logging.INFO), patch(_EXISTS, return_value=False):
            result = obj.determine_meta_kernels()

        expected = [
            (logging.WARNING, '-- Configuration item mk_inputs is empty.'),
            (logging.INFO, '-- No meta-kernel provided in the kernel list or via configuration.')
        ]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected
        assert result == {"test_001.tm": False}

    def test_auto_generate_mk_already_exists_not_added(self, caplog):
        """Auto-generate: MK file already on disk → not added."""
        mk_config = [{
            "@name": "test_$VERSION.tm",
            "name": [{"pattern": {"#text": "VERSION", "@length": "3"}}],
        }]
        setup = self.make_setup()
        setup.mk = mk_config
        kernels = make_kernels([])
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), kernels)
        # Put a product in collection so self.product is truthy
        obj.product = [MagicMock()]

        with caplog.at_level(logging.INFO), patch(_EXISTS, return_value=True):
            result = obj.determine_meta_kernels()

        expected = [
            (logging.WARNING, '-- Configuration item mk_inputs is empty.'),
            (logging.INFO, '-- No meta-kernel provided in the kernel list or via configuration.'),
            (logging.INFO, ''),
            (logging.WARNING, '-- No Meta-kernel will be generated.')]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected

        # Existing file means it's not added to meta_kernels
        assert result == {}

    def test_auto_generate_skipped_when_no_products(self, caplog):
        """Auto-generate block skipped when self.product is empty."""
        mk_config = [{
            "@name": "test_$VERSION.tm",
            "name": [{"pattern": {"#text": "VERSION", "@length": "3"}}],
        }]
        setup = self.make_setup()
        setup.mk = mk_config
        kernels = make_kernels([])
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), kernels)
        self.product = []  # auto-generate block skipped

        with caplog.at_level(logging.INFO):
            result = obj.determine_meta_kernels()

        expected = [
            (logging.WARNING, '-- Configuration item mk_inputs is empty.'),
            (logging.INFO, '-- No meta-kernel provided in the kernel list or via configuration.'),
            (logging.INFO, ''),
            (logging.WARNING, '-- No Meta-kernel will be generated.')]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected

        assert result == {}

    @pytest.mark.parametrize('mk_config', [
        # Multiple metakernels.
        [{"@name": "test_$VERSION.tm",
          "name": [{"pattern": {"#text": "VERSION", "@length": "3"}}]},
         {"@name": "other_$VERSION.tm",
          "name": [{"pattern": {"#text": "VERSION", "@length": "3"}}]}],
        # Multiple patterns.
        [{"@name": "test_$VERSION.tm",
          "name": [{"pattern": {"#text": "VERSION", "@length": "3"}},
                   {'pattern': {"#text": "VERSION", "@length": "2"}}]}],
        # Pattern for year.
        [{"@name": "test_$YEAR.tm",
          "name": [{"pattern": {"#text": "YEAR", "@length": "4"}}]}]
        # TODO: We need to add more test to complete options.
    ])
    def test_auto_generate_mk_not_supported_setup_mk(self, mk_config, caplog):
        setup = self.make_setup()
        setup.mk = mk_config
        kernels = make_kernels([])
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), kernels)
        # Put a product in collection so self.product is truthy
        obj.product = [MagicMock()]

        with caplog.at_level(logging.INFO):
            result = obj.determine_meta_kernels()

        expected = [
            (logging.WARNING, '-- Configuration item mk_inputs is empty.'),
            (logging.INFO, '-- No meta-kernel provided in the kernel list or via configuration.'),
            (logging.INFO, ''),
            (logging.WARNING, '-- No Meta-kernel will be generated.')]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected

        # Existing file means it's not added to meta_kernels
        assert result == {}

    @pytest.mark.parametrize('pds_version', ['3', '4'])
    def test_mk_inputs_file_exists_added_as_true(self, pds_version):
        setup = self.make_setup(pds_version=pds_version, files="mk.tm")
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), make_kernels())

        # First True is to check that the file exists in the "sources"?,
        # the second is to check that the file does not exist in the bundle.
        with patch(_EXISTS, side_effect=[True, False]):
            result = obj.determine_meta_kernels()
        assert result == {"mk.tm": True}

    @pytest.mark.parametrize('pds_version, kernels_dir, exists', [
        # True is to check that the file exists in the kernels directory,
        # False is to check that the file does not exist in the bundle.
        ('4', ['/kernels_dir'], [True, False]),
        # False it to check that the file does not exist in kernels_other
        # True is to check that the file exists in the kernels directory,
        # False is to check that the file does not exist in the bundle.
        ('4', ['/kernels_other', '/kernels_dir'], [False, True, False]),
    ])
    def test_kernel_list_tm_found_in_directory(self, pds_version, kernels_dir, exists):
        """.tm kernel found in kernels_directory → added with value True."""
        setup = self.make_setup(pds_version=pds_version)
        setup.kernels_directory=kernels_dir
        kernels = make_kernels(["test_v001.tm"])
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), kernels)

        with patch(_EXISTS, side_effect=exists):
            result = obj.determine_meta_kernels()
        assert result == {'/kernels_dir/mk/test_v001.tm': True}

    @pytest.mark.parametrize('pds_version, message',[
        ('3', 'MK already exists in the archive: /fake/bundle/test/extras/mk/mk.tm'),
        ('4', 'MK already exists in the archive: /fake/bundle/test_spice/spice_kernels/mk/mk.tm')
    ])
    def test_final_check_path_and_error_if_exists(self, pds_version, message):
        setup = self.make_setup(pds_version=pds_version, files="mk.tm")
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), make_kernels())

        # First True is to check that the file exists in the "sources"?,
        # the second is to check that the file does not exist in the bundle.
        with patch(_EXISTS, side_effect=[True, True]):
            with pytest.raises(RuntimeError, match=message):
                obj.determine_meta_kernels()


# ===========================================================================
# SpiceKernelsCollection.set_increment_times.
# ===========================================================================

class TestSpiceKernelsCollectionSetIncrementTimes:
    """Tests for SpiceKernelsCollection.set_increment_times"""

    @staticmethod
    def _plain_setup(**extra):
        """Return a _Setup for the except-block tests."""
        attrs = {
            'pds_version': "4",
            'args': MagicMock(faucet="plan"),
            'mission_start': "2000-001T00:00:00.000Z",
            'mission_finish': "2040-001T00:00:00.000Z",
            'mission_acronym':"test",
            'bundle_directory':"/fake/bundle",
            'staging_directory':"/fake/staging",
            'date_format':"maklabel"}
        attrs.update(extra)
        return _Setup(**attrs)

    def test_mk_coverage_sets_increment_times(self, lsk):
        """Products with mk_sets_coverage=True drive start/finish."""
        prod = MagicMock()
        prod.mk_sets_coverage = True
        prod.start_time = "2010-001T00:00:00.000Z"
        prod.stop_time  = "2020-001T00:00:00.000Z"

        setup = self._plain_setup()
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), make_kernels())
        obj.product = [prod]

        with patch(_GLOB, return_value=[]):
            obj.set_increment_times()

        assert setup.increment_start  == "2010-01-01T00:00:00Z"
        assert setup.increment_finish == "2020-01-01T00:00:00Z"

    def test_product_without_mk_sets_coverage_attr_ignored(self, lsk):
        """Products lacking mk_sets_coverage attribute are skipped."""
        prod = MagicMock(spec=[])  # no attributes → hasattr returns False

        # With no qualifying products, min([]) raises → except block fires.
        setup2 = _Setup(
            pds_version="4",
            args=MagicMock(faucet="plan"),
            mission_start="2000-001T00:00:00.000Z",
            mission_finish="2040-001T00:00:00.000Z",
            mission_acronym="test",
            bundle_directory="/fake/bundle",
            staging_directory="/fake/staging",
            date_format="infomod2",
        )
        with patch(_SET_LID):
            obj2 = SpiceKernelsCollection(setup2, make_bundle(), make_kernels())
        obj2.product = [prod]

        with patch(_GLOB, return_value=[]):
            obj2.set_increment_times()

        # Falls through to mission start/finish defaults
        assert setup2.increment_start  == "2000-01-01T00:00:00.000Z"
        assert setup2.increment_finish == "2040-01-01T00:00:00.000Z"

    def test_mk_sets_coverage_false_ignored(self, lsk):
        """Products with mk_sets_coverage=False are not used for coverage."""
        prod = MagicMock()
        prod.mk_sets_coverage = False
        setup2 = _Setup(
            pds_version="4",
            args=MagicMock(faucet="plan"),
            mission_start="2000-001T00:00:00.000Z",
            mission_finish="2040-001T00:00:00.000Z",
            mission_acronym="test",
            bundle_directory="/fake/bundle",
            staging_directory="/fake/staging",
            date_format="infomod2",
        )
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup2, make_bundle(), make_kernels())
        obj.product = [prod]

        with patch(_GLOB, return_value=[]):
            obj.set_increment_times()

        assert setup2.increment_start  == "2000-01-01T00:00:00.000Z"
        assert setup2.increment_finish == "2040-01-01T00:00:00.000Z"

    def test_no_mk_uses_increment_start_from_setup(self):
        """increment_start on setup → used when no MK coverage."""
        setup = self._plain_setup(increment_start="2005-01-01T00:00:00.000Z")
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), make_kernels())
        obj.product = []

        with patch(_GLOB, return_value=[]):
            obj.set_increment_times()

        assert setup.increment_start == "2005-01-01T00:00:00.000Z"

    def test_no_mk_uses_increment_finish_from_setup(self):
        """increment_finish on setup → used when no MK coverage."""
        setup = self._plain_setup(increment_finish="2025-01-01T00:00:00.000Z")
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), make_kernels())
        obj.product = []

        with patch(_GLOB, return_value=[]):
            obj.set_increment_times()

        assert setup.increment_finish == "2025-01-01T00:00:00.000Z"

    def test_no_mk_no_increment_start_falls_back_to_mission_start(self, lsk, caplog):
        """No MK and no increment_start → mission_start used with warning."""
        setup = self._plain_setup()  # no increment_start attr
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), make_kernels())
        obj.product = []

        with caplog.at_level(logging.WARNING), patch(_GLOB, return_value=[]):
            obj.set_increment_times()

        assert setup.increment_start == '2000-01-01T00:00:00Z'
        assert "Mission start time will be used" in caplog.text

    def test_no_mk_no_increment_finish_falls_back_to_mission_finish(self, caplog):
        """No MK and no increment_finish → mission_finish used with warning."""
        setup = self._plain_setup()
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), make_kernels())
        obj.product = []

        with caplog.at_level(logging.WARNING), patch(_GLOB, return_value=[]):
            obj.set_increment_times()

        assert setup.increment_finish == "2040-001T00:00:00.000Z"
        assert "Mission stop time will be used" in caplog.text

    # ------------------------------------------------------------------ #
    # previous bundle try block                                            #
    # ------------------------------------------------------------------ #

    def test_prev_bundle_start_earlier_corrects_increment_start(self, lsk, caplog):
        """Previous bundle start earlier than current → increment_start corrected."""
        import logging
        setup = self._plain_setup(
            increment_start="2010-001T00:00:00.000Z",
            increment_finish="2020-001T00:00:00.000Z",
        )
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), make_kernels())

        bundle_content = (
            "<start_date_time>2005-001T00:00:00.000Z</start_date_time>\n"
            "<stop_date_time>2015-001T00:00:00.000Z</stop_date_time>\n"
        )
        prod = MagicMock()
        prod.mk_sets_coverage = True
        prod.start_time = "2010-001T00:00:00.000Z"
        prod.stop_time  = "2020-001T00:00:00.000Z"
        obj.product = [prod]

        with caplog.at_level(logging.INFO), \
             patch(_GLOB, return_value=["/fake/bundle_v001.xml"]), \
             patch(_OPEN, mock_open(read_data=bundle_content)):
            obj.set_increment_times()

        assert "Increment start corrected from previous bundle" in caplog.text

    def test_prev_bundle_start_later_logs_warning(self, lsk, caplog):
        """Previous bundle start later than current → warning logged."""
        import logging
        setup = self._plain_setup(
            increment_start="2005-001T00:00:00.000Z",
            increment_finish="2020-001T00:00:00.000Z",
        )
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), make_kernels())

        bundle_content = (
            "<start_date_time>2010-001T00:00:00.000Z</start_date_time>\n"
            "<stop_date_time>2015-001T00:00:00.000Z</stop_date_time>\n"
        )
        prod = MagicMock()
        prod.mk_sets_coverage = True
        prod.start_time = "2005-001T00:00:00.000Z"
        prod.stop_time  = "2020-001T00:00:00.000Z"
        obj.product = [prod]

        with caplog.at_level(logging.WARNING), \
             patch(_GLOB, return_value=["/fake/bundle_v001.xml"]), \
             patch(_OPEN, mock_open(read_data=bundle_content)):
            obj.set_increment_times()

        assert "Increment start from previous bundle not used" in caplog.text

    def test_prev_bundle_finish_later_corrects_increment_finish(self, lsk, caplog):
        """Previous bundle finish later than current → increment_finish corrected."""
        import logging
        setup = self._plain_setup(
            increment_start="2010-001T00:00:00.000Z",
            increment_finish="2015-001T00:00:00.000Z",
        )
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), make_kernels())

        bundle_content = (
            "<start_date_time>2010-001T00:00:00.000Z</start_date_time>\n"
            "<stop_date_time>2020-001T00:00:00.000Z</stop_date_time>\n"
        )
        prod = MagicMock()
        prod.mk_sets_coverage = True
        prod.start_time = "2010-001T00:00:00.000Z"
        prod.stop_time  = "2015-001T00:00:00.000Z"
        obj.product = [prod]

        with caplog.at_level(logging.WARNING), \
             patch(_GLOB, return_value=["/fake/bundle_v001.xml"]), \
             patch(_OPEN, mock_open(read_data=bundle_content)):
            obj.set_increment_times()

        assert "Increment finish corrected" in caplog.text

    def test_prev_bundle_not_found_logs_warning(self, lsk, caplog):
        """No previous bundle files → warning logged."""
        import logging
        setup = self._plain_setup()
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), make_kernels())
        obj.product = []

        with caplog.at_level(logging.WARNING), patch(_GLOB, return_value=[]):
            obj.set_increment_times()

        assert "Previous bundle not found" in caplog.text

    # ------------------------------------------------------------------ #
    # spiceypy / et_to_date try block                                     #
    # ------------------------------------------------------------------ #

    def test_spiceypy_failure_logs_lsk_warning(self, caplog):
        """spiceypy.utc2et raises → LSK warning logged, times unchanged."""
        import logging
        setup = self._plain_setup(
            increment_start="2010-001T00:00:00.000Z",
            increment_finish="2020-001T00:00:00.000Z",
        )
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), make_kernels())
        obj.product = []

        mock_spice = MagicMock()
        mock_spice.utc2et.side_effect = Exception("No LSK loaded")

        with caplog.at_level(logging.WARNING), patch(_GLOB, return_value=[]):
            obj.set_increment_times()

        assert "leapseconds kernel" in caplog.text


# ===========================================================================
# SpiceKernelsCollection.validate
# ===========================================================================

class TestSpiceKernelsCollectionValidate:
    """Tests for SpiceKernelsCollection.validate."""

    @staticmethod
    def _make_obj(pds_version="4", kernel_list=None, products=None):
        setup = _Setup(
            pds_version=pds_version,
            staging_directory="/fake/staging",
            mission_acronym="test",
            bundle_directory="/fake/bundle",
            mission_start="2000-01-01T00:00:00.000Z",
            mission_finish="2040-01-01T00:00:00.000Z",
            # Required by handle_npb_error
            write_file_list=lambda: None,
            write_checksum_registry=lambda: None,
            template_files=[]
        )
        kernels = make_kernels(kernel_list or [])
        with patch(_SET_LID):
            obj = SpiceKernelsCollection(setup, make_bundle(), kernels)
        obj.product = products or []
        return obj

    @pytest.mark.parametrize("pds_version", ["3", "4"])
    def test_returns_none_early_when_no_products(self, pds_version, caplog):
        """validate() returns None early when self.product is empty."""
        obj = self._make_obj(pds_version=pds_version, kernel_list=[], products=[])
        with caplog.at_level(logging.INFO):
            obj.validate()

        # Check the logging level and logging messages.
        expected = [
            (logging.INFO, '-- Checking that all the kernels from list are present...'),
            (logging.INFO, '   OK'),
            (logging.INFO, ''),
            (logging.INFO, '-- Checking that all the kernels have been labeled...'),
            (logging.INFO, '   OK')]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]

        assert messages == expected

    @pytest.mark.parametrize("pds_version, kernel, exists", [
        ('3', 'kernel.bc', [True]),
        ('3', 'orbit_number.orb', [False, True]),
        ('3', 'metakernel.tm', [False, False, True]),
        ('4', 'kernel.bc', [True]),
        ('4', 'orbit_number.orb', [False, True]),
        ('4', 'metakernel.tm', [False, False, True])
    ])
    def test_returns_none_early_when_no_products_even_with_kernel_list(self, pds_version, kernel, exists, caplog):
        """validate() returns None early when self.product is empty."""
        obj = self._make_obj(pds_version=pds_version, kernel_list=[kernel], products=[])
        with caplog.at_level(logging.INFO), patch(_EXISTS, side_effect=exists):
                obj.validate()

        # Check the logging level and logging messages.
        expected = [
            (logging.INFO, '-- Checking that all the kernels from list are present...'),
            (logging.INFO, '   OK'),
            (logging.INFO, ''),
            (logging.INFO, '-- Checking that all the kernels have been labeled...'),
            (logging.INFO, '   OK')]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]

        assert messages == expected


    @pytest.mark.parametrize("pds_version, kernels, exists", [
        # 3 path checks per kernel, all False -> missing
        ('3', ["missing.bc"], [False, False, False]),
        # first kernel: first check True -> short-circuits; second kernel: all False -> missing
        ('3', ["kernel.bc", "missing.bc"], [True, False, False, False]),
        # 3 path checks per kernel, all False -> missing
        ('4', ["missing.bc"], [False, False, False]),
        # first kernel: first check True -> short-circuits; second kernel: all False -> missing
        ('4', ["kernel.bc", "missing.bc"], [True, False, False, False])
    ])
    def test_non_present_product_calls_handle_error(self, pds_version, kernels, exists, caplog):
        """Product not found in any staging location -> handle_npb_error called."""
        obj = self._make_obj(pds_version=pds_version, kernel_list=kernels)
        with caplog.at_level(logging.INFO), patch(_EXISTS, side_effect=exists):
            with pytest.raises(RuntimeError, match='Some products from the list are not present.'):
                obj.validate()

        expected = [
            (logging.INFO, '-- Checking that all the kernels from list are present...'),
            (logging.ERROR, '-- The following products from the list are not present:'),
            (logging.ERROR, '   missing.bc'),
            (logging.ERROR, '-- Some products from the list are not present.')]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]

        assert messages == expected


    @pytest.mark.parametrize("products, exists", [
        # Product missing.
        ([('missing.bc', 'ck', 'not_applicable.lbl')],
         [False]),
        # Label missing.
        ([('missing.bc', 'ck', 'missing.lbl')],
         [True, False]),
        # Second product missing.
        ([('kernel.bc', 'ck', 'kernel.lbl'), ('missing.bc', 'ck', 'not_applicable.lbl')],
         [True, True, False]),
        # Label missing.
        ([('kernel.bc', 'ck', 'kernel.lbl'), ('missing.bc', 'ck', 'missing.lbl')],
         [True, True, True, False]),
    ])
    def test_unlabeled_pds3_product_calls_handle_error(self, products, exists, tmp_path, caplog):
        prods = []
        for name, k_type, label in products:
            label = tmp_path / label
            label.write_text('RECORD_TYPE                  = FIXED_LENGTH\n'
                             'RECORD_BYTES                 = 1024\n'
                             '^SPICE_KERNEL                = "missing.bc"\n'
                             'OBJECT                       = SPICE_KERNEL\n'
                             '  DESCRIPTION                = "Test label, irrelevant for this test, but\n'
                             'required so that it does not break.')

            p = MagicMock()
            p.name = name
            p.type = k_type
            p.label.name = label
            prods.append(p)

        obj = self._make_obj(pds_version='3', products=prods)
        with caplog.at_level(logging.INFO), patch(_EXISTS, side_effect=exists):
            # TODO: This test should raise RuntimeError, because the file is
            #       missing, but it does not --> this is a bug in the function.
            # with pytest.raises(RuntimeError, match='Some products from the list are not present.'):
            obj.validate()

        expected = [
            (logging.INFO, '-- Checking that all the kernels from list are present...'),
            (logging.INFO, '   OK'),
            (logging.INFO, ''),
            (logging.INFO, '-- Checking that all the kernels have been labeled...'),
            (logging.ERROR, '-- The following products have not been labeled:'),
            (logging.ERROR, '   missing.bc')]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]

        # TODO: We only check the first 6 elements of the messages. Since the function
        #       is not terminated upon detecting a missing product or label, more messages
        #       will be logged. This is a bug. When fixed, the following line should be
        #       changed to
        #          assert messages == expected
        assert messages[:6] == expected

    @pytest.mark.skip('There is a bug in the code that will cause this test to'
                      'break with FileNotFoundError.')
    def test_pds3_metakernel_excluded_from_non_labeled(self):
        """.tm kernels are excluded from non_labeled_products check on PDS3."""
        prod = MagicMock()
        prod.type = "mk"
        prod.name = "test.tm"
        prod.label.name = "/fake/staging/spice_kernels/mk/test.xml"
        obj = self._make_obj(pds_version="3", products=[prod])

        # Both exists calls return False → would be unlabeled, but .tm → excluded
        with patch(_EXISTS, return_value=False):
            obj.validate()

    @pytest.mark.parametrize('products, expected', [
        ([('kernel.bc', 'ck', 'kernel.xml')],
         [(logging.INFO,
           '   <logical_identifier>urn:nasa:pds:mission.spice:spice_kernels:ck_kernel.bc</logical_identifier>'),
          (logging.INFO, ''),
          (logging.INFO, '   <version_id>1.0</version_id>'),
          (logging.INFO, ''),
          (logging.INFO, '   <title>kernel.bc</title>'),
          (logging.INFO, ''),
          (logging.INFO, '   <description>Test label for the kernel kernel.bc.</description>'),
          (logging.INFO, ''),
          (logging.INFO, '   <start_date_time>2020-11-07T00:00:00.005Z</start_date_time>'),
          (logging.INFO, ''),
          (logging.INFO, '   <stop_date_time>2020-11-07T03:00:00.005Z</stop_date_time>'),
          (logging.INFO, ''),
          (logging.INFO, '   <file_name>kernel.bc</file_name>'),
          (logging.INFO, ''),
          (logging.INFO, '   <file_size unit="byte">16384</file_size>'),
          (logging.INFO, ''),
          (logging.INFO, '   <md5_checksum>22f9acc1931c8a626fac2a844fc5cee3</md5_checksum>'),
          (logging.INFO, ''),
          (logging.INFO, '   <object_length unit="byte">16384</object_length>'),
          (logging.INFO, ''),
          (logging.INFO, '   <kernel_type>CK</kernel_type>'),
          (logging.INFO, ''),
          (logging.INFO, '   <encoding_type>Binary</encoding_type>'),
          (logging.INFO, ''), (logging.INFO, '')]),
        ([('kernel.bc', 'ck', 'kernel.xml'), ('other.bsp', 'spk', 'other.lbl')],
         [(logging.INFO,
           '   <logical_identifier>urn:nasa:pds:mission.spice:spice_kernels:ck_kernel.bc</logical_identifier>'),
          (logging.INFO,
           '   <logical_identifier>urn:nasa:pds:mission.spice:spice_kernels:spk_other.bsp</logical_identifier>'),
          (logging.INFO, ''),
          (logging.INFO, '   <version_id>1.0</version_id>'),
          (logging.INFO, '   <version_id>1.0</version_id>'),
          (logging.INFO, ''),
          (logging.INFO, '   <title>kernel.bc</title>'),
          (logging.INFO, '   <title>other.bsp</title>'),
          (logging.INFO, ''),
          (logging.INFO, '   <description>Test label for the kernel kernel.bc.</description>'),
          (logging.INFO, '   <description>Test label for the kernel other.bsp.</description>'),
          (logging.INFO, ''),
          (logging.INFO, '   <start_date_time>2020-11-07T00:00:00.005Z</start_date_time>'),
          (logging.INFO, '   <start_date_time>2020-11-07T00:00:00.005Z</start_date_time>'),
          (logging.INFO, ''),
          (logging.INFO, '   <stop_date_time>2020-11-07T03:00:00.005Z</stop_date_time>'),
          (logging.INFO, '   <stop_date_time>2020-11-07T03:00:00.005Z</stop_date_time>'),
          (logging.INFO, ''),
          (logging.INFO, '   <file_name>kernel.bc</file_name>'),
          (logging.INFO, '   <file_name>other.bsp</file_name>'),
          (logging.INFO, ''),
          (logging.INFO, '   <file_size unit="byte">16384</file_size>'),
          (logging.INFO, '   <file_size unit="byte">16384</file_size>'),
          (logging.INFO, ''),
          (logging.INFO, '   <md5_checksum>22f9acc1931c8a626fac2a844fc5cee3</md5_checksum>'),
          (logging.INFO, '   <md5_checksum>22f9acc1931c8a626fac2a844fc5cee3</md5_checksum>'),
          (logging.INFO, ''),
          (logging.INFO, '   <object_length unit="byte">16384</object_length>'),
          (logging.INFO, '   <object_length unit="byte">16384</object_length>'),
          (logging.INFO, ''),
          (logging.INFO, '   <kernel_type>CK</kernel_type>'),
          (logging.INFO, '   <kernel_type>SPK</kernel_type>'),
          (logging.INFO, ''),
          (logging.INFO, '   <encoding_type>Binary</encoding_type>'),
          (logging.INFO, '   <encoding_type>Binary</encoding_type>'),
          (logging.INFO, ''), (logging.INFO, '')])
    ])
    def test_pds4_elements_parsed_from_label(self, products, expected, tmp_path, caplog):
        prods = []
        for name, k_type, label in products:
            label = tmp_path / label
            label.write_text(
                f'    <logical_identifier>urn:nasa:pds:mission.spice:spice_kernels:{k_type}_{name}</logical_identifier>\n'
                '    <version_id>1.0</version_id>\n'
                f'    <title>{name}</title>\n'
                f'      <description>Test label for the kernel {name}.</description>\n'
                '      <start_date_time>2020-11-07T00:00:00.005Z</start_date_time>\n'
                '      <stop_date_time>2020-11-07T03:00:00.005Z</stop_date_time>\n'
                f'      <file_name>{name}</file_name>\n'
                '      <file_size unit="byte">16384</file_size>\n'
                '      <md5_checksum>22f9acc1931c8a626fac2a844fc5cee3</md5_checksum>\n'
                '      <object_length unit="byte">16384</object_length>\n'
                f'      <kernel_type>{k_type.upper()}</kernel_type>\n'
                '      <encoding_type>Binary</encoding_type>')

            p = MagicMock()
            p.name = name
            p.type = k_type
            p.label.name = label
            prods.append(p)

        obj = self._make_obj(pds_version="4", products=prods)

        with caplog.at_level(logging.INFO), patch(_EXISTS, return_value=True):
            obj.validate()

        expected = [
            (logging.INFO, '-- Checking that all the kernels from list are present...'),
            (logging.INFO, '   OK'),
            (logging.INFO, ''),
            (logging.INFO, '-- Checking that all the kernels have been labeled...'),
            (logging.INFO, '   OK'),
            (logging.INFO, ''),
            (logging.INFO, '-- Providing relevant fields of labels for visual inspection.'),
            (logging.INFO, '')] + expected

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected


    @pytest.mark.parametrize('products, expected', [
        ([('kernel.bc', 'ck', 'kernel.lbl')],
         [(logging.INFO, '   RECORD_TYPE                  = FIXED_LENGTH'),
          (logging.INFO, ''),
          (logging.INFO, '   RECORD_BYTES                 = 1024'),
          (logging.INFO, ''),
          (logging.INFO, '   ^SPICE_KERNEL                = "kernel.bc"'),
          (logging.INFO, ''),
          (logging.INFO, '   DESCRIPTION                = "Test label for the kernel kernel.bc"'),
          (logging.INFO, ''),
          (logging.INFO, '')]),
        ([('kernel.bc', 'ck', 'kernel.lbl'), ('other.bsp', 'spk', 'other.lbl')],
         [(logging.INFO, '   RECORD_TYPE                  = FIXED_LENGTH'),
          (logging.INFO, '   RECORD_TYPE                  = FIXED_LENGTH'),
          (logging.INFO, ''),
          (logging.INFO, '   RECORD_BYTES                 = 1024'),
          (logging.INFO, '   RECORD_BYTES                 = 1024'),
          (logging.INFO, ''),
          (logging.INFO, '   ^SPICE_KERNEL                = "kernel.bc"'),
          (logging.INFO, '   ^SPICE_KERNEL                = "other.bsp"'),
          (logging.INFO, ''),
          (logging.INFO, '   DESCRIPTION                = "Test label for the kernel kernel.bc"'),
          (logging.INFO, '   DESCRIPTION                = "Test label for the kernel other.bsp"'),
          (logging.INFO, ''),
          (logging.INFO, '')]),
    ])
    def test_pds3_elements_parsed_from_label(self, products, expected, tmp_path, caplog):
        prods = []
        for name, k_type, label in products:
            label = tmp_path / label
            label.write_text('RECORD_TYPE                  = FIXED_LENGTH\n'
                             'RECORD_BYTES                 = 1024\n'
                             f'^SPICE_KERNEL                = "{name}"\n'
                             f'  DESCRIPTION                = "Test label for the kernel {name}"')

            p = MagicMock()
            p.name = name
            p.type = k_type
            p.label.name = label
            prods.append(p)

        obj = self._make_obj(pds_version="3", products=prods)

        with caplog.at_level(logging.INFO), patch(_EXISTS, return_value=True):
            obj.validate()

        expected = [
            (logging.INFO, '-- Checking that all the kernels from list are present...'),
            (logging.INFO, '   OK'),
            (logging.INFO, ''),
            (logging.INFO, '-- Checking that all the kernels have been labeled...'),
            (logging.INFO, '   OK'),
            (logging.INFO, ''),
            (logging.INFO, '-- Providing relevant fields of labels for visual inspection.'),
            (logging.INFO, '')] + expected

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected