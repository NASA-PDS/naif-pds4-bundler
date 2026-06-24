"""Unit tests for MetaKernelProduct class."""
import copy
import logging
import os
import re
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from pds.naif_pds4_bundler.classes.product.product_metakernel import MetaKernelProduct

# ---------------------------------------------------------------------------
# Module path used to target patches
# ---------------------------------------------------------------------------

_MODULE = "pds.naif_pds4_bundler.classes.product.product_metakernel"

# ---------------------------------------------------------------------------
# Shared MK configuration structure (mirrors XML-parsed setup.mk entries)
# ---------------------------------------------------------------------------

MK_SETUP = {
    "@name": "insight_v$VERSION.tm",
    "name": [{"pattern": {"#text": "VERSION", "@length": "2"}}],
    "grammar": {
        "pattern": ["naif0012.tls", "pck00010.tpc"],
    },
    "metadata": {
        "description": "Test meta-kernel description.",
        "data": "",
    },
}

# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

def make_setup(
    pds_version="4",
    staging_directory=None,
    bundle_directory=None,
    working_directory=None,
    templates_directory=None,
    mission_acronym="insight",
    mission_name="InSight",
    spice_name="INSIGHT",
    institution="NAIF/JPL",
    producer_name="John Doe",
    logical_identifier="urn:nasa:pds:insight_spice",
    date_format="UTC",
    mission_start="2018-01-01T00:00:00Z",
    mission_finish="2023-01-01T00:00:00Z",
    increment_start=None,
    increment_finish=None,
    eol_mk="\n",
    increment=False,
    diff=False,
    mk_list=None,
):
    """Return a minimal mock Setup object for MetaKernelProduct tests."""
    setup = MagicMock()
    setup.pds_version = pds_version
    setup.staging_directory = staging_directory or "/staging"
    setup.bundle_directory = bundle_directory or "/bundle"
    setup.working_directory = working_directory or "/work"
    setup.templates_directory = templates_directory or "/templates"
    setup.mission_acronym = mission_acronym
    setup.mission_name = mission_name
    setup.spice_name = spice_name
    setup.institution = institution
    setup.producer_name = producer_name
    setup.logical_identifier = logical_identifier
    setup.date_format = date_format
    setup.mission_start = mission_start
    setup.mission_finish = mission_finish
    setup.eol_mk = eol_mk
    setup.increment = increment
    setup.diff = diff
    # Deep-copy the shared MK_SETUP so a test that mutates self.mk_setup (e.g.
    # write_product / get_description writing back "&value") cannot leak that
    # mutation into another test through the module-level dict.
    setup.mk = mk_list if mk_list is not None else [copy.deepcopy(MK_SETUP)]

    setup.args = MagicMock()
    setup.args.silent = True
    setup.args.verbose = False
    setup.args.debug = True  # prevents interrupt_to_update stdin prompt
    setup.args.checksum = False

    # Provide re_config and kernel_list_config so get_description works for
    # the default MK name "insight_v<N>.tm" without needing an extra mock.
    _mk_pattern = r"insight_v\d+\.tm"
    setup.re_config = [re.compile(_mk_pattern)]
    setup.kernel_list_config = {
        _mk_pattern: {
            "@pattern": _mk_pattern,
            "description": "Test InSight SPICE meta-kernel.",
        }
    }

    # These attributes should be absent by default so hasattr() returns False.
    del setup.secondary_missions
    del setup.creation_date_time
    del setup.mk_setup

    if increment_start is not None:
        setup.increment_start = increment_start
    else:
        del setup.increment_start

    if increment_finish is not None:
        setup.increment_finish = increment_finish
    else:
        del setup.increment_finish

    return setup


def make_collection(missions=None, observers=None, targets=None):
    """Return a minimal mock SPICE Kernels Collection object."""
    collection = MagicMock()
    collection.get_mission_and_observer_and_target.return_value = (
        missions or ["InSight"],
        observers or ["INSIGHT"],
        targets or ["MARS"],
    )
    return collection


def base_init_patches():
    """Return a fresh list of patches that isolate ``__init__`` collaborators.

    Every test that constructs a real ``MetaKernelProduct`` needs the same heavy
    collaborators stubbed out (directory creation, date, kernel listing,
    write/coverage/compare, the base ``Product.__init__`` and the PDS4 label).
    Returning a fresh list on each call keeps the patch objects single-use.

    Tests that need to assert on one of these collaborators can enter an extra
    ``patch`` for it *after* this set; the later patch shadows the default one.
    """
    return [
        patch(f"{_MODULE}.safe_make_directory"),
        patch(f"{_MODULE}.current_date", return_value="2024-01-01"),
        patch(f"{_MODULE}.mk_to_list", return_value=[]),
        patch(f"{_MODULE}.MetaKernelProduct.write_product"),
        patch(f"{_MODULE}.MetaKernelProduct.coverage"),
        patch(f"{_MODULE}.MetaKernelProduct.compare"),
        patch(f"{_MODULE}.shutil.copy2"),
        patch(f"{_MODULE}.Product.__init__", return_value=None),
        patch(f"{_MODULE}.MetaKernelPDS4Label", return_value=MagicMock()),
    ]


# ---------------------------------------------------------------------------
# Utility: build a fully-constructed MetaKernelProduct via __init__
# ---------------------------------------------------------------------------

def build_product(
    tmp_path,
    name="insight_v01.tm",
    pds_version="4",
    user_input=False,
    extra_setup_kwargs=None,
):
    """Construct a real MetaKernelProduct with all heavy collaborators mocked.

    Returns (product, setup, collection).
    """
    extra_setup_kwargs = extra_setup_kwargs or {}

    staging = str(tmp_path / "staging")
    bundle = str(tmp_path / "bundle")
    work = str(tmp_path / "work")
    templates = str(tmp_path / "templates")
    os.makedirs(staging, exist_ok=True)
    os.makedirs(work, exist_ok=True)
    os.makedirs(templates, exist_ok=True)

    # Create a minimal template so write_product's open() call works.
    template_path = os.path.join(templates, "template_metakernel.tm")
    Path(template_path).write_text("KPL/MK\n$KERNELS_IN_METAKERNEL\n", encoding="utf-8")

    setup = make_setup(
        pds_version=pds_version,
        staging_directory=staging,
        bundle_directory=bundle,
        working_directory=work,
        templates_directory=templates,
        **extra_setup_kwargs,
    )

    collection = make_collection()

    # For user_input=True, the source file must exist on disk.
    if user_input:
        src = str(tmp_path / name)
        Path(src).write_text("KPL/MK\n", encoding="utf-8")
        kernel_arg = src
    else:
        kernel_arg = name

    with ExitStack() as stack:
        for p in base_init_patches():
            stack.enter_context(p)
        product = MetaKernelProduct(setup, kernel_arg, collection, user_input=user_input)

    return product, setup, collection


# ===========================================================================
# MetaKernelProduct.__init__
# ===========================================================================

class TestMetaKernelProductInit:
    """Tests for MetaKernelProduct.__init__."""

    # ------------------------------------------------------------------
    # Shared helpers for tests that need setup mutation before construction
    # ------------------------------------------------------------------

    @staticmethod
    def _setup_dirs(tmp_path):
        """Create standard staging/bundle/work/templates dirs and MK template.

        Returns (staging, bundle, work, templates) as strings.
        """
        staging = str(tmp_path / "staging")
        bundle = str(tmp_path / "bundle")
        work = str(tmp_path / "work")
        templates = str(tmp_path / "templates")
        for d in (staging, work, templates):
            os.makedirs(d, exist_ok=True)
        Path(os.path.join(templates, "template_metakernel.tm")).write_text(
            "KPL/MK\n$KERNELS_IN_METAKERNEL\n", encoding="utf-8"
        )
        return staging, bundle, work, templates

    def _make_product(self, tmp_path, name="insight_v01.tm", pds_version="4",
                      mk_list=None, extra_setup_attrs=None,
                      extra_patches=None):
        """Build a MetaKernelProduct, optionally mutating setup after make_setup.

        extra_setup_attrs: dict of {attr: value} applied with setattr after
                           make_setup (useful for re-adding deleted attrs).
        extra_patches: list of additional context managers to enter.
        """
        staging, bundle, work, templates = self._setup_dirs(tmp_path)
        setup = make_setup(
            pds_version=pds_version,
            staging_directory=staging,
            bundle_directory=bundle,
            working_directory=work,
            templates_directory=templates,
            mk_list=mk_list,
        )
        for attr, value in (extra_setup_attrs or {}).items():
            setattr(setup, attr, value)
        collection = make_collection()
        all_patches = base_init_patches() + (extra_patches or [])
        with ExitStack() as stack:
            for p in all_patches:
                stack.enter_context(p)
            product = MetaKernelProduct(setup, name, collection)
        return product, setup

    @pytest.mark.parametrize("pds_version, subdir, kernelpath", [
        ("4", "spice_kernels", ".."),
        ("3", "extras", "./data"),
    ])
    def test_collection_path_and_kernelpath_by_pds_version(
            self, tmp_path, pds_version, subdir, kernelpath):
        product, setup, _ = build_product(tmp_path, pds_version=pds_version)
        assert product.collection_path == os.path.join(setup.staging_directory, subdir) + os.sep
        assert product.KERNELPATH == kernelpath

    def test_name_and_version_parsed_from_kernel_arg(self, tmp_path):
        product, _, _ = build_product(tmp_path, name="insight_v01.tm")
        assert product.name == "insight_v01.tm"
        assert product.version == "01"

    def test_setup_attributes_copied_to_product(self, tmp_path):
        product, setup, _ = build_product(tmp_path)
        assert product.AUTHOR == setup.producer_name
        assert product.SPICE_NAME == setup.spice_name
        assert product.INSTITUTION == setup.institution
        assert product.file_format == "Character"
        assert product.new_product is True
        assert product.PDS4_MISSION_NAME == setup.mission_name

    def test_pds4_mission_name_with_one_secondary_mission(self, tmp_path):
        # Re-add secondary_missions as a real list of one entry.
        product, _ = self._make_product(
            tmp_path,
            extra_setup_attrs={"secondary_missions": ["MEX"]},
        )
        assert product.PDS4_MISSION_NAME == "InSight and MEX"

    def test_user_input_true_copies_file(self, tmp_path):
        staging, bundle, work, templates = self._setup_dirs(tmp_path)
        src = str(tmp_path / "insight_v01.tm")
        Path(src).write_text("KPL/MK\n", encoding="utf-8")

        setup = make_setup(staging_directory=staging, bundle_directory=bundle,
                           working_directory=work, templates_directory=templates)
        collection = make_collection()

        with ExitStack() as stack:
            for p in base_init_patches():
                stack.enter_context(p)
            # Shadow the default copy2 patch with a mock we can assert on.
            mock_copy = stack.enter_context(patch(f"{_MODULE}.shutil.copy2"))
            MetaKernelProduct(setup, src, collection, user_input=True)

        mock_copy.assert_called_once()

    def test_user_input_false_calls_write_product(self, tmp_path):
        staging, bundle, work, templates = self._setup_dirs(tmp_path)
        setup = make_setup(staging_directory=staging, bundle_directory=bundle,
                           working_directory=work, templates_directory=templates)
        collection = make_collection()

        with ExitStack() as stack:
            for p in base_init_patches():
                stack.enter_context(p)
            # Shadow the default write_product patch with a mock we can assert on.
            mock_write = stack.enter_context(
                patch(f"{_MODULE}.MetaKernelProduct.write_product")
            )
            MetaKernelProduct(setup, "insight_v01.tm", collection, user_input=False)

        mock_write.assert_called_once()

    def test_init_end_to_end_renders_metakernel_to_disk(self, tmp_path):
        # Integration-style smoke test: unlike the other __init__ tests, this
        # one does NOT stub write_product, so __init__ actually renders the MK
        # template to a real file on disk.
        staging, bundle, work, templates = self._setup_dirs(tmp_path)
        # write_product opens the output path directly, so the nested mk
        # directory must exist (safe_make_directory only creates one level).
        os.makedirs(os.path.join(staging, "spice_kernels", "mk"), exist_ok=True)
        setup = make_setup(staging_directory=staging, bundle_directory=bundle,
                           working_directory=work, templates_directory=templates)
        collection = make_collection()
        collection.product = []

        with (
            patch(f"{_MODULE}.safe_make_directory"),
            patch(f"{_MODULE}.current_date", return_value="2024-01-01"),
            patch(f"{_MODULE}.mk_to_list", return_value=[]),
            patch(f"{_MODULE}.MetaKernelProduct.coverage"),
            patch(f"{_MODULE}.Product.__init__", return_value=None),
            patch(f"{_MODULE}.MetaKernelPDS4Label", return_value=MagicMock()),
            patch(f"{_MODULE}.get_latest_kernel", return_value=[]),
        ):
            product = MetaKernelProduct(setup, "insight_v01.tm", collection)

        # The rendered file exists in the staging mk directory and starts with
        # the KPL/MK header from the template; write_product set its attributes.
        expected_path = os.path.join(
            staging, "spice_kernels", "mk", "insight_v01.tm"
        )
        assert product.path == expected_path
        assert os.path.exists(expected_path)

        # The meta-kernel does not contain anything except the first line where the
        # kernel architecture and type are provided. Check that we have the right one.
        assert Path(expected_path).read_text(encoding="utf-8").startswith("KPL/MK")

    @pytest.mark.parametrize("diff, expect_compare", [
        (True, True),
        (False, False)
    ])
    def test_diff_flag_controls_compare_call(self, tmp_path, diff, expect_compare):
        compare_mock = MagicMock()
        self._make_product(
            tmp_path,
            extra_setup_attrs={"diff": diff},
            extra_patches=[patch(f"{_MODULE}.MetaKernelProduct.compare", compare_mock)],
        )
        assert compare_mock.called == expect_compare

    @pytest.mark.parametrize("pds_version, expect_label", [
        ("4", True),
        ("3", False)
    ])
    def test_pds4_label_created_only_for_pds4(self, tmp_path, pds_version, expect_label):
        label_mock = MagicMock()
        self._make_product(
            tmp_path,
            pds_version=pds_version,
            extra_patches=[patch(f"{_MODULE}.MetaKernelPDS4Label", label_mock)],
        )
        assert label_mock.called == expect_label

    def test_no_matching_mk_config_raises(self, tmp_path):
        staging = str(tmp_path / "staging")
        os.makedirs(staging, exist_ok=True)

        setup = make_setup(staging_directory=staging,
                           mk_list=[{
                               "@name": "other_v$VERSION.tm",
                               "name": [{"pattern": {"#text": "VERSION", "@length": "2"}}],
                               "grammar": {"pattern": []},
                               "metadata": {"description": ""},
                           }])

        collection = make_collection()

        with (patch(f"{_MODULE}.safe_make_directory"),
              patch(f"{_MODULE}.current_date", return_value="2024-01-01")):
            with pytest.raises(RuntimeError,
                               match="Meta-kernel insight_v01.tm has not been matched in configuration."):
                MetaKernelProduct(setup, "insight_v01.tm", collection)

    def test_collection_metakernel_set_from_mk_to_list(self, tmp_path):
        kernel_list = ["naif0012.tls", "insight_v01.bsp"]
        # The extra patch shadows the base mk_to_list patch so the product
        # receives kernel_list instead of the default empty list.
        product, _ = self._make_product(
            tmp_path,
            extra_patches=[
                patch(f"{_MODULE}.mk_to_list", return_value=kernel_list),
            ],
        )
        assert product.collection_metakernel == kernel_list

    def test_missions_observers_targets_stored_from_collection(self, tmp_path):
        product, _, collection = build_product(tmp_path)
        assert product.missions == ["InSight"]
        assert product.observers == ["INSIGHT"]
        assert product.targets == ["MARS"]

    def test_list_name_pattern_flattened_into_patterns(self, tmp_path):
        # when the "pattern" value in a metak["name"] entry is a list
        # (multiple sub-patterns), the list is extended into patterns with +=.
        list_mk_list = [{
            "@name": "insight_v$VERSION.tm",
            "name": [{"pattern": [{"#text": "VERSION", "@length": "2"}]}],
            "grammar": {"pattern": ["naif0012.tls"]},
            "metadata": {"description": "Test.", "data": ""},
        }]
        product, _ = self._make_product(tmp_path, mk_list=list_mk_list)
        assert product.version == "01"

    def test_yearly_mk_sets_year_and_YEAR_attributes(self, tmp_path):
        # when the MK template contains $YEAR and the filename
        # encodes the year, self.year and self.YEAR are set accordingly.
        yearly_mk_list = [{
            "@name": "insight_$YEAR_v$VERSION.tm",
            "name": [
                {"pattern": {"#text": "YEAR", "@length": "4"}},
                {"pattern": {"#text": "VERSION", "@length": "2"}},
            ],
            "grammar": {"pattern": ["naif0012.tls"]},
            "metadata": {"description": "Test.", "data": ""},
        }]
        yearly_pattern = r"insight_\d{4}_v\d+\.tm"
        product, _ = self._make_product(
            tmp_path,
            name="insight_2021_v01.tm",
            mk_list=yearly_mk_list,
            extra_setup_attrs={
                "re_config": [re.compile(yearly_pattern)],
                "kernel_list_config": {
                    yearly_pattern: {
                        "@pattern": yearly_pattern,
                        "description": "Test yearly InSight MK.",
                    }
                },
            },
        )
        assert product.year == "2021"
        assert product.YEAR == "2021"

    # ------------------------------------------------------------------
    # two or more secondary missions
    # ------------------------------------------------------------------

    def test_pds4_mission_name_with_multiple_secondary_missions(self, tmp_path):
        # when secondary_missions has 2+ entries the mission text is built in a
        # for-loop: non-last entries get ", " appended and the last gets "and ".
        product, _ = self._make_product(
            tmp_path,
            extra_setup_attrs={"secondary_missions": ["X", "MEX"]},
        )
        assert product.PDS4_MISSION_NAME == "InSight, X, and MEX"

    # ------------------------------------------------------------------
    # creation_date_time present on setup → used for MK date
    # ------------------------------------------------------------------

    def test_mk_creation_date_uses_creation_date_time_when_set(self, tmp_path):
        # when setup.creation_date_time is set, current_date is called with it
        # as the date= keyword argument rather than the no-arg form.
        #
        # We supply our own current_date mock (shadowing the one in the base
        # patch set) so we can assert *how* it was called; asserting only the
        # return value would not distinguish the two branches because the mock
        # returns the same value either way.
        current_date_mock = MagicMock(return_value="2024-01-01")
        product, _ = self._make_product(
            tmp_path,
            extra_setup_attrs={"creation_date_time": "2023-06-15T00:00:00"},
            extra_patches=[patch(f"{_MODULE}.current_date", current_date_mock)],
        )
        # The creation_date_time branch must call current_date(date=...); the
        # no-arg form would mean the wrong branch was taken.
        current_date_mock.assert_called_once_with(date="2023-06-15T00:00:00")
        assert product.MK_CREATION_DATE == "2024-01-01"

    # ------------------------------------------------------------------
    # increment=True + setup has mk_setup → check_version called
    # ------------------------------------------------------------------

    def test_check_version_called_when_increment_and_mk_setup_present(
            self, tmp_path):
        # when setup.increment is True AND setup has a mk_setup
        # attribute, check_version() is invoked on the product.
        staging, bundle, work, templates = self._setup_dirs(tmp_path)
        setup = make_setup(
            staging_directory=staging,
            bundle_directory=bundle,
            working_directory=work,
            templates_directory=templates,
        )
        setup.increment = True
        setup.mk_setup = MagicMock()
        collection = make_collection()

        with (
            patch(f"{_MODULE}.safe_make_directory"),
            patch(f"{_MODULE}.current_date", return_value="2024-01-01"),
            patch(f"{_MODULE}.mk_to_list", return_value=[]),
            patch(f"{_MODULE}.MetaKernelProduct.write_product"),
            patch(f"{_MODULE}.MetaKernelProduct.coverage"),
            patch(f"{_MODULE}.Product.__init__", return_value=None),
            patch(f"{_MODULE}.MetaKernelPDS4Label", return_value=MagicMock()),
            patch(f"{_MODULE}.MetaKernelProduct.check_version") as mock_check_version,
        ):
            MetaKernelProduct(setup, "insight_v01.tm", collection)

        mock_check_version.assert_called_once()

    # ------------------------------------------------------------------
    # output file already exists → overwrite warning logged
    # ------------------------------------------------------------------

    def test_existing_mk_file_logs_overwrite_warning(self, tmp_path, caplog):
        # when the computed output path already exists, three distinct warning
        # messages are logged before write_product is called.
        staging = str(tmp_path / "staging")
        # Pre-create the output file that __init__ would otherwise generate.
        mk_dir = Path(staging) / "spice_kernels" / "mk"
        mk_dir.mkdir(parents=True)
        (mk_dir / "insight_v01.tm").write_text("KPL/MK\n", encoding="utf-8")

        with caplog.at_level(logging.INFO):
            self._make_product(tmp_path)

        expected = [
            (logging.INFO, '-- Generate meta-kernel: insight_v01.tm'),
            (logging.WARNING, f'-- Meta-kernel already exists: {tmp_path / "staging/spice_kernels/mk/insight_v01.tm"}'),
            (logging.WARNING, '-- The meta-kernel will be generated and the one present in the '
                              'staging are will be overwritten.'),
            (logging.WARNING, '-- Note that to provide a meta-kernel as an input, it must be provided '
                              'via configuration file.'),
            (logging.INFO, ''),
            (logging.INFO, ''),
            (logging.INFO, '-- Labeling meta-kernel: insight_v01.tm...')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]
        assert expected == results


# ===========================================================================
# MetaKernelProduct.check_version
# ===========================================================================

class TestMetaKernelProductCheckVersion:
    """Tests for MetaKernelProduct.check_version."""

    @staticmethod
    def _make_stub(setup, name, version, values=None, year=None):
        product = object.__new__(MetaKernelProduct)
        product.setup = setup
        product.name = name
        product.version = version
        product.values = values or {"VERSION": version}
        product.mk_setup = {
            "@name": "insight_v$VERSION.tm",
        }
        if year is not None:
            product.year = year
        return product

    @pytest.mark.parametrize("name, version, expected", [
        ("insight_v02.tm", "02",
         [(logging.INFO, '-- Version from kernel list and from previous increment agree: 2.')]),
        ("insight_v05.tm", "05",
         [(logging.WARNING, '-- The meta-kernel version is not as expected from previous increment.'),
          (logging.WARNING, '   Version set to: 5, whereas it is expected to be: 2.'),
          (logging.WARNING, '   It is recommended to stop the execution and fix the issue.')]),
    ])
    def test_check_version_log_message(
            self, tmp_path, caplog, name, version, expected):
        bundle = str(tmp_path / "bundle")
        mk_dir = tmp_path / "bundle" / "insight_spice" / "spice_kernels" / "mk"
        mk_dir.mkdir(parents=True)
        (mk_dir / "insight_v01.tm").write_text("KPL/MK\n", encoding="utf-8")

        setup = make_setup(bundle_directory=bundle, increment=True,
                           mission_acronym="insight")
        product = self._make_stub(setup, name, version=version)

        with caplog.at_level(logging.INFO):
            product.check_version()

        results = [(r[1], r[2]) for r in caplog.record_tuples]
        assert expected == results

    def test_no_previous_mk_logs_warning(self, tmp_path, caplog):
        bundle = str(tmp_path / "bundle")
        mk_dir = tmp_path / "bundle" / "insight_spice" / "spice_kernels" / "mk"
        mk_dir.mkdir(parents=True)
        # No mk files present.

        setup = make_setup(bundle_directory=bundle, increment=True,
                           mission_acronym="insight")
        product = self._make_stub(setup, "insight_v01.tm", version="01")

        with caplog.at_level(logging.INFO):
            product.check_version()

        expected = [
            (logging.WARNING, '-- Meta-kernel from previous increment is not available.'),
            (logging.WARNING, '   Version will be set to: 01.')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]
        assert expected == results

    def test_year_substituted_in_pattern(self, tmp_path, caplog):
        bundle = str(tmp_path / "bundle")
        mk_dir = tmp_path / "bundle" / "insight_spice" / "spice_kernels" / "mk"
        mk_dir.mkdir(parents=True)
        # Create a yearly-style MK from the previous increment.
        (mk_dir / "insight_2021_v01.tm").write_text("KPL/MK\n", encoding="utf-8")

        setup = make_setup(bundle_directory=bundle, increment=True,
                           mission_acronym="insight")
        product = object.__new__(MetaKernelProduct)
        product.setup = setup
        product.name = "insight_2021_v02.tm"
        product.version = "02"
        product.year = "2021"
        # YEAR must appear before VERSION: match_patterns sorts by position in
        # the pattern template, and $YEAR precedes $VERSION in the filename.
        product.values = {"YEAR": "2021", "VERSION": "02"}
        product.YEAR = "2021"
        product.mk_setup = {"@name": "insight_$YEAR_v$VERSION.tm"}

        with caplog.at_level(logging.INFO):
            product.check_version()

        expected = [
            (logging.INFO, '-- Version from kernel list and from previous increment agree: 2.')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]
        assert expected == results


# ===========================================================================
# MetaKernelProduct.set_product_lid
# ===========================================================================

class TestMetaKernelProductSetProductLid:
    """Tests for MetaKernelProduct.set_product_lid."""

    @staticmethod
    def _make_stub(name, kernel_type="mk"):
        setup = make_setup()
        product = object.__new__(MetaKernelProduct)
        product.setup = setup
        product.name = name
        product.type = kernel_type
        return product

    @pytest.mark.parametrize("name, kernel_type, lid", [
        ("insight_v01.tm",
         "mk",
         "urn:nasa:pds:insight_spice:spice_kernels:mk_insight"),
        ("INSIGHT_V01.TM",
         'mk',
         "urn:nasa:pds:insight_spice:spice_kernels:mk_insight_v01.tm"),
        ("insight_data.txt",
         "txt",
         "urn:nasa:pds:insight_spice:spice_kernels:txt_insight_data.txt"),
        ("maven_v002.tm",
         "mk",
         "urn:nasa:pds:insight_spice:spice_kernels:mk_maven"),
        ("bc_v10.tm",
         "mk",
         "urn:nasa:pds:insight_spice:spice_kernels:mk_bc"),
    ])
    def test_set_product_lid(self, name, kernel_type, lid):
        product = self._make_stub(name, kernel_type=kernel_type)
        product.set_product_lid()
        assert product.lid == lid


# ===========================================================================
# MetaKernelProduct.set_product_vid
# ===========================================================================

class TestMetaKernelProductSetProductVid:
    """Tests for MetaKernelProduct.set_product_vid."""

    @staticmethod
    def _make_stub(version=None, name="insight_v01.tm"):
        setup = make_setup()
        product = object.__new__(MetaKernelProduct)
        product.setup = setup
        product.name = name
        if version is not None:
            product.version = version
        return product

    @pytest.mark.parametrize("version, expected_vid", [
        ("01", "1.0"),
        ("001", "1.0"),
        ("05", "5.0"),
        ("10", "10.0"),
        ("1", "1.0"),
    ])
    def test_version_lstrips_zeros_and_appends_dot_zero(self, version, expected_vid):
        product = self._make_stub(version=version)
        product.set_product_vid()
        assert product.vid == expected_vid

    def test_no_version_attribute_defaults_to_1_0_when_name_has_01(self, caplog):
        product = self._make_stub(name="insight_v01.tm")
        # No version attribute set → triggers BaseException handler.
        # Check the logging level and logging messages.
        with caplog.at_level(logging.INFO):
            product.set_product_vid()

        assert product.vid == "1.0"

        expected = [
            (logging.WARNING, '-- insight_v01.tm No VID explicit in kernel name: set to 1.0'),
            (logging.WARNING, '-- Make sure that the MK pattern in the configuration file is '
                              'correct, if manually provided make sure you provided the '
                              'appropriate name.')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]
        assert expected == results

    def test_no_version_attribute_raises_when_name_lacks_01(self):
        setup = make_setup()
        product = object.__new__(MetaKernelProduct)
        product.setup = setup
        product.name = "insight_v05.tm"  # no "01" → handle_npb_error called

        with pytest.raises(RuntimeError, match="version does not correspond to VID"):
            product.set_product_vid()

    def test_all_zero_version_yields_dot_zero(self):
        # Documents the quirk: "00".lstrip("0") == "" so the VID becomes
        # ".0" rather than "0.0".
        product = self._make_stub(version="00")
        product.set_product_vid()
        assert product.vid == ".0"

    def test_no_version_attribute_substring_01_in_name_does_not_raise(self):
        # Documents the substring quirk: the first-release guard is
        # `if "01" not in self.name`, so a name like "insight_v101.tm" (which
        # *contains* "01") silently passes and is assigned VID 1.0 even though
        # the name encodes version 101.
        product = self._make_stub(name="insight_v101.tm")  # version attr absent
        product.set_product_vid()
        assert product.vid == "1.0"


# ===========================================================================
# MetaKernelProduct.get_description
# ===========================================================================

class TestMetaKernelProductGetDescription:
    """Tests for MetaKernelProduct.get_description."""

    @staticmethod
    def _make_stub(name="insight_v01.tm", re_config=None, kernel_list_config=None):
        setup = make_setup()
        setup.re_config = re_config or []
        setup.kernel_list_config = kernel_list_config or {}
        product = object.__new__(MetaKernelProduct)
        product.setup = setup
        product.name = name
        return product

    @pytest.mark.parametrize("description, expected", [
        ("InSight SPICE MK.", "InSight SPICE MK."),
        ("Word1  word2   word3.", "Word1 word2 word3."),
        # TODO: Check this test. It shows unexpected behavior.
        ("Line one.\nLine two.\n", "Line one.Line two.")
    ])
    def test_returns_description_when_pattern_matches(self, description, expected):
        pattern = re.compile(r"insight_v\d+\.tm")
        product = self._make_stub(
            re_config=[pattern],
            kernel_list_config={
                pattern.pattern: {"description": description}
            },
        )
        assert product.get_description() == expected

    def test_raises_when_no_pattern_matches(self):
        pattern = re.compile(r"other_v\d+\.tm")
        product = self._make_stub(
            re_config=[pattern],
            kernel_list_config={
                pattern.pattern: {"description": "Not matched."}
            },
        )
        with pytest.raises(RuntimeError,
                           match="does not have a description on configuration file"):
            product.get_description()

    def test_last_matching_pattern_overwrites_description(self):
        # The loop does NOT break on first match, so the last matching pattern
        # in re_config wins. This documents the current behavior.
        p1 = re.compile(r"insight_v\d+\.tm")
        p2 = re.compile(r"insight_.*\.tm")
        product = self._make_stub(
            re_config=[p1, p2],
            kernel_list_config={
                p1.pattern: {"description": "First match."},
                p2.pattern: {"description": "Second match."},
            },
        )
        assert product.get_description() == "Second match."

    @pytest.mark.parametrize("description, pattern_text, expected", [
        ("Version $VER of InSight MK.",
         "kernel",
         "Version 05 of InSight MK."),
        ("InSight MK with no variable refs.",
         "kernel",
         "InSight MK with no variable refs."),
        ("Version $VER of InSight MK.",
         "KERNEL",
         "Version 05 of InSight MK."),
    ])
    def test_kernel_pattern_substitution_from_filename(self, description, pattern_text, expected):
        """A $VAR in description is replaced from the kernel filename."""
        pattern = re.compile(r"insight_v\d+\.tm")
        product = self._make_stub(
            name="insight_v05.tm",
            re_config=[pattern],
            kernel_list_config={
                pattern.pattern: {
                    "description": description,
                    "patterns": {
                        "VER": {
                            "@pattern": pattern_text,
                            "#text": "insight_v$VER.tm",
                        }
                    },
                }
            },
        )
        desc = product.get_description()
        assert desc == expected

    def test_non_kernel_pattern_list_substitutes_matching_value(self):
        # TODO: This test demonstrates that there is a bug.
        # when patterns[el] is a list (non-kernel pattern with
        # multiple @value entries) and a matching @value is found, the code
        # attempts patterns[el]["&value"] = value which raises TypeError because
        # list indices must be integers, not strings.
        pattern = re.compile(r"insight_v01\.tm")
        product = self._make_stub(
            name="insight_v01.tm",
            re_config=[pattern],
            kernel_list_config={
                pattern.pattern: {
                    "description": "Spacecraft $SC SPICE MK.",
                    "patterns": {
                        "SC": [
                            {"@value": "insight_v01.tm", "#text": "InSight"},
                            {"@value": "other_v01.tm", "#text": "Other"},
                        ]
                    },
                }
            },
        )
        with pytest.raises(TypeError):
            product.get_description()

    def test_kernel_pattern_template_missing_variable_raises(self):
        # when the "#text" template does not contain the variable being
        # substituted, patt_split has length 1 (not 2) and a RuntimeError
        # is raised.
        pattern = re.compile(r"insight_v\d+\.tm")
        product = self._make_stub(
            name="insight_v05.tm",
            re_config=[pattern],
            kernel_list_config={
                pattern.pattern: {
                    "description": "Version $VER of InSight MK.",
                    "patterns": {
                        "VER": {
                            "@pattern": "kernel",
                            "#text": "insight_fixed.tm",  # no $VER in template
                        }
                    },
                }
            },
        )
        with pytest.raises(RuntimeError, match="not adept to write description"):
            product.get_description()

    def test_non_kernel_pattern_no_matching_value_raises(self):
        # when the pattern entry is a list (non-kernel lookup) and no @value
        # matches the kernel name, value stays as the list and a RuntimeError
        # is raised.
        pattern = re.compile(r".*\.tm")
        product = self._make_stub(
            name="no_match_v01.tm",
            re_config=[pattern],
            kernel_list_config={
                pattern.pattern: {
                    "description": "Spacecraft $SC SPICE MK.",
                    "patterns": {
                        "SC": [
                            {"@value": "insight_v01.tm", "#text": "InSight"},
                        ]
                    },
                }
            },
        )
        with pytest.raises(RuntimeError,
                           match="Kernel description could not be updated with pattern"):
            product.get_description()


# ===========================================================================
# MetaKernelProduct.write_product
# ===========================================================================

class TestMetaKernelProductWriteProduct:
    """Tests for MetaKernelProduct.write_product."""

    @staticmethod
    def _make_stub(tmp_path, name="insight_v01.tm", grammar_patterns=None,
                   padding=None, data="", description="Test desc.", pds_version="4"):
        staging = str(tmp_path / "staging")
        templates = str(tmp_path / "templates")
        os.makedirs(staging, exist_ok=True)
        os.makedirs(templates, exist_ok=True)

        template_path = os.path.join(templates, "template_metakernel.tm")
        Path(template_path).write_text(
            "KPL/MK\n$KERNELS_IN_METAKERNEL\n", encoding="utf-8"
        )

        setup = make_setup(staging_directory=staging, templates_directory=templates,
                           pds_version=pds_version)
        collection = MagicMock()
        collection.product = []

        mk_grammar = {"pattern": grammar_patterns or ["naif0012.tls"]}
        if padding is not None:
            mk_grammar["padding"] = padding

        subdir = "spice_kernels" if pds_version == "4" else "extras"
        product = object.__new__(MetaKernelProduct)
        product.setup = setup
        product.collection = collection
        product.name = name
        product.template = template_path
        output_path = os.path.join(staging, subdir, "mk", name)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        product.path = output_path
        product.mk_setup = {
            "@name": "insight_v$VERSION.tm",
            "grammar": mk_grammar,
            "metadata": {"description": description, "data": data},
        }
        product.KERNELPATH = ".." if pds_version == "4" else "./data"
        product.PDS4_MISSION_NAME = "InSight"
        product.MK_CREATION_DATE = "2024-01-01"
        product.AUTHOR = "John Doe"
        product.INSTITUTION = "NAIF/JPL"
        product.FILE_NAME = name
        product.SPICE_NAME = "INSIGHT"
        product.version = "01"
        return product

    def test_missing_grammar_raises(self, tmp_path):
        product = self._make_stub(tmp_path)
        del product.mk_setup["grammar"]

        with pytest.raises(RuntimeError, match="grammar not defined in configuration"):
            product.write_product()

    @pytest.mark.parametrize("padding, mk", [
        ("True",
         "KPL/MK\n"
         "                          '$KERNELS/lsk/naif0012.tls'\n"
         "\n"),
        ("False",
         "KPL/MK\n"
         "'$KERNELS/lsk/naif0012.tls'\n"
         "\n")

    ])
    def test_padding(self, tmp_path, padding, mk):
        product = self._make_stub(tmp_path, padding=padding)
        with patch(f"{_MODULE}.get_latest_kernel", return_value=["naif0012.tls"]):
            product.write_product()

        content = Path(product.path).read_text(encoding="utf-8")
        assert content == mk

        # product path is stored after write
        assert product.product == product.path

    def test_invalid_padding_value_logs_warning(self, tmp_path, caplog):
        # NOTE: get_latest_kernel is forced to return an empty list on purpose.
        # When the grammar padding value is neither "True" nor "False", the
        # source logs this warning but never assigns `padding` (see the known
        # bug captured by test_invalid_padding_with_kernels_raises). An empty
        # kernel list skips the rendering loop that would dereference `padding`,
        # so the warning can be observed in isolation without hitting the bug.
        product = self._make_stub(tmp_path, padding="maybe")
        with (
            caplog.at_level(logging.WARNING),
            patch(f"{_MODULE}.get_latest_kernel", return_value=[]),
        ):
            product.write_product()

        expected = [
            (logging.WARNING, '-- Padding value in NPB configuration file MK grammar is maybe'),
            (logging.WARNING, '   The value should be "True" or "False". Case is not relevant.')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]
        assert results == expected

    def test_invalid_padding_with_kernels_raises(self, tmp_path):
        # KNOWN SOURCE BUG: an invalid grammar padding value ("maybe") leaves
        # the local `padding` variable unassigned. As soon as a kernel is
        # matched, the rendering loop evaluates `padding * 26` and raises
        # UnboundLocalError. This test documents the current behavior; the
        # companion test above only passes because it forces an empty kernel
        # list which sidesteps this path.
        product = self._make_stub(
            tmp_path, padding="maybe", grammar_patterns=["naif0012.tls"]
        )
        with (
            patch(f"{_MODULE}.get_latest_kernel", return_value=["naif0012.tls"]),
            pytest.raises(UnboundLocalError),
        ):
            product.write_product()

    def test_kernels_in_metakernel_written_to_file(self, tmp_path):
        product = self._make_stub(
            tmp_path, grammar_patterns=["naif0012.tls", "pck00010.tpc"]
        )
        with patch(
            f"{_MODULE}.get_latest_kernel",
            side_effect=[["naif0012.tls"], ["pck00010.tpc"]],
        ):
            product.write_product()

        # Each entry is rendered as '$KERNELS/<type>/<name>' with the kernel
        # type derived from the extension (tls → lsk, tpc → pck).
        expected = ("KPL/MK\n"
                    "                          '$KERNELS/lsk/naif0012.tls'\n"
                    "\n"
                    "                          '$KERNELS/pck/pck00010.tpc'\n"
                    "\n")
        content = Path(product.path).read_text(encoding="utf-8")
        assert content == expected

    def test_duplicate_kernel_entries_are_deduplicated(self, tmp_path):
        product = self._make_stub(
            tmp_path,
            grammar_patterns=["naif0012.tls", "naif0012.tls"],
        )
        with patch(f"{_MODULE}.get_latest_kernel", return_value=["naif0012.tls"]):
            product.write_product()

        # KERNELS_IN_METAKERNEL should have exactly one occurrence.
        assert product.KERNELS_IN_METAKERNEL.count("naif0012.tls") == 1

    def test_collection_metakernel_subset_to_collection_products(self, tmp_path, caplog):
        product = self._make_stub(tmp_path, grammar_patterns=["naif0012.tls"])
        # Simulate two products in the collection; only one matches MK grammar.
        mock_kernel = MagicMock()
        mock_kernel.name = "naif0012.tls"
        mock_other = MagicMock()
        mock_other.name = "unrelated.bsp"
        product.collection.product = [mock_kernel, mock_other]

        with (caplog.at_level(logging.WARNING),
              patch(f"{_MODULE}.get_latest_kernel", return_value=["naif0012.tls"])):
            product.write_product()

        assert mock_kernel in product.collection_metakernel
        assert mock_other not in product.collection_metakernel
        # 2 archived kernels but only 1 in the MK → the count-mismatch branch
        # logs both totals at WARNING level.
        expected = [
            (logging.WARNING, '-- Archived kernels:           2'),
            (logging.WARNING, '-- Kernels in meta-kernel:     1')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]
        assert results == expected

    def test_exclude_grammar_prefix_builds_excluded_list(self, tmp_path):
        product = self._make_stub(
            tmp_path,
            grammar_patterns=["naif0012.tls", "exclude:naif0012.tls"],
        )
        with patch(f"{_MODULE}.get_latest_kernel",
                   return_value=[]) as mock_glk:
            product.write_product()

        # The excluded list should contain "naif0012.tls" at least once.
        calls = mock_glk.call_args_list
        assert any(
            "naif0012.tls" in c.kwargs.get("excluded_kernels", [])
            for c in calls
        )

    def test_date_grammar_prefix_enables_dates_flag(self, tmp_path):
        product = self._make_stub(
            tmp_path,
            grammar_patterns=["date:naif0012.tls"],
        )
        with patch(f"{_MODULE}.get_latest_kernel",
                   return_value=[]) as mock_glk:
            product.write_product()

        calls = mock_glk.call_args_list
        assert any(c.kwargs.get("dates") is True for c in calls)

    def test_pds3_grammar_uses_data_subdirectory(self, tmp_path):
        product = self._make_stub(tmp_path, pds_version="3")
        staging = str(tmp_path / "staging")

        with patch(f"{_MODULE}.get_latest_kernel", return_value=[]) as mock_glk:
            product.write_product()

        calls = mock_glk.call_args_list
        assert any(staging + "/DATA" in c.args[1] for c in calls)

    @pytest.mark.parametrize("increment, expect_warning", [
        (True, True),
        (False, False)])
    def test_glob_raises_logs_warning_only_when_increment(
            self, tmp_path, caplog, increment, expect_warning):
        product = self._make_stub(tmp_path, grammar_patterns=["naif0012.tls"])
        product.setup.increment = increment

        with (
            caplog.at_level(logging.WARNING),
            patch(f"{_MODULE}.glob.glob", side_effect=OSError("glob failed")),
            patch(f"{_MODULE}.get_latest_kernel", return_value=[]),
        ):
            product.write_product()

        assert ("previous increment" in caplog.text) == expect_warning

    def test_get_latest_kernel_exception_logs_warning_and_continues(
            self, tmp_path, caplog):
        product = self._make_stub(tmp_path, grammar_patterns=["naif0012.tls"])

        with (
            caplog.at_level(logging.WARNING),
            patch(f"{_MODULE}.get_latest_kernel",
                  side_effect=ValueError("bad kernel path")),
        ):
            product.write_product()  # must not raise

        assert "bad kernel path" in caplog.text
        assert product.product == product.path

    def test_scalar_latest_kernel_wrapped_in_list(self, tmp_path):
        # when get_latest_kernel returns a plain string (not a list)
        # it is wrapped in a list so the subsequent loop works correctly.
        product = self._make_stub(tmp_path, grammar_patterns=["naif0012.tls"])

        with patch(f"{_MODULE}.get_latest_kernel",
                   return_value="naif0012.tls"):
            product.write_product()

        assert "                          '$KERNELS/lsk/naif0012.tls'\n" == product.KERNELS_IN_METAKERNEL

    def test_missing_data_key_defaults_to_empty(self, tmp_path):
        # when the "data" key is absent from mk_setup["metadata"],
        # data defaults to an empty string without raising.
        product = self._make_stub(tmp_path)
        del product.mk_setup["metadata"]["data"]

        with patch(f"{_MODULE}.get_latest_kernel", return_value=[]):
            product.write_product()  # must not raise

        assert product.DATA == ""

    def test_missing_description_key_defaults_to_empty(self, tmp_path):
        # when the "description" key is absent from metadata,
        # desc defaults to an empty string without raising.
        product = self._make_stub(tmp_path)
        del product.mk_setup["metadata"]["description"]

        with patch(f"{_MODULE}.get_latest_kernel", return_value=[]):
            product.write_product()  # must not raise

        # An empty desc still produces the eol from the blank-line loop path.
        assert product.DESCRIPTION == "\n"

    def test_non_empty_data_formatted_with_indentation(self, tmp_path):
        # non-blank lines in the "data" field are indented and
        # prefixed with an eol on the first line.
        product = self._make_stub(tmp_path, data="KERNELS_TO_LOAD = (")

        with patch(f"{_MODULE}.get_latest_kernel", return_value=[]):
            product.write_product()

        # The single data line is prefixed with a leading EOL and indented by
        # exactly 6 spaces.
        assert product.DATA == "\n      KERNELS_TO_LOAD = (\n"

    def test_blank_line_in_description_adds_eol(self, tmp_path):
        # a blank line in the "description" field produces just an
        # EOL character in the curated description.
        product = self._make_stub(
            tmp_path, description="First line.\n\nThird line."
        )

        with patch(f"{_MODULE}.get_latest_kernel", return_value=[]):
            product.write_product()

        # Non-blank lines are indented by 3 spaces; the blank middle line
        # contributes a bare EOL, producing a "\n\n" gap between the two.
        assert product.DESCRIPTION == "   First line.\n\n   Third line.\n"

    def test_description_spice_name_substituted(self, tmp_path):
        # when the description contains "$SPICE_NAME", it is replaced
        # with the value of product.SPICE_NAME.
        product = self._make_stub(
            tmp_path,
            description="Kernels for the $SPICE_NAME mission.",
        )
        product.SPICE_NAME = "INSIGHT"

        with patch(f"{_MODULE}.get_latest_kernel", return_value=[]):
            product.write_product()

        assert product.DESCRIPTION == "   Kernels for the INSIGHT mission.\n"

    @pytest.mark.parametrize("verbose, expect_print", [
        (False, True),
        (True, False)])
    def test_print_when_not_silent_and_not_verbose(
            self, tmp_path, capsys, verbose, expect_print):
        product = self._make_stub(tmp_path)
        product.setup.args.silent = False
        product.setup.args.verbose = verbose

        with patch(f"{_MODULE}.get_latest_kernel", return_value=[]):
            product.write_product()

        assert ("Created" in capsys.readouterr().out) == expect_print

    def test_interrupt_to_update_prompts_user_when_enabled(
            self, tmp_path, capsys):
        product = self._make_stub(tmp_path)
        product.setup.args.debug = False
        product.mk_setup["interrupt_to_update"] = "true"

        with (
            patch(f"{_MODULE}.get_latest_kernel", return_value=[]),
            patch("builtins.input", return_value="") as mock_input,
        ):
            product.write_product()

        mock_input.assert_called_once()

    def test_interrupt_to_update_vi_input_opens_editor(self, tmp_path):
        product = self._make_stub(tmp_path)
        product.setup.args.debug = False
        product.mk_setup["interrupt_to_update"] = "true"

        with (
            patch(f"{_MODULE}.get_latest_kernel", return_value=[]),
            patch("builtins.input", return_value="vi"),
            patch(f"{_MODULE}.subprocess.call") as mock_sub,
        ):
            product.write_product()

        mock_sub.assert_called_once()
        assert product.path in mock_sub.call_args[0][0]

    def test_interrupt_to_update_vi_subprocess_fails_prompts_fallback(
            self, tmp_path, capsys):
        product = self._make_stub(tmp_path)
        product.setup.args.debug = False
        product.mk_setup["interrupt_to_update"] = "true"

        input_returns = iter(["vi", ""])
        with (
            patch(f"{_MODULE}.get_latest_kernel", return_value=[]),
            patch("builtins.input", side_effect=input_returns),
            patch(f"{_MODULE}.subprocess.call",
                  side_effect=OSError("vi not found")),
        ):
            product.write_product()

        captured = capsys.readouterr()
        assert "not available" in captured.out

    @pytest.mark.parametrize("debug, itu_value", [
        (True, "true"),    # key present but debug=True bypasses the block
        (False, None),     # key absent
        (False, "false"),  # key present but value is not "true"
    ])
    def test_interrupt_to_update_skips_prompt(self, tmp_path, debug, itu_value):
        product = self._make_stub(tmp_path)
        product.setup.args.debug = debug
        if itu_value is not None:
            product.mk_setup["interrupt_to_update"] = itu_value

        with (
            patch(f"{_MODULE}.get_latest_kernel", return_value=[]),
            patch("builtins.input") as mock_input,
        ):
            product.write_product()

        mock_input.assert_not_called()

    def test_same_type_consecutive_kernels_no_blank_line_separator(self, tmp_path):
        product = self._make_stub(
            tmp_path,
            grammar_patterns=["naif0012.tls", "leapseconds.tls"],
        )
        with patch(
            f"{_MODULE}.get_latest_kernel",
            side_effect=[["naif0012.tls"], ["leapseconds.tls"]],
        ):
            product.write_product()

        # Both are LSK (tls) so no blank line between them inside the kernel
        # block; the KERNELS_IN_METAKERNEL string should contain both with no
        # blank line (double newline) separating the two entries.
        expected = ("                          '$KERNELS/lsk/naif0012.tls'\n"
                    "                          '$KERNELS/lsk/leapseconds.tls'\n")
        assert expected == product.KERNELS_IN_METAKERNEL

    def test_multi_line_data_second_line_not_first(self, tmp_path):
        product = self._make_stub(tmp_path, data="line one\nline two")

        with patch(f"{_MODULE}.get_latest_kernel", return_value=[]):
            product.write_product()

        # Only the first data line gets the leading EOL; both lines share the
        # 6-space indent.
        assert product.DATA == (
            "\n"
            "      line one\n"
            "      line two\n"
        )


# ===========================================================================
# MetaKernelProduct.compare
# ===========================================================================

class TestMetaKernelProductCompare:
    """Tests for MetaKernelProduct.compare."""

    @staticmethod
    def _make_stub(bundle_path, name="insight_v01.tm"):
        setup = make_setup(bundle_directory=bundle_path,
                           mission_acronym="insight")
        setup.working_directory = "/work"
        product = object.__new__(MetaKernelProduct)
        product.setup = setup
        product.name = name
        product.path = f"{bundle_path}/insight_spice/spice_kernels/mk/{name}"
        return product

    def test_compare_uses_previous_mk_when_found(self, tmp_path):
        mk_dir = tmp_path / "insight_spice" / "spice_kernels" / "mk"
        mk_dir.mkdir(parents=True)
        (mk_dir / "insight_v01.tm").write_text("KPL/MK\n", encoding="utf-8")

        product = self._make_stub(str(tmp_path), name="insight_v02.tm")

        with patch(f"{_MODULE}.compare_files") as mock_cmp:
            product.compare()

        fromfile, tofile, work_dir, diff = mock_cmp.call_args[0]
        assert fromfile == product.path
        assert tofile == f"{tmp_path}/insight_spice/spice_kernels/mk/insight_v01.tm"
        assert work_dir == product.setup.working_directory
        assert diff == product.setup.diff

    def test_compare_falls_back_to_template_when_no_previous(self, tmp_path, caplog):
        mk_dir = tmp_path / "insight_spice" / "spice_kernels" / "mk"
        mk_dir.mkdir(parents=True)
        # No previous MK files.

        setup = make_setup(bundle_directory=str(tmp_path),
                           templates_directory="/templates",
                           mission_acronym="insight")
        setup.working_directory = "/work"
        product = object.__new__(MetaKernelProduct)
        product.setup = setup
        product.name = "insight_v01.tm"
        product.path = f"{tmp_path}/insight_spice/spice_kernels/mk/insight_v01.tm"

        with (patch(f"{_MODULE}.compare_files") as mock_cmp,
              caplog.at_level(logging.INFO)):
            product.compare()

        fromfile, tofile, work_dir, diff = mock_cmp.call_args[0]
        assert fromfile == product.path
        assert tofile == "/templates/template_metakernel.tm"
        assert work_dir == setup.working_directory
        assert diff == setup.diff

        expected = [
            (logging.WARNING, '-- No other version of insight_v01.tm has been found.'),
            (logging.WARNING, '-- Comparing with meta-kernel template.'),
            (logging.INFO, '-- Comparing insight_v01.tm...')]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected

    def test_compare_finds_previous_mk_when_loop_exhausts_all_prefixes(self, tmp_path):
        # "a.tm" has length 4, so range(1, len-1) = range(1, 3) = [1, 2].
        # glob returns a match on both iterations (i=1: prefix "a";
        # i=2: prefix "a."), so val_mk is updated to prev_mk on each pass and
        # the else:break never fires. After the loop exhausts, compare_files
        # is called with prev_mk as the comparison target.
        prev_mk = str(tmp_path / "a_prev.tm")
        product = self._make_stub(str(tmp_path), name="a.tm")

        with patch(f"{_MODULE}.glob.glob", return_value=[prev_mk]):
            with patch(f"{_MODULE}.compare_files") as mock_cmp:
                product.compare()

        fromfile, tofile, work_dir, diff = mock_cmp.call_args[0]
        assert fromfile == product.path
        assert tofile == prev_mk
        assert work_dir == product.setup.working_directory
        assert diff == product.setup.diff


# ===========================================================================
# MetaKernelProduct.validate
# ===========================================================================

class TestMetaKernelProductValidate:
    """Tests for MetaKernelProduct.validate."""

    @staticmethod
    def _make_stub(tmp_path, name="insight_v01.tm", collection_metakernel=None):
        mk_dir = tmp_path / "insight_spice" / "spice_kernels" / "mk"
        mk_dir.mkdir(parents=True)
        mk_path = mk_dir / name
        mk_path.write_text("KPL/MK\n", encoding="utf-8")

        setup = make_setup(bundle_directory=str(tmp_path),
                           mission_acronym="insight")
        product = object.__new__(MetaKernelProduct)
        product.setup = setup
        product.name = name
        product.path = str(mk_path)
        product.collection_metakernel = collection_metakernel or []
        return product, str(mk_path)

    def test_furnsh_called_with_mk_path(self, tmp_path):
        product, mk_path = self._make_stub(tmp_path)

        with (
            patch(f"{_MODULE}.spiceypy.kclear"),
            patch(f"{_MODULE}.spiceypy.furnsh") as mock_furnsh,
            patch(f"{_MODULE}.spiceypy.ktotal", return_value=1),
            patch(f"{_MODULE}.check_line_length", return_value=[]),
            patch("os.chdir"),
        ):
            product.validate()

        mock_furnsh.assert_called_once_with(mk_path)

    def test_kernel_count_mismatch_logs_error(self, tmp_path, caplog):
        kernels = [MagicMock(), MagicMock()]
        product, _ = self._make_stub(tmp_path, collection_metakernel=kernels)

        with (
            caplog.at_level(logging.INFO),
            patch(f"{_MODULE}.spiceypy.kclear"),
            patch(f"{_MODULE}.spiceypy.furnsh"),
            # ktotal returns 5 (4 kernels + 1 MK); collection has only 2.
            patch(f"{_MODULE}.spiceypy.ktotal", return_value=5),
            patch(f"{_MODULE}.check_line_length", return_value=[]),
            patch("os.chdir"),
        ):
            product.validate()

        expected = [
            (logging.INFO, '-- Kernels loaded with FURNSH: 4'),
            (logging.INFO, '-- Kernels present in insight_v01.tm: 2'),
            (logging.ERROR, '-- Number of kernels loaded is not equal to kernels present in meta-kernel.')]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected

    def test_furnsh_failure_logs_error(self, tmp_path, caplog):
        product, _ = self._make_stub(tmp_path)

        with (
            caplog.at_level(logging.INFO),
            patch(f"{_MODULE}.spiceypy.kclear") as mock_kclear,
            patch(f"{_MODULE}.spiceypy.furnsh", side_effect=RuntimeError("fail")),
            patch(f"{_MODULE}.check_line_length", return_value=[]),
            patch("os.chdir"),
        ):
            product.validate()

        expected = [
            (logging.ERROR, '-- The MK could not be loaded with the SPICE API FURNSH.')
        ]
        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected

        # kclear must be called after the except block to guarantee cleanup
        # even when furnsh raises.
        assert mock_kclear.call_count == 2

    def test_line_length_errors_logged_as_warnings(self, tmp_path, caplog):
        product, _ = self._make_stub(tmp_path)

        with (
            caplog.at_level(logging.INFO),
            patch(f"{_MODULE}.spiceypy.kclear"),
            patch(f"{_MODULE}.spiceypy.furnsh"),
            patch(f"{_MODULE}.spiceypy.ktotal", return_value=1),
            patch(f"{_MODULE}.check_line_length",
                  return_value=["line_too_long_example"]),
            patch("os.chdir"),
        ):
            product.validate()

        expected = [
            (logging.INFO, '-- Kernels loaded with FURNSH: 0'),
            (logging.INFO, '-- Kernels present in insight_v01.tm: 0'),
            (logging.WARNING, '-- The MK has lines with length longer than 80 characters:'),
            (logging.WARNING, '   line_too_long_example')]
        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected

    def test_kclear_called_after_validation(self, tmp_path):
        product, _ = self._make_stub(tmp_path)

        with (
            patch(f"{_MODULE}.spiceypy.kclear") as mock_kclear,
            patch(f"{_MODULE}.spiceypy.furnsh"),
            patch(f"{_MODULE}.spiceypy.ktotal", return_value=1),
            patch(f"{_MODULE}.check_line_length", return_value=[]),
            patch("os.chdir"),
        ):
            product.validate()

        # kclear is called exactly twice: once before furnsh and once after.
        assert mock_kclear.call_count == 2

    def test_validate_restores_working_directory(self, tmp_path):
        product, _ = self._make_stub(tmp_path)
        cwd = os.getcwd()

        with (
            patch(f"{_MODULE}.spiceypy.kclear"),
            patch(f"{_MODULE}.spiceypy.furnsh"),
            patch(f"{_MODULE}.spiceypy.ktotal", return_value=1),
            patch(f"{_MODULE}.check_line_length", return_value=[]),
            patch("os.chdir") as mock_chdir,
        ):
            product.validate()

        # validate() chdirs into the MK directory and must restore the original
        # working directory as its final action.
        assert mock_chdir.call_args_list[-1] == call(cwd)

    def test_validate_restores_working_directory_even_on_furnsh_failure(self, tmp_path):
        product, _ = self._make_stub(tmp_path)
        cwd = os.getcwd()

        with (
            patch(f"{_MODULE}.spiceypy.kclear"),
            patch(f"{_MODULE}.spiceypy.furnsh", side_effect=RuntimeError("fail")),
            patch(f"{_MODULE}.check_line_length", return_value=[]),
            patch("os.chdir") as mock_chdir,
        ):
            product.validate()

        # The FURNSH failure is swallowed, so the cwd restore still runs.
        assert mock_chdir.call_args_list[-1] == call(cwd)


# ===========================================================================
# MetaKernelProduct.coverage
# ===========================================================================

class TestMetaKernelProductCoverage:
    """Tests for MetaKernelProduct.coverage."""

    @staticmethod
    def _make_stub(setup, name="insight_v01.tm", collection=None,
                   collection_metakernel=None, year=None):
        product = object.__new__(MetaKernelProduct)
        product.setup = setup
        product.name = name
        product.collection = collection or MagicMock()
        product.collection_metakernel = collection_metakernel or []
        product.mk_setup = {}  # no coverage_kernels key by default
        product.mk_sets_coverage = False
        if year is not None:
            product.year = year
            product.YEAR = year
        return product

    @staticmethod
    def _make_collection_with_kernel(name, start, stop):
        """Return a collection mock whose product list contains one kernel."""
        mock_kernel = MagicMock()
        mock_kernel.name = name
        mock_kernel.start_time = start
        mock_kernel.stop_time = stop
        collection = MagicMock()
        collection.product = [mock_kernel]
        return collection

    @pytest.mark.parametrize("increment_start, increment_finish, expected_start, expected_stop", [
        (None, None,
         "2018-05-01T00:00:00Z", "2023-01-01T00:00:00Z"),
        ("2022-01-01T00:00:00Z", "2022-12-31T00:00:00Z",
         "2022-01-01T00:00:00Z", "2022-12-31T00:00:00Z"),
    ])
    def test_no_coverage_kernels_uses_times_from_config(
            self, lsk, increment_start, increment_finish, expected_start, expected_stop):
        setup = make_setup(
            mission_start="2018-05-01T00:00:00Z",
            mission_finish="2023-01-01T00:00:00Z",
            increment_start=increment_start,
            increment_finish=increment_finish,
        )
        product = self._make_stub(setup)
        product.coverage()
        assert product.start_time == expected_start
        assert product.stop_time == expected_stop

    @pytest.mark.parametrize("pattern", [
        r"insight_cru_ops_v\d+\.bsp",        # bare string — normalized to list
        [r"insight_cru_ops_v\d+\.bsp"],       # already a list
    ])
    def test_mk_sets_coverage_true_when_kernel_matches_pattern(self, lsk, pattern):
        setup = make_setup(
            mission_start="2018-01-01T00:00:00Z",
            mission_finish="2023-01-01T00:00:00Z",
            increment_start="2019-01-01T00:00:00Z",
            increment_finish="2019-12-31T00:00:00Z",
            date_format="infomod2",
        )
        collection = self._make_collection_with_kernel(
            "insight_cru_ops_v01.bsp",
            "2019-01-01T00:00:00Z",
            "2019-12-01T00:00:00Z",
        )
        product = self._make_stub(
            setup,
            collection=collection,
            collection_metakernel=["insight_cru_ops_v01.bsp"],
        )
        product.mk_setup = {"coverage_kernels": {"pattern": pattern}}
        product.coverage()
        assert product.mk_sets_coverage

    def test_mk_sets_coverage_false_when_no_pattern_matches(self, lsk):
        # When no kernel in collection_metakernel matches the pattern the flag
        # stays False.
        setup = make_setup(
            mission_start="2018-01-01T00:00:00Z",
            mission_finish="2023-01-01T00:00:00Z",
        )
        product = self._make_stub(
            setup,
            collection_metakernel=["naif0012.tls"],
        )
        product.mk_setup = {
            "coverage_kernels": {
                "pattern": [r"insight_cru_ops_v\d+\.bsp"]
            }
        }
        product.coverage()
        assert not product.mk_sets_coverage

    def test_coverage_from_collection_product_times(self, lsk):
        # when the matched coverage kernel is present in the
        # collection, its start/stop times are read directly (no file I/O).
        setup = make_setup(
            mission_start="2018-01-01T00:00:00Z",
            mission_finish="2023-01-01T00:00:00Z",
            date_format="infomod2",
        )
        collection = self._make_collection_with_kernel(
            "insight_cru_ops_v01.bsp",
            "2019-01-01T00:00:00Z",
            "2020-01-01T00:00:00Z",
        )
        product = self._make_stub(
            setup,
            collection=collection,
            collection_metakernel=["insight_cru_ops_v01.bsp"],
        )
        product.mk_setup = {
            "coverage_kernels": {
                "pattern": [r"insight_cru_ops_v\d+\.bsp"]
            }
        }
        product.coverage()
        assert product.start_time == "2019-01-01T00:00:00.000Z"
        assert product.stop_time == "2020-01-01T00:00:00.000Z"
        assert product.mk_sets_coverage

    def test_coverage_kernel_not_in_collection_missing_file_logs_warning(
            self, lsk, tmp_path, caplog):
        # when the kernel file is absent, only a warning is
        # emitted — no times are collected and the fallback path is used.
        setup = make_setup(
            bundle_directory=str(tmp_path / "bundle"),
            mission_start="2019-01-01T00:00:00Z",
            mission_finish="2023-01-01T00:00:00Z",
            mission_acronym="insight",
        )
        # Empty collection — kernel will not be found there.
        collection = MagicMock()
        collection.product = []
        product = self._make_stub(
            setup,
            collection=collection,
            collection_metakernel=["insight_cru_ops_v01.bsp"],
        )
        product.mk_setup = {
            "coverage_kernels": {
                "pattern": [r"insight_cru_ops_v\d+\.bsp"]
            }
        }
        with caplog.at_level(logging.INFO):
            product.coverage()

        expected = [
            (logging.WARNING, '-- File not present in final area: '
                              f'{tmp_path / "bundle/insight_spice/spice_kernels/spk/insight_cru_ops_v01.bsp"}.'),
            (logging.WARNING, '   It will not be used to determine the coverage.'),
            (logging.INFO, '-- Meta-kernel will be used to determine SPICE Collection coverage.'),
            (logging.WARNING, '-- No kernel(s) found to determine MK coverage. Times from '
                              'configuration will be used: 2019-01-01T00:00:00Z - 2023-01-01T00:00:00Z')
        ]
        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected

    def test_coverage_kernel_not_in_collection_spk_calls_spk_coverage(
            self, lsk, tmp_path):
        # when the coverage kernel is a missing SPK in the
        # collection but the file IS on disk, spk_coverage() is called.
        bundle_dir = tmp_path / "bundle"
        spk_dir = bundle_dir / "insight_spice" / "spice_kernels" / "spk"
        spk_dir.mkdir(parents=True)
        spk_file = spk_dir / "insight_cru_ops_v01.bsp"
        spk_file.write_bytes(b"\x00" * 16)  # non-empty dummy file

        setup = make_setup(
            bundle_directory=str(bundle_dir),
            mission_start="2018-01-01T00:00:00Z",
            mission_finish="2023-01-01T00:00:00Z",
            mission_acronym="insight",
            date_format="infomod2",
        )
        collection = MagicMock()
        collection.product = []
        product = self._make_stub(
            setup,
            collection=collection,
            collection_metakernel=["insight_cru_ops_v01.bsp"],
        )
        product.mk_setup = {
            "coverage_kernels": {
                "pattern": [r"insight_cru_ops_v\d+\.bsp"]
            }
        }
        with patch(f"{_MODULE}.spk_coverage",
                   return_value=("2019-01-01T00:00:00Z",
                                 "2020-01-01T00:00:00Z")) as mock_spk:
            product.coverage()

        mock_spk.assert_called_once_with(
            str(spk_file), main_name=setup.spice_name
        )
        # Coverage derives from the (mocked) SPK times, round-tripped through
        # et_to_date in the "infomod2" format.
        assert product.start_time == "2019-01-01T00:00:00.000Z"
        assert product.stop_time == "2020-01-01T00:00:00.000Z"

    def test_coverage_kernel_not_in_collection_ck_calls_ck_coverage(
            self, lsk, tmp_path):
        # when the coverage kernel is a CK missing from
        # the collection but present on disk, ck_coverage() is called.
        bundle_dir = tmp_path / "bundle"
        ck_dir = bundle_dir / "insight_spice" / "spice_kernels" / "ck"
        ck_dir.mkdir(parents=True)
        ck_file = ck_dir / "insight_ida_enc_v01.bc"
        ck_file.write_bytes(b"\x00" * 16)

        setup = make_setup(
            bundle_directory=str(bundle_dir),
            mission_start="2018-01-01T00:00:00Z",
            mission_finish="2023-01-01T00:00:00Z",
            mission_acronym="insight",
            date_format="infomod2",
        )
        collection = MagicMock()
        collection.product = []
        product = self._make_stub(
            setup,
            collection=collection,
            collection_metakernel=["insight_ida_enc_v01.bc"],
        )
        product.mk_setup = {
            "coverage_kernels": {
                "pattern": [r"insight_ida_enc_v\d+\.bc"]
            }
        }
        with patch(f"{_MODULE}.ck_coverage",
                   return_value=("2019-06-01T00:00:00Z",
                                 "2019-12-01T00:00:00Z")) as mock_ck:
            product.coverage()

        mock_ck.assert_called_once_with(str(ck_file))
        # Coverage derives from the (mocked) CK times, round-tripped through
        # et_to_date in the "infomod2" format.
        assert product.start_time == "2019-06-01T00:00:00.000Z"
        assert product.stop_time == "2019-12-01T00:00:00.000Z"

    def test_coverage_kernel_not_in_collection_non_spk_ck_raises(
            self, lsk, tmp_path):
        # when the coverage kernel is neither SPK nor CK, a RuntimeError
        # is raised.
        bundle_dir = tmp_path / "bundle"
        lsk_dir = bundle_dir / "insight_spice" / "spice_kernels" / "lsk"
        lsk_dir.mkdir(parents=True)
        (lsk_dir / "naif0012.tls").write_bytes(b"\x00" * 16)

        setup = make_setup(
            bundle_directory=str(bundle_dir),
            mission_start="2018-01-01T00:00:00Z",
            mission_finish="2023-01-01T00:00:00Z",
            mission_acronym="insight",
        )
        collection = MagicMock()
        collection.product = []
        product = self._make_stub(
            setup,
            collection=collection,
            collection_metakernel=["naif0012.tls"],
        )
        product.mk_setup = {
            "coverage_kernels": {
                "pattern": [r"naif\d+\.tls"]
            }
        }
        with pytest.raises(RuntimeError, match="not a SPK or CK kernel"):
            product.coverage()

    def test_collection_non_matching_product_skipped_in_coverage_loop(self, lsk):
        # when iterating over self.collection.product to find
        # a coverage kernel, products whose name does not match are skipped and
        # the loop continues to the next product.
        setup = make_setup(
            mission_start="2018-01-01T00:00:00Z",
            mission_finish="2023-01-01T00:00:00Z",
            date_format="infomod2",
        )
        matching = MagicMock()
        matching.name = "insight_cru_ops_v01.bsp"
        matching.start_time = "2019-01-01T00:00:00Z"
        matching.stop_time = "2020-01-01T00:00:00Z"
        unrelated = MagicMock()
        unrelated.name = "naif0012.tls"

        collection = MagicMock()
        collection.product = [unrelated, matching]  # unrelated first → False branch taken

        product = self._make_stub(
            setup,
            collection=collection,
            collection_metakernel=["insight_cru_ops_v01.bsp"],
        )
        product.mk_setup = {
            "coverage_kernels": {
                "pattern": [r"insight_cru_ops_v\d+\.bsp"]
            }
        }
        product.coverage()
        # The matching product's times are used even though the unrelated
        # product appears first in the collection.
        assert product.start_time == "2019-01-01T00:00:00.000Z"
        assert product.stop_time == "2020-01-01T00:00:00.000Z"

    @pytest.mark.parametrize("mission_start, mission_finish, kernel_start, kernel_stop, year, expected_start, expected_stop", [
        (   # year == mission_start year → start clamped to mission_start, not Jan 1
            "2018-05-01T00:00:00Z", "2023-01-01T00:00:00Z",
            "2018-06-01T00:00:00Z", "2018-12-01T00:00:00Z",
            "2018", "2018-05-01T00:00:00.000Z", "2018-12-01T00:00:00.000Z",
        ),
        (   # kernel stop extends past year-end → stop clamped to Jan 1 of next year
            "2018-01-01T00:00:00Z", "2023-01-01T00:00:00Z",
            "2022-01-15T00:00:00Z", "2023-06-01T00:00:00Z",
            "2022", "2022-01-01T00:00:00.000Z", "2023-01-01T00:00:00.000Z",
        ),
    ])
    def test_yearly_mk_coverage_boundary_clamping(
            self, lsk, mission_start, mission_finish,
            kernel_start, kernel_stop, year,
            expected_start, expected_stop):
        setup = make_setup(
            mission_start=mission_start,
            mission_finish=mission_finish,
            date_format="infomod2",
        )
        collection = self._make_collection_with_kernel(
            "insight_cru_ops_v01.bsp", kernel_start, kernel_stop,
        )
        product = self._make_stub(
            setup,
            collection=collection,
            collection_metakernel=["insight_cru_ops_v01.bsp"],
            year=year,
        )
        product.mk_setup = {
            "coverage_kernels": {"pattern": [r"insight_cru_ops_v\d+\.bsp"]}
        }
        product.coverage()
        assert product.start_time == expected_start
        assert product.stop_time == expected_stop

    @pytest.mark.parametrize("mission_start, mission_finish, increment_start, increment_finish, expected_start, expected_stop", [
        (   # year == mission_start year; Jan 1 still precedes it
            "2021-05-01T00:00:00Z", "2023-01-01T00:00:00Z",
            "2021-03-01T00:00:00Z", "2021-11-01T00:00:00Z",
            "2021-01-01T00:00:00Z", "2021-11-01T00:00:00Z",
        ),
        (   # year is after mission start year (common case)
            "2018-05-01T00:00:00Z", "2023-01-01T00:00:00Z",
            "2021-03-01T00:00:00Z", "2021-11-01T00:00:00Z",
            "2021-01-01T00:00:00Z", "2021-11-01T00:00:00Z",
        ),
        (   # increment_finish within year → stop = increment_finish
            "2018-01-01T00:00:00Z", "2023-01-01T00:00:00Z",
            "2021-01-01T00:00:00Z", "2021-09-15T00:00:00Z",
            "2021-01-01T00:00:00Z", "2021-09-15T00:00:00Z",
        ),
        (   # mission_finish within year → stop = mission_finish
            "2021-01-01T00:00:00Z", "2021-08-01T00:00:00Z",
            "2021-01-01T00:00:00Z", "2022-03-01T00:00:00Z",
            "2021-01-01T00:00:00Z", "2021-08-01T00:00:00Z",
        ),
        (   # both exceed year → stop = year-end
            "2021-01-01T00:00:00Z", "2022-06-01T00:00:00Z",
            "2021-01-01T00:00:00Z", "2022-03-01T00:00:00Z",
            "2021-01-01T00:00:00Z", "2022-01-01T00:00:00Z",
        ),
    ])
    def test_yearly_mk_exception_coverage(
            self, lsk, mission_start, mission_finish, increment_start,
            increment_finish, expected_start, expected_stop):
        setup = make_setup(
            mission_start=mission_start,
            mission_finish=mission_finish,
            increment_start=increment_start,
            increment_finish=increment_finish,
        )
        product = self._make_stub(setup, year="2021")
        product.coverage()
        assert product.start_time == expected_start
        assert product.stop_time == expected_stop


    @pytest.mark.parametrize("increment_start, increment_finish, expected_start, expected_stop", [
        (
            "2022-06-01T00:00:00Z", "2022-12-31T00:00:00Z",
            "2022-06-01T00:00:00Z", "2022-12-31T00:00:00Z",
        ),
        (
            "2022-01-01T00:00:00Z", "2022-08-15T00:00:00Z",
            "2022-01-01T00:00:00Z", "2022-08-15T00:00:00Z",
        ),
    ])
    def test_increment_corrects_coverage_times(
            self, lsk, increment_start, increment_finish, expected_start, expected_stop):
        setup = make_setup(
            mission_start="2018-01-01T00:00:00Z",
            mission_finish="2023-01-01T00:00:00Z",
            increment_start=increment_start,
            increment_finish=increment_finish,
        )
        product = self._make_stub(setup)
        product.coverage()
        assert product.start_time == expected_start
        assert product.stop_time == expected_stop

    @pytest.mark.parametrize("increment_start, increment_finish, kernel_start, kernel_stop, expected_start, expected_stop", [
        (   # increment same year as start → start corrected; same year as stop → stop corrected
            "2021-03-01T00:00:00Z", "2021-12-31T00:00:00Z",
            "2021-02-01T00:00:00Z", "2021-10-01T00:00:00Z",
            "2021-03-01T00:00:00.000Z", "2021-12-31T00:00:00.000Z",
        ),
        (   # increment different year from start → start unchanged; different year from stop → stop unchanged
            "2022-06-01T00:00:00Z", "2022-12-31T00:00:00Z",
            "2021-02-01T00:00:00Z", "2021-10-01T00:00:00Z",
            "2021-01-01T00:00:00.000Z", "2021-10-01T00:00:00.000Z",
        ),
        (   # increment same year as stop → stop corrected; same year as start → start corrected
            "2021-01-01T00:00:00Z", "2021-09-15T00:00:00Z",
            "2021-02-01T00:00:00Z", "2021-11-01T00:00:00Z",
            "2021-01-01T00:00:00.000Z", "2021-09-15T00:00:00.000Z",
        ),
        (   # increment same year as start → start corrected; different year from stop → stop unchanged
            "2021-01-01T00:00:00Z", "2022-06-01T00:00:00Z",
            "2021-02-01T00:00:00Z", "2021-10-01T00:00:00Z",
            "2021-01-01T00:00:00.000Z", "2021-10-01T00:00:00.000Z",
        ),
    ])
    def test_increment_corrects_yearly_mk_coverage(
            self, lsk, increment_start, increment_finish,
            kernel_start, kernel_stop,
            expected_start, expected_stop):
        setup = make_setup(
            mission_start="2018-01-01T00:00:00Z",
            mission_finish="2023-01-01T00:00:00Z",
            increment_start=increment_start,
            increment_finish=increment_finish,
            date_format="infomod2",
        )
        collection = self._make_collection_with_kernel(
            "insight_cru_ops_v01.bsp", kernel_start, kernel_stop,
        )
        product = self._make_stub(
            setup,
            collection=collection,
            collection_metakernel=["insight_cru_ops_v01.bsp"],
            year="2021",
        )
        product.mk_setup = {
            "coverage_kernels": {"pattern": [r"insight_cru_ops_v\d+\.bsp"]}
        }
        product.coverage()
        assert product.start_time == expected_start
        assert product.stop_time == expected_stop

    # ------------------------------------------------------------------
    # Success path: PDS3 uses TDB time system
    # ------------------------------------------------------------------

    def test_pds3_version_uses_tdb_system(self, lsk):
        # for a PDS3 MK, et_to_date is called with
        # system="TDB", producing times offset from UTC by the ET-UTC delta.
        setup = make_setup(
            pds_version="3",
            mission_start="2018-01-01T00:00:00Z",
            mission_finish="2023-01-01T00:00:00Z",
            date_format="infomod2",
        )
        collection = self._make_collection_with_kernel(
            "insight_cru_ops_v01.bsp",
            "2019-01-01T00:00:00Z",
            "2020-01-01T00:00:00Z",
        )
        product = self._make_stub(
            setup,
            collection=collection,
            collection_metakernel=["insight_cru_ops_v01.bsp"],
        )
        product.mk_setup = {
            "coverage_kernels": {
                "pattern": [r"insight_cru_ops_v\d+\.bsp"]
            }
        }
        with patch(f"{_MODULE}.et_to_date",
                   return_value=("2019-01-01T00:00:00Z",
                                 "2020-01-01T00:00:00Z")) as mock_et2date:
            product.coverage()

        assert mock_et2date.call_args.kwargs["system"] == "TDB"
