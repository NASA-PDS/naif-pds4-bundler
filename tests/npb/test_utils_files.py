"""Unit tests for the pds.naif_pds4_bundler.utils.files module."""
from dataclasses import dataclass
import io
import logging
from pathlib import Path
import shutil
from unittest.mock import call, MagicMock, patch
from xml.etree import ElementTree

import pytest
import spiceypy

from pds.naif_pds4_bundler.utils import files

# Get the directory where the data is located.
KERNELS = Path(__file__).parent.parent / "naif_pds4_bundler" / "data" / "kernels"
DOCS = Path(__file__).parent.parent / "naif_pds4_bundler" / "data"

# ----------------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------------
@pytest.fixture
def daf_handle():
    """Provides a valid and existing DAF handle.."""
    daf_file = str(KERNELS/"ck"/"insight_ida_enc_200829_201220_v1.bc")
    handle = spiceypy.dafopr(daf_file)
    yield handle

    spiceypy.dafcls(handle) # Cleanup after the test finishes

# ----------------------------------------------------------------------------
# files.add_carriage_return tests
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("inputs, eol, outputs", [
    ("Kitty\n", "\n", 'Kitty\n'),
    ("Meow \n", "\n", 'Meow \n'),
    ("Meow Meow\r\n", "\n", 'Meow Meow\n'),
    ("\n", "\n", '\n'),
    ("", "\n", '\n'),
    ("No CR", "\n", 'No CR\n'),

    ("Chatty\nkitty\n", "\r\n", 'Chatty\r\nkitty\r\n'),
    ("", "\r\n", '\r\n'),
    ("\r\n", "\r\n", '\r\n'),
    ("WaterBottle \r\n", "\r\n", 'WaterBottle \r\n'),
    ("No CR", "\r\n", 'No CR\r\n'),
])
def test_add_carriage_return(inputs, eol, outputs):
    """Test add_carriage_return function using pytest."""
    result = files.add_carriage_return(inputs, eol)
    assert result == outputs

@pytest.mark.parametrize("inputs, eol, expected", [
    ("Meww", "", [(logging.ERROR, "Invalid EOL requested: ''.")]),
    ("Meww", "\a", [(logging.ERROR, "Invalid EOL requested: '\\x07'.")]),
    ("Meww", "\n", []),
    ("Meww", "\r\n", []),
    ("Meww\n", "", [(logging.ERROR, "Invalid EOL requested: ''.")]),
    ("Meww\r\n", "", [(logging.ERROR, "Invalid EOL requested: ''.")]),
    ("Meww\n", "\r\n", []),
    ("Meww\r\n", "\n", []),
    ("Meww\n", "\n", []),
    ("Meww\r\n", "\r\n", []),
])
def test_add_carriage_return_logging_error(monkeypatch, inputs, eol, expected,  caplog):
    """Test add_carriage_return function using pytest.
    This is to test logging errors"""

    def mock_handle_error(msg, setup):
        if not setup:
            logging.error(msg)

    monkeypatch.setattr(files, "handle_npb_error", mock_handle_error)

    # Capture and check the logging level and logging messages.
    with caplog.at_level(files.logging.ERROR):
        files.add_carriage_return(inputs, eol, setup=False)

    results = [(r[1], r[2]) for r in caplog.record_tuples]
    # [1] is log level (logging.ERROR = 40)
    # [2] is log message

    assert results == expected

# ----------------------------------------------------------------------------
# files.add_crs_to_file tests
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("inputs, outputs", [
    ("Chatty\nkitty\n", "Chatty\nkitty\n"),
    ("Chatty kitty ", "Chatty kitty \n"),
    ("Kitty", "Kitty\n"),
    ("Kitty\n", "Kitty\n"),
    ("Meow \r\n", "Meow \n"),
    ("Meow\r\n Meow\r\n", 'Meow\n Meow\n'),
    ("\n", "\n"),
    ("", ""),
])
def test_add_crs_to_file_success_alt(tmp_path, inputs, outputs):
    """Test add_crs_to_file function using pytest.
    This is for a successful case"""
    fake_file = tmp_path / "file.txt"
    fake_file.write_text(inputs, newline='')

    files.add_crs_to_file(str(fake_file), eol="\n", setup=False)

    assert fake_file.read_text() == outputs

def test_add_crs_to_file_logging_error(monkeypatch, caplog):
    """Test add_crs_to_file function using pytest.
    This is to test logging errors"""
    def mock_handle_error(msg, setup):
        if not setup:
            logging.error(msg)

    monkeypatch.setattr(files, "handle_npb_error", mock_handle_error)
    bad_path = "/bad/path/file.txt"

    with caplog.at_level(files.logging.ERROR):
        files.add_crs_to_file(bad_path, eol="\n")

    expected = [(logging.ERROR, 'Carriage return adding error for /bad/path/file.txt.')]

    results = [(r[1], r[2]) for r in caplog.record_tuples]

    assert results == expected

# ----------------------------------------------------------------------------
# files.check_badchar tests
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("contents, expected", [
    ("the OSIRIS-REx spacecraft",[]),
    ("where\nVersion",[]),
    ("Mission © Bennu",["NON-ASCII character(s) in line 1:","Mission © Bennu","        ^      "]),
    ("INS-155101_FOV_REF_ANGLE”=",["NON-ASCII character(s) in line 1:","INS-155101_FOV_REF_ANGLE”=",
     "                        ^ "]),
    ("π = 3.14 & Σ = sum",["NON-ASCII character(s) in line 1:","π = 3.14 & Σ = sum",
     "^          ^      "]),
    ("Line 1: Mission\nLine 2: Ma”rs\nLine 3: and bye”nd",["NON-ASCII character(s) in line 2:","Line 2: Ma”rs",
     "          ^  ","NON-ASCII character(s) in line 3:","Line 3: and bye”nd","               ^  "]),
    ("",[]),
])
def test_check_badchar(tmp_path, contents, expected):
    """"Test check_badchar function using pytest."""
    test_file = tmp_path / "test_chars.txt"
    test_file.write_text(contents, encoding="utf-8")

    errors = files.check_badchar(str(test_file))

    assert errors == expected

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
    (Path('ek', 'lroevnt_2010193_2010200_v01.bes'), 'little',
     "The kernel cannot be loaded because of its endianness. Use NAIF's utility BINGO to convert the file."),
    (Path('ek','eros_n2000129x_v01_ltl.bpe'), 'little', None),
    (Path('ek', 'eros_n2000129x_v01.bpe'), 'little',
     "The kernel cannot be loaded because of its endianness. Use NAIF's utility BINGO to convert the file."),
    (Path('ek', 'S99_CIMSSSUPa.bep'), 'little',
     "The kernel cannot be loaded because of its endianness. Use NAIF's utility BINGO to convert the file."),
    (Path('ek', '11A.bdb'), 'little',
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
    (Path('ek', 'lroevnt_2010193_2010200_v01.bes'), 'big', None),
    (Path('ek', 'eros_n2000129x_v01_ltl.bpe'), 'big',
     "The kernel cannot be loaded because of its endianness. Use NAIF's utility BINGO to convert the file."),
    (Path('ek', 'eros_n2000129x_v01.bpe'), 'big', None),
    (Path('ek', 'S99_CIMSSSUPa.bep'), 'big', None),
    (Path('ek', '11A.bdb'), 'big', None),
    # Tests for "invalid SPICE kernel architecture."
    (Path('ck', 'insight_ida_enc_200829_201220_v1.xc'), 'little',
     'The binary kernel does not have a DAF or DAS architecture.'),
    (Path('pck', 'pck00010.tpc'), 'little',
     'The binary kernel does not have a DAF or DAS architecture.'),
    (Path('ek', 'm01_mmdmt_ext10.ten'), 'little',
     'The binary kernel does not have a DAF or DAS architecture.'),
    (Path('ck', 'insight_ida_enc_200829_201220_v1.xc'), 'big',
     'The binary kernel does not have a DAF or DAS architecture.'),
    (Path('pck', 'pck00010.tpc'), 'big',
     'The binary kernel does not have a DAF or DAS architecture.'),
    (Path('ek', 'm01_mmdmt_ext10.ten'), 'big',
     'The binary kernel does not have a DAF or DAS architecture.'),
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
    ([19], False),
    ([1, 19], False),
    ([1, 2], True),
])
def test_check_consecutive(lst, cc_bool):
    """Test check_consecutive function with pytest."""
    # Note - the function does not work if the list is empty, contains
    # no integer values or if the numbers within the list are negative.
    assert files.check_consecutive(list(lst)) is cc_bool

# ----------------------------------------------------------------------------
# files.check_eol tests
# ----------------------------------------------------------------------------

@pytest.mark.parametrize( "kern, eol, expected", [
    (Path(KERNELS/"mk"/"m2020_v09.tm"), "\n", ''),
    (Path(KERNELS/"mk"/"m2020_v09.tm"), "\r\n", "Incorrect EOL in file, CRLF (\\r\\n) expected."),
    (Path(KERNELS/"fk"/"clps_to_2ab_v01.tf"), "\r\n", "Incorrect EOL in file, CRLF (\\r\\n) expected."),
    (Path(KERNELS/"spk"/"maven_orb_rec_210101_210401_v2.bsp"), "\n", "Incorrect EOL in file, LF (\\n) expected."),
    (Path(KERNELS/"spk"/"maven_orb_rec_210101_210401_v2.bsp"), "\r\n", "Incorrect EOL in file, CRLF (\\r\\n) expected."),
    (Path(KERNELS/"dsk"/"DEIMOS_K005_THO_V01.BDS"), "\r\n", "Incorrect EOL in file, CRLF (\\r\\n) expected."),
    (Path(KERNELS / "dsk" / "DEIMOS_K005_THO_V01.BDS"), "\n", "Incorrect EOL in file, LF (\\n) expected."),
])
def test_check_eol(kern, eol, expected):
    """Test check_eol function using pytest."""
    result = files.check_eol(kern, eol)
    assert result == expected

@pytest.mark.parametrize("words, eol, expected", [
    ("happy\r\nday\r\n", "\r\n", ""),
    ("happy\nday\n", "\n", ""),
    ("hello\r\nworld\r\n", "\n", "Incorrect EOL in file, LF (\\n) expected."), #this doesn't work
    ("hello\nworld\r\n", "\r\n", "Incorrect EOL in file, CRLF (\\r\\n) expected.") #this doesn't work
])
def test_check_eol_alt(tmp_path, words, eol, expected):
    """Test check_eol function using pytest."""
    file_path = tmp_path / "test_eol.txt"
    with open(file_path, "wt", encoding='utf-8', newline='') as f:
        f.write(words)

    result = files.check_eol(str(file_path), eol)
    assert result == expected

def test_check_eol_logging_error(monkeypatch, tmp_path, caplog):
    """Test check_eol function using pytest.
    This is to test logging errors"""

    def mock_handle_error(msg, setup=False):
        if not setup:
            logging.error(msg)

    monkeypatch.setattr(files, "handle_npb_error", mock_handle_error)

    fake_file = tmp_path / "file.txt"
    fake_file.write_text("Hi \a")
    eol = "\a"

    # Capture and check the logging level and logging messages.
    with caplog.at_level(files.logging.ERROR):
        files.check_eol(fake_file, eol)

    expected = [(logging.ERROR,'Incorrect EOL in configuration: \a')]

    results = [(r[1], r[2]) for r in caplog.record_tuples]

    assert results == expected

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

    # Subcase 3: Incorrect file name → should raise ValueError
    bad_name = str(KERNELS / "ck" / "insight_ida_enc_200829_201220_v1.xc")

    expected_message = (
        "Unsupported kernel extension 'XC' for kernel "
        "insight_ida_enc_200829_201220_v1.xc: not present in the SPICE "
        "kernel type map.")

    with pytest.raises(ValueError, match=expected_message):
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
    """Test check_line_length function using pytest."""

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
# files.check_list_duplicates test
# ----------------------------------------------------------------------------

@pytest.mark.parametrize( "lst, expected", [
    ([KERNELS/'ck'/'insight_ida_enc_200829_201220_v1.bc'], False),
    ([KERNELS/'dsk'/'DEIMOS_K005_THO_V01.BDS', KERNELS/'dsk'/'DEIMOS_K005_THO_V01.BDS'], True),
    ([], False),
])
def test_check_list_duplicates(lst, expected):
    """Test check_list_duplicates function using pytest."""
    result = files.check_list_duplicates(list(lst))
    assert result == expected

# ----------------------------------------------------------------------------
# files.check_permissions test
# ----------------------------------------------------------------------------

@pytest.mark.parametrize( "path", [
    (Path(KERNELS/'ck'/'insight_ida_enc_200829_201220_v1.bc')),
    (Path(KERNELS/'dsk'/'DEIMOS_K005_THO_V01.BDS')),
])
def test_check_permissions(path):
    """Test check_permissions function using pytest."""
    files.check_permissions(str(path))

def test_check_permissions_error(monkeypatch, tmp_path, caplog):
    """Test check_permissions function using pytest.
    This is to test logging errors"""
    def mock_handle_error(msg):
        logging.error(msg)

    def raise_permission_error(*_, **__):
        raise PermissionError()


    fake_file = tmp_path / "file.txt"
    fake_file.write_text("Secret")

    monkeypatch.setattr(files, "handle_npb_error", mock_handle_error)
    monkeypatch.setattr(files.Path, "open", raise_permission_error)

    with caplog.at_level(logging.ERROR):
        files.check_permissions(str(fake_file))

    assert (
        f"File {fake_file} is not readable by the account that runs NPB. "
        "Update permissions." in caplog.text
    )

# ----------------------------------------------------------------------------
# files.checksum_from_label test
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("prod_path, expected, expected_logs",[
    (Path(KERNELS/"ck"/"insight_ida_enc_200829_201220_v1.bc"),
     "22f9acc1931c8a626fac2a844fc5cee3",
     [(logging.WARNING, '-- Checksum obtained from existing label: insight_ida_enc_200829_201220_v1.xml')]),
    (Path(KERNELS/"mk"/"none.tm"), "",
     []),
])
def test_checksum_from_label(prod_path, expected, expected_logs, caplog):
    """Test checksum_from_label function using pytest."""
    with caplog.at_level(logging.WARNING):
        result = files.checksum_from_label(str(prod_path))
    assert result == expected
    logs = [(r[1], r[2]) for r in caplog.record_tuples]
    assert logs == expected_logs

# TODO: Check if this option (having a label without checksum is valid for SPICE PDS4) is valid.
def test_checksum_from_label_without_checksum(tmp_path, caplog):
    path = tmp_path / "file.bc"
    label = tmp_path / "file.xml"
    label.write_text("""<?xml version="1.0" encoding="utf-8"?>""")
    with caplog.at_level(logging.WARNING):
        result = files.checksum_from_label(str(path))
    logs = [(r[1], r[2]) for r in caplog.record_tuples]
    assert result == ''
    assert logs == []

def test_checksum_from_label_multi_dot_name(tmp_path, caplog):
    """Multi-dot kernel names must resolve to their correctly-suffixed label,
    not one truncated at the first dot."""
    kernel = tmp_path / "kernel.v1.2.bc"
    kernel.write_text("dummy")
    label = tmp_path / "kernel.v1.2.xml"
    label.write_text(
        "<product><md5_checksum>ABC123</md5_checksum></product>"
    )

    with caplog.at_level(logging.INFO):
        result = files.checksum_from_label(str(kernel))

    logs = [(r[1], r[2]) for r in caplog.record_tuples]
    assert result == "ABC123"
    assert logs == [
        (logging.WARNING, "-- Checksum obtained from existing label: kernel.v1.2.xml")
    ]

# ----------------------------------------------------------------------------
# files.checksum_from_registry test
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("prod_path, chcksm", [
    ("ladee_v10.tm", {"1.checksum": "path/ladee_v10.tm   abcdefg10987654321"}),
    ("mars2020_v04.bc", {"1.checksum": "not_the_right.bc  wrong", "2.checksum": "path/mars2020_v04.bc  looksright6789"}),
    ("missing.tf", {"1.checksum": "other.tf  nothere12345"}),
    ("any.bsp", {}),
])
def test_checksum_from_registry_logging_error(monkeypatch, tmp_path, prod_path, chcksm, caplog):
    """Test checksum_from_registry function using pytest
    This is to test logging errors"""
    # checksum_found will always be False: the for loop in line 731 will either finish when one checksum is found
    # -- see break in line 743, or when no checksum is found and no more registries are in checksum_registries
    for filename, content in chcksm.items():
        file_path = tmp_path / filename
        file_path.write_text(content)

    def mock_handle_error(msg, setup):
        if not setup:
            logging.error(msg)

    monkeypatch.setattr(files, "handle_npb_error", mock_handle_error)

    # Capture and check the logging level and logging messages.
    with caplog.at_level(files.logging.ERROR):
        files.checksum_from_registry(prod_path, str(tmp_path))

    expected = []

    results = [(r[1], r[2]) for r in caplog.record_tuples]

    assert results == expected

# ----------------------------------------------------------------------------
# files.compare_files test
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("from_text, to_text, disp, expected, files_created",[
    ("Meow\n", "Meow\n", "log", False, 0),
    ("Meow\r\n", "Meow\n", "log", True, 0),
    ("Meow\n", "Meow\n", "files", False, 0),
    ("Meow\n", "Meow\n", "all", False, 0),
    ("Unicorn\n", "Donkey\n", "log", True, 0),
    ("Unicorn\n", "Donkey\n", "files", True, 1),
    ("Donkey\n", "Shrek\n", "all", True, 1),
    ("Donkey\nvisits\nShrek", "Fiona\nvisits\nShrek", "all", True, 1),
])
def test_compare_files(tmp_path, from_text, to_text, disp, expected, files_created):
    """Test compare_files function using pytest. Mocks files/contents to test."""
    fromfile = tmp_path / "from.txt"
    tofile = tmp_path / "to.txt"
    dest = tmp_path / "diffs"
    dest.mkdir()

    fromfile.write_text(from_text)
    tofile.write_text(to_text)

    files.md5.side_effect = lambda x: "hash_a" if "line1" in Path(x).read_text() else "hash_b"

    with patch("logging.info"):
        with patch("builtins.open", side_effect=open):
            result = files.compare_files(str(fromfile), str(tofile), str(dest), disp)

    assert result == expected

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

def test_copy_enotdir(tmp_path):
    """Test copy function using pytest.
    This tests ENOTDIR.
    """
    src = tmp_path / "source.txt"
    src.write_text("Happy Kitty")
    dest = tmp_path / "destination.txt"

    files.copy(str(src), str(dest))

    assert dest.exists()
    assert dest.read_text() == "Happy Kitty"

def test_copy_error_file(monkeypatch, tmp_path, caplog):
    """Test copy function using pytest.
    This is for a case when the source was a file"""
    src = "file.txt"
    dest = tmp_path / "destination"

    with caplog.at_level(files.logging.WARNING):
        files.copy(str(src), str(dest))

    # The error generated by the OS is different in different platforms.
    # Check that part of the message that NPB generates is the expected
    # one.
    assert len(caplog.records) == 1
    assert caplog.messages[0].startswith("-- Directory file.txt not copied, probably "
                                         "because the increment directory exists.\nError:")

# ----------------------------------------------------------------------------
# files.etree_to_dict test
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("xml, outputs", [
    ( "<root>howdy</root>", {"root": "howdy"}),
    ("<empty></empty>",{"empty": None}),
    ("<version_id>2.0</version_id>", {"version_id": "2.0"}),
    ("<purpose>Observation Geometry</purpose>", {"purpose": "Observation Geometry"}),
    ("<lidvid_reference>urn:nasa:pds:psyche.spice:document::1.0</lidvid_reference>", {"lidvid_reference": "urn:nasa:pds:psyche.spice:document::1.0"}),
    ("""
        <Internal_Reference>
          <lid_reference>urn:nasa:pds:psyche.spice:document:spiceds</lid_reference>
        </Internal_Reference>
      """ , {"Internal_Reference": {"lid_reference": "urn:nasa:pds:psyche.spice:document:spiceds"}}),
    ("""
        <Target_Identification>
          <Internal_Reference>
            <lid_reference>urn:nasa:pds:context:target:asteroid.16_psyche</lid_reference>
            <reference_type>bundle_to_target</reference_type>
          </Internal_Reference>
        </Target_Identification>""", {"Target_Identification": {'Internal_Reference': {'lid_reference': 'urn:nasa:pds:context:target:asteroid.16_psyche', 'reference_type': 'bundle_to_target'}}}),
    ("""    
        <Investigation_Area>
          <name>Psyche Mission</name>
          <type>Mission</type>
          <Internal_Reference>
            <lid_reference>urn:nasa:pds:context:investigation:mission.psyche</lid_reference>
            <reference_type>data_to_investigation</reference_type>
          </Internal_Reference>
        </Investigation_Area>""" , {"Investigation_Area": {'name': 'Psyche Mission', 'type': 'Mission','Internal_Reference': {'lid_reference': 'urn:nasa:pds:context:investigation:mission.psyche', 'reference_type': 'data_to_investigation'}}}),
    ("""
        <File>
          <file_name>collection_miscellaneous_inventory_v002.csv</file_name>
          <creation_date_time>2025-11-04T11:11:21</creation_date_time>
          <file_size unit="byte">128</file_size>
          <md5_checksum>a82b2c60ef82e51ae237eb09f82d2eaa</md5_checksum>
        </File>""", {"File": {"file_name": "collection_miscellaneous_inventory_v002.csv", "creation_date_time": "2025-11-04T11:11:21", "file_size": {"@unit": "byte", "#text": "128"}, "md5_checksum": "a82b2c60ef82e51ae237eb09f82d2eaa"}}),
])
def test_etree_to_dict(xml, outputs):
    """Test etree_to_dict function using pytest."""
    etree = ElementTree.fromstring(xml)

    result = files.etree_to_dict(etree)
    assert result == outputs

# ----------------------------------------------------------------------------
# files.extract_comment tests
# ----------------------------------------------------------------------------

def test_extract_comment_ck():
    """Test extract_comment function using pytest - comment extraction from kernel."""
    comment = files.extract_comment(str(KERNELS/"ck"/"insight_ida_enc_200829_201220_v1.bc"))
    comment_line = " This CK file was created using CKSLICER Utility Ver. 1.3.0, October 28, 2011"

    assert comment_line == comment[3]

@pytest.mark.parametrize("kern, comment, num",[
    (KERNELS/"ck"/"mro_sa_psp_210705_210717p.bc",
     " This CK file was created using CKSLICER Utility Ver. 1.3.0, October 28, 2011", "3"),
    (KERNELS/"ck"/"one_blank.bc",
     "LSK_FILE_NAME           = 'naif0012.tls'", "8"),
    (KERNELS/"ck"/"many_blanks.bc",
     "LSK_FILE_NAME           = 'naif0012.tls'", "8"),
])
def test_extract_comment_ck_2(kern, comment, num):
    """Test extract_comment function using pytest.
    Extract comments from normal DAF, as well as others"""
    result = files.extract_comment(str(kern))

    assert comment == result[int(num)]

@pytest.mark.parametrize("kern",[
    (KERNELS/"ck"/"buffer_buster.bc"),
])
def test_extract_comment_error(monkeypatch, kern, caplog):
    """Test extract_comment function using pytest. This is to test logging errors"""

    def mock_handle_error(msg, **_):
        files.logging.getLogger("files").error(msg)

    monkeypatch.setattr(files, "handle_npb_error", mock_handle_error)

    with caplog.at_level(files.logging.ERROR):
        files.extract_comment(str(kern))

    assert f"Comment from {kern} is longer than buffer size." in caplog.text

def test_extract_comments_with_daf_handle(daf_handle):
    """Test that the function also operates on already opened DAF files.
    """
    files.extract_comment('Path is not relevant for this test.', daf_handle)

    # Test if the DAF file is still open by reading the summary format
    # associated with the handle. If the file is closed, this call will
    # return an error (SpiceDAFNOSUCHHANDLE).
    spiceypy.dafhsf(daf_handle)


@pytest.mark.parametrize('read_comments, comments_out', [
    (['some comment', '', 'Some other comment', '', ' ', ''], ['some comment', '', 'Some other comment']),
    (['some comment', '', 'Some other comment', ''], ['some comment', '', 'Some other comment']),
    (['some comment', '', 'Some other comment'], ['some comment', '', 'Some other comment']),
    ([' ', '', ' '], [])
])
def test_extract_comments_remove_blanks_end_of_comments(monkeypatch, daf_handle, read_comments, comments_out):
    """Test that the function also operates on already opened DAF files.
    """
    # Patch the dafec call to have proper control of the comments, without having to
    # write a new file.
    monkeypatch.setattr("spiceypy.dafec", lambda *args: (6, read_comments, True))

    result = files.extract_comment('Path is not relevant for this test.', daf_handle)

    assert result == comments_out

# ----------------------------------------------------------------------------
# files.fill_template tests
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("contents, dct, expected", [
    ("$MISSION_NAME is a mission to $TARGET!", {"MISSION_NAME": "Mars2020", "TARGET": "Mars"}, "Mars2020 is a mission to Mars!\n"),
    ("<Time_Coordinates>\n<start_date_time>$START_TIME</start_date_time>\n<stop_date_time>$STOP_TIME</stop_date_time>\n</Time_Coordinates>", {"START_TIME": "2021-10-16T10:32:00Z", "STOP_TIME": "2025-05-05T00:29:39Z"}, "<Time_Coordinates>\n<start_date_time>2021-10-16T10:32:00Z</start_date_time>\n<stop_date_time>2025-05-05T00:29:39Z</stop_date_time>\n</Time_Coordinates>\n"),
    ("My cats like to $WHAT", {"WHAT": "purrrr"}, "My cats like to purrrr\n"),
    ("<title>$PDS4_MISSION_NAME SPICE Kernel Collection</title>", {"PDS4_MISSION_NAME": "Lucy"}, "<title>Lucy SPICE Kernel Collection</title>\n" ),
])
def test_fill_template(tmp_path, contents, dct, expected):
    """Test fill_template function using pytest."""

    class MockListObject:
        def __init__(self, template_path):
            self.template = template_path

    template_file = tmp_path / "template.txt"
    template_file.write_text(contents)
    product_file = tmp_path / "output.txt"
    product_dictionary = dct

    list_object = MockListObject(str(template_file))

    files.fill_template(list_object, str(product_file), product_dictionary)

    result = product_file.read_text()
    assert result == expected

# ----------------------------------------------------------------------------
# files.format_multiple_values tests
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("value, expected", [
    ("NAIF", "NAIF"),
    (["NAIF","SSD","PRIMARY"], ["NAIF", "SSD", "PRIMARY"]),
    ("NAIF, SSD, PRIMARY", '{\n                               NAIF,\n                                SSD,\n                                PRIMARY\n                               }\n'),
])
def test_format_multiple_values(value, expected):
    """Test format_multiple_values function using pytest."""
    result = files.format_multiple_values(value)
    assert result == expected

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
def test_get_context_products_no_optional_info_in_config_file(mission, observer, target, expected_bcp):
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

def test_get_context_products_overwrite_and_append(tmp_path):
    """Test get_context_products using pytest. Update existing products via setup.context_products."""
    setup = MagicMock()
    setup.mission_name = "Mars 2020: Perseverance Rover"
    setup.observer = "The Mars 2020 Perseverance Rover"
    setup.target = "Mars"

    #config defined context products
    setup.context_products = {
        "product": [
            {"@name": "Mars 2020: Perseverance Rover", "type": "Mission", "lidvid": "urn:nasa:pds:context:investigation:mission.mars2020::2.1"},
            {"@name": "Mars", "type": "Planet", "lidvid": "urn:nasa:pds:context:target:planet.mars::1.3"},
            {"@name": "The Mars 2020 Perseverance Rover", "type": "Rover", "lidvid": "urn:nasa:pds:context:instrument_host:spacecraft.mars2020::1.3"}
        ]
    }

    result = files.get_context_products(setup)

    miss_prod = next(cp for cp in result if cp["name"][0] == "Mars 2020: Perseverance Rover")
    assert miss_prod["lidvid"] == "urn:nasa:pds:context:investigation:mission.mars2020::2.1"

    targ_prod = next(cp for cp in result if cp["name"][0] == "Mars")
    assert targ_prod["lidvid"] == "urn:nasa:pds:context:target:planet.mars::1.3"

    obs_prod = next(cp for cp in result if cp["name"][0] == "The Mars 2020 Perseverance Rover")
    assert obs_prod["type"] == ["Rover"]
    assert obs_prod["lidvid"] == "urn:nasa:pds:context:instrument_host:spacecraft.mars2020::1.3"


def test_get_context_products_overwrite_updates_matched_entry():
    """The override must land on the registered product that actually matches by
    name, not on an unrelated entry. Uses override values that differ from the
    registered defaults, so a version of the code that writes to the wrong
    entry would leave this entry with its stale (pre-override) values and fail
    the assertions."""
    setup = MagicMock()
    setup.mission_name = "MARS 2020"
    setup.observer = "Perseverance"
    setup.target = "MARS"

    setup.context_products = {
        "product": [
            {"@name": "Perseverance", "type": "Rover", "lidvid": "urn:nasa:pds:context:instrument_host:spacecraft.mars2020::9.9"},
        ]
    }

    result = files.get_context_products(setup)

    obs_prod = next(cp for cp in result if cp["name"][0] == "Perseverance")
    assert obs_prod["type"] == ["Rover"]
    assert obs_prod["lidvid"] == "urn:nasa:pds:context:instrument_host:spacecraft.mars2020::9.9"


def test_get_context_products_same_name_different_type():
    """A mission and its own spacecraft/observer commonly share a name in real
    configs (e.g. LADEE, MAVEN) but differ in type. Overriding one must not
    clobber the other -- matching must be keyed on (name, type), not name
    alone."""
    setup = MagicMock()
    setup.mission_name = "LADEE"
    setup.observer = "LADEE"
    setup.target = "MOON"

    setup.context_products = {
        "product": [
            {"@name": "LADEE", "type": "Mission", "lidvid": "urn:nasa:pds:context:investigation:mission.ladee::1.3"},
            {"@name": "LADEE", "type": "Spacecraft", "lidvid": "urn:nasa:pds:context:instrument_host:spacecraft.ladee::1.2"},
        ]
    }

    result = files.get_context_products(setup)

    ladee_entries = [cp for cp in result if cp["name"][0] == "LADEE"]
    assert len(ladee_entries) == 2

    mission = next(cp for cp in ladee_entries if cp["type"] == ["Mission"])
    spacecraft = next(cp for cp in ladee_entries if cp["type"] == ["Spacecraft"])
    assert mission["lidvid"] == "urn:nasa:pds:context:investigation:mission.ladee::1.3"
    assert spacecraft["lidvid"] == "urn:nasa:pds:context:instrument_host:spacecraft.ladee::1.2"


def test_get_context_products_type_match_is_case_insensitive():
    """The registry and configs don't always agree on type casing (e.g. registry
    stores MOON as 'SATELLITE', configs say 'Satellite'). A case-sensitive type
    match would treat this as no match and append a spurious duplicate entry
    instead of updating the existing one."""
    setup = MagicMock()
    setup.mission_name = "MISSION"
    setup.observer = "OBSERVER"
    setup.target = "MOON"

    setup.context_products = {
        "product": [
            {"@name": "MOON", "type": "Satellite", "lidvid": "urn:nasa:pds:context:target:satellite.earth.moon::9.9"},
        ]
    }

    result = files.get_context_products(setup)

    moon_entries = [cp for cp in result if cp["name"][0] == "MOON"]
    assert len(moon_entries) == 1
    assert moon_entries[0]["lidvid"] == "urn:nasa:pds:context:target:satellite.earth.moon::9.9"


def test_get_context_products_override_updates_all_matching_entries():
    """(name, type) is not a unique key in the registry -- e.g. ULYSSES has both
    an ESA PSA and a NASA PDS 'Mission' entry with different lidvids. When a
    user provides an override for a (name, type) pair, all registry entries
    sharing that pair are updated to the override lidvid."""
    setup = MagicMock()
    setup.mission_name = "ULYSSES"
    setup.observer = "OBSERVER"
    setup.target = "TARGET"

    override_lidvid = "urn:nasa:pds:context:investigation:mission.ulysses::9.9"

    setup.context_products = {
        "product": [
            {"@name": "ULYSSES", "type": "Mission", "lidvid": override_lidvid},
        ]
    }

    result = files.get_context_products(setup)

    mission_entries = [cp for cp in result if cp["name"][0] == "ULYSSES" and cp["type"] == ["Mission"]]
    assert len(mission_entries) == 2
    assert all(cp["lidvid"] == override_lidvid for cp in mission_entries)


def test_get_context_products_overwrite_and_append_2(tmp_path):
    """Test get_context_products using pytest. Default products match products via setup.context_products."""
    setup = MagicMock()
    setup.mission_name = "MARS 2020"
    setup.observer = "Perseverance"
    setup.target = "MARS"

    #config defined context products
    setup.context_products = {
        "product": [
            {"@name": "Mars 2020: Perseverance Rover", "type": "Mission", "lidvid": "urn:nasa:pds:context:investigation:mission.mars2020::1.0"},
            {"@name": "Perseverance", "type": "Rover", "lidvid": "urn:nasa:pds:context:instrument_host:spacecraft.mars2020::1.0"},
            {"@name": "MARS", "type": "PLANET", "lidvid": "urn:nasa:pds:context:target:planet.mars::1.2"}
        ]
    }

    result = files.get_context_products(setup)

    miss_prod = next(cp for cp in result if cp["name"][0] == "MARS 2020")
    assert miss_prod["lidvid"] == "urn:nasa:pds:context:investigation:mission.mars2020::1.0"
    assert miss_prod["type"] == ["Mission"]

    targ_prod = next(cp for cp in result if cp["name"][0] == "MARS")
    assert targ_prod["lidvid"] == "urn:nasa:pds:context:target:planet.mars::1.2"
    assert targ_prod["type"] == ["PLANET"]

    obs_prod = next(cp for cp in result if cp["name"][0] == "Perseverance")
    assert obs_prod["type"] == ["Rover"]
    assert obs_prod["lidvid"] == "urn:nasa:pds:context:instrument_host:spacecraft.mars2020::1.0"

def test_get_context_products_from_a_dict(tmp_path):
    """Test get_context_products using pytest. setup has context_products and product is a dict and not a list.
    TODO: Analyze if this case is possible, otherwise update the code.
    """
    setup = MagicMock()
    setup.mission_name = "MARS 2020"
    setup.observer = "Perseverance"
    setup.target = "MARS"

    #config defined context products
    setup.context_products = {
        "product": {"@name": "Mars 2020: Perseverance Rover",
                    "type": "Mission",
                    "lidvid": "urn:nasa:pds:context:investigation:mission.mars2020::1.0"}
    }

    result = files.get_context_products(setup)
    expected = [
        {'name': ['Perseverance'],
         'type': ['Rover'],
         'lidvid': 'urn:nasa:pds:context:instrument_host:spacecraft.mars2020::1.0'},
        {'name': ['MARS'],
         'type': ['PLANET'],
         'lidvid': 'urn:nasa:pds:context:target:planet.mars::1.2'},
        {'name': ['MARS 2020'],
         'type': ['Mission'],
         'lidvid': 'urn:nasa:pds:context:investigation:mission.mars2020::1.0'}]
    assert result == expected

def test_get_context_products_list_with_empty_dictionary(tmp_path):
    """Test get_context_products using pytest. setup has context_products but it is a list
    with an empty dictionary. In this case, it should go be to default.
    TODO: Analyze if this case is possible, otherwise update the code.
    """
    setup = MagicMock()
    setup.mission_name = "MARS 2020"
    setup.observer = "Perseverance"
    setup.target = "MARS"

    #config defined context products
    setup.context_products = {
        "product": [{}]
    }

    result = files.get_context_products(setup)
    expected = [
        {'name': ['Perseverance'],
         'type': ['Rover'],
         'lidvid': 'urn:nasa:pds:context:instrument_host:spacecraft.mars2020::1.0'},
        {'name': ['MARS'],
         'type': ['PLANET'],
         'lidvid': 'urn:nasa:pds:context:target:planet.mars::1.2'},
        {'name': ['MARS 2020'],
         'type': ['Mission'],
         'lidvid': 'urn:nasa:pds:context:investigation:mission.mars2020::1.0'}]
    assert result == expected

# default should probably be removed .... requires a JSON file to be updated and I
# do not want this capability

# ----------------------------------------------------------------------------
# files.get_latest_kernel test
# ----------------------------------------------------------------------------

def test_get_latest_kernel_success():
    """Test get_latest_kernel using pytest - basic."""
    pattern = "insight_ida_enc_[0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9]_v[0-9].bc"

    result = files.get_latest_kernel("ck", [str(KERNELS)], pattern)
    assert result == 'insight_ida_enc_200829_201220_v1.bc'

def test_get_latest_kernel_invalid_pattern_no_kernels_found():
    """Test get_latest_kernel using pytest - basic."""
    pattern = "([a-z]+"  # --> this produces a re.error.

    result = files.get_latest_kernel("ck", [str(KERNELS)], pattern)
    assert result == []

def test_get_latest_kernel_with_dates_logic(tmp_path):
    """Test get_latest_kernel using pytest.
    Test filtering versions when dates=True in config.
    Expectation - return latest version for each date/pattern"""
    pth = tmp_path / "ck"
    pth.mkdir()

    kern = [
        "mission_20260101_v01.bc",
        "mission_20260101_v02.bc",
        "mission_20260401_v01.bc"
    ]
    for k in kern:
        (pth / k).write_text("")

    pths = [str(tmp_path)]
    pttrn = "mission_[0-9]{8}_v[0-9][0-9].bc"

    result = files.get_latest_kernel("ck", pths, pttrn, dates=True)

    assert "mission_20260101_v02.bc" in result
    assert "mission_20260401_v01.bc" in result
    assert "mission_20260101_v01.bc" not in result

def test_get_latest_kernel_with_mks(tmp_path):
    """Test get_latest_kernel using pytest.
    Test that kernel strings parsed out of an MK are collected."""
    spk_pth = tmp_path / "spk"
    spk_pth.mkdir()
    (spk_pth / "mission_v01.bsp").touch()

    mk_pth = tmp_path / "mk"
    mk_pth.mkdir()
    meta_kernel_file = mk_pth / "mk.tm"

    meta_kernel_file.write_text(
        "KERNELS_TO_LOAD = (\n"
        "    '$KERNELS/spk/mission_v02.bsp'\n"
        ")",
        encoding="utf-8"
    )

    result = files.get_latest_kernel(
        kernel_type="spk",
        paths=[str(tmp_path)],
        pattern=r"mission_v\d+\.bsp",
        dates=False,
        mks=[str(meta_kernel_file)]
    )

    assert result == "mission_v02.bsp"

def test_get_latest_kernel_excluded_kernels(tmp_path):
    """Test get_latest_kernel using pytest.
    Test that only the files you want to include are included."""
    fk_pth = tmp_path / "fk"
    fk_pth.mkdir()

    (fk_pth / "frames_v01.tf").touch()
    (fk_pth / "frames_v02.tf").touch()
    (fk_pth / "alt_frames_v01.tf").touch()

    result = files.get_latest_kernel(
        kernel_type="fk",
        paths=[str(tmp_path)],
        pattern=r".*\.tf",
        dates=False,
        excluded_kernels=["alt*"]
    )

    assert result == "frames_v02.tf"

def test_get_latest_kernel_excluded_kernels_consecutive_matches(tmp_path):
    """Excluding kernels that are consecutive in sorted order must not skip any
    of them (list.remove() during iteration used to skip the element following
    each removed item)."""
    fk_pth = tmp_path / "fk"
    fk_pth.mkdir()

    (fk_pth / "alt_frames_v01.tf").touch()
    (fk_pth / "alt_frames_v02.tf").touch()
    (fk_pth / "frames_v01.tf").touch()
    (fk_pth / "frames_v02.tf").touch()
    (fk_pth / "other_frames_v01.tf").touch()

    result = files.get_latest_kernel(
        kernel_type="fk",
        paths=[str(tmp_path)],
        pattern=r".*\.tf",
        dates=False,
        excluded_kernels=["alt*", "other*"]
    )

    assert result == "frames_v02.tf"

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
    """Test match_patterns utils function using pytest. Basic."""
    name_w_pattern = "insight_$YEAR_v$VERSION.tm"
    name = "insight_2021_v02.tm"
    patterns = [
        {"@length": "2", "#text": "VERSION"},
        {"@length": "4", "#text": "YEAR"},
    ]

    values = files.match_patterns(name, name_w_pattern, patterns)

    assert values == {"YEAR": "2021", "VERSION": "02"}

def test_match_patterns_missing_pattern():
    """Test match_patterns utils function using pytest.
    Check for missing patterns."""
    name_w_pattern = "insight_$YEAR_v$VERSION.tm"
    name = "insight_2021_v02.tm"
    patterns = [{"@length": "2", "#text": "VERSION"}]

    with pytest.raises(RuntimeError, match=r"Pattern mismatch at index 9: expected 'Y' but got '0'"):
        files.match_patterns(name, name_w_pattern, patterns)

def test_match_patterns_typo_in_template():
    """Test match_patterns utils function using pytest.
    Check for issues with patterns - typos in template."""
    name_w_pattern = "insight_$YER_v$VERSION.tm"
    name = "insight_2021_v02.tm"
    patterns = [
        {"@length": "2", "#text": "VERSION"},
        {"@length": "4", "#text": "YEAR"},
    ]

    with pytest.raises(RuntimeError, match=r"Pattern mismatch at index 9: expected 'Y' but got '0'"):
        files.match_patterns(name, name_w_pattern, patterns)

def test_match_patterns_typo_in_patterns():
    """Test match_patterns utils function using pytest.
    Check for issues with patterns - typos in patterns."""
    name_w_pattern = "insight_$YEAR_v$VERSION.tm"
    name = "insight_2021_v02.tm"
    patterns = [
        {"@length": "2", "#text": "VERSION"},
        {"@length": "4", "#text": "YAR"},
    ]

    with pytest.raises(RuntimeError, match=r"Pattern mismatch at index 9: expected 'Y' but got '0'"):
        files.match_patterns(name, name_w_pattern, patterns)

def test_match_patterns_wrong_length():
    """Test match_patterns utils function using pytest.
    Check for issues with patterns - wrong length."""
    name_w_pattern = "insight_$YEAR_v$VERSION.tm"
    name = "insight_2021_v02.tm"
    patterns = [
        {"@length": "2", "#text": "VERSION"},
        {"@length": "10", "#text": "YEAR"},
    ]

    with pytest.raises(RuntimeError, match=r"Pattern mismatch at index 18: expected '_' but got 'm'"):
        files.match_patterns(name, name_w_pattern, patterns)

# ----------------------------------------------------------------------------
# files.md5 test
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("fname, expected", [
    ( KERNELS / "ck" / "insight_ida_enc_200829_201220_v1.bc" , "22f9acc1931c8a626fac2a844fc5cee3"),
])
def test_md5(fname, expected):
    """Test md5 function using pytest."""
    result = files.md5(str(fname))
    assert result == expected

# ----------------------------------------------------------------------------
# files.mk_to_list tests
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("mk, num_kernels, first, last", [
    (KERNELS / "mk" / "vco_v01.tm", 46, 'naif0012.tls', 'vco_xmga_2016_v01.bc'),
    (KERNELS / "mk" / "msl_v29.tm", 220, 'naif0012.tls', 'msl_surf_rsm_tlmres_3192_3289_v1.bc')
])
def test_mk_to_list(mk, num_kernels, first, last):
    """Test mk_to_list function using pytest."""
    kernels = files.mk_to_list(str(mk), False)
    assert num_kernels == len(kernels)
    assert kernels[0] == first  # First kernel in the list
    assert kernels[-1] == last  # Last kernel in the list


def test_mk_to_list_error(monkeypatch, tmp_path, caplog):
    """Test mk_to_list function using pytest. This is to test logging errors"""
    mk_content = (
        "KPL/MK\n"
        "\n"
        "\\begindata\n"
        "\n"
        "PATH_VALUES = ( './data' )\n"
        "PATH_SYMBOLS = ( 'KERNELS' )\n"
        "KERNELS_TO_LOAD = (\n"
        ")\n"
    )
    mk = tmp_path / "empty_kernels.tm"
    mk.write_text(mk_content)

    def mock_handle_error(msg, **_):
        files.logging.getLogger("files").error(msg)

    monkeypatch.setattr(files, "handle_npb_error", mock_handle_error)

    with caplog.at_level(files.logging.ERROR):
        files.mk_to_list(str(mk), setup=False)

    assert [f"No kernels present in {mk}. Please review MK generation."] == caplog.messages

# TODO: BUG: This demonstrates an issue with the code. The proposed metakernel is
#       not valid. If loaded into SPICE,  it would produce a SPICE(FILEREADFAILED)
#       error, caused by the empty kernel name. This means, that in this case, NPB
#       shall produce an error and not silently skipping the invalid entry in the
#       metakernel.
def test_mk_to_list_skips_empty_kernel_after_trailing_slash(tmp_path):
    """Kernel paths ending with '/' produce an empty string after split('/') [-1].
    Those entries must be silently skipped while valid entries are still collected."""
    mk_content = (
        "KPL/MK\n"
        "\n"
        "\\begindata\n"
        "\n"
        "PATH_VALUES = ( './data' )\n"
        "PATH_SYMBOLS = ( 'KERNELS' )\n"
        "KERNELS_TO_LOAD = (\n"
        "  '$KERNELS/'\n"                     # trailing slash → empty kernel name
        "  '$KERNELS/naif0012.tls'\n"
        ")\n"
    )
    mk = tmp_path / "trailing_slash.tm"
    mk.write_text(mk_content)

    kernels = files.mk_to_list(str(mk), setup=False)
    assert kernels == ["naif0012.tls"]


# ----------------------------------------------------------------------------
# files.product_mapping test
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("miss_acr, rel, ker_list, text, name, expected", [
    ("VOYAGER",
     "5" ,
     "VOYAGER_Release_05.kernel_list",
     "my_kernel\n  MAPPING = success",
     'my_kernel',
     "success"),
    ("M2020",
     "1",
     "M2020_Release_01.kernel_list",
     "M2020_168_SCLKSCET.20260419.tsc\n  MAPPING = m2020_168_sclkscet_20260419.tsc",
     'M2020_168_SCLKSCET.20260419.tsc',
     "m2020_168_sclkscet_20260419.tsc" )
])
def test_product_mapping(tmp_path, miss_acr,  rel, ker_list, text, name, expected):
    """Test product_mapping function using pytest."""
    setup = MagicMock()
    setup.working_directory = str(tmp_path)
    setup.mission_acronym = miss_acr
    setup.run_type = "Release"
    setup.release = rel

    kernel_list_file = tmp_path / ker_list
    kernel_list_file.write_text(text)

    result = files.product_mapping(name, setup)

    assert result == expected

def test_product_mapping_error_handling(monkeypatch, tmp_path):
    """Test product_mapping using pytest. Check error handling is triggered correctly."""
    setup = MagicMock()
    setup.working_directory = str(tmp_path)
    setup.mission_acronym = "NoOne"
    setup.run_type = "Release"
    setup.release = "1"

    monkeypatch.setattr("builtins.open", lambda f, read, encoding: io.StringIO(""))

    # Track calls to handle_npb_error in list
    called = []

    def mock_error_handler(msg, **_):
        called.append(msg)

    monkeypatch.setattr(files,"handle_npb_error", mock_error_handler)

    files.product_mapping("NON_EXISTENT", setup, cleanup=True)

    assert len(called) == 1
    assert "does not have mapping" in called[0]


def test_product_mapping_cleanup(monkeypatch, tmp_path):
    """Test product_mapping using pytest - check cleanup=False prevents the error handler from running."""
    setup = MagicMock()
    setup.working_directory = str(tmp_path)
    setup.mission_acronym = "NoOne"
    setup.run_type = "Release"
    setup.release = "1"

    monkeypatch.setattr("builtins.open", lambda f, read, encoding: io.StringIO(""))

    result = files.product_mapping("NON_EXISTENT", setup, cleanup=False)

    assert result is False

# ----------------------------------------------------------------------------
# files.replace_string_in_file test
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("contents, old_str, new_str, eol_pds3, expected", [
    ("Howdy Cowboy\n", "Cowboy", "Cowgirl", "\n", "Howdy Cowgirl\n"),
    ("Venus Saturn Mars Venus\n", "Venus", "Earth", "\n", "Earth Saturn Mars Earth\n"),
    ("Mission A\nMission B\n", "Mission", "Spacecraft", "\n", "Spacecraft A\nSpacecraft B\n"),
    ("Happy Kitty\n", "Kitty", "kitty", "\n", "Happy kitty\n"),
])
def test_replace_string_in_file(tmp_path, contents, old_str, new_str, eol_pds3, expected):
    """Test replace_string_in_file function using pytest."""
    fake_file = tmp_path / "fake_file.txt"
    fake_file.write_text(contents)

    mock_setup = MagicMock()
    mock_setup.eol_pds3 = eol_pds3

    files.replace_string_in_file(str(fake_file), old_str, new_str, mock_setup)
    final_content = fake_file.read_text()
    assert final_content == expected

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

def test_safe_make_directory_logging(mocker, tmp_path):
    """Test safe_make_directory function using pytest.
    This is for reporting in logging"""
    mock_mkdir = mocker.patch("os.mkdir")
    mock_info = mocker.patch("logging.info")
    path = tmp_path / "dir_path"

    files.safe_make_directory(str(path))
    mock_mkdir.assert_called_once_with(str(path))

    expected_calls = [
        call('-- Generated directory: %s  ', str(path)),
        call('')
    ]
    assert mock_info.call_args_list == expected_calls

# ----------------------------------------------------------------------------
# files.string_in_file test
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("kern, str_to_check, reps, expected", [
    (Path(KERNELS/"mk"/"mro_2021_v02.tm"),"Marc Costa Sitja, NAIF/JPL", 1, True),
    (Path(KERNELS/"mk"/"mro_2021_v02.tm"), "mro_hga", 29, True),
    (Path(KERNELS / "mk" / "mro_2021_v02.tm"), "Unicorn", 1, False),
    (Path(KERNELS / "mk" / "mro_2021_v02.tm"), "Unicorn", 0, True),
])
def test_string_in_file(kern, str_to_check, reps, expected):
    """Test string_in_file function using pytest."""
    assert files.string_in_file(str(kern), str_to_check, reps) == expected

# ----------------------------------------------------------------------------
# files.type_to_extension test
# ----------------------------------------------------------------------------

@pytest.mark.parametrize( "inputs, outputs", [
    ("IK", ['ti']),
    ("ik", ['ti']),
    ("FK", ['tf']),
    ("MK", ['tm']),
    ("SCLK", ['tsc']),
    ("LSK", ['tls']),
    ("PCK", ['tpc', 'bpc']),
    ("CK", ['bc']),
    ("SPK", ['bsp']),
    ("DSK", ['bds']),
    ("EK", ['bes','bpe', 'bep', 'bdb', 'ten', 'tep']),
    ("ORB", ['nrb', 'orb']),
])
def test_type_to_extension(inputs, outputs):
    """Test type_to_extension function using pytest."""
    assert files.type_to_extension(inputs) == outputs

# ----------------------------------------------------------------------------
# files.extension_to_type test
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("kern, expected", [
    ("fakey_fake.bc", "ck"),
    ("DEIMOS_K005_THO_V01.BDS", "dsk"),
    ("m01_ext3.nrb", "orb"),
    ("lroevnt_2009271_2009278_v01.bes", "ek"),
    ("11A.bdb", "ek"),
    ("eros_n2000129x_v01.bpe", "ek"),
    ("S99_CIMSSSUPa.bep", "ek"),
    ("m01_mmdmt_ext10.ten", "ek"),
    ("fakey.tep", "ek"),
    ("m2020_chronos_v01.tm", "mk"),
])
def test_type_to_extension_object(kern, expected):
    """Test type_to_extension function using pytest where the input is an object."""
    mock_kernel = MagicMock()
    mock_kernel.extension = kern.split('.')[-1]

    assert files.extension_to_type(mock_kernel) == expected

# ----------------------------------------------------------------------------
# files.type_to_pds3_type test
# ----------------------------------------------------------------------------

#TODO Currently no pds3 labels are made for either MKs or ORBNUMs - might
# need this logic for migration?? Put MK and ORBNUMs in as placeholders...
@pytest.mark.parametrize( "inputs, outputs", [
    ("IK", "INSTRUMENT"),
    ("ik", "INSTRUMENT"),
    ("FK", "FRAMES"),
    ("fk", "FRAMES"),
    ("SCLK",  "CLOCK_COEFFICIENTS"),
    ("sclk", "CLOCK_COEFFICIENTS"),
    ("LSK", "LEAPSECONDS"),
    ("lsk", "LEAPSECONDS"),
    ("PCK",  "TARGET_CONSTANTS"),
    ("pck", "TARGET_CONSTANTS"),
    ("CK",  "POINTING"),
    ("ck", "POINTING"),
    ("SPK",  "EPHEMERIS"),
    ("spk", "EPHEMERIS"),
    ("DSK",  "SHAPE"),
    ("dsk", "SHAPE"),
    ("EK", "EVENTS"),
    ("ek", "EVENTS"),
    ("MK", "METAKERNEL"), #no pds3 labels for MK or ORBNUMS
    ("mk", "METAKERNEL"), #no pds3 labels for MK or ORBNUMS
    ("ORB", "ORBIT NUMBER"), #no pds3 labels for MK or ORBNUMS
    ("orb", "ORBIT NUMBER"), #no pds3 labels for MK or ORBNUMS
])
def test_type_to_pds3_type(inputs, outputs):
    """Test type_to_pds3 function using pytest."""
    assert files.type_to_pds3_type(inputs) == outputs

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
    """Test `utf8len` function with pytest."""
    assert files.utf8len(str(strn)) == int(length)
