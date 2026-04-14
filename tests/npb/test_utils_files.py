"""Unit tests for the pds.naif_pds4_bundler.utils.files module."""
from dataclasses import dataclass
from errno import ENOTDIR
from pathlib import Path
import shutil

import pytest

# import os
# from unittest import mock

from pds.naif_pds4_bundler.utils import files


# Get the directory where the data is located.
KERNELS = Path(__file__).parent.parent / "naif_pds4_bundler" / "data" / "kernels"


# ----------------------------------------------------------------------------
# files.check_binary_endianness tests
# ----------------------------------------------------------------------------
@pytest.mark.parametrize("kernel, endianness, expected_error",[
    # Tests for "required little endian kernels."
    (Path('ck', 'insight_ida_enc_200829_201220_v1.bc'), 'little', None),
    (Path('ck', 'mro_sc_psp_210706_210712.big.bc'), 'little',
     "The kernel cannot be loaded because of its endianness. Use NAIF's utility BINGO to convert the file."),
    (Path('dsk', 'DEIMOS_K005_THO_V01.BDS'), 'little', None),
    (Path('dsk', 'deimos_k005_tho_v01.big.bds'), 'little',
     "The kernel cannot be loaded because of its endianness. Use NAIF's utility BINGO to convert the file."),
    (Path('pck', 'lunar_de403s_pa_v0.bpc'), 'little', None),
    (Path('pck', 'lunar_de403s_pa_v0.big.bpc'), 'little',
     "The kernel cannot be loaded because of its endianness. Use NAIF's utility BINGO to convert the file."),
    (Path('spk', 'm2020_cruise_od138_v1.bsp'), 'little', None),
    (Path('spk', 'mro_psp60.big.bsp'), 'little',
     "The kernel cannot be loaded because of its endianness. Use NAIF's utility BINGO to convert the file."),
    # Tests for "required big endian kernels."
    (Path('ck', 'insight_ida_enc_200829_201220_v1.bc'), 'big',
     "The kernel cannot be loaded because of its endianness. Use NAIF's utility BINGO to convert the file."),
    (Path('ck', 'mro_sc_psp_210706_210712.big.bc'), 'big', None),
    (Path('dsk', 'DEIMOS_K005_THO_V01.BDS'), 'big',
     "The kernel cannot be loaded because of its endianness. Use NAIF's utility BINGO to convert the file."),
    (Path('dsk', 'deimos_k005_tho_v01.big.bds'), 'big', None),
    (Path('pck', 'lunar_de403s_pa_v0.bpc'), 'big',
     "The kernel cannot be loaded because of its endianness. Use NAIF's utility BINGO to convert the file."),
    (Path('pck', 'lunar_de403s_pa_v0.big.bpc'), 'big', None),
    (Path('spk', 'm2020_cruise_od138_v1.bsp'), 'big',
     "The kernel cannot be loaded because of its endianness. Use NAIF's utility BINGO to convert the file."),
    (Path('spk', 'mro_psp60.big.bsp'), 'big', None),
    # Tests for "invalid SPICE kernel architecture."
    (Path('ck', 'insight_ida_enc_200829_201220_v1.xc'), 'little',
     'The binary kernel does not have a DAF or DAS architecture.'),
    (Path('pck', 'pck00010.tpc'), 'little',
     'The binary kernel does not have a DAF or DAS architecture.'),
    (Path('ck', 'insight_ida_enc_200829_201220_v1.xc'), 'big',
     'The binary kernel does not have a DAF or DAS architecture.'),
    (Path('pck', 'pck00010.tpc'), 'big',
     'The binary kernel does not have a DAF or DAS architecture.'),
    # TODO: Add tests for EKs (.bdb and .bes)
])
def test_check_binary_endianness(kernel, endianness, expected_error) -> None:
    """Test checking binary file format."""
    error = files.check_binary_endianness(str(KERNELS / kernel), endianness=endianness)
    assert error == expected_error

# ----------------------------------------------------------------------------
# files.check_consecutive test
# ----------------------------------------------------------------------------

@pytest.mark.parametrize( "lst, cc_bool", [
    ([1, 2, 3, 4, 5], True),
    ([1, 2, 3, 4, 5, 5, 5], False),
    ([1, 2, 3, 4, 7, 5], False),
])
def test_check_consecutive(lst, cc_bool):
    """Test check_consecutive function with pytest."""
    assert files.check_consecutive(list(lst)) is cc_bool

# ----------------------------------------------------------------------------
# files.check_kernel_integrity tests
# ----------------------------------------------------------------------------

def test_check_kernel_integrity_binary_kernel(tmp_path):
    """Test binary kernel integrity."""

    src_kernel = str(KERNELS / "ck" / "insight_ida_enc_200829_201220_v1.bc")

    # Subcase 1: Correct binary kernel architecture
    error = files.check_kernel_integrity(src_kernel)
    assert not error

    # Subcase 2: Incorrect kernel type (wrong extension)
    wrong_ext = tmp_path / "insight_ida_enc_200829_201220_v1.bsp"
    shutil.copy(src_kernel, wrong_ext)
    error = files.check_kernel_integrity(str(wrong_ext))
    assert error

    # Subcase 3: Incorrect file name → should raise KeyError
    bad_name = str(KERNELS / "ck" / "insight_ida_enc_200829_201220_v1.xc")
    with pytest.raises(KeyError):
        files.check_kernel_integrity(bad_name)

    # Subcase 4: Incorrect architecture (copy bad file into .bc)
    bad_arch_copy = tmp_path / "insight_ida_enc_200829_201220_v1.bc"
    shutil.copy(bad_name, bad_arch_copy)
    error = files.check_kernel_integrity(str(bad_arch_copy))
    assert error


def test_check_kernel_integrity_text_kernel(tmp_path):
    """Test text kernel integrity."""

    kernel_path = tmp_path / "test.tf"

    # Subcase 1: Correct text kernel architecture
    kernel_path.write_text("KPL/FK\n")
    error = files.check_kernel_integrity(str(kernel_path))
    assert not error

    # Subcase 2: Non-existing kernel architecture
    kernel_path.write_text("KPLO/FK\n")
    error = files.check_kernel_integrity(str(kernel_path))
    assert error

    # Subcase 3: Incorrect text kernel architecture
    kernel_path.write_text("DAF/FK\n")
    error = files.check_kernel_integrity(str(kernel_path))
    assert error

    # Subcase 4: Mismatch text kernel type (extension vs content)
    ti_path = tmp_path / "test.ti"
    ti_path.write_text("KPL/FK\n")
    error = files.check_kernel_integrity(str(kernel_path))
    assert error

    # Subcase 5: Non-existing text kernel type
    kernel_path.write_text("KPL/SLC\n")
    error = files.check_kernel_integrity(str(kernel_path))
    assert error

# ----------------------------------------------------------------------------
# files.check_kernel_integrity tests
# ----------------------------------------------------------------------------

def test_check_line_length():
    """Test line length check."""

    mk = str(KERNELS / "mk" / "bc_v001.tm")

    expected = [
        "Line 97 is longer than 80 characters",
        "Line 100 is longer than 80 characters",
        "Line 103 is longer than 80 characters",
        "Line 104 is longer than 80 characters",
        "Line 105 is longer than 80 characters",
        "Line 106 is longer than 80 characters",
        "Line 107 is longer than 80 characters",
        "Line 108 is longer than 80 characters",
        "Line 109 is longer than 80 characters",
        "Line 110 is longer than 80 characters",
        "Line 111 is longer than 80 characters",
        "Line 112 is longer than 80 characters",
        "Line 113 is longer than 80 characters",
        "Line 114 is longer than 80 characters",
        "Line 115 is longer than 80 characters",
        "Line 116 is longer than 80 characters",
        "Line 117 is longer than 80 characters",
        "Line 118 is longer than 80 characters",
        "Line 121 is longer than 80 characters",
        "Line 123 is longer than 80 characters",
        "Line 124 is longer than 80 characters",
        "Line 125 is longer than 80 characters",
        "Line 126 is longer than 80 characters",
        "Line 127 is longer than 80 characters",
    ]

    errors = files.check_line_length(mk)
    assert errors == expected


# ----------------------------------------------------------------------------
# files.copy test
# ----------------------------------------------------------------------------

def test_copy_success(tmp_path):
    """Test copy function using pytest.
    This is for a successful case"""
    src = tmp_path / "source"
    src.mkdir()
    dest = tmp_path / "destination"
    files.copy(str(src), str(dest))

    assert dest.exists()

# def check_directory_exists(path):
#     return os.path.exists(path)
#
# def test_copy_dir_already_exists(tmp_path):
#     """Test copy function using pytest.
#     This is for a case where the source directory does not exist"""
#     path = tmp_path / "source"
#
#     with mock.patch("os.path.exists") as mock_exists:
#         mock_exists.return_value = False
#
#         result = check_directory_exists(path)
#
#         assert result is False
#         mock_exists.assert_called_with(path)


def test_copy_error_not_dir(monkeypatch, tmp_path, caplog):
    """Test copy function using pytest.
    This is for a case when the source was not a directory"""
    src = ""
    dest = tmp_path / "destination"

    def mock_copytree(*args):
        # Not such file or directory Error (errno 2)
        raise OSError(files.errno.ENOENT, "No such file or directory")

    monkeypatch.setattr(shutil, "copytree", mock_copytree)

    with caplog.at_level(files.logging.WARNING):
        files.copy(str(src), str(dest))

    assert "WARNING  root:files.py:91 -- Directory  not copied, probably because the increment directory exists.\n Error: [Errno 2] No such file or directory" in caplog.text


# ----------------------------------------------------------------------------
# files.etree_to_dict test
# ----------------------------------------------------------------------------

#def test_etree_to_dict():




# ----------------------------------------------------------------------------
# files.extract_comment tests
# ----------------------------------------------------------------------------

def test_extract_comment_ck():
    """Test comment extraction from kernel."""
    comment = files.extract_comment(str(KERNELS / "ck" / "insight_ida_enc_200829_201220_v1.bc"))
    comment_line = (
        " This CK file was created using CKSLICER Utility Ver. 1.3.0, October 28, 2011"
    )

    assert comment_line == comment[3]


# ----------------------------------------------------------------------------
# files.get_context_products tests
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("mission, observer, target, expected_bcp",[
    ('NEOWISE', 'SPACECRAFT', 'TARGET',
     [{'name': ['NEOWISE'],
       'type': ['Mission'],
       'lidvid': 'urn:nasa:pds:context:investigation:mission.neowise::1.0'}]),
    ('MISSION', 'Insight Deployment Camera', 'TARGET',
     [{'name': ['INSIGHT DEPLOYMENT CAMERA'],
       'type': ['IMAGER'],
       'lidvid': 'urn:nasa:pds:context:instrument:idc.insight::1.0'}]),
    ('INSIGHT', 'InSight', 'TARGET',
    [{'name': ['InSight'],
      'type': ['Lander'],
      'lidvid': 'urn:nasa:pds:context:instrument_host:spacecraft.insight::2.0'},
     {'name': ['INSIGHT'],
      'type': ['Mission'],
      'lidvid': 'urn:nasa:pds:context:investigation:mission.insight::2.0'}])
])
def test_get_context_products_no_optional_info_in_config_file(
        mission, observer, target, expected_bcp
):
    """Test getting context products, assuming a configuration file that
    does not have `context_products`, `secondary_missions`,
    `secondary_observers` or `secondary_targets`"""

    # Create a mockup of the NPB setup, as required for this test.
    @dataclass
    class Config:
        mission_name: str
        observer: str
        target: str

    result = files.get_context_products(Config(mission, observer, target))
    assert result == expected_bcp

# ----------------------------------------------------------------------------
# files.kernel_name test
# ----------------------------------------------------------------------------

@pytest.mark.parametrize( "path, expected", [
    (Path('ck', 'insight_ida_enc_200829_201220_v1.bc'), 'insight_ida_enc_200829_201220_v1.bc'),
    (Path('ck', 'mro_sc_psp_210706_210712.big.bc'), 'mro_sc_psp_210706_210712.big.bc'),
    (Path('dsk', 'DEIMOS_K005_THO_V01.BDS'), 'DEIMOS_K005_THO_V01.BDS'),
    (Path('dsk', 'deimos_k005_tho_v01.big.bds'), 'deimos_k005_tho_v01.big.bds'),
    (Path('pck', 'lunar_de403s_pa_v0.bpc'), 'lunar_de403s_pa_v0.bpc'),
    (Path('pck', 'lunar_de403s_pa_v0.big.bpc'), 'lunar_de403s_pa_v0.big.bpc'),
    (Path('spk', 'm2020_cruise_od138_v1.bsp'), 'm2020_cruise_od138_v1.bsp'),
    (Path('amb', 'alyssa.txt'), 'alyssa.txt'),
    (Path('noodle_party.t'), 'noodle_party.t'),
])
def test_kernel_name(path, expected):
    """Test kernel_name function with pytest."""
    assert files.kernel_name(str(path)) == expected

# ----------------------------------------------------------------------------
# files.match_patterns tests
# ----------------------------------------------------------------------------

def test_match_patterns_basic():
    """Test match_patterns utils function."""

    name_w_pattern = "insight_$YEAR_v$VERSION.tm"
    name = "insight_2021_v02.tm"
    patterns = [
        {"@length": "2", "#text": "VERSION"},
        {"@length": "4", "#text": "YEAR"},
    ]

    values = files.match_patterns(name, name_w_pattern, patterns)

    assert values == {"YEAR": "2021", "VERSION": "02"}


def test_match_patterns_missing_pattern():
    name_w_pattern = "insight_$YEAR_v$VERSION.tm"
    name = "insight_2021_v02.tm"
    patterns = [{"@length": "2", "#text": "VERSION"}]

    with pytest.raises(RuntimeError):
        files.match_patterns(name, name_w_pattern, patterns)


def test_match_patterns_typo_in_template():
    name_w_pattern = "insight_$YER_v$VERSION.tm"
    name = "insight_2021_v02.tm"
    patterns = [
        {"@length": "2", "#text": "VERSION"},
        {"@length": "4", "#text": "YEAR"},
    ]

    with pytest.raises(RuntimeError):
        files.match_patterns(name, name_w_pattern, patterns)


def test_match_patterns_typo_in_patterns():
    name_w_pattern = "insight_$YEAR_v$VERSION.tm"
    name = "insight_2021_v02.tm"
    patterns = [
        {"@length": "2", "#text": "VERSION"},
        {"@length": "4", "#text": "YAR"},
    ]

    with pytest.raises(RuntimeError):
        files.match_patterns(name, name_w_pattern, patterns)


def test_match_patterns_wrong_length():
    name_w_pattern = "insight_$YEAR_v$VERSION.tm"
    name = "insight_2021_v02.tm"
    patterns = [
        {"@length": "2", "#text": "VERSION"},
        {"@length": "10", "#text": "YEAR"},
    ]

    with pytest.raises(RuntimeError):
        files.match_patterns(name, name_w_pattern, patterns)


# ----------------------------------------------------------------------------
# files.md5 test
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("fname,expected", [
    ( KERNELS / "ck" / "insight_ida_enc_200829_201220_v1.bc" , "22f9acc1931c8a626fac2a844fc5cee3"),
])
def test_md5(fname, expected):
    """Test md5 function using pytest."""
    result = files.md5(str(fname))
    assert result == expected

# ----------------------------------------------------------------------------
# files.mk_to_list tests
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("mk", [
    KERNELS / "mk" / "vco_v01.tm",
    KERNELS / "mk" / "msl_v29.tm",
])
def test_mk_to_list(mk):
    assert files.mk_to_list(str(mk), False)

# ----------------------------------------------------------------------------
# files.safe_make_directory test
# ----------------------------------------------------------------------------

def test_safe_make_directory(tmp_path):
    """Test safe_make_directory function using pytest.
    This is for a successful case"""
    path = tmp_path / "dir_path"
    path.mkdir()
    files.safe_make_directory(str(path))

    assert path.exists()
    assert path.is_dir()

#Need to add logging.info in here somehow

# ----------------------------------------------------------------------------
# files.utf8len test
# ----------------------------------------------------------------------------

@pytest.mark.parametrize( "strn, length", [
    ("I_am_happy_today", "16"),
    ("lunar_de403s_pa_v0.big.bpc", "26"),
    ("NPB is Great", "12"),
    ("kernels/pck/pck00010.tpc", "24")
])
def test_utf8len(strn, length):
    """Test utf8len function with pytest."""
    assert files.utf8len(str(strn)) == int(length)
