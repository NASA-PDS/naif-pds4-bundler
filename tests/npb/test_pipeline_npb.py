"""Tests for pds.naif_pds4_bundler.pipeline.npb.run_pipeline.

Strategy
--------
``run_pipeline`` is a pure orchestrator: it constructs objects, calls methods on
them, and branches on a handful of flags.  Every external collaborator is
therefore replaced by a ``MagicMock`` so that tests focus exclusively on the
orchestration logic — not on the internals of Setup, Bundle, etc.

All patches target the names as imported *inside* the ``npb`` module
(``pds.naif_pds4_bundler.pipeline.npb.<Name>``).

Phase → Test class mapping
--------------------------
  1  Initialization                      TestPhase1Initialization
  2  Clear mode                          TestPhase2ClearMode
  3  Release Plan                        TestPhase3ReleasePlan
  4  Kernel List                         TestPhase4KernelList
  5  Product checks                      TestPhase5ProductChecks
  6  Staging: Bundle + Collections       TestPhase6StagingBundleAndCollections
  7  Labels-only mode                    TestPhase7LabelsOnlyMode
  8  Collection metadata (PDS4)          TestPhase8CollectionMetadata
  9  PDS4 document + misc + checksum     TestPhase9PDS4DocumentMiscChecksum
 10  PDS3 path                           TestPhase10PDS3Path
 11  Staging recap + copy                TestPhase11StagingRecapAndCopy
 12  Final validation                    TestPhase12FinalValidation
 13  NPBError -> handle_npb_error routing TestNPBErrorHandling
"""
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from pds.naif_pds4_bundler.pipeline.npb import run_pipeline
from pds.naif_pds4_bundler.classes.exceptions import NPBError
from pds.naif_pds4_bundler.utils.types.datatypes import PipelineArgs

# Imported to create specified mocks that pass isinstance checks in Phase 12.
from pds.naif_pds4_bundler.classes.product.product_metakernel import MetaKernelProduct

class _StubChecksum:
    # Standalone test double for ChecksumProduct (lines 443-444 coverage).
    # No inheritance is needed: when the module-level name ``ChecksumProduct``
    # is patched to this class, the isinstance check in npb.py evaluates
    # against _StubChecksum directly, so any instance created via the patched
    # name passes automatically.
    def __init__(self, _setup=None, _collection=None, **_kw):
        self.new_product = True

    def set_coverage(self): pass  # no-op: test only observes new_product flag
    def generate(self, history=None): pass  # no-op: output generation not under test
    def read_current_product(self, **_kw): pass  # no-op: reading existing products not under test

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_MODULE = 'pds.naif_pds4_bundler.pipeline.npb'

_PATCH_TARGETS = [
    'Setup',
    'Log',
    'Bundle',
    'SpiceKernelsCollection',
    'MiscellaneousCollection',
    'KernelList',
    'ReleasePlan',
    'MetaKernelProduct',
    'SpiceKernelProduct',
    'OrbnumFileProduct',
    'InventoryProduct',
    'ChecksumProduct',
    'SpicedsProduct',
    'DocumentCollection',
    'ReadmeProduct',
    'clear_run',
    'finish_execution',
    'log_step',
    'isdir',
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _args(**overrides) -> PipelineArgs:
    """Build a minimal valid PipelineArgs, applying any overrides."""
    defaults = {
        'config': 'dummy.xml',
        'silent': True,
        'verbose': False,
        'debug': True,
        'log': False,
        'plan': None,
        'kerlist': None,
        'faucet': '',
        'clear': None,
        'checksum': False,
        'diff': None,
    }
    defaults.update(overrides)
    return PipelineArgs(**defaults)


def _configure_pds4_defaults(m: SimpleNamespace) -> None:
    """Set mock defaults that let a full PDS4 run complete without errors."""
    setup = m.Setup.return_value
    setup.faucet = ''
    setup.pds_version = '4'
    setup.increment = False
    setup.step = 1
    setup.mission_acronym = 'maven'
    setup.bundle_directory = '/fake/bundle'

    release_plan = m.ReleasePlan.return_value
    release_plan.kernel_list = []
    release_plan.write_plan.return_value = True

    k_list = m.KernelList.return_value
    k_list.kernel_list = []

    skc = m.SpiceKernelsCollection.return_value
    skc.updated = False
    skc.product = []
    skc.name = 'spice_kernels'
    skc.determine_meta_kernels.return_value = {}

    misc = m.MiscellaneousCollection.return_value
    misc.product = []
    misc.kind = 'miscellaneous'
    misc.name = 'miscellaneous'

    m.SpicedsProduct.return_value.generated = False

    bundle = m.Bundle.return_value
    bundle.history = {}

    m.isdir.return_value = True


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mocks():
    """Patch every external collaborator of run_pipeline.

    Yields a SimpleNamespace whose attributes are the patch mock objects,
    pre-configured for a complete PDS4 run with an empty kernel list.
    """
    with ExitStack() as stack:
        m = SimpleNamespace(**{
            name: stack.enter_context(patch(f'{_MODULE}.{name}'))
            for name in _PATCH_TARGETS
        })
        _configure_pds4_defaults(m)
        yield m


@pytest.fixture()
def mocks_no_mk():
    """Like ``mocks`` but leaves ``MetaKernelProduct`` unpatched.

    ``isinstance(x, MetaKernelProduct)`` in the final validation loop requires
    ``MetaKernelProduct`` to be the real class, not a MagicMock.  When the real
    class is in place, ``MagicMock(spec=MetaKernelProduct)`` instances pass
    the isinstance check via their ``__class__`` property.  With an empty
    kernel list the meta-kernel construction loop never runs, so the real
    constructor is never called.
    """
    targets = [t for t in _PATCH_TARGETS if t != 'MetaKernelProduct']
    with ExitStack() as stack:
        m = SimpleNamespace(**{
            name: stack.enter_context(patch(f'{_MODULE}.{name}'))
            for name in targets
        })
        # MetaKernelProduct attribute is the real class so tests can use it.
        m.MetaKernelProduct = MetaKernelProduct
        _configure_pds4_defaults(m)
        yield m


# ---------------------------------------------------------------------------
# Phase 1 – Initialization
# ---------------------------------------------------------------------------

class TestPhase1Initialization:
    # Phase 1 – Initialization
    # Setup is constructed from the raw PipelineArgs; it validates configuration,
    # locates the config file, and derives all path and metadata attributes used
    # throughout the pipeline. Log is constructed next and attached to `setup` so
    # that every subsequent phase can write to the same log stream. The pipeline
    # then calls setup.check_configuration() to assert the archive is self-onsistent,
    # and setup.set_release() to determine the current release number.

    def test_setup_constructed_with_args_and_version(self, mocks):
        # Setup receives the raw args object and the package version string.
        from pds.naif_pds4_bundler import __version__
        args = _args()
        run_pipeline(args)
        mocks.Setup.assert_called_once_with(args, __version__)

    def test_log_constructed_with_setup_instance_and_args(self, mocks):
        # Log receives the Setup instance (not the class) and the raw args.
        args = _args()
        run_pipeline(args)
        setup_instance = mocks.Setup.return_value
        mocks.Log.assert_called_once_with(setup_instance, args)

    def test_log_start_called(self, mocks):
        # Logging begins immediately after the Log object is created.
        run_pipeline(_args())
        mocks.Log.return_value.start.assert_called_once()

    def test_log_is_assigned_to_setup(self, mocks):
        # The log is back-referenced on setup so interrupted runs can still emit the file list.
        run_pipeline(_args())
        setup = mocks.Setup.return_value
        log = mocks.Log.return_value
        assert setup.log is log

    def test_check_configuration_called(self, mocks):
        # The configuration is validated before any work starts.
        run_pipeline(_args())
        mocks.Setup.return_value.check_configuration.assert_called_once()

    def test_set_release_called(self, mocks):
        # The archive version is resolved before the release plan is built.
        run_pipeline(_args())
        mocks.Setup.return_value.set_release.assert_called_once()


# ---------------------------------------------------------------------------
# Phase 2 – Clear mode
# ---------------------------------------------------------------------------

class TestPhase2ClearMode:
    # Phase 2 – Clear mode
    # If PipelineArgs.clear is set, the pipeline calls clear_run(setup) to wipe
    # any previous staging output before the current run begins. This is
    # independent of the faucet: clear_run fires even when faucet='clear', so
    # cleanup always precedes the exit check. The 'clear' faucet then calls
    # finish_execution and returns immediately, making clear-only runs a two-step
    # sequence of cleanup → graceful shutdown.

    def test_clear_run_called_when_args_clear_is_set(self, mocks):
        # When args.clear names a file list, clear_run is delegated to runtime.
        args = _args(clear='/some/path.file_list', faucet='checks')
        run_pipeline(args)
        mocks.clear_run.assert_called_once_with(mocks.Setup.return_value)

    def test_clear_run_not_called_when_args_clear_is_none(self, mocks):
        # Without a clear argument the cleanup step is skipped entirely.
        run_pipeline(_args())
        mocks.clear_run.assert_not_called()

    def test_finish_execution_called_when_faucet_is_clear(self, mocks):
        # faucet='clear' stops the pipeline with a clean shutdown.
        mocks.Setup.return_value.faucet = 'clear'
        run_pipeline(_args())
        mocks.finish_execution.assert_called_once_with(
            mocks.Setup.return_value, mocks.Log.return_value
        )

    def test_pipeline_stops_after_clear_faucet(self, mocks):
        # No further steps run once the clear faucet fires.
        mocks.Setup.return_value.faucet = 'clear'
        run_pipeline(_args())
        mocks.ReleasePlan.assert_not_called()

    def test_clear_run_and_faucet_exit_are_independent(self, mocks):
        # args.clear triggers cleanup regardless of which faucet stops the pipeline later.
        mocks.Setup.return_value.faucet = 'checks'
        args = _args(clear='/some/path.file_list', faucet='checks')
        run_pipeline(args)
        mocks.clear_run.assert_called_once()
        # execution continues past the 'clear' faucet gate
        mocks.ReleasePlan.assert_called_once()


# ---------------------------------------------------------------------------
# Phase 3 – Release Plan
# ---------------------------------------------------------------------------

class TestPhase3ReleasePlan:
    # Phase 3 – Release plan
    # ReleasePlan is constructed with setup and immediately asked to compute the
    # set of kernels that belong to this release. When PipelineArgs.kerlist is
    # absent the pipeline calls release_plan.write_plan() to derive and persist
    # the plan from scratch; when kerlist is provided it calls
    # release_plan.read_plan(kerlist) to load a pre-computed plan instead.
    # The 'plan' faucet causes an early finish_execution and return after this
    # step, allowing the pipeline to be stopped after plan generation for review.

    def test_release_plan_constructed_with_setup(self, mocks):
        # ReleasePlan is always created with the shared setup object.
        run_pipeline(_args())
        mocks.ReleasePlan.assert_called_once_with(mocks.Setup.return_value)

    def test_write_plan_called_when_no_kerlist_and_no_plan_file(self, mocks):
        # With no plan or kerlist input, a plan is generated from the kernels' directory.
        run_pipeline(_args(plan=None, kerlist=None))
        mocks.ReleasePlan.return_value.write_plan.assert_called_once()

    def test_read_plan_called_when_plan_file_provided(self, mocks):
        # A .plan path in args is read rather than generated.
        plan_path = 'mission_release_01.plan'
        run_pipeline(_args(plan=plan_path))
        mocks.ReleasePlan.return_value.read_plan.assert_called_once_with(
            Path(plan_path)
        )

    def test_write_plan_not_called_when_plan_file_provided(self, mocks):
        # A .plan path suppresses auto-generation.
        run_pipeline(_args(plan='mission_release_01.plan'))
        mocks.ReleasePlan.return_value.write_plan.assert_not_called()

    def test_write_plan_not_called_when_kerlist_provided(self, mocks):
        # A kerlist bypasses the release plan step entirely.
        run_pipeline(_args(kerlist='mission_release_01.kernel_list'))
        mocks.ReleasePlan.return_value.write_plan.assert_not_called()

    def test_early_return_when_labels_faucet_and_write_plan_returns_falsy(self, mocks):
        # In labels mode with no products found, the pipeline returns before building a kernel list.
        mocks.ReleasePlan.return_value.write_plan.return_value = False
        run_pipeline(_args(faucet='labels'))
        # No KernelList should be constructed if we returned early
        mocks.KernelList.assert_not_called()

    def test_finish_execution_called_when_faucet_is_plan(self, mocks):
        # faucet='plan' stops the pipeline with a clean shutdown after the plan step.
        mocks.Setup.return_value.faucet = 'plan'
        run_pipeline(_args())
        mocks.finish_execution.assert_called_once_with(
            mocks.Setup.return_value, mocks.Log.return_value
        )

    def test_pipeline_stops_after_plan_faucet(self, mocks):
        # No further steps run once the plan faucet fires.
        mocks.Setup.return_value.faucet = 'plan'
        run_pipeline(_args())
        mocks.KernelList.assert_not_called()


# ---------------------------------------------------------------------------
# Phase 4 – Kernel List
# ---------------------------------------------------------------------------

class TestPhase4KernelList:
    # Phase 4 – Kernel list
    # KernelList is constructed with setup, then its kernel_list attribute is
    # populated from release_plan.kernel_list (the pipeline assigns the reference
    # directly, so anything set on the KernelList mock before this point is
    # overwritten). When PipelineArgs.kerlist is absent the pipeline calls
    # k_list.write_list(); when kerlist is provided it calls k_list.read_list().
    # The 'list' faucet triggers finish_execution and an early return, enabling
    # the pipeline to stop after the kernel list is produced for inspection.

    def test_kernel_list_constructed_with_setup(self, mocks):
        # KernelList is always created with the shared setup object.
        run_pipeline(_args())
        mocks.KernelList.assert_called_once_with(mocks.Setup.return_value)

    def test_kernel_list_loaded_from_release_plan(self, mocks):
        # The kernel list is taken directly from the release plan output.
        sentinel = ['maven_2024.bc']
        mocks.ReleasePlan.return_value.kernel_list = sentinel
        run_pipeline(_args())
        assert mocks.KernelList.return_value.kernel_list is sentinel

    def test_write_list_called_when_no_kerlist(self, mocks):
        # Without a kerlist argument, the list is written from the release plan.
        run_pipeline(_args(kerlist=None))
        mocks.KernelList.return_value.write_list.assert_called_once()

    def test_read_list_called_when_kerlist_provided(self, mocks):
        # A kerlist path is read rather than generated.
        kerlist_path = 'mission_release_01.kernel_list'
        run_pipeline(_args(kerlist=kerlist_path))
        mocks.KernelList.return_value.read_list.assert_called_once_with(kerlist_path)

    def test_write_list_not_called_when_kerlist_provided(self, mocks):
        # A kerlist suppresses the write step.
        run_pipeline(_args(kerlist='mission_release_01.kernel_list'))
        mocks.KernelList.return_value.write_list.assert_not_called()

    def test_finish_execution_called_when_faucet_is_list(self, mocks):
        # faucet='list' stops the pipeline with a clean shutdown after the list step.
        mocks.Setup.return_value.faucet = 'list'
        run_pipeline(_args())
        mocks.finish_execution.assert_called_once_with(
            mocks.Setup.return_value, mocks.Log.return_value
        )

    def test_pipeline_stops_after_list_faucet(self, mocks):
        # No further steps run once the list faucet fires.
        mocks.Setup.return_value.faucet = 'list'
        run_pipeline(_args())
        mocks.Bundle.assert_not_called()


# ---------------------------------------------------------------------------
# Phase 5 – Product checks
# ---------------------------------------------------------------------------

class TestPhase5ProductChecks:
    # Phase 5 – Product checks
    # k_list.check_products() is called to validate that every kernel referenced
    # in the kernel list is physically present on disk and passes format checks.
    # This is the last gate before any archive products are written, so a failure
    # here aborts the run before any staging output is produced. The 'checks'
    # faucet stops the pipeline cleanly after this validation, allowing the check
    # to be run without generating any output products.

    def test_check_products_called(self, mocks):
        # All products in the kernel list are validated before staging begins.
        run_pipeline(_args())
        mocks.KernelList.return_value.check_products.assert_called_once()

    def test_finish_execution_called_when_faucet_is_checks(self, mocks):
        # faucet='checks' stops the pipeline with a clean shutdown after product validation.
        mocks.Setup.return_value.faucet = 'checks'
        run_pipeline(_args())
        mocks.finish_execution.assert_called_once_with(
            mocks.Setup.return_value, mocks.Log.return_value
        )

    def test_pipeline_stops_after_checks_faucet(self, mocks):
        # No further steps run once the checks faucet fires.
        mocks.Setup.return_value.faucet = 'checks'
        run_pipeline(_args())
        mocks.Bundle.assert_not_called()


# ---------------------------------------------------------------------------
# Phase 6 – Staging: Bundle + Collections
# ---------------------------------------------------------------------------

class TestPhase6StagingBundleAndCollections:
    # Phase 6 – Staging, bundle, and collection initialization
    # Bundle is constructed with setup, then load_kernels() furnishes the SPICE
    # toolkit with the archive's kernels. SpiceKernelsCollection and
    # MiscellaneousCollection are both constructed with setup and the bundle.
    # The pipeline then iterates over k_list.kernel_list and dispatches each
    # entry to the correct product class: .bc/.bsp extensions → SpiceKernelProduct,
    # .orb/.nrb extensions → OrbnumFileProduct, .tm (meta-kernel) entries are
    # skipped here because they are handled separately. After the loop,
    # release_plan.determine_meta_kernels() is called and each resulting MK is
    # wrapped in a MetaKernelProduct, which is added to SpiceKernelsCollection
    # for PDS4 or to MiscellaneousCollection for PDS3.

    def test_bundle_constructed_with_setup(self, mocks):
        # Bundle is always created with the shared setup object.
        run_pipeline(_args())
        mocks.Bundle.assert_called_once_with(mocks.Setup.return_value)

    def test_load_kernels_called(self, mocks):
        # LSK, PCK, FK and SCLK kernels are loaded before any product is processed.
        run_pipeline(_args())
        mocks.Setup.return_value.load_kernels.assert_called_once()

    def test_spice_kernels_collection_constructed(self, mocks):
        # SpiceKernelsCollection receives setup, bundle, and the kernel list.
        run_pipeline(_args())
        setup = mocks.Setup.return_value
        bundle = mocks.Bundle.return_value
        k_list = mocks.KernelList.return_value
        mocks.SpiceKernelsCollection.assert_called_once_with(setup, bundle, k_list)

    def test_miscellaneous_collection_constructed(self, mocks):
        # MiscellaneousCollection receives setup, bundle, and the kernel list.
        run_pipeline(_args())
        setup = mocks.Setup.return_value
        bundle = mocks.Bundle.return_value
        k_list = mocks.KernelList.return_value
        mocks.MiscellaneousCollection.assert_called_once_with(setup, bundle, k_list)

    def test_spice_kernel_product_dispatched_for_bc_kernel(self, mocks):
        # .bc files are dispatched to SpiceKernelProduct and added to the SPICE collection.
        # The pipeline assigns k_list.kernel_list = release_plan.kernel_list,
        # so the kernel list must be set on the ReleasePlan mock.
        mocks.ReleasePlan.return_value.kernel_list = ['maven_2024.bc']
        run_pipeline(_args())
        mocks.SpiceKernelProduct.assert_called_once()
        mocks.SpiceKernelsCollection.return_value.add.assert_called()

    def test_spice_kernel_product_dispatched_for_bsp_kernel(self, mocks):
        # .bsp files are dispatched to SpiceKernelProduct.
        mocks.ReleasePlan.return_value.kernel_list = ['maven_2024.bsp']
        run_pipeline(_args())
        mocks.SpiceKernelProduct.assert_called_once()

    def test_orbnum_product_dispatched_for_nrb_kernel(self, mocks):
        # .nrb files are dispatched to OrbnumFileProduct and added to the miscellaneous collection.
        mocks.ReleasePlan.return_value.kernel_list = ['maven_2024.nrb']
        run_pipeline(_args())
        mocks.OrbnumFileProduct.assert_called_once()
        mocks.MiscellaneousCollection.return_value.add.assert_called()

    def test_orbnum_product_dispatched_for_orb_kernel(self, mocks):
        # .orb files are dispatched to OrbnumFileProduct.
        mocks.ReleasePlan.return_value.kernel_list = ['maven_2024.orb']
        run_pipeline(_args())
        mocks.OrbnumFileProduct.assert_called_once()

    def test_tm_kernel_skipped_in_product_dispatch_loop(self, mocks):
        # .tm files are skipped; meta-kernels are handled in a later dedicated step.
        mocks.ReleasePlan.return_value.kernel_list = ['maven_2024.tm']
        run_pipeline(_args())
        mocks.SpiceKernelProduct.assert_not_called()
        mocks.OrbnumFileProduct.assert_not_called()

    def test_multiple_kernels_produce_multiple_products(self, mocks):
        # Each non-meta kernel in the list produces exactly one product of the correct type.
        mocks.ReleasePlan.return_value.kernel_list = [
            'maven_2024.bc', 'maven_2024.bsp', 'maven_2024.nrb'
        ]
        run_pipeline(_args())
        assert mocks.SpiceKernelProduct.call_count == 2
        assert mocks.OrbnumFileProduct.call_count == 1

    def test_determine_meta_kernels_called(self, mocks):
        # Meta-kernels are identified from the SPICE kernels collection after the loop.
        run_pipeline(_args())
        mocks.SpiceKernelsCollection.return_value.determine_meta_kernels.assert_called_once()

    def test_meta_kernel_product_added_to_skc_for_pds4(self, mocks):
        # In PDS4 mode, a determined meta-kernel is added to the SPICE kernels collection.
        mocks.SpiceKernelsCollection.return_value.determine_meta_kernels.return_value = {
            'maven_v01.tm': None
        }
        mocks.Setup.return_value.pds_version = '4'
        run_pipeline(_args())
        mocks.MetaKernelProduct.assert_called_once()
        mocks.SpiceKernelsCollection.return_value.add.assert_called()

    def test_meta_kernel_product_added_to_misc_for_pds3(self, mocks):
        # In PDS3 mode, a determined meta-kernel is added to the miscellaneous collection.
        mocks.SpiceKernelsCollection.return_value.determine_meta_kernels.return_value = {
            'maven_v01.tm': None
        }
        mocks.Setup.return_value.pds_version = '3'
        run_pipeline(_args())
        mocks.MetaKernelProduct.assert_called_once()
        mocks.MiscellaneousCollection.return_value.add.assert_called()

    def test_no_meta_kernel_product_when_none_determined(self, mocks):
        # When determine_meta_kernels returns empty, no MetaKernelProduct is constructed.
        mocks.SpiceKernelsCollection.return_value.determine_meta_kernels.return_value = {}
        run_pipeline(_args())
        mocks.MetaKernelProduct.assert_not_called()


# ---------------------------------------------------------------------------
# Phase 7 – Labels-only mode
# ---------------------------------------------------------------------------

class TestPhase7LabelsOnlyMode:
    # Phase 7 – Labels-only mode
    # When faucet='labels' the pipeline enters a dedicated branch that skips all
    # product generation and jumps straight to label writing for products already
    # in the staging area. Inside this branch, if write_plan() returns a falsy
    # value (no products found) the pipeline returns immediately without writing
    # any labels. Otherwise, it calls files_in_staging(), copy_to_bundle(), and
    # finish_execution() before returning — mirroring the normal tail of the
    # pipeline but without creating any new archive products.

    @pytest.fixture(autouse=True)
    def set_labels_faucet(self, mocks):
        mocks.Setup.return_value.faucet = 'labels'

    def test_bundle_add_called_with_spice_kernels_collection(self, mocks):
        # The SPICE kernels collection is registered with the bundle in labels mode.
        run_pipeline(_args(faucet='labels'))
        mocks.Bundle.return_value.add.assert_called_with(
            mocks.SpiceKernelsCollection.return_value
        )

    def test_files_in_staging_called(self, mocks):
        # Staging area contents are listed before copying in labels mode.
        run_pipeline(_args(faucet='labels'))
        mocks.Bundle.return_value.files_in_staging.assert_called_once()

    def test_copy_to_bundle_called(self, mocks):
        # Products are copied to the bundle area before the labels-mode exit.
        run_pipeline(_args(faucet='labels'))
        mocks.Bundle.return_value.copy_to_bundle.assert_called_once()

    def test_finish_execution_called(self, mocks):
        # The pipeline shuts down cleanly after the labels-mode copy.
        run_pipeline(_args(faucet='labels'))
        mocks.finish_execution.assert_called_once_with(
            mocks.Setup.return_value, mocks.Log.return_value
        )

    def test_document_collection_not_created_in_labels_mode(self, mocks):
        # DocumentCollection is not created when the pipeline exits at the labels faucet.
        run_pipeline(_args(faucet='labels'))
        mocks.DocumentCollection.assert_not_called()

    def test_checksum_not_created_in_labels_mode(self, mocks):
        # ChecksumProduct is not created when the pipeline exits at the labels faucet.
        run_pipeline(_args(faucet='labels'))
        mocks.ChecksumProduct.assert_not_called()


# ---------------------------------------------------------------------------
# Phase 8 – Collection metadata (PDS4)
# ---------------------------------------------------------------------------

class TestPhase8CollectionMetadata:
    # Phase 8 – SPICE kernel collection metadata
    # For PDS4, set_increment_times() is called on the SPICE kernels collection
    # to record the temporal coverage of the release. If the collection was
    # updated (spice_kernels_collection.updated is truthy), set_collection_vid()
    # is called for PDS4 to bump the collection version identifier, and
    # InventoryProduct is created for the collection regardless of PDS version.
    # validate() is called on the collection to check internal consistency.
    # For PDS3, set_increment_times() and set_collection_vid() are both skipped,
    # but an InventoryProduct is still created when the collection is updated.

    def test_set_increment_times_called_for_pds4(self, mocks):
        # Increment start/stop times are computed for PDS4 archives.
        run_pipeline(_args())
        mocks.SpiceKernelsCollection.return_value.set_increment_times.assert_called_once()

    def test_set_increment_times_not_called_for_pds3(self, mocks):
        # Increment times are not computed for PDS3 archives.
        mocks.Setup.return_value.pds_version = '3'
        run_pipeline(_args())
        mocks.SpiceKernelsCollection.return_value.set_increment_times.assert_not_called()

    def test_collection_vid_set_for_pds4(self, mocks):
        # The SPICE kernels collection version ID is set for PDS4 archives.
        run_pipeline(_args())
        mocks.SpiceKernelsCollection.return_value.set_collection_vid.assert_called()

    def test_validate_called_on_spice_kernels_collection(self, mocks):
        # The SPICE kernels collection is validated after products are generated.
        run_pipeline(_args())
        mocks.SpiceKernelsCollection.return_value.validate.assert_called_once()

    def test_inventory_product_created_when_collection_updated(self, mocks):
        # An InventoryProduct is generated for the SPICE kernels collection when it has new products.
        mocks.SpiceKernelsCollection.return_value.updated = True
        run_pipeline(_args())
        # InventoryProduct should be called at least once (for the SKC)
        mocks.InventoryProduct.assert_called()
        first_call_collection = mocks.InventoryProduct.call_args_list[0][0][1]
        assert first_call_collection is mocks.SpiceKernelsCollection.return_value

    def test_inventory_product_not_created_for_skc_when_not_updated(self, mocks):
        # No InventoryProduct is generated for the SPICE kernels collection when nothing changed.
        mocks.SpiceKernelsCollection.return_value.updated = False
        run_pipeline(_args())
        # When SKC is not updated, no InventoryProduct for it specifically.
        # All InventoryProduct calls should be for other collections.
        skc = mocks.SpiceKernelsCollection.return_value
        calls_for_skc = [
            c for c in mocks.InventoryProduct.call_args_list
            if c[0][1] is skc
        ]
        assert calls_for_skc == []

    def test_pds3_updated_skc_creates_inventory_without_vid_call(self, mocks):
        # For PDS3, an updated SKC gets an inventory but set_collection_vid is not called (line 311).
        mocks.Setup.return_value.pds_version = '3'
        mocks.SpiceKernelsCollection.return_value.updated = True
        run_pipeline(_args())

        skc = mocks.SpiceKernelsCollection.return_value
        skc.set_collection_vid.assert_not_called()
        calls_for_skc = [
            c for c in mocks.InventoryProduct.call_args_list
            if c[0][1] is skc
        ]
        assert len(calls_for_skc) == 1
        skc.add.assert_called()


# ---------------------------------------------------------------------------
# Phase 9 – PDS4 document + miscellaneous + checksum
# ---------------------------------------------------------------------------

class TestPhase9PDS4DocumentMiscChecksum:
    # Phase 9 – PDS4 document collection, miscellaneous products, and checksum
    # DocumentCollection is constructed and its VID is set. SpicedsProduct is
    # constructed; if it was generated, both the product and an InventoryProduct
    # are added to the document collection. All three collections (SPICE kernels,
    # miscellaneous, document) are registered with the bundle via bundle.add().
    # ChecksumProduct is then constructed for the miscellaneous collection, with
    # set_coverage() and generate() called in order. ReadmeProduct is constructed,
    # and the miscellaneous collection VID is updated. If setup.increment is True
    # and the checksum directory does not yet exist, a backfill loop creates one
    # ChecksumProduct per historical release in bundle.history. Finally, the
    # pipeline iterates over misc.product and sets new_product=False on any item
    # that is already a ChecksumProduct (lines 443-444).

    def test_document_collection_constructed_with_setup_and_bundle(self, mocks):
        # DocumentCollection is constructed with the shared setup and bundle objects.
        run_pipeline(_args())
        mocks.DocumentCollection.assert_called_with(
            mocks.Setup.return_value, mocks.Bundle.return_value
        )

    def test_document_collection_vid_set(self, mocks):
        # The document collection version ID is set before any documents are added.
        run_pipeline(_args())
        mocks.DocumentCollection.return_value.set_collection_vid.assert_called()

    def test_spiceds_product_constructed(self, mocks):
        # SpicedsProduct is constructed with setup and the document collection.
        run_pipeline(_args())
        mocks.SpicedsProduct.assert_called_once_with(
            mocks.Setup.return_value, mocks.DocumentCollection.return_value
        )

    def test_document_inventory_created_when_spiceds_generated(self, mocks):
        # When a SPICEDS document is generated, it and its inventory are added to the document collection.
        mocks.SpicedsProduct.return_value.generated = True
        run_pipeline(_args())
        doc_col = mocks.DocumentCollection.return_value
        # The code calls doc_col.add(spiceds) first, then doc_col.add(inventory).
        # assert_any_call checks that spiceds was added at some point.
        doc_col.add.assert_any_call(mocks.SpicedsProduct.return_value)
        inventory_calls_for_doc = [
            c for c in mocks.InventoryProduct.call_args_list
            if c[0][1] is doc_col
        ]
        assert len(inventory_calls_for_doc) >= 1

    def test_document_inventory_not_created_when_spiceds_not_generated(self, mocks):
        # When SPICEDS is not generated, no inventory is created for the document collection.
        mocks.SpicedsProduct.return_value.generated = False
        run_pipeline(_args())
        doc_col = mocks.DocumentCollection.return_value
        inventory_calls_for_doc = [
            c for c in mocks.InventoryProduct.call_args_list
            if c[0][1] is doc_col
        ]
        assert inventory_calls_for_doc == []

    def test_bundle_add_called_with_spice_kernels_collection(self, mocks):
        # The SPICE kernels collection is registered with the bundle.
        run_pipeline(_args())
        add_calls = mocks.Bundle.return_value.add.call_args_list
        added_args = [c[0][0] for c in add_calls]
        assert mocks.SpiceKernelsCollection.return_value in added_args

    def test_bundle_add_called_with_miscellaneous_collection(self, mocks):
        # The miscellaneous collection is registered with the bundle.
        run_pipeline(_args())
        add_calls = mocks.Bundle.return_value.add.call_args_list
        added_args = [c[0][0] for c in add_calls]
        assert mocks.MiscellaneousCollection.return_value in added_args

    def test_bundle_add_called_with_document_collection(self, mocks):
        # The document collection is registered with the bundle.
        run_pipeline(_args())
        add_calls = mocks.Bundle.return_value.add.call_args_list
        added_args = [c[0][0] for c in add_calls]
        assert mocks.DocumentCollection.return_value in added_args

    def test_checksum_product_created_for_miscellaneous_collection(self, mocks):
        # A ChecksumProduct is created for the miscellaneous collection.
        run_pipeline(_args())
        misc = mocks.MiscellaneousCollection.return_value
        checksum_calls_for_misc = [
            c for c in mocks.ChecksumProduct.call_args_list
            if c[0][1] is misc
        ]
        assert len(checksum_calls_for_misc) >= 1

    def test_checksum_set_coverage_called(self, mocks):
        # Coverage times are computed before the checksum file is written.
        run_pipeline(_args())
        mocks.ChecksumProduct.return_value.set_coverage.assert_called_once()

    def test_checksum_generate_called(self, mocks):
        # The checksum file is written for the current release.
        run_pipeline(_args())
        mocks.ChecksumProduct.return_value.generate.assert_called()

    def test_readme_product_created(self, mocks):
        # A ReadmeProduct is created with the shared setup and bundle.
        run_pipeline(_args())
        mocks.ReadmeProduct.assert_called_once_with(
            mocks.Setup.return_value, mocks.Bundle.return_value
        )

    def test_misc_collection_vid_set(self, mocks):
        # The miscellaneous collection version ID is updated after its products are finalized.
        run_pipeline(_args())
        mocks.MiscellaneousCollection.return_value.set_collection_vid.assert_called()

    def test_backfill_loop_runs_when_increment_and_no_checksum_dir(self, mocks):
        # When the checksum directory is absent, one ChecksumProduct is created per past release.
        setup = mocks.Setup.return_value
        setup.increment = True
        mocks.isdir.return_value = False
        bundle = mocks.Bundle.return_value
        bundle.history = {'release_01': ('data', 'label'), 'release_02': ('data2', 'label2')}

        run_pipeline(_args())

        # ChecksumProduct should be called once per historical release
        # (add_previous_checksum=False) plus once for the current release.
        backfill_calls = [
            c for c in mocks.ChecksumProduct.call_args_list
            if c[1].get('add_previous_checksum') is False
        ]
        assert len(backfill_calls) == len(bundle.history)

    def test_backfill_loop_skipped_when_checksum_dir_exists(self, mocks):
        # When the checksum directory already exists, the backfill loop does not run.
        setup = mocks.Setup.return_value
        setup.increment = True
        mocks.isdir.return_value = True

        run_pipeline(_args())

        backfill_calls = [
            c for c in mocks.ChecksumProduct.call_args_list
            if c[1].get('add_previous_checksum') is False
        ]
        assert len(backfill_calls) == 0

    def test_backfill_loop_skipped_when_not_an_increment(self, mocks):
        # The backfill loop is gated on setup.increment; non-increment runs skip it.
        mocks.Setup.return_value.increment = False
        mocks.isdir.return_value = False

        run_pipeline(_args())

        backfill_calls = [
            c for c in mocks.ChecksumProduct.call_args_list
            if c[1].get('add_previous_checksum') is False
        ]
        assert len(backfill_calls) == 0

    def test_existing_checksum_in_misc_product_marked_as_not_new(self, mocks):
        # A ChecksumProduct already in misc.product is marked new_product=False before the current checksum is added.
        prior_checksum = _StubChecksum()

        with patch(f'{_MODULE}.ChecksumProduct', _StubChecksum):
            mocks.MiscellaneousCollection.return_value.product = [prior_checksum]
            run_pipeline(_args())

        assert prior_checksum.new_product is False

    def test_non_checksum_product_in_misc_product_not_mutated(self, mocks):
        # A non-ChecksumProduct in misc.product is not mutated by the isinstance guard (branch 443->442).
        prior_checksum = _StubChecksum()
        other_product = MagicMock()

        with patch(f'{_MODULE}.ChecksumProduct', _StubChecksum):
            mocks.MiscellaneousCollection.return_value.product = [
                prior_checksum, other_product
            ]
            run_pipeline(_args())

        assert prior_checksum.new_product is False
        assert other_product.new_product != False


# ---------------------------------------------------------------------------
# Phase 10 – PDS3 path
# ---------------------------------------------------------------------------

class TestPhase10PDS3Path:
    # Phase 10 – PDS3 path (document collection and checksum)
    # When setup.pds_version == '3' the pipeline takes a separate branch that
    # constructs DocumentCollection and calls get_pds3_documents() on it instead
    # of building a SpicedsProduct. All three collections are then registered
    # with the bundle. ChecksumProduct is created with add_previous_checksum=False
    # (PDS3 archives do not chain checksum files across releases) and generate()
    # is called immediately. set_increment_times() and bundle.validate() are both
    # skipped, reflecting the simpler structure of PDS3 delivery packages.

    @pytest.fixture(autouse=True)
    def set_pds3(self, mocks):
        mocks.Setup.return_value.pds_version = '3'

    def test_document_collection_constructed_for_pds3(self, mocks):
        # DocumentCollection is constructed with setup and bundle for PDS3.
        run_pipeline(_args())
        mocks.DocumentCollection.assert_called_with(
            mocks.Setup.return_value, mocks.Bundle.return_value
        )

    def test_get_pds3_documents_called(self, mocks):
        # PDS3 documents are retrieved from the document collection.
        run_pipeline(_args())
        mocks.DocumentCollection.return_value.get_pds3_documents.assert_called_once()

    def test_bundle_add_called_for_skc_doc_misc(self, mocks):
        # All three collections are registered with the bundle for PDS3.
        run_pipeline(_args())
        add_calls = [c[0][0] for c in mocks.Bundle.return_value.add.call_args_list]
        assert mocks.SpiceKernelsCollection.return_value in add_calls
        assert mocks.DocumentCollection.return_value in add_calls
        assert mocks.MiscellaneousCollection.return_value in add_calls

    def test_checksum_created_without_previous_checksum(self, mocks):
        # The PDS3 checksum is created without referencing any previous checksum.
        run_pipeline(_args())
        mocks.ChecksumProduct.assert_called_once_with(
            mocks.Setup.return_value,
            mocks.MiscellaneousCollection.return_value,
            add_previous_checksum=False,
        )

    def test_checksum_generate_called_for_pds3(self, mocks):
        # The checksum file is written for the current PDS3 release.
        run_pipeline(_args())
        mocks.ChecksumProduct.return_value.generate.assert_called_once()

    def test_set_increment_times_not_called_for_pds3(self, mocks):
        # Increment times are not computed for PDS3 archives.
        run_pipeline(_args())
        mocks.SpiceKernelsCollection.return_value.set_increment_times.assert_not_called()

    def test_bundle_validate_not_called_for_pds3(self, mocks):
        # Bundle history validation is skipped for PDS3 archives.
        run_pipeline(_args())
        mocks.Bundle.return_value.validate.assert_not_called()


# ---------------------------------------------------------------------------
# Phase 11 – Staging recap + copy
# ---------------------------------------------------------------------------

class TestPhase11StagingRecapAndCopy:
    # Phase 11 – Staging recap and bundle copy
    # bundle.files_in_staging() is called to log the full contents of the staging
    # area before anything is moved. The 'staging' faucet stops the pipeline here
    # via finish_execution(), leaving all products in staging for manual review.
    # On a full run, bundle.copy_to_bundle() transfers the staged products to the
    # final bundle directory. The 'bundle' faucet then stops the pipeline via
    # finish_execution() after the copy, skipping the final validation step.

    def test_files_in_staging_called(self, mocks):
        # Staging contents are listed before products are copied to the bundle area.
        run_pipeline(_args())
        mocks.Bundle.return_value.files_in_staging.assert_called_once()

    def test_finish_execution_called_when_faucet_is_staging(self, mocks):
        # faucet='staging' stops the pipeline with a clean shutdown after staging.
        mocks.Setup.return_value.faucet = 'staging'
        run_pipeline(_args())
        mocks.finish_execution.assert_called_once_with(
            mocks.Setup.return_value, mocks.Log.return_value
        )

    def test_copy_to_bundle_not_called_when_faucet_is_staging(self, mocks):
        # The bundle copy is skipped when the pipeline exits at the staging faucet.
        mocks.Setup.return_value.faucet = 'staging'
        run_pipeline(_args())
        mocks.Bundle.return_value.copy_to_bundle.assert_not_called()

    def test_copy_to_bundle_called_on_full_run(self, mocks):
        # Products are copied to the bundle area on a full run.
        run_pipeline(_args())
        mocks.Bundle.return_value.copy_to_bundle.assert_called_once()

    def test_finish_execution_called_when_faucet_is_bundle(self, mocks):
        # faucet='bundle' stops the pipeline with a clean shutdown after the bundle copy.
        mocks.Setup.return_value.faucet = 'bundle'
        run_pipeline(_args())
        mocks.finish_execution.assert_called_once_with(
            mocks.Setup.return_value, mocks.Log.return_value
        )

    def test_bundle_validate_not_called_when_faucet_is_bundle(self, mocks):
        # Final validation is skipped when the pipeline exits at the bundle faucet.
        mocks.Setup.return_value.faucet = 'bundle'
        run_pipeline(_args())
        mocks.Bundle.return_value.validate.assert_not_called()


# ---------------------------------------------------------------------------
# Phase 12 – Final validation
# ---------------------------------------------------------------------------

class TestPhase12FinalValidation:
    # Phase 12 – Final validation and shutdown
    # For PDS4, bundle.validate() cross-checks the bundle history against the
    # generated checksum files to detect any inconsistencies introduced during
    # the run. This call is skipped entirely for PDS3. The pipeline then iterates
    # over spice_kernels_collection.product and calls validate() on every item
    # that is an instance of MetaKernelProduct, verifying that each meta-kernel
    # references only kernels that are present in the archive. Finally,
    # finish_execution(setup, log) is called unconditionally as the last action
    # of a complete pipeline run, closing the log and writing the run summary.

    def test_bundle_validate_called_for_pds4(self, mocks):
        # Bundle history is validated against checksum files for PDS4 archives.
        run_pipeline(_args())
        mocks.Bundle.return_value.validate.assert_called_once()

    def test_bundle_validate_not_called_for_pds3(self, mocks):
        # Bundle history validation is skipped for PDS3 archives.
        mocks.Setup.return_value.pds_version = '3'
        run_pipeline(_args())
        mocks.Bundle.return_value.validate.assert_not_called()

    def test_meta_kernel_validate_called_for_mk_product(self, mocks_no_mk):
        # A MetaKernelProduct in the collection has validate() called on it.
        mk_instance = MagicMock(spec=MetaKernelProduct)
        mk_instance.name = 'maven_v01.tm'
        mocks_no_mk.SpiceKernelsCollection.return_value.product = [mk_instance]

        run_pipeline(_args())

        mk_instance.validate.assert_called_once()

    def test_non_meta_kernel_product_not_validated(self, mocks_no_mk):
        # Products that are not MetaKernelProduct instances are not validated.
        plain_product = MagicMock()
        mocks_no_mk.SpiceKernelsCollection.return_value.product = [plain_product]

        run_pipeline(_args())

        plain_product.validate.assert_not_called()

    def test_validate_called_for_each_mk_in_collection(self, mocks_no_mk):
        # validate() is called once per MetaKernelProduct in the collection.
        mk1 = MagicMock(spec=MetaKernelProduct)
        mk1.name = 'maven_v01.tm'
        mk2 = MagicMock(spec=MetaKernelProduct)
        mk2.name = 'maven_v02.tm'
        mocks_no_mk.SpiceKernelsCollection.return_value.product = [mk1, mk2]

        run_pipeline(_args())

        mk1.validate.assert_called_once()
        mk2.validate.assert_called_once()

    def test_finish_execution_called_at_end_of_full_run(self, mocks):
        # finish_execution is the last call in a complete pipeline run.
        run_pipeline(_args())
        mocks.finish_execution.assert_called_once_with(
            mocks.Setup.return_value, mocks.Log.return_value
        )

    def test_finish_execution_receives_log_instance(self, mocks):
        # The log instance (not the class) is passed to finish_execution.
        run_pipeline(_args())
        _, log_arg = mocks.finish_execution.call_args[0]
        assert log_arg is mocks.Log.return_value


# ---------------------------------------------------------------------------
# Phase 13 - NPBError -> handle_npb_error routing
# ---------------------------------------------------------------------------

class TestNPBErrorHandling:
    # run_pipeline wraps its body in two broad try/except blocks: Block A
    # around Setup() construction alone, Block B around everything from
    # Log() construction to the end. Both catch NPBError and forward it to
    # the *real* handle_npb_error (not mocked here). Block B's handler
    # performs cleanup -- writes the file list and checksum registry, removes
    # template files, clears the SPICE kernel pool -- and then always raises
    # RuntimeError with the same message; Block A's handler skips cleanup
    # entirely since no setup instance exists yet. Each parametrized case
    # below forces one Block-B call site to raise NPBError and asserts both
    # that cleanup ran and that the RuntimeError carries the original
    # message. Two call sites need their own dedicated test instead of a
    # table row: ReleasePlan.read_plan() (only reached with a non-default
    # `args.plan`) and Setup() construction (Block A's no-setup case).

    @staticmethod
    def _apply_overrides(mocks, overrides):
        for path, value in overrides.items():
            *attrs, last = path.split('.')
            target = mocks
            for attr in attrs:
                target = getattr(target, attr)
            setattr(target, last, value)

    @staticmethod
    def _resolve(mocks, dotted_path):
        # Walks a dotted path off `mocks` (e.g. "ChecksumProduct" for a
        # construction-site failure, or "ChecksumProduct.return_value.generate"
        # for a failure in a call on the constructed instance) and returns the
        # mock at the end of it, so the caller can set .side_effect on it.
        target = mocks
        for attr in dotted_path.split('.'):
            target = getattr(target, attr)
        return target

    # Each case: (dotted attribute overrides on `mocks`, dotted mock attribute
    # to fail (resolved via `_resolve`, e.g. a bare class name for a
    # construction-site failure, or "ChecksumProduct.return_value.generate"
    # for a failure in a call on the constructed instance), expected message).
    @pytest.mark.parametrize('overrides, target_attr, message', [
        pytest.param(
            {'ReleasePlan.return_value.kernel_list': ['maven_2024.orb']},
            'OrbnumFileProduct', 'boom orbnum', id='orbnum_file_product',
        ),
        pytest.param(
            {'ReleasePlan.return_value.kernel_list': ['maven_2024.bc']},
            'SpiceKernelProduct', 'boom kernel', id='spice_kernel_product',
        ),
        pytest.param(
            {'SpiceKernelsCollection.return_value.determine_meta_kernels.return_value': {'maven_v01.tm': None}},
            'MetaKernelProduct', 'boom mk', id='meta_kernel_product',
        ),
        pytest.param(
            {'SpiceKernelsCollection.return_value.updated': True},
            'InventoryProduct', 'boom skc inventory', id='skc_inventory',
        ),
        pytest.param({}, 'SpicedsProduct', 'boom spiceds', id='spiceds_product'),
        pytest.param(
            {'SpicedsProduct.return_value.generated': True},
            'InventoryProduct', 'boom doc inventory', id='doc_inventory',
        ),
        pytest.param(
            {
                'Setup.return_value.increment': True,
                'isdir.return_value': False,
                'Bundle.return_value.history': {'release_01': ('data', 'label')},
            },
            'ChecksumProduct', 'boom checksum backfill', id='release_checksum_backfill',
        ),
        pytest.param(
            {
                'Setup.return_value.increment': True,
                'isdir.return_value': False,
                'Bundle.return_value.history': {'release_01': ('data', 'label')},
            },
            'InventoryProduct', 'boom release misc inventory', id='release_misc_inventory',
        ),
        pytest.param({}, 'ChecksumProduct', 'boom checksum misc', id='misc_checksum'),
        pytest.param({}, 'InventoryProduct', 'boom misc inventory', id='misc_inventory'),
        pytest.param({}, 'ReadmeProduct', 'boom readme', id='readme_product'),
        pytest.param(
            {'Setup.return_value.pds_version': '3'},
            'ChecksumProduct', 'boom checksum pds3', id='pds3_checksum',
        ),
        # The four sites below are not construction calls but post-construction
        # calls on an already-built ChecksumProduct (.generate()/.set_coverage()),
        # which previously sat outside any try/except NPBError. Failing them
        # exercises the same routing via the dotted
        # "ChecksumProduct.return_value.<method>" path.
        pytest.param(
            {
                'Setup.return_value.increment': True,
                'isdir.return_value': False,
                'Bundle.return_value.history': {'release_01': ('data', 'label')},
            },
            'ChecksumProduct.return_value.generate', 'boom release checksum generate',
            id='release_checksum_generate',
        ),
        pytest.param(
            {}, 'ChecksumProduct.return_value.set_coverage', 'boom checksum set_coverage',
            id='misc_checksum_set_coverage',
        ),
        pytest.param(
            {}, 'ChecksumProduct.return_value.generate', 'boom checksum generate',
            id='misc_checksum_generate',
        ),
        pytest.param(
            {'Setup.return_value.pds_version': '3'},
            'ChecksumProduct.return_value.generate', 'boom checksum pds3 generate',
            id='pds3_checksum_generate',
        ),
        # ReleasePlan.write_plan() is called with the default args (no
        # kerlist, no .plan file), so it needs no extra overrides to be
        # reached -- unlike read_plan(), which needs args.plan set to a
        # .plan path and is covered separately below.
        pytest.param(
            {}, 'ReleasePlan.return_value.write_plan', 'boom write_plan',
            id='release_plan_write_plan',
        ),
    ])
    def test_npb_error_is_routed_to_handle_npb_error(self, mocks, overrides, target_attr, message):
        self._apply_overrides(mocks, overrides)
        self._resolve(mocks, target_attr).side_effect = NPBError(message)
        args = _args()

        with pytest.raises(RuntimeError, match=message):
            run_pipeline(args)

        setup = mocks.Setup.return_value
        setup.write_file_list.assert_called_once()
        setup.write_checksum_registry.assert_called_once()

    def test_npb_error_from_release_plan_read_plan_is_routed_to_handle_npb_error(self, mocks):
        # read_plan() is only reached when args.plan is set to a .plan path
        # (kerlist absent), so it can't be folded into the parametrize table
        # above, which relies on the default args() reaching write_plan()
        # instead.
        mocks.ReleasePlan.return_value.read_plan.side_effect = NPBError('boom read_plan')
        args = _args(plan='mission_release_01.plan')

        with pytest.raises(RuntimeError, match='boom read_plan'):
            run_pipeline(args)

        setup = mocks.Setup.return_value
        setup.write_file_list.assert_called_once()
        setup.write_checksum_registry.assert_called_once()

    def test_npb_error_from_setup_construction_is_routed_without_setup(self, mocks):
        # Setup() itself failing is a special case (Block A): there is no
        # setup instance yet, so handle_npb_error is called with no `setup`
        # kwarg and no cleanup (write_file_list/write_checksum_registry) is
        # attempted. Log must never be constructed either, since it depends
        # on a successfully-built setup.
        mocks.Setup.side_effect = NPBError('boom setup')
        args = _args()

        with pytest.raises(RuntimeError, match='boom setup'):
            run_pipeline(args)

        mocks.Log.assert_not_called()
        mocks.Setup.return_value.write_file_list.assert_not_called()
        mocks.Setup.return_value.write_checksum_registry.assert_not_called()
