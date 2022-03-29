"""Test family for comment extraction."""
from pds.naif_pds4_bundler.utils import extract_comment


def test_ck(self):
    """Test comment extraction from kernel."""
    comment = extract_comment(
        "../data/kernels/ck/insight_ida_enc_200829_201220_v1.bc"
    )
    comment_line = " This CK file was created using CKSLICER Utility Ver. 1.3.0, October 28, 2011"

    assert comment_line == comment[3]
