import datetime
import logging
import os
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

import pytest

from pds.naif_pds4_bundler.classes.product.product import Product
from pds.naif_pds4_bundler.classes.product.product_orbnum import OrbnumFileProduct

MOD = 'pds.naif_pds4_bundler.classes.product.product_orbnum'

ORBNUM_CONTENT = (
    " No.   Event UTC PERI\n"
    " ===== ====================\n"
    "     1  2020 JAN 01 00:00:00\n"
)


@pytest.fixture
def mock_setup(tmp_path):
    orbnum_dir = tmp_path / "orbnum_dir"
    orbnum_dir.mkdir()
    (orbnum_dir / "test_file.orb").write_text(ORBNUM_CONTENT)

    setup = MagicMock()
    setup.orbnum_directory = str(orbnum_dir)
    setup.staging_directory = str(tmp_path / "staging_dir")
    setup.bundle_directory = str(tmp_path / "bundle_dir")
    setup.pds_version = "4"
    setup.logical_identifier = "urn:nasa:pds:test"
    setup.mission_acronym = "test_mission"
    setup.eol = "\r\n"
    setup.target = "mars"
    setup.information_model_float = 1007000000.0
    setup.spice_name = "test_spice"
    setup.orbnum = [
        {
            "pattern": r".*\.orb",
            "header_start_line": "1",
            "event_detection_frame": {"description": "Frame Desc", "spice_name": "FRAME_NAME"},
            "pck": {"description": "PCK Desc", "kernel_name": "pck.tpc"},
            "author": "Test Author",
            "mission_name": "Test Mission",
            "observer": "Test Observer",
            "target": "Test Target",
        }
    ]
    return setup


@pytest.fixture
def mock_collection():
    collection = MagicMock()
    collection.get_mission_and_observer_and_target.return_value = (["mission1"], ["obs1"], ["target1"])
    return collection


@pytest.fixture
def mock_kernels_collection():
    collection = MagicMock()
    collection.list.kernel_list = ["test_file.orb", "other.orb"]
    return collection


class TestOrbnumFileProductInit:
    """Test the __init__ method (integrates set_product_lid and set_product_vid)."""

    def test_init_no_matching_pattern(self, mock_setup, mock_collection, mock_kernels_collection):
        """Test initialization fails if filename does not match pattern."""
        mock_setup.orbnum[0]["pattern"] = r"nomatch\.txt"
        with pytest.raises(RuntimeError, match="The orbnum file does not match any type "
                                               "described in the configuration."):
            OrbnumFileProduct(mock_setup, "test_file.orb", mock_collection, mock_kernels_collection)

    @patch.object(Product, "register")
    @patch(f"{MOD}.OrbnumFilePDS4Label")
    @patch(f"{MOD}.safe_make_directory")
    @patch(f"{MOD}.shutil.copy2")
    @patch(f"{MOD}.os.path.isfile", return_value=False)
    @patch(f"{MOD}.check_eol", return_value=True)
    @patch(f"{MOD}.add_crs_to_file")
    @patch.object(OrbnumFileProduct, "read_header", return_value=["Event UTC PERI", "==="])
    @patch.object(OrbnumFileProduct, "set_event_detection_key")
    @patch.object(OrbnumFileProduct, "get_header_length", return_value=100)
    @patch.object(OrbnumFileProduct, "set_previous_orbnum")
    @patch.object(OrbnumFileProduct, "read_records", return_value=10)
    @patch.object(OrbnumFileProduct, "get_sample_record", return_value="sample record")
    @patch.object(OrbnumFileProduct, "get_description", return_value="desc")
    @patch.object(OrbnumFileProduct, "table_character_description", return_value="table desc")
    @patch.object(OrbnumFileProduct, "get_params")
    @patch.object(OrbnumFileProduct, "set_params")
    @patch.object(OrbnumFileProduct, "coverage")
    def test_init_pds4_new_file(
        self,
        mock_coverage, _mock_set_params, _mock_get_params, _mock_table_char,
        _mock_get_desc, _mock_get_sample, _mock_read_records, _mock_set_prev,
        _mock_get_header_len, _mock_set_event, _mock_read_header, _mock_add_crs,
        mock_check_eol, _mock_isfile, _mock_copy2, _mock_safe_mkdir, _mock_label,
        _mock_register,
        mock_setup, mock_collection, mock_kernels_collection):
        """Test full PDS4 initialization with a new file."""
        obj = OrbnumFileProduct(mock_setup, "test_file.orb", mock_collection, mock_kernels_collection)

        assert obj.extension == "orb"
        assert obj.new_product is True
        assert obj.lid == "urn:nasa:pds:test:miscellaneous:orbnum_test_file.orb"  # Tests set_product_lid
        assert obj.vid == "1.0"  # Tests set_product_vid
        assert obj.missions == ["Test Mission"]
        assert obj.observers == ["Test Observer"]
        assert obj.targets == ["Test Target"]
        mock_check_eol.assert_called_once()
        mock_coverage.assert_called_once()

    @patch.object(Product, "register")
    @patch(f"{MOD}.safe_make_directory")
    @patch(f"{MOD}.os.path.isfile", return_value=True)
    def test_init_pds3(self, _mock_isfile, _mock_safe_mkdir, _mock_register, mock_setup, mock_collection, mock_kernels_collection):
        """Test PDS3 initialization (skips PDS4 specific logic)."""
        setup = mock_setup
        setup.pds_version = "3"
        # Remove overrides to test fallback
        del setup.orbnum[0]["mission_name"]
        del setup.orbnum[0]["observer"]
        del setup.orbnum[0]["target"]

        obj = OrbnumFileProduct(setup, "test_file.orb", mock_collection, mock_kernels_collection)

        assert obj.new_product is False
        assert obj.path == str(Path(setup.staging_directory, 'extras/orbnum/test_file.orb'))
        assert not hasattr(obj, "lid")

    @patch.object(Product, "register")
    @patch(f"{MOD}.OrbnumFilePDS4Label")
    @patch(f"{MOD}.safe_make_directory")
    @patch(f"{MOD}.os.path.isfile", return_value=True)
    @patch(f"{MOD}.check_eol", return_value=False)
    @patch(f"{MOD}.add_crs_to_file")
    @patch.object(OrbnumFileProduct, "read_header", return_value=["Event UTC PERI", "==="])
    @patch.object(OrbnumFileProduct, "set_event_detection_key")
    @patch.object(OrbnumFileProduct, "get_header_length", return_value=100)
    @patch.object(OrbnumFileProduct, "set_previous_orbnum")
    @patch.object(OrbnumFileProduct, "read_records", return_value=10)
    @patch.object(OrbnumFileProduct, "get_sample_record", return_value="sample record")
    @patch.object(OrbnumFileProduct, "get_description", return_value="desc")
    @patch.object(OrbnumFileProduct, "table_character_description", return_value="table desc")
    @patch.object(OrbnumFileProduct, "get_params")
    @patch.object(OrbnumFileProduct, "set_params")
    @patch.object(OrbnumFileProduct, "coverage")
    def test_init_pds4_existing_file_no_overrides(
        self,
        _mock_coverage, _mock_set_params, _mock_get_params, _mock_table_char,
        _mock_get_desc, _mock_get_sample, _mock_read_records, _mock_set_prev,
        _mock_get_header_len, _mock_set_event, _mock_read_header, mock_add_crs,
        _mock_check_eol, _mock_isfile, _mock_safe_mkdir, _mock_label, _mock_register,
        mock_setup, mock_collection, mock_kernels_collection,
    ):
        """When check_eol is False, add_crs_to_file is skipped; and missing mission/observer/target keys fall back to the collection values."""
        del mock_setup.orbnum[0]["mission_name"]
        del mock_setup.orbnum[0]["observer"]
        del mock_setup.orbnum[0]["target"]

        obj = OrbnumFileProduct(mock_setup, "test_file.orb", mock_collection, mock_kernels_collection)

        assert obj.new_product is False
        mock_add_crs.assert_not_called()
        assert obj.missions == ["mission1"]
        assert obj.observers == ["obs1"]
        assert obj.targets == ["target1"]

    def test_init_pds4_integration(self, mock_setup, mock_collection, mock_kernels_collection):
        """End-to-end PDS4 init on a realistic ORBNUM file.

        Unlike the other init tests, the ORBNUM-specific methods (read_header,
        set_event_detection_key, read_records, get_params, set_params,
        get_description, coverage, ...) all run for real against a file on disk.
        Only genuinely external concerns are mocked: the label class, the
        bundle-directory kernel scan, and Product.register (covered elsewhere).
        """
        #
        # Build a realistic ORBNUM file. Header and record share an identical
        # column layout so that read_records sees one clean, fixed-length
        # record and does not trigger the blank-record version bump.
        #
        h0 = " No.   Event UTC PERI       Event SCLK PERI\n"
        h1 = " " + "=" * 5 + " " + "=" * 20 + " " + "=" * 16 + "\n"
        r1 = " " + "{:>5}".format(1) + " " + "2020 JAN 01 00:00:00" + " " + "1/0496935200.000" + "\n"
        orbnum_file = os.path.join(mock_setup.orbnum_directory, "test_file.orb")
        with open(orbnum_file, "w", newline="") as f:
            f.write(h0 + h1 + r1)

        #
        # The staging collection tree is created earlier by the pipeline;
        # safe_make_directory only adds the final level. Reproduce that here.
        #
        os.makedirs(os.path.join(mock_setup.staging_directory, "miscellaneous", "orbnum"))

        #
        # Deterministic but real coverage resolution via a look-up table.
        #
        mock_setup.orbnum[0]["coverage"] = {"lookup_table": {"file": {
            "@name": "test_file.orb",
            "start": "2020-01-01T00:00:00Z",
            "finish": "2020-01-02T00:00:00Z",
        }}}
        #
        # Drop the explicit overrides so mission/observer/target fall back to
        # the values provided by the collection.
        #
        for key in ("mission_name", "observer", "target"):
            mock_setup.orbnum[0].pop(key, None)

        with patch(f"{MOD}.OrbnumFilePDS4Label") as mock_label, \
                patch(f"{MOD}.get_latest_kernel", return_value=[]), \
                patch.object(Product, "register"):
            obj = OrbnumFileProduct(mock_setup, "test_file.orb", mock_collection, mock_kernels_collection)

        # Identity, LID and VID computed for real.
        assert obj.extension == "orb"
        assert obj.new_product is True
        assert obj.lid == "urn:nasa:pds:test:miscellaneous:orbnum_test_file.orb"
        assert obj.vid == "1.0"

        # read_header ran and set the fixed record length (header separator line).
        assert obj.record_fixed_length == len(h1)

        # set_event_detection_key parsed the real header.
        assert obj._event_detection_key == "PERI"

        # read_records found a single clean record: no length mismatch, so no
        # blank records and no version-bump rename.
        assert obj.records == 1
        assert obj.blank_records == []
        assert obj.name == "test_file.orb"

        # get_params / set_params produced the real parameter dictionary.
        assert list(obj.params.keys()) == ["No.", "Event UTC", "Event SCLK"]
        assert obj.params["Event UTC"]["name"] == "Event UTC PERI"
        assert ("UTC time of the pericenter event that "
                "signifies the start of an orbit.") == obj.params["Event UTC"]["description"]
        # Length of the variable-width column is derived from the header.
        assert obj.params["Event SCLK"]["length"] == "16"

        # get_description ran for real.
        assert "periapsis" in obj.description
        assert "Test Author" in obj.description

        # coverage() resolved through the real look-up-table branch.
        assert obj.start_time == "2020-01-01T00:00:00Z"
        assert obj.stop_time == "2020-01-02T00:00:00Z"

        # mission/observer/target fell back to the collection values.
        assert obj.missions == ["mission1"]
        assert obj.observers == ["obs1"]
        assert obj.targets == ["target1"]

        # The label was constructed exactly once.
        mock_label.assert_called_once()


class TestOrbnumFileProductSetPreviousOrbnum:
    """Test determining previous version of an ORBNUM file."""

    @patch(f"{MOD}.get_latest_kernel", return_value=["test_file_v02.orb"])
    def test_set_previous_orbnum_found_with_version(self, _mock_get_latest):
        obj = object.__new__(OrbnumFileProduct)
        obj.setup = MagicMock(bundle_directory="/b", mission_acronym="m")
        obj._pattern = r".*_v[0-9]*\.orb"

        obj.set_previous_orbnum()

        assert obj._previous_version == "02"
        assert obj.previous_orbnum == "test_file_v02.orb"

    # Fails first pattern, succeeds second
    @patch(f"{MOD}.get_latest_kernel", side_effect=[[], ["test_file.orb"]])
    def test_set_previous_orbnum_found_no_explicit_version(self, _mock_get_latest):
        obj = object.__new__(OrbnumFileProduct)
        obj.setup = MagicMock(bundle_directory="/b", mission_acronym="m")
        obj._pattern = r"test_file_[vV]\[0\-9\]*[\.]orb"

        obj.set_previous_orbnum()

        assert obj._previous_version == "1"
        assert obj._previous_orbnum == ["test_file.orb"]

    @patch(f"{MOD}.get_latest_kernel", return_value=[])
    def test_set_previous_orbnum_not_found(self, _mock_get_latest):
        obj = object.__new__(OrbnumFileProduct)
        obj.setup = MagicMock()
        obj._pattern = r"test_file.orb"

        obj.set_previous_orbnum()

        assert obj._previous_version == "1"
        assert obj._previous_orbnum == ""


class TestOrbnumFileProductReadHeader:
    """Test reading and verifying the ORBNUM file header."""

    @patch("builtins.open", new_callable=mock_open, read_data="skip\nEvent UTC PERI\n===========\n")
    def test_read_header_success(self, _mock_file):
        obj = object.__new__(OrbnumFileProduct)
        obj.path = "/fake/path.orb"
        obj._orbnum_type = {"header_start_line": "2"}
        
        header = obj.read_header()

        assert header[0] == "Event UTC PERI\n"
        assert "===========\n" == header[1]
        assert obj.record_fixed_length == len("===========\n")

    @pytest.mark.parametrize('data', [
        "Wrong Header\n===========\n",
        "Event UTC PERI\nNo separator here\n"
    ])
    def test_read_header_missing_separator(self, data):
        """Test that RuntimeError is raised when the separator line lacks '==='."""
        obj = object.__new__(OrbnumFileProduct)
        obj.path = "/fake/path.orb"
        obj.name = "test_file.orb"
        obj._orbnum_type = {"header_start_line": "1"}
        obj.setup = MagicMock()

        with(
            patch("builtins.open", new_callable=mock_open, read_data=data),
            pytest.raises(RuntimeError, match="The header of the orbnum file test_file.orb "
                                              "is not as expected.")):
            obj.read_header()


class TestOrbnumFileProductGetHeaderLength:

    @pytest.mark.parametrize('data', [
        "line1\nline2\nline3\n",
        "line1\nline2\n"
    ])
    @patch(f"{MOD}.utf8len", return_value=10)
    def test_get_header_length_short_file(self, _mock_utf8len, data):
        """The header-length loop ends at EOF rather than via break: every line
        satisfies the accumulation condition so the break is never reached."""
        obj = object.__new__(OrbnumFileProduct)
        obj.path = "test.orb"
        obj._orbnum_type = {"header_start_line": "1"}

        with patch("builtins.open", new_callable=mock_open, read_data=data):
            assert obj.get_header_length() == 20


class TestOrbnumFileProductGetSampleRecord:
    @patch("builtins.open", new_callable=mock_open, read_data="header1\nheader2\n   \n  1976 JUN 22 18:07:09 \n")
    def test_get_sample_record_success(self, _mock_file):
        obj = object.__new__(OrbnumFileProduct)
        obj.path = "test.orb"
        obj._orbnum_type = {"header_start_line": "1"}
        obj.utc_blanks_to_dashes = MagicMock(return_value="1976-JUN-22-18:07:09")

        record = obj.get_sample_record()
        assert record == "1976-JUN-22-18:07:09"

    @patch("builtins.open", new_callable=mock_open, read_data="header1\nheader2\n")
    def test_get_sample_record_empty(self, _mock_file):
        obj = object.__new__(OrbnumFileProduct)
        obj.path = "test.orb"
        obj._orbnum_type = {"header_start_line": "1"}
        obj.setup = MagicMock()

        with pytest.raises(RuntimeError, match="The orbnum file has no records."):
            obj.get_sample_record()


class TestOrbnumFileProductUtcBlanksToDashes:
    @pytest.mark.parametrize('sample, expected', [
        ("  1  2020 JUL 01 01:24:31  other data ", "  1  2020-JUL-01-01:24:31  other data "),
        ("  1  2020-JUL-01-01:24:31  other data ", "  1  2020-JUL-01-01:24:31  other data ")
    ])
    def test_utc_blanks_to_dashes(self, sample, expected):
        result = OrbnumFileProduct.utc_blanks_to_dashes(sample)
        assert result == expected


class TestOrbnumFileProductReadRecords:
    @patch("builtins.open", new_callable=mock_open, read_data="h1\nh2\n1 data\n2 data\n")
    def test_read_records_clean(self, _mock_file):
        obj = object.__new__(OrbnumFileProduct)
        obj.path = "test.orb"
        obj._orbnum_type = {"header_start_line": "1"}
        obj.record_fixed_length = 7
        
        records = obj.read_records()
        assert records == 2
        assert obj.blank_records == []

    @patch(f"{MOD}.os.remove")
    def test_read_records_with_blanks_and_version_bump(self, mock_remove, mock_kernels_collection, caplog):
        # We need a custom mock open to handle reading then writing to a new file
        file_data = "h1\nh2\n1 data       \n2\n3 data       \n"
        mock_files = {"test_v1.orb": file_data, "test_v2.orb": ""}

        # Capture everything written to the new (version-bumped) file.
        written = []

        def custom_open(filename, mode, *_args, **_kwargs):
            m = mock_open(read_data=mock_files.get(filename, ""))()
            if mode == 'w':
                m.write = MagicMock(side_effect=written.append)
            return m

        obj = object.__new__(OrbnumFileProduct)
        obj.path = "test_v1.orb"
        obj.name = "test_v1.orb"
        obj._orbnum_type = {"header_start_line": "1"}
        obj.record_fixed_length = 14
        obj.setup = MagicMock(eol="\n")
        obj.kernels_collection = mock_kernels_collection
        obj.kernels_collection.list.kernel_list = ["test_v1.orb"]

        with patch("builtins.open", side_effect=custom_open):
            with caplog.at_level(logging.INFO):
                records = obj.read_records()

        assert records == 3
        assert obj.blank_records == ["2"]
        assert obj.name == "test_v2.orb"
        assert obj.kernels_collection.list.kernel_list == ["test_v2.orb"]
        mock_remove.assert_called_once_with("test_v1.orb")

        expected = [
            (logging.WARNING, '-- Orbit number 2 record has an incorrect length, the record will be '
                              'expanded to cover the adequate fixed length.'),
            (logging.WARNING, '-- Orbnum name updated to: test_v2.orb')
        ]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected

        #
        # Verify the rewritten content: header lines and well-formed records are
        # copied verbatim (with the configured EOL) while the blank record ("2")
        # is padded out to the fixed record length.
        #
        new_content = "".join(written)
        assert new_content == (
            "h1\n"
            "h2\n"
            "1 data       \n"
            "2            \n"  # blank record padded with spaces
            "3 data       \n"
        )
        # The padded blank record occupies exactly record_fixed_length bytes
        # (13 visible characters + the 1-byte EOL).
        padded_line = new_content.splitlines(keepends=True)[3]
        assert len(padded_line) == obj.record_fixed_length

    @patch("builtins.open", new_callable=mock_open, read_data="h1\nh2\n1 data\n3 data\n")
    def test_read_records_non_consecutive_orbits(self, _mock_file, caplog):
        """Test that a warning is logged when orbit numbers are not sequential."""
        obj = object.__new__(OrbnumFileProduct)
        obj.path = "test.orb"
        obj._orbnum_type = {"header_start_line": "1"}
        obj.record_fixed_length = 7

        with caplog.at_level(logging.INFO):
            records = obj.read_records()

        assert records == 2
        assert obj.blank_records == []
        expected = [
            (logging.WARNING, '-- Orbit number 1 record is followed by 3.')
        ]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected

    @patch(f"{MOD}.os.remove")
    def test_read_records_with_blanks_no_explicit_version(self, mock_remove, mock_kernels_collection):
        """Test blank records handling when filename has no explicit version number."""
        file_data = "h1\nh2\n1 short \n"
        mock_files = {"/some/dir/test.orb": file_data, "/some/dir/test_v2.orb": ""}

        # Capture everything written to the new (version-bumped) file.
        written = []

        def custom_open(filename, mode, *_args, **_kwargs):
            m = mock_open(read_data=mock_files.get(filename, ""))()
            if mode == "w":
                m.write = MagicMock(side_effect=written.append)
            return m

        obj = object.__new__(OrbnumFileProduct)
        obj.path = "/some/dir/test.orb"
        obj.name = "test.orb"
        obj._orbnum_type = {"header_start_line": "1"}
        obj.record_fixed_length = 12
        obj.setup = MagicMock(eol="\n")
        obj.kernels_collection = mock_kernels_collection
        obj.kernels_collection.list.kernel_list = ["other.orb", "test.orb"]

        with patch("builtins.open", side_effect=custom_open):
            records = obj.read_records()

        assert records == 1
        assert obj.blank_records == ["1"]
        assert obj.name == "test_v2.orb"
        assert obj.kernels_collection.list.kernel_list == ["other.orb", "test_v2.orb"]
        mock_remove.assert_called_once_with("/some/dir/test.orb")

        #
        # The single short record is padded out to the fixed record length.
        #
        new_content = "".join(written)
        assert new_content == (
            "h1\n"
            "h2\n"
            "1 short    \n"  # padded from "1 short " to the fixed length
        )
        padded_line = new_content.splitlines(keepends=True)[2]
        assert len(padded_line) == obj.record_fixed_length


class TestOrbnumFileProductSetEventDetectionKey:
    @pytest.mark.parametrize('header, key', [
        ("Event UTC PERI Event SCLK PERI", 'PERI'),
        ("Desc-Node Asc-Node", 'D-NODE'),
        ("Asc-Node Desc-Node", 'A-NODE')
    ])
    def test_set_event_detection_key(self, header, key):
        obj = object.__new__(OrbnumFileProduct)
        obj.set_event_detection_key([header])
        assert obj._event_detection_key == key

    def test_set_event_detection_key_error(self):
        obj = object.__new__(OrbnumFileProduct)
        obj.setup = MagicMock()
        header = ["Invalid Header Line"]
        with pytest.raises(RuntimeError, match="orbnum event detection key is incorrect."):
            obj.set_event_detection_key(header)


class TestOrbnumFileProductGetParams:
    def test_get_params(self):
        obj = object.__new__(OrbnumFileProduct)
        header = ["No. Event UTC SolLon invalid_param"]
        obj.get_params(header)
        assert obj._params == ["No.", "Event UTC", "SolLon"]


class TestOrbnumFileProductSetParams:
    """Test set_params (also implicitly tests event_mapping and opposite_event_mapping)."""
    
    def test_set_params(self):
        obj = object.__new__(OrbnumFileProduct)
        obj._params = ["No.", "Event UTC", "SolLon"]
        obj._sample_record = "12345 2020-01-01T00:00:00 123.456"
        obj._event_detection_key = "PERI"
        obj._orbnum_type = {"event_detection_frame": {"description": "Mars", "spice_name": "IAU_MARS"}}
        obj.setup = MagicMock(target="MARS", information_model_float=1007000000.0)

        header = ["ignore", "===== ==================== ======="]
        
        obj.set_params(header)
        
        assert "No." in obj.params
        assert obj.params["Event UTC"]["name"] == "Event UTC PERI"
        assert "pericenter" in obj.params["Event UTC"]["description"] # from event_mapping
        assert obj.params["SolLon"]["format"] == "%7.3f"
        
    def test_set_params_legacy_im(self):
        obj = object.__new__(OrbnumFileProduct)
        obj._params = ["No.", "SolLon"]
        obj._sample_record = "12345 123.456"
        obj._event_detection_key = "APO"
        obj._orbnum_type = {"event_detection_frame": {"description": "M", "spice_name": "I"}}
        obj.setup = MagicMock(target="MARS", information_model_float=1006000000.0)

        header = ["ignore", "===== ======="]
        
        obj.set_params(header)
        assert obj.params["No."]["format"] == "I5"
        assert obj.params["SolLon"]["format"] == "F7.3"

    def test_set_params_sclk_legacy_im(self):
        """A legacy-IM ASCII_String parameter with no predefined length derives its length from the header separator and is formatted as 'A<length>'."""
        obj = object.__new__(OrbnumFileProduct)
        obj._params = ["Node SCLK"]
        obj._sample_record = "2/0496935200.34677"
        obj._event_detection_key = "PERI"
        obj._orbnum_type = {}
        obj.setup = MagicMock(target="MARS", information_model_float=1006000000.0)

        header = ["ignore", "===================="]

        obj.set_params(header)

        assert obj.params["Node SCLK"]["format"] == "A20"
        assert obj.params["Node SCLK"]["length"] == "20"

    def test_set_params_op_event_utc(self):
        """An OP-Event UTC parameter exercises the $OPPEVENT substitution (via
        opposite_event_mapping), the OP-Event name suffix, and a description with
        no $EVENT token."""
        obj = object.__new__(OrbnumFileProduct)
        obj._params = ["OP-Event UTC"]
        obj._sample_record = "2020-01-01T00:00:00"
        obj._event_detection_key = "PERI"
        obj._orbnum_type = {}
        obj.setup = MagicMock(target="MARS", information_model_float=1007000000.0)

        header = ["ignore", "===================="]

        obj.set_params(header)

        assert obj.params["OP-Event UTC"]["name"] == "OP-Event UTC APO"
        assert "apocenter" in obj.params["OP-Event UTC"]["description"]
        assert obj.params["OP-Event UTC"]["format"] == "%20s"

    def test_set_params_with_target_substitution(self):
        """An Alt parameter exercises the $TARGET substitution in its description."""
        obj = object.__new__(OrbnumFileProduct)
        obj._params = ["Alt"]
        obj._sample_record = "12345.678"
        obj._event_detection_key = "PERI"
        obj._orbnum_type = {}
        obj.setup = MagicMock(target="MARS", information_model_float=1007000000.0)

        header = ["ignore", "=========="]

        obj.set_params(header)

        assert "Mars" in obj.params["Alt"]["description"]
        assert obj.params["Alt"]["format"] == "%10.3f"


class TestOrbnumFileProductGetDescription:
    def test_get_description(self):
        obj = object.__new__(OrbnumFileProduct)
        obj._event_detection_key = "PERI"
        obj._orbnum_type = {
            "pck": {"description": "PCK Desc", "kernel_name": "pck.tpc"},
            "author": "NAIF"
        }
        obj._previous_orbnum = "old.orb"

        desc = obj.get_description()
        assert desc == ('SPICE text orbit number file containing orbit numbers and start times '
                        'for orbits numbered by/starting at periapsis events, and sets of '
                        'selected geometric parameters at the orbit start times. SPICE text '
                        'PCK file constants from the PCK Desc (pck.tpc). This file supersedes '
                        'the following orbit number file: old.orb. Created by NAIF.')

    def test_get_description_no_previous_orbnum_attr(self):
        """When the object has no _previous_orbnum attribute, the description omits the 'supersedes' clause."""
        obj = object.__new__(OrbnumFileProduct)
        obj._event_detection_key = "APO"
        obj._orbnum_type = {
            "pck": {"description": "PCK Desc", "kernel_name": "pck.tpc"},
            "author": "NAIF"
        }
        # _previous_orbnum is intentionally not set

        desc = obj.get_description()
        assert desc == ('SPICE text orbit number file containing orbit numbers and start times '
                        'for orbits numbered by/starting at apoapsis events, and sets of selected '
                        'geometric parameters at the orbit start times. SPICE text PCK file '
                        'constants from the PCK Desc (pck.tpc). Created by NAIF.')

    def test_get_description_empty_previous_orbnum(self):
        """When _previous_orbnum is an empty string, the description omits the 'supersedes' clause."""
        obj = object.__new__(OrbnumFileProduct)
        obj._event_detection_key = "APO"
        obj._orbnum_type = {
            "pck": {"description": "PCK Desc", "kernel_name": "pck.tpc"},
            "author": "NAIF"
        }
        obj._previous_orbnum = ""

        desc = obj.get_description()
        assert desc == ('SPICE text orbit number file containing orbit numbers and start times '
                        'for orbits numbered by/starting at apoapsis events, and sets of selected '
                        'geometric parameters at the orbit start times. SPICE text PCK file '
                        'constants from the PCK Desc (pck.tpc). Created by NAIF.')


class TestOrbnumFileProductTableCharacterDescription:
    @pytest.mark.parametrize(
        "blank_records, expected",
        [
            (["1", "2"],
             'Since the SPK file(s) used to generate this orbit number file did not provide '
             'continuous coverage, the file contains 2 records that only provide the orbit '
             'number in the first field (No.) with all other fields set to blank spaces.'),
            (["1"],
             'Since the SPK file(s) used to generate this orbit number file did not provide '
             'continuous coverage, the file contains 1 record that only provide the orbit '
             'number in the first field (No.) with all other fields set to blank spaces.'),
            ([],
             "")
        ],
    )
    def test_table_character_description(self, blank_records, expected):
        obj = object.__new__(OrbnumFileProduct)
        obj.blank_records = blank_records

        desc = obj.table_character_description()
        assert desc == expected


def _make_fallback_file_mock(last_line_bytes=b"123 2021-01-01T00:00:00Z unused 2021-02-01T00:00:00Z\n"):
    """Create a binary file mock for the coverage() fallback path."""
    f = MagicMock()
    f.read.return_value = b"\n"  # while f.read(1) != b"\n": exits on first iteration
    f.readline.return_value = last_line_bytes
    f.__enter__ = MagicMock(return_value=f)
    f.__exit__ = MagicMock(return_value=False)
    return f


class TestOrbnumFileProductCoverage:

    @pytest.mark.parametrize('cutoff, stop_time, expected',[
        ('False', "2020-02-01T00:00:00Z", "2020-02-01T00:00:00Z"),
        ('True', "2020-02-05T12:30:00Z", "2020-02-05T00:00:00Z")
    ])
    @patch(f"{MOD}.spk_coverage")
    @patch(f"{MOD}.os.path.isfile", return_value=True)
    def test_coverage_via_kernel_exact_match_and_cutoff(
            self, _mock_isfile, mock_spk_coverage, cutoff, stop_time, expected):
        obj = object.__new__(OrbnumFileProduct)
        obj.name = "test.orb"
        obj._orbnum_type = {"coverage": {"kernel": {"#text": "/path/test.bsp", "@cutoff": cutoff}}}
        obj.setup = MagicMock(spice_name="test_spice")
        mock_spk_coverage.return_value = ("2020-01-01T00:00:00Z", stop_time)
        
        # Mock os.listdir to pretend kernel is found in the path
        with patch(f"{MOD}.os.listdir", return_value=["test.bsp"]):
            obj.coverage()

        assert obj.start_time == "2020-01-01T00:00:00Z"
        assert obj.stop_time == expected

    def test_coverage_via_lookup_table(self):
        obj = object.__new__(OrbnumFileProduct)
        obj.name = "test.orb"
        obj._orbnum_type = {"coverage": {"lookup_table": {"file": [
            {"@name": "test.orb", "start": "start_time", "finish": "end_time"}
        ]}}}
        
        obj.coverage()
        assert obj.start_time == "start_time"
        assert obj.stop_time == "end_time"

    @patch(f"{MOD}.parse_date")
    def test_coverage_fallback_data(self, mock_parse_date):
        obj = object.__new__(OrbnumFileProduct)
        obj.name = "test.orb"
        obj.path = "test.orb"
        obj._orbnum_type = {}
        obj._sample_record = "1 2020-01-01T00:00:00 data"
        obj.utc_blanks_to_dashes = MagicMock(return_value="1 2020-01-01T00:00:00 data 2020-01-02T00:00:00")
        
        mock_parse_date.return_value = datetime.datetime(2020, 1, 1)

        with patch("builtins.open", mock_open(read_data=b"dummy\n1 2020-01-01T00:00:00 data 2020-01-02T00:00:00\n")) as m_open:
            m_open.return_value.seek = MagicMock()
            obj.coverage()

        assert mock_parse_date.call_count == 2

    # --- Group 1: kernel path-resolution fallback chain ---

    @patch(f"{MOD}.spk_coverage")
    @patch(f"{MOD}.os.path.isfile", return_value=True)
    @patch(f"{MOD}.os.listdir", side_effect=[OSError("not found"), ["test.bsp"]])
    def test_coverage_kernel_fallback_to_staging(self, _mock_listdir, _mock_isfile, mock_spk_coverage):
        """When listing the configured kernel path raises, the search falls back to the staging directory."""
        obj = object.__new__(OrbnumFileProduct)
        obj.name = "test.orb"
        obj._orbnum_type = {"coverage": {"kernel": {"#text": "/path/test.bsp", "@cutoff": "False"}}}
        obj.setup = MagicMock(spice_name="test_spice", staging_directory="/staging", bundle_directory="/bundle")
        mock_spk_coverage.return_value = ("2020-01-01T00:00:00Z", "2020-02-01T00:00:00Z")

        obj.coverage()

        assert obj.start_time == "2020-01-01T00:00:00Z"
        assert obj.stop_time == "2020-02-01T00:00:00Z"

    @patch(f"{MOD}.spk_coverage")
    @patch(f"{MOD}.os.path.isfile", return_value=True)
    @patch(f"{MOD}.os.listdir", side_effect=[OSError("fail"), OSError("fail"), ["test.bsp"]])
    def test_coverage_kernel_fallback_to_bundle(self, _mock_listdir, _mock_isfile, mock_spk_coverage):
        """When both the configured path and the staging directory raise, the search falls back to the bundle directory."""
        obj = object.__new__(OrbnumFileProduct)
        obj.name = "test.orb"
        obj._orbnum_type = {"coverage": {"kernel": {"#text": "/path/test.bsp", "@cutoff": "False"}}}
        obj.setup = MagicMock(spice_name="test_spice", staging_directory="/staging", bundle_directory="/bundle")
        mock_spk_coverage.return_value = ("2020-01-01T00:00:00Z", "2020-02-01T00:00:00Z")

        obj.coverage()

        assert obj.start_time == "2020-01-01T00:00:00Z"
        assert obj.stop_time == "2020-02-01T00:00:00Z"

    @patch(f"{MOD}.spk_coverage")
    @patch(f"{MOD}.os.path.isfile", return_value=True)
    @patch(f"{MOD}.os.listdir", side_effect=[OSError("fail"), OSError("fail"), OSError("fail")])
    def test_coverage_kernel_all_searches_fail(self, _mock_listdir, _mock_isfile, mock_spk_coverage):
        """When every directory search raises (no kernels found), the originally configured kernel path is still used via os.path.isfile."""
        obj = object.__new__(OrbnumFileProduct)
        obj.name = "test.orb"
        obj._orbnum_type = {"coverage": {"kernel": {"#text": "/path/test.bsp", "@cutoff": "False"}}}
        obj.setup = MagicMock(spice_name="test_spice", staging_directory="/staging", bundle_directory="/bundle")
        mock_spk_coverage.return_value = ("2020-01-01T00:00:00Z", "2020-02-01T00:00:00Z")

        obj.coverage()

        assert obj.start_time == "2020-01-01T00:00:00Z"
        assert obj.stop_time == "2020-02-01T00:00:00Z"

    # --- Group 2: multiple kernels found ---

    @patch(f"{MOD}.spk_coverage")
    @patch(f"{MOD}.os.path.isfile", return_value=True)
    @patch(f"{MOD}.os.listdir", return_value=["other.bsp", "test.bsp"])
    def test_coverage_kernel_multiple_matches(self, _mock_listdir, _mock_isfile, mock_spk_coverage):
        """When multiple kernels match the pattern, the one whose basename matches the orbnum name is selected."""
        obj = object.__new__(OrbnumFileProduct)
        obj.name = "test.orb"
        obj._orbnum_type = {"coverage": {"kernel": {"#text": "/path/.*\\.bsp", "@cutoff": "False"}}}
        obj.setup = MagicMock(spice_name="test_spice")
        mock_spk_coverage.return_value = ("2020-01-01T00:00:00Z", "2020-02-01T00:00:00Z")

        obj.coverage()

        assert obj.start_time == "2020-01-01T00:00:00Z"
        assert obj.stop_time == "2020-02-01T00:00:00Z"

    # --- Group 3: cutoff edge case ---

    @patch(f"{MOD}.spk_coverage")
    @patch(f"{MOD}.os.path.isfile", return_value=True)
    @patch(f"{MOD}.os.listdir", return_value=["test.bsp"])
    def test_coverage_kernel_invalid_cutoff(self, _mock_listdir, _mock_isfile, mock_spk_coverage, caplog):
        """An unrecognised @cutoff value logs an error and leaves the stop time unchanged."""
        obj = object.__new__(OrbnumFileProduct)
        obj.name = "test.orb"
        obj._orbnum_type = {"coverage": {"kernel": {"#text": "/path/test.bsp", "@cutoff": "Invalid"}}}
        obj.setup = MagicMock(spice_name="test_spice")
        mock_spk_coverage.return_value = ("2020-01-01T00:00:00Z", "2020-02-01T00:00:00Z")

        with caplog.at_level(logging.ERROR):
            obj.coverage()

        assert obj.start_time == "2020-01-01T00:00:00Z"
        assert obj.stop_time == "2020-02-01T00:00:00Z"
        assert "cutoff value of <kernel>" in caplog.text

    # --- Group 4: kernel found but file missing / kernel key empty ---

    @patch(f"{MOD}.parse_date")
    @patch(f"{MOD}.os.path.isfile", return_value=False)
    @patch(f"{MOD}.os.listdir", side_effect=OSError("not found"))
    def test_coverage_kernel_isfile_false(self, _mock_listdir, _mock_isfile, mock_parse_date):
        """When the resolved kernel is not a file, coverage falls back to the orbnum file data."""
        obj = object.__new__(OrbnumFileProduct)
        obj.name = "test.orb"
        obj.path = "/path/test.orb"
        obj._orbnum_type = {"coverage": {"kernel": {"#text": "/path/test.bsp", "@cutoff": "False"}}}
        obj.setup = MagicMock(spice_name="test_spice", staging_directory="/staging", bundle_directory="/bundle")
        obj._sample_record = "1 2021-01-01T00:00:00Z data"
        obj.utc_blanks_to_dashes = MagicMock(
            return_value="123 2021-01-01T00:00:00Z unused 2021-02-01T00:00:00Z"
        )
        mock_parse_date.side_effect = [datetime.datetime(2021, 1, 1), datetime.datetime(2021, 2, 1)]

        with patch("builtins.open", return_value=_make_fallback_file_mock()):
            obj.coverage()

        assert obj.start_time == "2021-01-01T00:00:00Z"
        assert obj.stop_time == "2021-02-01T00:00:00Z"

    @pytest.mark.parametrize(
        "orbnum_type",
        [
            pytest.param({"coverage": {"kernel": ""}}, id="kernel-falsy"),
            pytest.param(
                {"coverage": {"lookup_table": {"file": [
                    {"@name": "other.orb", "start": "t0", "finish": "t1"}
                ]}}},
                id="lookup-table-no-match",
            ),
            pytest.param({"coverage": {"lookup_table": ""}}, id="lookup-table-falsy"),
        ],
    )
    @patch(f"{MOD}.parse_date")
    def test_coverage_falls_back_to_file_data(self, mock_parse_date, orbnum_type):
        """When no coverage source resolves, coverage falls back to the orbnum file data."""
        obj = object.__new__(OrbnumFileProduct)
        obj.name = "test.orb"
        obj.path = "/path/test.orb"
        obj._orbnum_type = orbnum_type
        obj.setup = MagicMock()
        obj._sample_record = "1 2021-01-01T00:00:00Z data"
        obj.utc_blanks_to_dashes = MagicMock(
            return_value="123 2021-01-01T00:00:00Z unused 2021-02-01T00:00:00Z"
        )
        mock_parse_date.side_effect = [datetime.datetime(2021, 1, 1), datetime.datetime(2021, 2, 1)]

        with patch("builtins.open", return_value=_make_fallback_file_mock()):
            obj.coverage()

        assert obj.start_time == "2021-01-01T00:00:00Z"
        assert obj.stop_time == "2021-02-01T00:00:00Z"

    # --- Group 5: lookup table variants ---

    def test_coverage_lookup_table_single_file_dict(self):
        """A lookup table whose single file is provided as a dict (not a list) is handled."""
        obj = object.__new__(OrbnumFileProduct)
        obj.name = "test.orb"
        obj._orbnum_type = {"coverage": {"lookup_table": {
            "file": {"@name": "test.orb", "start": "t0", "finish": "t1"}
        }}}

        obj.coverage()

        assert obj.start_time == "t0"
        assert obj.stop_time == "t1"

    # --- Group 6: fallback path variants ---

    @patch(f"{MOD}.parse_date")
    def test_coverage_fallback_unable_to_determine(self, mock_parse_date):
        """When the last record contains 'Unable to determine', the stop time is taken from the event UTC (field 1) rather than the opposite-event UTC."""
        obj = object.__new__(OrbnumFileProduct)
        obj.name = "test.orb"
        obj.path = "/path/test.orb"
        obj._orbnum_type = {}
        obj._sample_record = "1 2021-01-01T00:00:00Z data"
        obj.utc_blanks_to_dashes = MagicMock(
            return_value="123 2021-01-01T00:00:00Z Unable to determine stop-time"
        )
        mock_parse_date.side_effect = [datetime.datetime(2021, 1, 1), datetime.datetime(2021, 1, 1)]

        fallback_mock = _make_fallback_file_mock(
            b"123 2021-01-01T00:00:00Z Unable to determine stop-time\n"
        )
        with patch("builtins.open", return_value=fallback_mock):
            obj.coverage()

        assert obj.stop_time == "2021-01-01T00:00:00Z"

    @patch(f"{MOD}.parse_date")
    def test_coverage_fallback_stop_time_parse_exception(self, mock_parse_date):
        """When parse_date fails on the opposite-event UTC, the stop time falls back to strptime on the event UTC."""
        obj = object.__new__(OrbnumFileProduct)
        obj.name = "test.orb"
        obj.path = "/path/test.orb"
        obj._orbnum_type = {}
        obj._sample_record = "1 2021-01-01T00:00:00Z data"
        obj.utc_blanks_to_dashes = MagicMock(
            return_value="123 2021-Jan-01-00:00:00 x 2021-Jan-02-00:00:00"
        )
        mock_parse_date.side_effect = [
            datetime.datetime(2021, 1, 1),
            ValueError("cannot parse"),
        ]

        fallback_mock = _make_fallback_file_mock(
            b"123 2021-Jan-01-00:00:00 x 2021-Jan-02-00:00:00\n"
        )
        with patch("builtins.open", return_value=fallback_mock):
            obj.coverage()

        assert obj.stop_time == "2021-01-01T00:00:00Z"
