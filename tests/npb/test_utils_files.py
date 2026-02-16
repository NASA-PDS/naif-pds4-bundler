"""Unit tests for the pds.naif_pds4_bundler.utils.files module."""
from pathlib import Path
import shutil

import pytest

from pds.naif_pds4_bundler.utils import files


# Get the directory where the data is located.
KERNELS = Path(__file__).parent.parent / "naif_pds4_bundler" / "data" / "kernels"


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
# files.mk_to_list tests
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("mk", [
    KERNELS / "mk" / "vco_v01.tm",
    KERNELS / "mk" / "msl_v29.tm",
])
def test_mk_to_list(mk):
    assert files.mk_to_list(str(mk), False)
