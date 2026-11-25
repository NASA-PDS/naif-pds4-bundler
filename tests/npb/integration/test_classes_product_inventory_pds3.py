"""Integration tests for the InventoryPDS3Product class.

The Setup, the KernelList and the inventory product are real, and so are the
files they read and write in a sandbox. The kernels of the collection are
plain objects that carry only the attributes the index reads, because the
index does not need the kernel files themselves.
"""
import logging
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from pds.naif_pds4_bundler.classes.label.pds3_inventory import (
    InventoryPDS3Label)
from pds.naif_pds4_bundler.classes.list import KernelList
from pds.naif_pds4_bundler.classes.product.product_inventory_pds3 import (
    InventoryPDS3Product)

pytestmark = pytest.mark.integration

# Message logged instead of comparing the index with anything.
SKIP_MESSAGE = ('-- No previous-index comparison is available for PDS3, '
                'skipping the comparison of index.tab.')


def make_kernel(name: str) -> SimpleNamespace:
    """Provide the attributes of a binary kernel that the index reads."""
    return SimpleNamespace(
        name=name,
        type="spk",
        path=f"/archive/mrosp_1000/data/spk/{name}",
        start_time="2020-001T00:00:00Z",
        stop_time="2021-001T00:00:00Z",
        creation_time="2020-002T00:00:00",
    )


@pytest.fixture
def pds3_collection(make_setup, request):
    """Build a PDS3 Setup and a collection with two kernels.

    The diff scope of the run is taken from the test parameter.

    :param make_setup: function that builds a real Setup
    :param request: pytest request, whose parameter is the ``--diff`` value
    :return: collection whose ``list`` is a real KernelList
    """
    setup = make_setup("mro.xml", diff=request.param)

    # The index is written in a folder of the volume in the staging area.
    Path(setup.staging_directory, "index").mkdir(parents=True)

    return SimpleNamespace(
        name="spice_kernels",
        type="spice_kernels",
        setup=setup,
        list=KernelList(setup),
        product=[make_kernel("mro_psp1.bsp"), make_kernel("mro_psp2.bsp")],
    )


@pytest.mark.parametrize("pds3_collection", ["log", "files", "all"],
                         indirect=True)
class TestInventoryPDS3ProductDiff:
    """Tests for a PDS3 run that asks for diffs."""

    def test_index_is_generated_and_not_compared(
            self, pds3_collection, sandbox, caplog) -> None:
        """The index is written and nothing is compared with it.

        No sample inventory is read and no diff file is written in the
        working directory.
        """
        # Build the index of the collection, as the pipeline does
        with caplog.at_level(logging.INFO):
            inventory = InventoryPDS3Product(
                pds3_collection.setup, pds3_collection)

        # The index has one row per kernel. Blank lines are left out because
        # on Windows the file ends up with a doubled carriage return at the
        # end of each row, which reads back as an empty line in between.
        lines = Path(inventory.path).read_text(encoding="utf-8").splitlines()
        rows = [line for line in lines if line]
        assert len(rows) == 2
        assert inventory.path_current == ""

        # The comparison was skipped and left no trace on disk
        assert SKIP_MESSAGE in caplog.messages
        assert '-- Comparing with InSight test inventory product.' \
            not in caplog.messages
        assert list(sandbox.working.glob("diff_*")) == []

    def test_index_label_is_the_same_as_without_diff(
            self, pds3_collection, sandbox, caplog) -> None:
        """The index label does not depend on the diff option.

        The label is written with the diff scope of the run, which looks for
        a label to compare with, and then written again without it.
        """
        # Build and label the index, as the pipeline does
        with caplog.at_level(logging.INFO):
            inventory = InventoryPDS3Product(
                pds3_collection.setup, pds3_collection)
            InventoryPDS3Label(inventory).write_label()

        label = Path(inventory.path).with_suffix(".lbl")
        label_with_diff = label.read_bytes()

        # Label the same index again, this time without --diff
        label.unlink()
        setup = pds3_collection.setup
        setup.args = replace(setup.args, diff=None)
        InventoryPDS3Label(inventory).write_label()

        # The comparison was attempted, wrote no file and changed nothing
        assert "-- Comparing label..." in caplog.messages
        assert list(sandbox.working.glob("diff_*")) == []
        assert label.read_bytes() == label_with_diff
