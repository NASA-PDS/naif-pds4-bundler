"""Unit tests for the pds.naif_pds4_bundler.utils.files module."""
import io
import logging
from dataclasses import dataclass
from pathlib import Path
import shutil

import pytest
import xml.etree.ElementTree as tree

from unittest.mock import call, MagicMock, patch

import os

from pds.naif_pds4_bundler.utils import files

# Get the directory where the data is located.
KERNELS = Path(__file__).parent.parent / "naif_pds4_bundler" / "data" / "kernels"
DOCS = Path(__file__).parent.parent / "naif_pds4_bundler" / "data"

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

def test_add_carriage_return_logging_error(monkeypatch, caplog):
    """Test add_carriage_return function using pytest.
    This is to test logging errors"""

    def mock_handle_error(msg, setup):
        if not setup:
            logging.error(msg)

    monkeypatch.setattr(files, "handle_npb_error", mock_handle_error)
    wrong_cr = "Mew "

    # Capture and check the logging level and logging messages.
    with caplog.at_level(files.logging.ERROR):
        files.add_carriage_return(wrong_cr, eol="", setup=False)

    expected = [(logging.ERROR, 'File has incorrect CR at line: Mew .')]

    results = [(r[1], r[2]) for r in caplog.record_tuples]

    assert results == expected

#Only covers \n part not \r\n .... not sure how to make this cover both

# ----------------------------------------------------------------------------
# files.add_crs_to_file tests
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("inputs, outputs", [
    ( "Chatty\nkitty\n", "Chatty<CR>\nkitty<CR>\n"),
    ("Kitty\n", "Kitty<CR>\n"),
    ("Meow \n", "Meow<CR>\n"),
    ("\n", "<CR>\n"),
    ("", ""),
])
def test_add_crs_to_file_success(monkeypatch, tmp_path, inputs, outputs):
    """Test add_crs_to_file function using pytest.
    This is for a successful case"""
    fake_file = tmp_path / "file.txt"
    fake_file.write_text(inputs)

    def mock_add_cr(line, eol, setup):
        return line.strip() + "<CR>\n"

    monkeypatch.setattr(files, "add_carriage_return", mock_add_cr)

    files.add_crs_to_file(str(fake_file), eol="\n", setup=False)

    expected = outputs
    assert fake_file.read_text() == expected

def test_add_crs_to_file_logging_error(monkeypatch, caplog):
    """Test add_crs_to_file function using pytest.
    This is to test logging errors"""

    def mock_handle_error(msg, setup):
        files.logging.getLogger("files").error(msg)

    monkeypatch.setattr(files, "handle_npb_error", mock_handle_error)
    bad_path = "/bad/path/file.txt"

    with caplog.at_level(files.logging.ERROR):
        files.add_crs_to_file(bad_path, eol="\n")

    assert f"Carriage return adding error for {bad_path}" in caplog.text

# ----------------------------------------------------------------------------
# files.check_badchar tests
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("contents, expected", [
    ("the OSIRIS-REx spacecraft",[]),
    ("where\nVersion",[]),
    ("Mission © Bennu",["NON-ASCII character(s) in line 1:","Mission © Bennu","        ^      "]),
    ("INS-155101_FOV_REF_ANGLE”=",["NON-ASCII character(s) in line 1:","INS-155101_FOV_REF_ANGLE”=","                        ^ "]),
    ("π = 3.14 & Σ = sum",["NON-ASCII character(s) in line 1:","π = 3.14 & Σ = sum","^          ^      "]),
    ("Line 1: Mission\nLine 2: Ma”rs\nLine 3: and bye”nd",["NON-ASCII character(s) in line 2:","Line 2: Ma”rs","          ^  ","NON-ASCII character(s) in line 3:","Line 3: and bye”nd","               ^  "]),
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
    # TODO: Add tests for EKs (.bdb and .bes - .bep/.bpe too?)
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
# files.check_eol tests
# ----------------------------------------------------------------------------

@pytest.mark.parametrize( "kern, eol, expected", [
    (Path(KERNELS/"mk"/"m2020_v09.tm"), "\n", ''),
    (Path(KERNELS/"mk"/"m2020_v09.tm"), "\r\n", "Incorrect EOL in file, CRLF (\\r\\n) expected."),
    (Path(KERNELS/"spk"/"maven_orb_rec_210101_210401_v2.bsp"), "\n", "Incorrect EOL in file, LF (\\n) expected."),
    (Path(KERNELS/"spk"/"maven_orb_rec_210101_210401_v2.bsp"), "\r\n", "Incorrect EOL in file, CRLF (\\r\\n) expected."),
    (Path(KERNELS/"dsk"/"DEIMOS_K005_THO_V01.BDS"), "\r\n", "Incorrect EOL in file, CRLF (\\r\\n) expected."),
    (Path(KERNELS / "dsk" / "DEIMOS_K005_THO_V01.BDS"), "\n", "Incorrect EOL in file, LF (\\n) expected."),
])
def test_check_eol(kern, eol, expected):
    """Test check_eol function using pytest."""
    result = files.check_eol(kern, eol)
    assert result == expected

def test_check_eol_error(monkeypatch, tmp_path, caplog):
    """Test check_eol function using pytest.
    This is to test logging errors"""

    def mock_handle_error(msg, setup=False):
        files.logging.getLogger("files").error(msg)

    monkeypatch.setattr(files, "handle_npb_error", mock_handle_error)

    fake_file = tmp_path / "file.txt"
    fake_file.write_text("Hi \a")
    eol = "\a"

    with caplog.at_level(files.logging.ERROR):
        files.check_eol(fake_file, eol)

    assert f"Incorrect EOL in configuration: {eol}" in caplog.text

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

@pytest.mark.parametrize( "path, rtype", [
    (Path(KERNELS/'ck'/'insight_ida_enc_200829_201220_v1.bc'), None),
    (Path(KERNELS/'dsk'/'DEIMOS_K005_THO_V01.BDS'), None),
])
def test_check_permissions(path, rtype):
    """Test check_permissions function using pytest."""
    assert files.check_permissions(str(path)) == rtype

def test_check_permissions_error(monkeypatch, tmp_path, caplog):
    """Test check_permissions function using pytest.
    This is to test logging errors"""
    def mock_handle_error(msg):
        logging.error(msg)

    def raise_permission_error(*args, **kwargs):
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

@pytest.mark.parametrize("prod_path, expected",[
    (Path(KERNELS/"ck"/"insight_ida_enc_200829_201220_v1.xml"), "22f9acc1931c8a626fac2a844fc5cee3"),
    (Path(KERNELS/"ck"/"insight_ida_pot_200829_201220_v1.xml"), "ccffc3675be188196359680bcd08c1ca"),
    (Path(KERNELS/"mk"/"none.xml"), ""),
])
def test_checksum_from_label(prod_path, expected):
    """Test checksum_from_label function using pytest."""
    result = files.checksum_from_label(str(prod_path))
    assert result == expected

# ----------------------------------------------------------------------------
# files.checksum_from_registry test
# ----------------------------------------------------------------------------

#attempt with real kernels --
# def test_checksum_from_registry():
#     """Test checksum_from_registry function."""
#     chcksm = DOCS/"ladee_release_01.checksum"
#     kern = KERNELS/"mk"/"ladee_v01.tm"
#
#     result = files.checksum_from_registry(str(chcksm), str(kern))
#     assert result == ''

@pytest.mark.parametrize("prod_path, chcksm, expected", [
    ("ladee_v10.tm", {"1.checksum": "path/ladee_v10.tm   abcdefg10987654321"}, "abcdefg10987654321"),
    ("mars2020_v04.bc", {"1.checksum": "not_the_right.bc  wrong", "2.checksum": "path/mars2020_v04.bc  looksright6789"}, "looksright6789"),
    ("missing.tf", {"1.checksum": "other.tf  nothere12345"},"" ),
    ("any.bsp", {},""),
])
def test_checksum_from_registry(tmp_path, prod_path, chcksm, expected, caplog):
    """Test checksum_from_registry function using pytest"""
    for filename, content in chcksm.items():
        file_path = tmp_path / filename
        file_path.write_text(content)

    with caplog.at_level(files.logging.WARNING):
        result = files.checksum_from_registry(prod_path, str(tmp_path))

    assert result == expected

    if expected:
        assert "-- Checksum obtained from Checksum Registry file" in caplog.text
    else:
        assert "-- Checksum obtained from Checksum Registry file" not in caplog.text

# ----------------------------------------------------------------------------
# files.compare_files test
# ----------------------------------------------------------------------------

# Uses real files - doesn't account for everything - is technically redundant
@pytest.mark.parametrize( "fromfile, tofile, expected",  [
    (Path(KERNELS/'ik'/"clps_to_2ab_pll_v01.ti"), Path(KERNELS/'ik'/"clps_to_2im_ncll_v01.ti"), True),
    (Path(KERNELS/'mk'/"m2020_v08.tm"), Path(KERNELS/'mk'/"m2020_v09.tm"), True),
    (Path(KERNELS/'fk'/"licia_002.tf"), Path(KERNELS/'fk'/"licia_002a.tf"), False),
    (Path(DOCS/"spiceds_em16.html"), Path(DOCS/"spiceds_mars2020.html"), True),
])
def test_compare_files(tmp_path, fromfile, tofile, expected):
    """Test compare_files function using pytest."""
    dest = str(tmp_path)

    result = files.compare_files(str(fromfile), str(tofile), dest, '')
    assert result == expected

@pytest.mark.parametrize("from_text, to_text, disp, expected, files_created",[
    ("Meow\n", "Meow\n", "log", False, 0),
    ("Meow\n", "Meow\n", "files", False, 0),
    ("Meow\n", "Meow\n", "all", False, 0),
    ("Unicorn\n", "Donkey\n", "log", True, 0),
    ("Unicorn\n", "Donkey\n", "files", True, 1),
    ("Donkey\n", "Shrek\n", "all", True, 1),
])
def test_compare_files_alt(tmp_path, from_text, to_text, disp, expected, files_created):
    """Test compare_files function using pytest. Mocks files/contents to test."""
    fromfile = tmp_path / "from.txt"
    tofile = tmp_path / "to.txt"
    dest = tmp_path / "diffs"
    dest.mkdir()

    fromfile.write_text(from_text)
    tofile.write_text(to_text)

    files.md5.side_effect = lambda x: "hash_a" if "line1" in Path(x).read_text() else "hash_b"

    with patch("logging.info") as mock_log:
        with patch("builtins.open", side_effect=open) as mock_builtin_open:
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

    def mock_copytree(*args):
        # Not such file or directory Error (errno 2)
        raise OSError(files.errno.ENOENT, "No such file or directory")

    monkeypatch.setattr(shutil, "copytree", mock_copytree)

    with caplog.at_level(files.logging.WARNING):
        files.copy(str(src), str(dest))

    assert caplog.messages == ["-- Directory file.txt not copied, probably because the increment directory exists.\nError: [Errno 2] No such file or directory"]

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
    eltree = tree.fromstring(xml)

    result = files.etree_to_dict(eltree)
    assert result == outputs

# ----------------------------------------------------------------------------
# files.extract_comment tests
# ----------------------------------------------------------------------------

def test_extract_comment_ck():
    """Test extract_comment function using pytest - comment extraction from kernel."""
    comment = files.extract_comment(str(KERNELS / "ck" / "insight_ida_enc_200829_201220_v1.bc"))
    comment_line = (
        " This CK file was created using CKSLICER Utility Ver. 1.3.0, October 28, 2011"
    )

    assert comment_line == comment[3]

# def test_extract_comment_remove_empty_lines(tmp_path):
#     """Test extract_comment function using pytest - remove empty lines."""
#
#     fake_file = tmp_path / "fake.bc"
#     fake_file.write_text(" This CK file was created using CKSLICER Utility Ver. 1.3.0, October 28, 2011 \n"
#                          "\n"
#                          "\n"
#                          "\n"
#                          "\n")
#     expected = " This CK file was created using CKSLICER Utility Ver. 1.3.0, October 28, 2011"
#
#     result = files.extract_comment(str(fake_file))
#
#     assert result == expected


# def test_extract_comment_error(monkeypatch, tmp_path, caplog):
#     """Test extract_comment function using pytest. This is to test logging errors"""
#     file_content = """
#     This CK file was created using CKSLICER Utility Ver. 1.3.0, October 28, 2011 This comment is going to be incredibly long and hit the error
#     """
#     file = tmp_path / "empty_kernels.bc"
#     file.write_text(file_content) #doesn't work cuz binary...
#
#     def mock_handle_error(msg, setup=False):
#         files.logging.getLogger("files").error(msg)
#
#     monkeypatch.setattr(files, "handle_npb_error", mock_handle_error)
#
#     with caplog.at_level(files.logging.ERROR):
#         files.extract_comment(str(file))
#
#     assert f"Comment from {file} is longer than buffer size." in caplog.text

#Not sure how to fix these to make them work...

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

#Another test case may need to be added to test when one variable is used to build out an entire section of the label
#Not sure best way to do this though..
# FOR EXAMPLE -
# $MISSION
# -->
# <Investigation_Area>
# <name>Lucy Mission</name>
# <type>Mission</type>
# <Internal_Reference>
# <lid_reference>urn:nasa:pds:context:investigation:mission.lucy</lid_reference>
# <reference_type>collection_to_investigation</reference_type>
# </Internal_Reference>
# </Investigation_Area>

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
    #default context products
    text = [{"name": ["MARS 2020"],
            "type": ["Mission"],
            "lidvid": "urn:nasa:pds:context:investigation:mission.mars2020::1.0"},
            {"name": ["Perseverance"],
             "type": ["Lander"],
             "lidvid": "urn:nasa:pds:context:instrument_host:spacecraft.mars2020::1.0"},
            {"name": ["MARS"],
             "type": ["PLANET"],
             "lidvid": "urn:nasa:pds:context:target:planet.mars::1.2"}]

    is_default_file = tmp_path / "default.json"
    is_default_file.write_text(str(text))

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

def test_get_context_products_overwrite_and_append_2(tmp_path):
    """Test get_context_products using pytest. Default products match products via setup.context_products."""
    # default context products
    text = [{"name": ["MARS 2020"],
            "type": ["Mission"],
            "lidvid": "urn:nasa:pds:context:investigation:mission.mars2020::1.0"},
            {"name": ["Perseverance"],
             "type": ["Rover"],
             "lidvid": "urn:nasa:pds:context:instrument_host:spacecraft.mars2020::1.0"},
            {"name": ["MARS"],
             "type": ["PLANET"],
             "lidvid": "urn:nasa:pds:context:target:planet.mars::1.2"}]

    is_default_file = tmp_path / "default.json"
    is_default_file.write_text(str(text))

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

# Could probably use a similar setup to test_get_context_products_no_optional_info_in_config_file
# for these two tests to make it less bulky ....

#default should probably be removed .... requires a json file to be updated and with the use
#of multi missions I messed up this capability ... I also do not want this capability

# ----------------------------------------------------------------------------
# files.get_latest_kernel test
# ----------------------------------------------------------------------------

def test_get_latest_kernel():
    """Test get_latest_kernel using pytest - basic."""
    pth = KERNELS/'ck'
    pttrn = "insight_ida_enc_[0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9]_v[0-9].bc"

    result = files.get_latest_kernel("ck", str(pth), pttrn)
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
    """Test get_latest_kernel using pytest. Test meta-kernel files."""
    pth = tmp_path / "mk"
    pth.mkdir()
    (pth / "kitty_v01.tm").write_text("")

    kern = pth / "kitty.tm"
    kern.write_text(" '$KERNELS/mk/cat_v01.tm' ")

    pttrn = "cat_v[0-9][0-9].tm"

    result = files.get_latest_kernel("mk", str(pth), pttrn, mks=[str(kern)])
    assert result ==  "cat_v01.tm"

def test_get_latest_kernel_excluded_kernels(tmp_path):
    """Test get_latest_kernel using pytest.
    Test that only the files you want to include are included."""
    pth = tmp_path / "spk"
    pth.mkdir()
    (pth / "include_v01.bsp").write_text("")
    (pth / "exclude_v01.bsp").write_text("")

    pths = [str(tmp_path)]
    pttrn = "include_v[0-9][0-9].bsp"

    result = files.get_latest_kernel(
        "spk", pths, pttrn, excluded_kernels=["exclude*"]
    )

    assert result == "include_v01.bsp"

# could probably make these less clunky and do a @pytest.mark.parametrize .... need to think about this more

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

    with pytest.raises(RuntimeError):
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

    with pytest.raises(RuntimeError):
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

    with pytest.raises(RuntimeError):
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
    """Test mk_to_list function using pytest."""
    assert files.mk_to_list(str(mk), False)

def test_mk_to_list_error(monkeypatch, tmp_path, caplog):
    """Test mk_to_list function using pytest. This is to test logging errors"""
    mk_content = """
    KPL/MK
    PATH_SYMBOLS = ( 'KERNELS' )
    \\KERNELS_TO_LOAD = (
        # This list is intentionally empty
    )
    """
    mk = tmp_path / "empty_kernels.tm"
    mk.write_text(mk_content)

    def mock_handle_error(msg, setup=False):
        files.logging.getLogger("files").error(msg)

    monkeypatch.setattr(files, "handle_npb_error", mock_handle_error)

    with caplog.at_level(files.logging.ERROR):
        files.mk_to_list(str(mk), setup=False)

    assert f"No kernels present in {mk}. " f"Please review MK generation." in caplog.text

# ----------------------------------------------------------------------------
# files.product_mapping test
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("miss_acr, rel, ker_list, text, expected", [
    ("VOYAGER", "5" , "VOYAGER_Release_05.kernel_list", "my_kernel\n  MAPPING = success", "success"),
    #("M2020", "1", "M2020_Release_01.kernel_list", "M2020_168_SCLKSCET.20260419.tsc\n  MAPPING = m2020_168_sclkscet_20260419.tsc", "m2020_168_sclkscet_20260419.tsc" ) #not sure how to make a real example work...
])
def test_product_mapping(tmp_path, miss_acr,  rel, ker_list, text, expected):
    """Test product_mapping function using pytest."""
    setup = MagicMock()
    setup.working_directory = str(tmp_path)
    setup.mission_acronym = miss_acr
    setup.run_type = "Release"
    setup.release = rel

    kernel_list_file = tmp_path / ker_list
    kernel_list_file.write_text(text)

    result = files.product_mapping("my_kernel", setup)

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

    def mock_error_handler(msg, setup=None):
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

    called = False

    def mock_error_handler(msg, setup=None):
        nonlocal called
        called = True

    monkeypatch.setattr(files,"handle_npb_error", mock_error_handler)

    result = files.product_mapping("NON_EXISTENT", setup, cleanup=False)

    assert result is False
    assert called is False

# ----------------------------------------------------------------------------
# files.replace_string_in_file test
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("contents, old_str, new_str, eol_pds3, expected", [
    ("Howdy Cowboy\n", "Cowboy", "Cowgirl", False, "Howdy Cowgirl\n"),
    ("Venus Saturn Mars Venus\n", "Venus", "Earth", False, "Earth Saturn Mars Earth\n"),
    ("Mission A\nMission B\n", "Mission", "Spacecraft", True, "Spacecraft A\nSpacecraft B\n"),
    ("Happy Kitty\n", "Kitty", "kitty", True, "Happy kitty\n"),
])
def test_replace_string_in_file(tmp_path, contents, old_str, new_str, eol_pds3, expected):
    """Test replace_string_in_file function using pytest."""
    fake_file = tmp_path / "fake_file.txt"
    fake_file.write_text(contents)

    mock_setup = MagicMock()
    mock_setup.eol_pds3 = eol_pds3

    try:
        files.replace_string_in_file(str(fake_file), old_str, new_str, mock_setup)

        final_content = fake_file.read_text()
        assert final_content == expected
    finally:
        if os.path.exists("tmp.file"):
            os.remove("tmp.file")

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

@pytest.mark.parametrize("kern, str_to_check, expected", [
    (Path(KERNELS/"mk"/"mro_2021_v02.tm"),"Marc Costa Sitja, NAIF/JPL", True),
    (Path(KERNELS/"mk"/"mro_2021_v02.tm"),"Unicorn", False),
])
def test_string_in_file(kern, str_to_check, expected):
    """Test string_in_file function using pytest."""
    assert files.string_in_file(str(kern), str_to_check) == expected

# ----------------------------------------------------------------------------
# files.type_to_extension test
# ----------------------------------------------------------------------------

#TODO EK extensions need to be added. Orbnums?
@pytest.mark.parametrize( "inputs, outputs", [
    ("IK", ['ti']),
    ("FK", ['tf']),
    ("MK", ['tm']),
    ("SCLK",  ['tsc']),
    ("LSK", ['tls']),
    ("PCK",  ['tpc', 'bpc']),
    ("CK",  ['bc']),
    ("SPK",  ['bsp']),
    ("DSK",  ['bds']),
])
def test_type_to_extension(inputs, outputs):
    """Test type_to_extension function using pytest."""
    assert files.type_to_extension(inputs) == outputs

# ----------------------------------------------------------------------------
# files.type_to_pds3_type test
# ----------------------------------------------------------------------------

#TODO EKs need to be added! Should MKs/Orbnums be added .. in extras??
@pytest.mark.parametrize( "inputs, outputs", [
    ("IK", "INSTRUMENT"),
    ("FK", "FRAMES"),
    ("SCLK",  "CLOCK_COEFFICIENTS"),
    ("LSK", "LEAPSECONDS"),
    ("PCK",  "TARGET_CONSTANTS"),
    ("CK",  "POINTING"),
    ("SPK",  "EPHEMERIS"),
    ("DSK",  "SHAPE"),
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
    """Test utf8len function with pytest."""
    assert files.utf8len(str(strn)) == int(length)
