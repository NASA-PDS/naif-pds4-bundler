"""Unit tests for kernel integrity.

Kernel integrity tests verify if the kernel type and architecture
is as expected from the kernel header.
"""

import shutil

# import unittest

from pds.naif_pds4_bundler.utils import check_kernel_integrity


def test_text_kernel_integrity(self):
    """Test text kernel integrity.

    The following tests are performed:
       * Correct text kernel architecture
       * Non-existing kernel architecture
       * Incorrect text kernel architecture
       * Mismatch text kernel type
       * Non-existing text kernel type
    """
    kernel_path = "working/test.tf"

    #
    # Test sub-case 1: Correct text kernel architecture.
    #
    with open(kernel_path, "w") as k:
        k.write("KPL/FK\n")
    error = check_kernel_integrity(kernel_path)
    if error:
        raise BaseException

    #
    # Test sub-case 2: Non-existing kernel architecture.
    #
    with open(kernel_path, "w") as k:
        k.write("KPLO/FK\n")
    error = check_kernel_integrity(kernel_path)
    if not error:
        raise BaseException

    #
    # Test sub-case 3: Incorrect text kernel architecture.
    #
    with open(kernel_path, "w") as k:
        k.write("DAF/FK\n")
    error = check_kernel_integrity(kernel_path)
    if not error:
        raise BaseException

    #
    # Test sub-case 4: Mismatch text kernel type.
    #
    with open("working/test.ti", "w") as k:
        k.write("KPL/FK\n")
    error = check_kernel_integrity(kernel_path)
    if not error:
        raise BaseException

    #
    # Test sub-case 5: Non-existing text kernel type.
    #
    with open(kernel_path, "w") as k:
        k.write("KPL/SLC\n")
    error = check_kernel_integrity(kernel_path)
    if not error:
        raise BaseException


def test_binary_kernel_integrity(self):
    """Test binary kernel integrity.

    The following tests are performed:
       * Correct binary kernel architecture
       * Incorrect kernel type
       * Incorrect architecture
    """
    kernel_path = "../data/kernels/ck/insight_ida_enc_200829_201220_v1.bc"

    #
    # Test sub-case 1: Correct binary kernel architecture.
    #
    error = check_kernel_integrity(kernel_path)
    if error:
        raise BaseException

    #
    # Test sub-case 2: Incorrect kernel type.
    #
    kernel_path_updated = "insight_ida_enc_200829_201220_v1.bsp"
    shutil.copy(kernel_path, kernel_path_updated)
    error = check_kernel_integrity(kernel_path_updated)
    if not error:
        raise BaseException

    #
    # Test sub-case 3: Incorrect file name.
    #
    kernel_path = "../data/kernels/ck/insight_ida_enc_200829_201220_v1.xc"
    with self.assertRaises(KeyError):
        check_kernel_integrity(kernel_path)

    #
    # Test sub-case 4: Incorrect architecture.
    #
    kernel_path = "../data/kernels/ck/insight_ida_enc_200829_201220_v1.xc"
    kernel_path_updated = "insight_ida_enc_200829_201220_v1.bc"
    shutil.copy(kernel_path, kernel_path_updated)
    error = check_kernel_integrity(kernel_path_updated)
    if not error:
        raise BaseException
