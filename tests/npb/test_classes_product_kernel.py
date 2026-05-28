"""Unit tests for SpiceKernelProduct class."""
import os
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from pds.naif_pds4_bundler.classes.product.product_kernel import SpiceKernelProduct

# ---------------------------------------------------------------------------
# Helpers / shared fixtures
# ---------------------------------------------------------------------------

def make_setup(
    pds_version="4",
    staging_directory=None,
    kernels_directory=None,
    working_directory=None,
    mission_acronym="test",
    run_type="release",
    release=1,
    logical_identifier="urn:nasa:pds:test_bundle",
    spice_name="TEST",
    date_format="UTC",
    mission_start="2000-01-01T00:00:00Z",
    mission_finish="2025-01-01T00:00:00Z",
):
    """Return a minimal mock Setup object."""
    setup = MagicMock()
    setup.pds_version = pds_version
    setup.staging_directory = staging_directory or "/staging"
    setup.kernels_directory = kernels_directory or ["/kernels"]
    setup.working_directory = working_directory or "/work"
    setup.mission_acronym = mission_acronym
    setup.run_type = run_type
    setup.release = release
    setup.logical_identifier = logical_identifier
    setup.spice_name = spice_name
    setup.date_format = date_format
    setup.mission_start = mission_start
    setup.mission_finish = mission_finish
    return setup


def make_collection(missions=None, observers=None, targets=None):
    """Return a minimal mock collection object."""
    collection = MagicMock()
    collection.get_mission_and_observer_and_target.return_value = (
        missions or ["TEST_MISSION"],
        observers or ["SPACECRAFT"],
        targets or ["MARS"],
    )
    return collection


# Patch targets used throughout
_MODULE = "pds.naif_pds4_bundler.classes.product.product_kernel"


# ---------------------------------------------------------------------------
# Fixture: temporary real directory tree so shutil.copy2 works in __init__
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_env(tmp_path):
    """Create a minimal on-disk environment for SpiceKernelProduct.__init__."""
    kernel_dir = tmp_path / "kernels"
    kernel_dir.mkdir()
    staging = tmp_path / "staging"
    staging.mkdir()
    work = tmp_path / "work"
    work.mkdir()
    return {
        "tmp_path": tmp_path,
        "kernel_dir": str(kernel_dir),
        "staging": str(staging),
        "work": str(work),
    }


def write_kernel_file(env, name):
    """Write a dummy kernel file to the kernel directory and return its path."""
    path = os.path.join(env["kernel_dir"], name)
    with open(path, "wb") as f:
        f.write(b"\x00" * 16)
    return path


def write_kernel_list(env, setup, name, description="Test kernel desc",
                      maklabel_options="MAKLABEL_OPT"):
    """Write a minimal .kernel_list file."""
    kl_path = os.path.join(
        env["work"],
        f"{setup.mission_acronym}_{setup.run_type}_{int(setup.release):02d}.kernel_list",
    )
    with open(kl_path, "w", encoding="utf-8") as f:
        f.write(f"FILE             = {name}\n"
                f"DESCRIPTION      = {description}\n"
                f"MAKLABEL_OPTIONS = {maklabel_options}\n")
    return kl_path


# ---------------------------------------------------------------------------
# Utility: build a fully-constructed SpiceKernelProduct via __init__
# ---------------------------------------------------------------------------

def build_product(env, name="test.bsp", pds_version="4", extra_setup_kwargs=None):
    """
    Construct a real SpiceKernelProduct with all heavy collaborators mocked.
    Returns (product, setup, collection).
    """
    extra_setup_kwargs = extra_setup_kwargs or {}
    setup = make_setup(
        pds_version=pds_version,
        staging_directory=env["staging"],
        kernels_directory=[env["kernel_dir"]],
        working_directory=env["work"],
        **extra_setup_kwargs,
    )
    collection = make_collection()

    write_kernel_file(env, name)
    write_kernel_list(env, setup, name)

    with (
        patch(f"{_MODULE}.extension_to_type", return_value="spk"),
        patch(f"{_MODULE}.safe_make_directory"),
        patch(f"{_MODULE}.product_mapping", return_value=name),
        patch(f"{_MODULE}.shutil.copy2"),
        patch(f"{_MODULE}.spk_coverage", return_value=["2000-01-01T00:00:00Z", "2020-01-01T00:00:00Z"]),
        patch(f"{_MODULE}.ck_coverage", return_value=["2000-01-01T00:00:00Z", "2020-01-01T00:00:00Z"]),
        patch(f"{_MODULE}.pck_coverage", return_value=["2000-01-01T00:00:00Z", "2020-01-01T00:00:00Z"]),
        patch(f"{_MODULE}.dsk_coverage", return_value=["2000-01-01T00:00:00Z", "2020-01-01T00:00:00Z"]),
        patch(f"{_MODULE}.Product.__init__", return_value=None),
        patch(f"{_MODULE}.SpiceKernelPDS4Label", return_value=MagicMock()),
        patch(f"{_MODULE}.SpiceKernelPDS3Label", return_value=MagicMock()),
    ):
        product = SpiceKernelProduct(setup, name, collection)

    return product, setup, collection


# ===========================================================================
# SpiceKernelProduct.__init__
# ===========================================================================

class TestSpiceKernelProductInit:
    """Tests for SpiceKernelProduct.__init__, product_lid, and product_vid."""

    def test_pds4_binary_kernel_sets_binary_file_format(self, tmp_env):
        product, _, _ = build_product(tmp_env, name="test.bsp", pds_version="4")
        assert product.file_format == "Binary"

    def test_pds4_text_kernel_sets_character_file_format(self, tmp_env):
        product, _, _ = build_product(tmp_env, name="test.tls", pds_version="4")
        # extension_to_type is mocked; just verify Character branch
        assert product.file_format == "Character"

    def test_pds4_lid_format(self, tmp_env):
        product, setup, _ = build_product(tmp_env, name="test.bsp", pds_version="4")
        expected = f"{setup.logical_identifier}:spice_kernels:spk_test.bsp".lower()
        assert product.lid == expected

    def test_pds4_vid_is_one_dot_zero(self, tmp_env):
        product, _, _ = build_product(tmp_env, name="test.bsp", pds_version="4")
        assert product.vid == "1.0"

    def test_pds4_collection_path_uses_spice_kernels_dir(self, tmp_env):
        setup = make_setup(pds_version="4", staging_directory=tmp_env["staging"],
                           kernels_directory=[tmp_env["kernel_dir"]],
                           working_directory=tmp_env["work"])
        collection = make_collection()
        write_kernel_file(tmp_env, "test.bsp")
        write_kernel_list(tmp_env, setup, "test.bsp")

        with (
            patch(f"{_MODULE}.extension_to_type", return_value="spk"),
            patch(f"{_MODULE}.safe_make_directory"),
            patch(f"{_MODULE}.shutil.copy2"),
            patch(f"{_MODULE}.spk_coverage", return_value=["2000T", "2020T"]),
            patch(f"{_MODULE}.Product.__init__", return_value=None),
            patch(f"{_MODULE}.SpiceKernelPDS4Label", return_value=MagicMock()),
        ):
            product = SpiceKernelProduct.__new__(SpiceKernelProduct)
            product.__init__(setup, "test.bsp", collection)

        assert product.collection_path == str(Path(f"{tmp_env['staging']}/spice_kernels/"))

    def test_pds3_binary_kernel_sets_binary_file_format(self, tmp_env):
        product, _, _ = build_product(tmp_env, name="test.bsp", pds_version="3")
        assert product.file_format == "BINARY"
        assert product.record_type == "FIXED_LENGTH"
        assert product.record_bytes == "1024"

        assert product.collection_path == str(Path(f"{tmp_env['staging']}/data/"))
        assert product.maklabel_options == ['MAKLABEL_OPT']

    def test_pds3_text_kernel_sets_ascii_file_format(self, tmp_env):
        product, _, _ = build_product(tmp_env, name="test.tls", pds_version="3")
        assert product.file_format == "ASCII"
        assert product.record_type == "STREAM"
        assert product.record_bytes == '"N/A"'

        assert product.collection_path == str(Path(f"{tmp_env['staging']}/data/"))
        assert product.maklabel_options == ['MAKLABEL_OPT']

    def test_kernel_already_in_staging_sets_new_product_true(self, tmp_env):
        """When kernel already exists in staging, new_product should still be True."""
        setup = make_setup(
            pds_version="4",
            staging_directory=tmp_env["staging"],
            kernels_directory=[tmp_env["kernel_dir"]],
            working_directory=tmp_env["work"],
        )
        collection = make_collection()

        # Pre-create the file in the staging path that __init__ will check
        spk_dir = os.path.join(tmp_env["staging"], "spice_kernels", "spk")
        os.makedirs(spk_dir, exist_ok=True)
        with open(os.path.join(spk_dir, "test.bsp"), "wb") as f:
            f.write(b"\x00")

        write_kernel_list(tmp_env, setup, "test.bsp")

        with (
            patch(f"{_MODULE}.extension_to_type", return_value="spk"),
            patch(f"{_MODULE}.safe_make_directory"),
            patch(f"{_MODULE}.spk_coverage", return_value=["2000T", "2020T"]),
            patch(f"{_MODULE}.Product.__init__", return_value=None),
            patch(f"{_MODULE}.SpiceKernelPDS4Label", return_value=MagicMock()),
        ):
            product = SpiceKernelProduct(setup, "test.bsp", collection)

        assert product.new_product is True

    def test_kernel_found_via_mapping_on_second_loop(self, tmp_env):
        """If direct name lookup fails, fallback to product_mapping."""
        setup = make_setup(
            pds_version="4",
            staging_directory=tmp_env["staging"],
            kernels_directory=[tmp_env["kernel_dir"]],
            working_directory=tmp_env["work"],
        )
        collection = make_collection()
        # Write file with a different name that mapping resolves to
        write_kernel_file(tmp_env, "mapped_test.bsp")
        write_kernel_list(tmp_env, setup, "test.bsp")

        with (
            patch(f"{_MODULE}.extension_to_type", return_value="spk"),
            patch(f"{_MODULE}.safe_make_directory"),
            patch(f"{_MODULE}.product_mapping", return_value="mapped_test.bsp"),
            patch(f"{_MODULE}.shutil.copy2"),
            patch(f"{_MODULE}.spk_coverage", return_value=["2000T", "2020T"]),
            patch(f"{_MODULE}.Product.__init__", return_value=None),
            patch(f"{_MODULE}.SpiceKernelPDS4Label", return_value=MagicMock()),
        ):
            product = SpiceKernelProduct(setup, "test.bsp", collection)

        assert product.new_product is True

    def test_missing_kernel_raises_error(self, tmp_env):
        setup = make_setup(
            pds_version="4",
            staging_directory=tmp_env["staging"],
            kernels_directory=[tmp_env["kernel_dir"]],
            working_directory=tmp_env["work"],
        )
        collection = make_collection()
        # Do NOT write any kernel file

        with (
            patch(f"{_MODULE}.extension_to_type", return_value="spk"),
            patch(f"{_MODULE}.safe_make_directory"),
            patch(f"{_MODULE}.product_mapping", return_value="nonexistent.bsp"),
            patch(f"{_MODULE}.handle_npb_error", side_effect=RuntimeError("not found")) as mock_err,
        ):
            with pytest.raises(RuntimeError, match="not found"):
                SpiceKernelProduct(setup, "missing.bsp", collection)

        mock_err.assert_called_once()

    def test_init_stores_missions_observers_targets(self, tmp_env):
        product, _, _ = build_product(tmp_env, name="test.bsp")
        assert product.missions == ["TEST_MISSION"]
        assert product.observers == ["SPACECRAFT"]
        assert product.targets == ["MARS"]

    def test_pds4_label_is_created(self, tmp_env):
        with (
            patch(f"{_MODULE}.extension_to_type", return_value="spk"),
            patch(f"{_MODULE}.safe_make_directory"),
            patch(f"{_MODULE}.shutil.copy2"),
            patch(f"{_MODULE}.spk_coverage", return_value=["2000T", "2020T"]),
            patch(f"{_MODULE}.Product.__init__", return_value=None),
            patch(f"{_MODULE}.SpiceKernelPDS4Label") as mock_label,
        ):
            setup = make_setup(
                pds_version="4",
                staging_directory=tmp_env["staging"],
                kernels_directory=[tmp_env["kernel_dir"]],
                working_directory=tmp_env["work"],
            )
            write_kernel_file(tmp_env, "test.bsp")
            write_kernel_list(tmp_env, setup, "test.bsp")
            collection = make_collection()

            SpiceKernelProduct(setup, "test.bsp", collection)

        mock_label.assert_called_once()

    def test_pds3_label_is_created(self, tmp_env):
        with (
            patch(f"{_MODULE}.extension_to_type", return_value="spk"),
            patch(f"{_MODULE}.safe_make_directory"),
            patch(f"{_MODULE}.shutil.copy2"),
            patch(f"{_MODULE}.spk_coverage", return_value=["2000T", "2020T"]),
            patch(f"{_MODULE}.Product.__init__", return_value=None),
            patch(f"{_MODULE}.SpiceKernelPDS3Label") as mock_label,
        ):
            setup = make_setup(
                pds_version="3",
                staging_directory=tmp_env["staging"],
                kernels_directory=[tmp_env["kernel_dir"]],
                working_directory=tmp_env["work"],
            )
            write_kernel_file(tmp_env, "test.bsp")
            write_kernel_list(tmp_env, setup, "test.bsp")
            collection = make_collection()

            SpiceKernelProduct(setup, "test.bsp", collection)

        mock_label.assert_called_once()


# ===========================================================================
# SpiceKernelProduct.read_description
# ===========================================================================

class TestSpiceKernelProductReadDescription:
    """Tests for SpiceKernelProduct.read_description."""

    @staticmethod
    def _make_product_stub(setup):
        product = SpiceKernelProduct.__new__(SpiceKernelProduct)
        product.setup = setup
        product.name = "test.bsp"
        return product

    def test_returns_description_when_present(self, tmp_env):
        setup = make_setup(working_directory=tmp_env["work"])
        write_kernel_list(tmp_env, setup, "test.bsp", description="My kernel description")
        product = self._make_product_stub(setup)
        desc = product.read_description()
        assert desc == "My kernel description"

    def test_raises_error_when_description_missing(self, tmp_env):
        setup = make_setup(working_directory=tmp_env["work"])
        # Write a kernel_list with NO DESCRIPTION line for "test.bsp"
        kl_path = os.path.join(
            tmp_env["work"],
            f"{setup.mission_acronym}_{setup.run_type}_{int(setup.release):02d}.kernel_list",
        )
        with open(kl_path, "w", encoding="utf-8") as f:
            f.write("FILE = other_kernel.bsp\n"
                    "DESCRIPTION = something else\n")

        product = self._make_product_stub(setup)

        with patch(f"{_MODULE}.handle_npb_error", side_effect=RuntimeError("no desc")) as mock_err:
            with pytest.raises(RuntimeError, match="no desc"):
                product.read_description()

        mock_err.assert_called_once()

    def test_description_stripped_of_whitespace(self, tmp_env):
        setup = make_setup(working_directory=tmp_env["work"])
        write_kernel_list(tmp_env, setup, "test.bsp", description="  Stripped desc  ")
        product = self._make_product_stub(setup)
        desc = product.read_description()
        # strip() is applied in the implementation
        assert desc == "Stripped desc"


# ===========================================================================
# SpiceKernelProduct.read_maklabel_options
# ===========================================================================

class TestSpiceKernelProductReadMaklabelOptions:
    """Tests for SpiceKernelProduct.read_maklabel_options."""

    @staticmethod
    def _make_product_stub(setup):
        product = SpiceKernelProduct.__new__(SpiceKernelProduct)
        product.setup = setup
        product.name = "test.bsp"
        return product

    def test_returns_maklabel_options_as_list(self, tmp_env):
        setup = make_setup(working_directory=tmp_env["work"])
        write_kernel_list(tmp_env, setup, "test.bsp", maklabel_options="-SPICE OPTION2")
        product = self._make_product_stub(setup)
        opts = product.read_maklabel_options()
        assert opts == ['-SPICE', 'OPTION2']

    def test_raises_error_when_maklabel_options_missing(self, tmp_env):
        setup = make_setup(working_directory=tmp_env["work"])
        kl_path = os.path.join(
            tmp_env["work"],
            f"{setup.mission_acronym}_{setup.run_type}_{int(setup.release):02d}.kernel_list",
        )
        with open(kl_path, "w", encoding="utf-8") as f:
            f.write("FILE = other.bsp\n")

        product = self._make_product_stub(setup)

        with patch(f"{_MODULE}.handle_npb_error", side_effect=RuntimeError("no maklabel")) as mock_err:
            with pytest.raises(RuntimeError, match="no maklabel"):
                product.read_maklabel_options()

        mock_err.assert_called_once()

    def test_get_token_resets_after_finding_options(self, tmp_env):
        """MAKLABEL_OPTIONS found -> get_token set to False; last match returned."""
        setup = make_setup(working_directory=tmp_env["work"])
        kl_path = os.path.join(
            tmp_env["work"],
            f"{setup.mission_acronym}_{setup.run_type}_{int(setup.release):02d}.kernel_list",
        )
        with open(kl_path, "w", encoding="utf-8") as f:
            f.write("FILE             = test.bsp\n"
                    "MAKLABEL_OPTIONS = -OPT1\n"
                    "FILE             = test.bsp\n"
                    "MAKLABEL_OPTIONS = -OPT2\n")

        product = self._make_product_stub(setup)
        opts = product.read_maklabel_options()
        # The last match is returned
        assert opts == ["-OPT2"]


# ===========================================================================
# SpiceKernelProduct.coverage
# ===========================================================================

class TestSpiceKernelProductCoverage:
    """Tests for SpiceKernelProduct.coverage."""

    @staticmethod
    def _make_product_stub(setup, kernel_type, extension, path):
        product = SpiceKernelProduct.__new__(SpiceKernelProduct)
        product.setup = setup
        product.type = kernel_type
        product.extension = extension
        product.path = path
        return product

    def test_coverage_from_existing_label(self, tmp_path):
        """If an XML label already exists, coverage is read from it."""
        setup = make_setup(pds_version="4")
        label_path = str(tmp_path / "fake.xml")
        kernel_path = str(tmp_path / "fake.bsp")

        with open(label_path, "w") as f:
            f.write("<start_date_time>2001-01-01T00:00:00Z</start_date_time>\n")
            f.write("<stop_date_time>2010-01-01T00:00:00Z</stop_date_time>\n")

        product = self._make_product_stub(setup, "spk", "bsp", path=kernel_path)
        product.coverage()

        assert product.start_time == "2001-01-01T00:00:00Z"
        assert product.stop_time == "2010-01-01T00:00:00Z"

    def test_spk_coverage_pds4(self, tmp_path):
        setup = make_setup(pds_version="4")
        kernel_path = str(tmp_path / "fake.bsp")
        product = self._make_product_stub(setup, "spk", "bsp", path=kernel_path)

        with patch(f"{_MODULE}.spk_coverage", return_value=["2000T", "2020T"]) as mock_spk:
            product.coverage()

        mock_spk.assert_called_once_with(
            kernel_path,
            main_name=setup.spice_name,
            date_format=setup.date_format,
            system="UTC",
        )
        assert product.start_time == "2000T"
        assert product.stop_time == "2020T"

    def test_spk_coverage_pds3_no_main_name(self, tmp_path):
        setup = make_setup(pds_version="3")
        kernel_path = str(tmp_path / "fake.bsp")
        product = self._make_product_stub(setup, "spk", "bsp", path=kernel_path)

        with patch(f"{_MODULE}.spk_coverage", return_value=["2000T", "2020T"]) as mock_spk:
            product.coverage()

        mock_spk.assert_called_once_with(
            kernel_path,
            main_name=False,
            date_format=setup.date_format,
            system="UTC",
        )

    def test_ck_coverage(self, tmp_path):
        setup = make_setup(pds_version="4")
        kernel_path = str(tmp_path / "fake.bc")
        product = self._make_product_stub(setup, "ck", "bc", path=kernel_path)

        with patch(f"{_MODULE}.ck_coverage", return_value=["2001T", "2021T"]) as mock_ck:
            product.coverage()

        mock_ck.assert_called_once()
        assert product.start_time == "2001T"

    def test_pck_coverage_for_bpc_extension(self, tmp_path):
        setup = make_setup(pds_version="4")
        kernel_path = str(tmp_path / "fake.bpc")
        product = self._make_product_stub(setup, "pck", "bpc", path=kernel_path)

        with patch(f"{_MODULE}.pck_coverage", return_value=["2002T", "2022T"]) as mock_pck:
            product.coverage()

        mock_pck.assert_called_once()
        assert product.stop_time == "2022T"

    def test_dsk_coverage(self, tmp_path):
        setup = make_setup(pds_version="4")
        kernel_path = str(tmp_path / "fake.bds")
        product = self._make_product_stub(setup, "dsk", "bds", path=kernel_path)

        with patch(f"{_MODULE}.dsk_coverage", return_value=["2003T", "2023T"]) as mock_dsk:
            product.coverage()

        mock_dsk.assert_called_once()
        assert product.start_time == "2003T"

    def test_other_kernel_pds4_uses_mission_times(self, tmp_path):
        setup = make_setup(pds_version="4", mission_start="2005T", mission_finish="2025T")
        kernel_path = str(tmp_path / "fake.tls")
        product = self._make_product_stub(setup, "lsk", "tls", path=kernel_path)
        product.coverage()
        assert product.start_time == "2005T"
        assert product.stop_time == "2025T"

    def test_other_kernel_pds3_uses_na_times(self, tmp_path):
        setup = make_setup(pds_version="3")
        kernel_path = str(tmp_path / "fake.tls")
        product = self._make_product_stub(setup, "lsk", "tls", path=kernel_path)
        product.coverage()
        assert product.start_time == '"N/A"'
        assert product.stop_time == '"N/A"'

    def test_no_existing_label_triggers_computation(self, tmp_path):
        """When no XML label exists, coverage function is called (not skipped)."""
        setup = make_setup(pds_version="4")
        kernel_path = str(tmp_path / "no_label.bsp")
        # Ensure XML label does not exist
        product = self._make_product_stub(setup, "spk", "bsp", path=kernel_path)

        with patch(f"{_MODULE}.spk_coverage", return_value=["1999T", "2019T"]) as mock_spk:
            product.coverage()

        mock_spk.assert_called_once()

    # TODO: This test shows that in the event of a label without coverage information,
    #       the `coverage` method will compute it from the kernel. But, is this a valid
    #       input label? Should the user be informed about this?
    def test_existing_label_without_coverage_info_triggers_computation(self, tmp_path):
        """When no XML label exists, coverage function is called (not skipped)."""
        setup = make_setup(pds_version="4")
        label_path = str(tmp_path / "fake.xml")
        kernel_path = str(tmp_path / "fake.bsp")

        with open(label_path, "w") as f:
            f.write("No_coverage_information_provided\n")

        # Ensure XML label does not exist
        product = self._make_product_stub(setup, "spk", "bsp", path=kernel_path)

        with patch(f"{_MODULE}.spk_coverage", return_value=["1999T", "2019T"]) as mock_spk:
            product.coverage()

        mock_spk.assert_called_once()


# ===========================================================================
# TestCkKernelIds
# ===========================================================================

class TestCkKernelIds:
    """Tests for SpiceKernelProduct.ck_kernel_ids."""

    @staticmethod
    def _make_product_stub(path):
        product = SpiceKernelProduct.__new__(SpiceKernelProduct)
        product.path = path
        return product

    @pytest.mark.parametrize('ids, expected_str', [
        ([-100, -200, -300], '-300,-200,-100'),
        ([-99], '-99'),
        ([-300, -100, -200], '-300,-200,-100'),
        ([], '')
    ])
    def test_ck_kernel_ids(self, tmp_path, ids, expected_str):
        with patch(f"{_MODULE}.spiceypy.ckobj", return_value=ids):
            product = self._make_product_stub(path=tmp_path / "fake.bc")
            product.ck_kernel_ids()
            result = product.ck_kernel_ids()

        assert result == expected_str

# ===========================================================================
# TestIkKernelIds
# ===========================================================================

class TestIkKernelIds:
    """Tests for SpiceKernelProduct.ik_kernel_ids."""

    @staticmethod
    def _run_with_content(path, content):
        product = SpiceKernelProduct.__new__(SpiceKernelProduct)
        product.path = path / "fake.ti"

        m = mock_open(read_data=content)
        with patch("builtins.open", m):
            return product.ik_kernel_ids()

    def test_extracts_ids_from_begindata_section(self, tmp_path):
        content = (
            "\\begindata\n"
            "INS-12345_FOV_SHAPE = 'CIRCLE'\n"
            "\\begintext\n"
        )
        result = self._run_with_content(tmp_path, content)
        assert result == "-12345"

    def test_ignores_ids_outside_begindata(self, tmp_path):
        content = (
            "\\begintext\n"
            "INS-99999_COMMENT = 'ignored'\n"
            "\\begindata\n"
            "INS-11111_FOV = 1.0\n"
        )
        result = self._run_with_content(tmp_path, content)

        assert result == "-11111"

    def test_deduplicates_ids(self, tmp_path):
        content = (
            "\\begindata\n"
            "INS-55555_FOV_SHAPE = 'CIRCLE'\n"
            "INS-55555_FOV_SIZE = 1.0\n"
        )
        result = self._run_with_content(tmp_path, content)
        assert result == "-55555"

    def test_multiple_distinct_ids(self, tmp_path):
        content = (
            "\\begindata\n"
            "INS-11111_FOV = 1.0\n"
            "INS-22222_FOV = 2.0\n"
        )
        result = self._run_with_content(tmp_path, content)
        assert result == '-11111,-22222'

    def test_empty_file_returns_empty_string(self, tmp_path):
        result = self._run_with_content(tmp_path,"")
        assert result == ""

    def test_parse_bool_toggled_by_begintext(self, tmp_path):
        """IDs after begintext and before next begindata should be skipped."""
        content = (
            "\\begindata\n"
            "INS-11111_FOV = 1.0\n"
            "\\begintext\n"
            "INS-22222_IGNORE = 1\n"
            "\\begindata\n"
            "INS-33333_FOV = 1.0\n"
        )
        result = self._run_with_content(tmp_path, content)
        assert result == '-11111,-33333'
