"""Unit tests for kernel integrity.

Kernel integrity tests verify if the kernel type and architecture
is as expected from the kernel header.
"""
import unittest

from pds.naif_pds4_bundler.classes.object import Object
from pds.naif_pds4_bundler.classes.product import SpiceKernelProduct


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

    test_kernel = Object()
    test_kernel.name = "test.tf"
    test_kernel.type = "FK"
    test_kernel.file_format = "Character"
    test_kernel.setup = False

    #
    # Test sub-case 1: Correct text kernel architecture.
    #
    with open(kernel_path, "w") as k:
        k.write("KPL/FK\n")
    SpiceKernelProduct.check_kernel_integrity(test_kernel, test_kernel, kernel_path)

    #
    # Test sub-case 2: Non-existing kernel architecture.
    #
    with open(kernel_path, "w") as k:
        k.write("KPLO/FK\n")
    with self.assertRaises(RuntimeError):
        SpiceKernelProduct.check_kernel_integrity(
            test_kernel, test_kernel, kernel_path
        )

    #
    # Test sub-case 3: Incorrect text kernel architecture.
    #
    with open(kernel_path, "w") as k:
        k.write("DAF/FK\n")
    with self.assertRaises(RuntimeError):
        SpiceKernelProduct.check_kernel_integrity(
            test_kernel, test_kernel, kernel_path
        )

    #
    # Test sub-case 4: Mismatch text kernel type.
    #
    test_kernel.type = "IK"
    with open(kernel_path, "w") as k:
        k.write("KPL/FK\n")
    with self.assertRaises(RuntimeError):
        SpiceKernelProduct.check_kernel_integrity(
            test_kernel, test_kernel, kernel_path
        )

    #
    # Test sub-case 5: Non-existing text kernel type.
    #
    with open(kernel_path, "w") as k:
        k.write("KPL/SLC\n")
    with self.assertRaises(RuntimeError):
        SpiceKernelProduct.check_kernel_integrity(
            test_kernel, test_kernel, kernel_path
        )

def test_binary_kernel_integrity(self):
    """Test binary kernel integrity.

    The following tests are performed:
       * Correct binary kernel architecture
       * Incorrect kernel type
       * Incorrect architecture
    """
    kernel_path = "../data/kernels/ck/insight_ida_enc_200829_201220_v1.bc"

    test_kernel = Object()
    test_kernel.name = "insight_ida_enc_200829_201220_v1.bc"
    test_kernel.type = "CK"
    test_kernel.file_format = "Binary"
    test_kernel.setup = False

    #
    # Test sub-case 1: Correct binary kernel architecture.
    #
    SpiceKernelProduct.check_kernel_integrity(test_kernel, test_kernel, kernel_path)

    test_kernel.type = "SPK"

    #
    # Test sub-case 2: Incorrect kernel type.
    #
    with self.assertRaises(RuntimeError):
        SpiceKernelProduct.check_kernel_integrity(
            test_kernel, test_kernel, kernel_path
        )

    test_kernel.type = "CK"
    kernel_path = "../data/kernels/ck/insight_ida_enc_200829_201220_v1.xc"

    #
    # Test sub-case 3: Incorrect architecture.
    #
    with self.assertRaises(RuntimeError):
        SpiceKernelProduct.check_kernel_integrity(
            test_kernel, test_kernel, kernel_path
        )
