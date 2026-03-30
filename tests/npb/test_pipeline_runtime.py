import logging
import os
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

import spiceypy

from pds.naif_pds4_bundler.pipeline import runtime

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def dirs(tmp_path):
    """Create the standard directory tree used by most tests.

    Layout
    ------
    tmp/
      staging/
        mars2020_spice/     <- self.staging_directory
      bundle/
        mars2020_spice/     <- bundle final area
      working/              <- self.working_directory
    """
    staging = tmp_path / "staging" / "mars2020_spice"
    bundle = tmp_path / "bundle"
    working = tmp_path / "working"

    staging.mkdir(parents=True)
    (bundle / "mars2020_spice").mkdir(parents=True)
    working.mkdir()

    return SimpleNamespace(
        staging=str(staging),
        bundle=str(bundle),
        working=str(working),
        tmp=tmp_path,
    )

@pytest.fixture()
def file_list(dirs):
    """Write a .file_list with two kernel entries and return its path."""
    content = (
        "spice_kernels/ck/mars2020_surf_rover_tlm_0000_0089_v1.bc\n"
        "spice_kernels/spk/mars2020_cruise_od138_v1.bsp\n"
    )
    path = dirs.tmp / "mars2020_release_01.file_list"
    path.write_text(content)
    return str(path)

@pytest.fixture()
def file_list_with_byproducts(dirs):
    """A .file_list that also contains .plan and .kernel_list lines."""
    content = (
        "spice_kernels/ck/mars2020_surf_rover_tlm_0000_0089_v1.bc\n"
        "mars2020_release_01.plan\n"
        "mars2020_release_01.kernel_list\n"
        "spice_kernels/spk/mars2020_cruise_od138_v1.bsp\n"
    )
    path = dirs.tmp / "mars2020_release_01.file_list"
    path.write_text(content)
    return str(path)

# ---------------------------------------------------------------------------
# Setup.clean_run tests
#
# Strategy
# --------
# clear_run only reads six attributes from `self`:
#     self.args.clear       – path to the .file_list from the previous run
#     self.args.kerlist     – truthy when a kernel list was supplied as input
#     self.args.plan        – truthy when a plan file was produced
#     self.staging_directory
#     self.bundle_directory
#     self.working_directory
#     self.mission_acronym  (only in the error message path)
#     self.run_type         (only in the error message path)
#
# We therefore construct a minimal Setup-like object via object.__new__,
# setting only those attributes, and never invoke __init__. This avoids
# the need for a real XML config file, a real SPICE installation, or any
# other infrastructure.
#
# handle_npb_error raises RuntimeError. We patch it with a side_effect of RuntimeError
# so assertions are possible.
#
# All filesystem interaction uses tmp_path (pytest's built-in temporary
# directory fixture) so no real files are left behind and tests are fully
# isolated.
# """
# ---------------------------------------------------------------------------

def test_clear_run_nonexistent_file_list_calls_error_message(dirs):
    """error_message must be called when args.clear points to nothing."""
    setup = _make_setup(
        staging_directory=dirs.staging,
        bundle_directory=dirs.bundle,
        working_directory=dirs.working,
        args=_make_args(clear="/nonexistent/path.file_list"),
    )

    expected_error = (
        'The file provided with the "clear" argument does not exist or is not '
        'readable. Make sure that the file follows the name pattern: '
        'mars2020_release_NN.file_list. where NN is the release number.')

    with patch(
            "pds.naif_pds4_bundler.classes.setup.handle_npb_error"
    ) as mock_err:
        mock_err.side_effect = RuntimeError("handle_npb_error called")
        with pytest.raises(RuntimeError):
            setup.clear_run()

    mock_err.assert_called_once()
    assert expected_error == mock_err.call_args[0][0]


def test_clear_run_files_removed_from_staging_area(dirs, file_list):
    """Kernel files listed in the file_list are removed from staging area."""
    # Create the files that should be removed
    ck_dir = os.path.join(dirs.staging, "spice_kernels", "ck")
    spk_dir = os.path.join(dirs.staging, "spice_kernels", "spk")
    os.makedirs(ck_dir)
    os.makedirs(spk_dir)

    ck_file = os.path.join(ck_dir, "mars2020_surf_rover_tlm_0000_0089_v1.bc")
    spk_file = os.path.join(spk_dir, "mars2020_cruise_od138_v1.bsp")
    open(ck_file, "w").close()
    open(spk_file, "w").close()

    setup = _make_setup(
        staging_directory=dirs.staging,
        bundle_directory=dirs.bundle,
        working_directory=dirs.working,
        args=_make_args(clear=file_list),
    )
    setup.clear_run()

    assert not os.path.exists(ck_file), "CK file should have been removed"
    assert not os.path.exists(spk_file), "SPK file should have been removed"


def test_clear_run_missing_file_logs_warning(
        dirs, file_list, caplog
):
    """A file absent from staging must produce a warning, not an exception."""
    setup = _make_setup(
        staging_directory=dirs.staging,
        bundle_directory=dirs.bundle,
        working_directory=dirs.working,
        args=_make_args(clear=file_list),
    )

    expected_warnings = [
        '     File p/staging/mars2020_spice/spice_kernels/ck/mars2020_surf_rover_tlm_0000_0089_v1.bc not found.',
        '     File p/staging/mars2020_spice/spice_kernels/spk/mars2020_cruise_od138_v1.bsp not found.',
        '     File spice_kernels/ck/mars2020_surf_rover_tlm_0000_0089_v1.bc not found.',
        '     File spice_kernels/spk/mars2020_cruise_od138_v1.bsp not found.']

    with caplog.at_level(logging.WARNING):
        setup.clear_run()  # files do not exist — must not raise

    messages = [r.message.replace(str(dirs.tmp), 'p') for r in caplog.records]
    assert expected_warnings == messages


@pytest.mark.parametrize("extension, message", [
    (".plan", ".plan paths must not be passed to os.remove during staging cleanup"),
    (".kernel_list", ".kernel_list paths must not be passed to os.remove during staging cleanup")
])
def test_clear_run_plan_lines_skipped_in_staging_and_bundle(dirs, file_list_with_byproducts, extension, message):
    """.plan/.kernel_list entries in the file_list must not trigger
    removal attempts in the staging area (they are handled separately)."""
    setup = _make_setup(
        staging_directory=dirs.staging,
        bundle_directory=dirs.bundle,
        working_directory=dirs.working,
        args=_make_args(clear=file_list_with_byproducts),
    )

    # Patch os.remove to record what would be deleted
    removed = []
    original_remove = os.remove

    def capturing_remove(path):
        removed.append(path)
        # Don't actually raise; files may not exist in this test
        try:
            original_remove(path)
        except FileNotFoundError:
            pass

    with patch("os.remove", side_effect=capturing_remove):
        setup.clear_run()

    assert not any(extension in p for p in removed), message


def test_clear_run_files_removed_from_bundle_final_area(dirs, file_list):
    """Kernel files are removed from bundle/mission_acronym_spice/."""
    final_area = os.path.join(dirs.bundle, "mars2020_spice")
    ck_dir = os.path.join(final_area, "spice_kernels", "ck")
    spk_dir = os.path.join(final_area, "spice_kernels", "spk")
    os.makedirs(ck_dir)
    os.makedirs(spk_dir)

    ck_file = os.path.join(ck_dir, "mars2020_surf_rover_tlm_0000_0089_v1.bc")
    spk_file = os.path.join(spk_dir, "mars2020_cruise_od138_v1.bsp")
    open(ck_file, "w").close()
    open(spk_file, "w").close()

    setup = _make_setup(
        staging_directory=dirs.staging,
        bundle_directory=dirs.bundle,
        working_directory=dirs.working,
        args=_make_args(clear=file_list),
    )
    setup.clear_run()

    assert not os.path.exists(ck_file), "CK should have been removed from bundle"
    assert not os.path.exists(spk_file), "SPK should have been removed from bundle"


def test_clear_run_label_mode_uses_alternative_path(dirs):
    """When bundle/mission_acronym_spice/ is absent, the file is removed
    via bundle_directory + the portion of the path after 'spice_kernels'."""
    # Deliberately do NOT create mars2020_spice/ so the label branch fires
    label_fl = _make_label_file_list(dirs.tmp)

    # Remove the "standard" path for the bundle directory:
    os.rmdir(os.path.join(dirs.bundle, "mars2020_spice"))

    # Create the file at the path the label branch will compute:
    # bundle_directory + "/ck/mars2020_surf_rover_tlm_0000_0089_v1.bc"
    target_dir = os.path.join(dirs.bundle, "ck")
    os.makedirs(target_dir)
    target_file = os.path.join(
        target_dir, "mars2020_surf_rover_tlm_0000_0089_v1.bc"
    )
    open(target_file, "w").close()

    setup = _make_setup(
        staging_directory=dirs.staging,
        bundle_directory=dirs.bundle,
        working_directory=dirs.working,
        run_type="labels",
        args=_make_args(clear=label_fl),
    )
    setup.clear_run()

    assert not os.path.exists(target_file), (
        "Label-mode path construction must remove the correct file"
    )


def test_clear_run_label_mode_missing_file_logs_warning(dirs, caplog):
    """Absent file in label mode must log a warning, not raise."""
    label_fl = _make_label_file_list(dirs.tmp)

    # Remove the "standard" path for the bundle directory:
    os.rmdir(os.path.join(dirs.bundle, "mars2020_spice"))

    # Do not create the target file or mission_dir
    setup = _make_setup(
        staging_directory=dirs.staging,
        bundle_directory=dirs.bundle,
        working_directory=dirs.working,
        run_type="labels",
        args=_make_args(clear=label_fl),
    )

    expected_warnings = [
        '     File p/staging/mars2020_spice/spice_kernels/ck/mars2020_surf_rover_tlm_0000_0089_v1.bc not found.',
        '     File spice_kernels/ck/mars2020_surf_rover_tlm_0000_0089_v1.bc not found.']

    with caplog.at_level(logging.WARNING):
        setup.clear_run()

    messages = [r.message.replace(str(dirs.tmp), 'p') for r in caplog.records]
    assert expected_warnings == messages


def test_clear_run_plan_file_removed_when_kerlist_flag_set(dirs, file_list):
    """When args.kerlist is set, the corresponding .plan by-product
    is removed from the working directory."""
    plan_name = "mars2020_release_01.plan"
    plan_file = os.path.join(dirs.working, plan_name)
    open(plan_file, "w").close()

    setup = _make_setup(
        staging_directory=dirs.staging,
        bundle_directory=dirs.bundle,
        working_directory=dirs.working,
        args=_make_args(clear=file_list, kerlist='mars2020_release_00.kernel_list'),
    )
    setup.clear_run()

    assert not os.path.exists(plan_file), ".plan file should have been removed"


def test_clear_run_plan_file_not_removed_when_kerlist_flag_unset(dirs, file_list):
    """When args.kerlist is falsy the .plan file must be left alone."""
    plan_name = "mars2020_release_01.plan"
    plan_file = os.path.join(dirs.working, plan_name)
    open(plan_file, "w").close()

    setup = _make_setup(
        staging_directory=dirs.staging,
        bundle_directory=dirs.bundle,
        working_directory=dirs.working,
        args=_make_args(clear=file_list, kerlist=None),
    )
    setup.clear_run()

    assert os.path.exists(plan_file), ".plan must survive when kerlist not provided"


def test_clear_run_kernel_list_removed_when_plan_flag_set(dirs, file_list):
    """When args.plan is truthy the .kernel_list by-product is removed."""
    kl_name = "mars2020_release_01.kernel_list"
    kl_file = os.path.join(dirs.working, kl_name)
    open(kl_file, "w").close()

    setup = _make_setup(
        staging_directory=dirs.staging,
        bundle_directory=dirs.bundle,
        working_directory=dirs.working,
        args=_make_args(clear=file_list, plan='mars2020_release_01.plan'),
    )
    setup.clear_run()

    assert not os.path.exists(kl_file), ".kernel_list should have been removed"


def test_clear_run_kernel_list_not_removed_when_plan_flag_unset(dirs, file_list):
    """When args.plan is falsy the .kernel_list must be left alone."""
    kl_name = "mars2020_release_01.kernel_list"
    kl_file = os.path.join(dirs.working, kl_name)
    open(kl_file, "w").close()

    setup = _make_setup(
        staging_directory=dirs.staging,
        bundle_directory=dirs.bundle,
        working_directory=dirs.working,
        args=_make_args(clear=file_list, plan=None),
    )
    setup.clear_run()

    assert os.path.exists(kl_file), ".kernel_list must survive when plan is not provided"


def test_clear_run_missing_plan_byproduct_logs_warning_not_raises(dirs, file_list, caplog):
    """A missing .plan by-product must log a warning, not raise."""
    setup = _make_setup(
        staging_directory=dirs.staging,
        bundle_directory=dirs.bundle,
        working_directory=dirs.working,
        args=_make_args(clear=file_list, kerlist="mars2020_release_00.kernel_list"),
    )

    with caplog.at_level(logging.WARNING):
        setup.clear_run()  # .plan does not exist — must not raise

    messages = [r.message.replace(str(dirs.tmp), 'p') for r in caplog.records]
    assert '     File p/mars2020_release_01.plan not found.' in messages


def test_clear_run_missing_kernel_list_byproduct_logs_warning_not_raises(dirs, file_list, caplog):
    """A missing .kernel_list by-product must log a warning, not raise."""
    setup = _make_setup(
        staging_directory=dirs.staging,
        bundle_directory=dirs.bundle,
        working_directory=dirs.working,
        args=_make_args(clear=file_list, plan='mars2020_release_01.plan'),
    )

    with caplog.at_level(logging.WARNING):
        setup.clear_run()

    messages = [r.message.replace(str(dirs.tmp), 'p') for r in caplog.records]
    print(messages)
    assert '     File p/mars2020_release_01.kernel_list not found.' in messages


def test_clear_run_empty_file_list_removes_nothing(dirs, tmp_path):
    """An empty .file_list must complete without error and remove nothing."""
    fl = tmp_path / "mars2020_release_01.file_list"
    fl.write_text("")

    sentinel = os.path.join(dirs.working, "sentinel.txt")
    open(sentinel, "w").close()

    setup = _make_setup(
        staging_directory=dirs.staging,
        bundle_directory=dirs.bundle,
        working_directory=dirs.working,
        args=_make_args(clear=str(fl)),
    )
    setup.clear_run()

    assert os.path.exists(sentinel), "Unrelated files must not be touched"

# ---------------------------------------------------------------------------
# runtime.handle_npb_error tests
# ---------------------------------------------------------------------------

def test_handle_error_raises_runtime_error(caplog):
    """Verifies that the function always raises RuntimeError with the message."""
    message = "Test failure message"

    with pytest.raises(RuntimeError, match=message):
        runtime.handle_npb_error(message)

    assert f"-- {message}" in caplog.text


def test_handle_error_calls_setup_methods(tmp_path, monkeypatch):
    """Verifies artifact generation and template cleanup when setup is provided."""
    # Setup mocks
    mock_setup = MagicMock()
    mock_setup.write_file_list = MagicMock()
    mock_setup.write_checksum_registry = MagicMock()

    # Create a dummy template file to test removal
    temp_file = tmp_path / "template.xml"
    temp_file.write_text("<xml/>")
    mock_setup.template_files = [str(temp_file)]

    # Mock SPICE and os.remove
    monkeypatch.setattr(spiceypy, "kclear", MagicMock())

    with pytest.raises(RuntimeError):
        runtime.handle_npb_error("Error", setup=mock_setup)

    # Verify side effects
    mock_setup.write_file_list.assert_called_once()
    mock_setup.write_checksum_registry.assert_called_once()
    assert not temp_file.exists()
    spiceypy.kclear.assert_called_once()


def test_handle_error_spice_cleanup_without_setup(monkeypatch):
    """Verifies that SPICE is cleared even if no setup object is provided."""
    mock_kclear = MagicMock()
    monkeypatch.setattr(spiceypy, "kclear", mock_kclear)

    with pytest.raises(RuntimeError):
        runtime.handle_npb_error("Quick Error", setup=None)

    mock_kclear.assert_called_once()


def test_handle_error_handles_missing_templates(monkeypatch):
    """Verifies it doesn't crash if a template file in the list is already gone."""
    mock_setup = MagicMock()
    mock_setup.template_files = ["/non/existent/path.xml"]

    monkeypatch.setattr(spiceypy, "kclear", MagicMock())

    # This should not raise FileNotFoundError because of the os.path.exists check
    with pytest.raises(RuntimeError):
        runtime.handle_npb_error("Error with missing template", setup=mock_setup)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_args(
        clear: str,
        kerlist: str | None = None,
        plan: str | None = None,
) -> SimpleNamespace:
    """Build a minimal args namespace."""
    return SimpleNamespace(clear=clear, kerlist=kerlist, plan=plan)


def _make_label_file_list(tmp_path) -> str:
    content = (
        "spice_kernels/ck/mars2020_surf_rover_tlm_0000_0089_v1.bc\n"
    )
    path = tmp_path / "mars2020_labels_01.file_list"
    path.write_text(content)
    return str(path)


def _make_setup(
        staging_directory: str,
        bundle_directory: str,
        working_directory: str,
        mission_acronym: str = "mars2020",
        run_type: str = "release",
        args: SimpleNamespace | None = None,
) -> object:
    """Construct a Setup-like object without invoking __init__.

    Imports Setup lazily so that the test module can be collected even
    when the wider package is not installed (e.g. in CI before install).
    """
    from pds.naif_pds4_bundler.classes.setup import Setup

    obj = object.__new__(Setup)
    obj.staging_directory = staging_directory
    obj.bundle_directory = bundle_directory
    obj.working_directory = working_directory
    obj.mission_acronym = mission_acronym
    obj.run_type = run_type
    obj.args = args or _make_args(clear="")
    return obj
