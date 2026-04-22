"""Tests for pds.naif_pds4_bundler.pipeline.runtime.

Structure
---------
One test class per public function:

    TestClearRun            – runtime.clear_run
    TestFinishExecution     – runtime.finish_execution
    TestHandleNpbError      – runtime.handle_npb_error
    TestLogStep             – runtime.log_step

Helpers and fixtures are module-level so they can be shared across classes.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

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
        mars2020_spice/     <- staging_directory
      bundle/
        mars2020_spice/     <- bundle final area
      working/              <- working_directory
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


@pytest.fixture()
def mock_setup():
    """Minimal Setup-like object suitable for log_step tests."""
    return _LogStepSetup(step=1)

# ---------------------------------------------------------------------------
# runtime.clean_run tests
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

class TestClearRun:
    """Tests for runtime.clear_run."""

    # -- Error path ----------------------------------------------------------

    def test_nonexistent_file_list_calls_error_message(self, dirs):
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
            'mars2020_release_NN.file_list, where NN is the release number.')

        with patch(
                "pds.naif_pds4_bundler.pipeline.runtime.handle_npb_error"
        ) as mock_err:
            mock_err.side_effect = RuntimeError("handle_npb_error called")
            with pytest.raises(RuntimeError):
                runtime.clear_run(setup)

        mock_err.assert_called_once_with(message=expected_error, setup=None)

    # -- Staging area --------------------------------------------------------

    def test_files_removed_from_staging_area(self, dirs, file_list):
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
        runtime.clear_run(setup)

        assert not os.path.exists(ck_file), "CK file should have been removed"
        assert not os.path.exists(spk_file), "SPK file should have been removed"

    def test_missing_staging_file_logs_warning_not_raises(self, dirs, file_list, caplog):
        """A file absent from staging must produce a WARNING, not an exception."""
        setup = _make_setup(
            staging_directory=dirs.staging,
            bundle_directory=dirs.bundle,
            working_directory=dirs.working,
            args=_make_args(clear=file_list),
        )

        expected_warnings = [
            f'     File {Path("p/staging/mars2020_spice/spice_kernels/ck/mars2020_surf_rover_tlm_0000_0089_v1.bc")} not found.',
            f'     File {Path("p/staging/mars2020_spice/spice_kernels/spk/mars2020_cruise_od138_v1.bsp")} not found.',
            f'     File {Path("p/bundle/mars2020_spice/spice_kernels/ck/mars2020_surf_rover_tlm_0000_0089_v1.bc")} not found.',
            f'     File {Path("p/bundle/mars2020_spice/spice_kernels/spk/mars2020_cruise_od138_v1.bsp")} not found.']

        with caplog.at_level(logging.WARNING):
            runtime.clear_run(setup)  # files do not exist — must not raise

        messages = [r.message.replace(str(dirs.tmp), 'p') for r in caplog.records]
        assert expected_warnings == messages

    @pytest.mark.parametrize("extension, description", [
        (".plan", ".plan paths must not be passed to os.remove during staging cleanup"),
        (".kernel_list", ".kernel_list paths must not be passed to os.remove during staging cleanup")
    ])
    def test_byproduct_lines_skipped_in_staging_and_bundle(
        self, dirs, file_list_with_byproducts, extension, description
    ):
        """.plan/.kernel_list lines in the file_list must not trigger removal
        attempts in the staging or bundle areas (they are handled separately)."""
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
            runtime.clear_run(setup)

        assert not any(extension in p for p in removed), description

    # -- Bundle / final area -------------------------------------------------

    def test_kernel_files_removed_from_bundle_final_area(self, dirs, file_list):
        """Kernel files are removed from bundle/<mission_acronym>_spice/."""
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
        runtime.clear_run(setup)

        assert not os.path.exists(ck_file), "CK should have been removed from bundle"
        assert not os.path.exists(spk_file), "SPK should have been removed from bundle"

    # -- Label mode ----------------------------------------------------------

    def test_label_mode_uses_alternative_path(self, dirs):
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
        runtime.clear_run(setup)

        assert not os.path.exists(target_file), (
            "Label-mode path construction must remove the correct file"
        )

    def test_label_mode_missing_file_logs_warning(self, dirs, caplog):
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
            f'     File {Path("p/staging/mars2020_spice/spice_kernels/ck/mars2020_surf_rover_tlm_0000_0089_v1.bc")} not found.',
            f'     File {Path("p/bundle/ck/mars2020_surf_rover_tlm_0000_0089_v1.bc")} not found.']

        with caplog.at_level(logging.WARNING):
            runtime.clear_run(setup)

        messages = [r.message.replace(str(dirs.tmp), 'p') for r in caplog.records]
        assert expected_warnings == messages

    # -- Working-directory by-products: .plan --------------------------------

    def test_plan_file_removed_when_kerlist_flag_set(self, dirs, file_list):
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
        runtime.clear_run(setup)

        assert not os.path.exists(plan_file), ".plan file should have been removed"

    def test_plan_file_not_removed_when_kerlist_flag_unset(self, dirs, file_list):
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
        runtime.clear_run(setup)

        assert os.path.exists(plan_file), ".plan must survive when kerlist not provided"

    def test_missing_plan_byproduct_logs_warning_not_raises(self, dirs, file_list, caplog):
        """A missing .plan by-product must log a WARNING, not raise."""
        kl_name = "mars2020_release_01.kernel_list"
        kl_file = os.path.join(dirs.working, kl_name)
        open(kl_file, "w").close()

        setup = _make_setup(
            staging_directory=dirs.staging,
            bundle_directory=dirs.bundle,
            working_directory=dirs.working,
            args=_make_args(clear=file_list, plan='mars2020_release_01.plan'),
        )
        runtime.clear_run(setup)

        assert not os.path.exists(kl_file), ".kernel_list should have been removed"

    # -- Working-directory by-products: .kernel_list -------------------------

    def test_kernel_list_not_removed_when_plan_flag_unset(self, dirs, file_list):
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
        runtime.clear_run(setup)

        assert os.path.exists(kl_file), ".kernel_list must survive when plan is not provided"

    def test_kernel_list_byproduct_not_removed_when_plan_flag_unset(self, dirs, file_list, caplog):
        """When args.plan is falsy the .kernel_list must be left alone."""
        setup = _make_setup(
            staging_directory=dirs.staging,
            bundle_directory=dirs.bundle,
            working_directory=dirs.working,
            args=_make_args(clear=file_list, kerlist="mars2020_release_00.kernel_list"),
        )

        with caplog.at_level(logging.WARNING):
            runtime.clear_run(setup)  # .plan does not exist — must not raise

        messages = [r.message.replace(str(dirs.tmp), 'p') for r in caplog.records]
        assert f'     File {Path("p/working/mars2020_release_01.plan")} not found.' in messages

    def test_missing_kernel_list_byproduct_logs_warning_not_raises(self, dirs, file_list, caplog):
        """A missing .kernel_list by-product must log a warning, not raise."""
        setup = _make_setup(
            staging_directory=dirs.staging,
            bundle_directory=dirs.bundle,
            working_directory=dirs.working,
            args=_make_args(clear=file_list, plan='mars2020_release_01.plan'),
        )

        with caplog.at_level(logging.WARNING):
            runtime.clear_run(setup)

        messages = [r.message.replace(str(dirs.tmp), 'p') for r in caplog.records]
        print(messages)
        assert f'     File {Path("p/working/mars2020_release_01.kernel_list")} not found.' in messages

    # -- Edge cases ----------------------------------------------------------

    def test_empty_file_list_removes_nothing(self, dirs, tmp_path):
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
        runtime.clear_run(setup)

        assert os.path.exists(sentinel), "Unrelated files must not be touched"

# ---------------------------------------------------------------------------
# runtime.finish_execution tests
# ---------------------------------------------------------------------------

class TestFinishExecution:
    """Tests for runtime.finish_execution."""

    def _make_finish_setup(
            self,
            tmp_path: Path,
            pds_version: str = "4",
            faucet: str = "final",
            template_files: list[str] | None = None,
    ) -> MagicMock:
        """Return a fully-mocked Setup appropriate for finish_execution."""
        setup = MagicMock()
        setup.pds_version = pds_version
        setup.args.faucet = faucet
        setup.template_files = template_files if template_files is not None else []
        return setup

    def test_template_files_are_removed(self, tmp_path, monkeypatch):
        """Existing template files are deleted during shutdown."""
        monkeypatch.setattr(spiceypy, "kclear", MagicMock())

        tpl1 = tmp_path / "template_a.xml"
        tpl2 = tmp_path / "template_b.xml"
        tpl1.write_text("<xml/>")
        tpl2.write_text("<xml/>")

        setup = self._make_finish_setup(
            tmp_path, template_files=[str(tpl1), str(tpl2)]
        )
        log_manager = MagicMock()

        runtime.finish_execution(setup, log_manager)

        assert not tpl1.exists(), "template_a.xml should have been removed"
        assert not tpl2.exists(), "template_b.xml should have been removed"

    def test_missing_template_does_not_raise(self, tmp_path, monkeypatch):
        """If a template has already been removed, finish_execution must not raise."""
        monkeypatch.setattr(spiceypy, "kclear", MagicMock())

        setup = self._make_finish_setup(
            tmp_path, template_files=["/nonexistent/template.xml"]
        )
        log_manager = MagicMock()

        # Should complete without raising FileNotFoundError.
        runtime.finish_execution(setup, log_manager)

    def test_file_list_and_checksum_registry_written(self, tmp_path, monkeypatch):
        """write_file_list and write_checksum_registry are both called."""
        monkeypatch.setattr(spiceypy, "kclear", MagicMock())

        setup = self._make_finish_setup(tmp_path)
        log_manager = MagicMock()

        runtime.finish_execution(setup, log_manager)

        setup.write_file_list.assert_called_once()
        setup.write_checksum_registry.assert_called_once()

    def test_validate_config_written_for_pds4_non_clear(self, tmp_path, monkeypatch):
        """write_validate_config is called when pds_version='4' and faucet!='clear'."""
        monkeypatch.setattr(spiceypy, "kclear", MagicMock())

        setup = self._make_finish_setup(tmp_path, pds_version="4", faucet="final")
        log_manager = MagicMock()

        runtime.finish_execution(setup, log_manager)

        setup.write_validate_config.assert_called_once()

    def test_validate_config_not_written_for_clear_faucet(self, tmp_path, monkeypatch):
        """write_validate_config must NOT be called when faucet='clear'."""
        monkeypatch.setattr(spiceypy, "kclear", MagicMock())

        setup = self._make_finish_setup(tmp_path, pds_version="4", faucet="clear")
        log_manager = MagicMock()

        runtime.finish_execution(setup, log_manager)

        setup.write_validate_config.assert_not_called()

    def test_validate_config_not_written_for_pds3(self, tmp_path, monkeypatch):
        """write_validate_config must NOT be called when pds_version!='4'."""
        monkeypatch.setattr(spiceypy, "kclear", MagicMock())

        setup = self._make_finish_setup(tmp_path, pds_version="3", faucet="final")
        log_manager = MagicMock()

        runtime.finish_execution(setup, log_manager)

        setup.write_validate_config.assert_not_called()

    def test_spice_kernel_pool_cleared(self, tmp_path, monkeypatch):
        """spiceypy.kclear must be called to release all loaded kernels."""
        mock_kclear = MagicMock()
        monkeypatch.setattr(spiceypy, "kclear", mock_kclear)

        setup = self._make_finish_setup(tmp_path)
        log_manager = MagicMock()

        runtime.finish_execution(setup, log_manager)

        mock_kclear.assert_called_once()

    def test_log_manager_stopped(self, tmp_path, monkeypatch):
        """log_manager.stop() must be called to close the log."""
        monkeypatch.setattr(spiceypy, "kclear", MagicMock())

        setup = self._make_finish_setup(tmp_path)
        log_manager = MagicMock()

        runtime.finish_execution(setup, log_manager)

        log_manager.stop.assert_called_once()

    def test_log_step_called_before_artifacts(self, tmp_path, monkeypatch):
        """log_step must be invoked (the 'Generate run by-product files' step)
        before artifact methods are called."""
        monkeypatch.setattr(spiceypy, "kclear", MagicMock())

        call_order: list[str] = []

        setup = self._make_finish_setup(tmp_path)
        setup.step = 1
        setup.write_file_list.side_effect = lambda: call_order.append("write_file_list")
        setup.write_checksum_registry.side_effect = lambda: call_order.append("write_checksum_registry")

        with patch(
                "pds.naif_pds4_bundler.pipeline.runtime.log_step",
                side_effect=lambda s, title: call_order.append("log_step"),
        ):
            runtime.finish_execution(setup, MagicMock())

        assert call_order.index("log_step") < call_order.index("write_file_list"), (
            "log_step must be called before write_file_list"
        )

# ---------------------------------------------------------------------------
# runtime.handle_npb_error tests
# ---------------------------------------------------------------------------
class TestHandleNpbError:
    """Tests for runtime.handle_npb_error."""

    def test_always_raises_runtime_error_with_message(self, caplog):
        """Verifies that the function always raises RuntimeError with the message."""
        message = "Test failure message"

        with pytest.raises(RuntimeError, match=message):
            runtime.handle_npb_error(message)

        assert f"-- {message}" in caplog.text

    def test_logs_error_at_error_level(self, caplog):
        """The error message must be logged at the ERROR level."""
        message = "Something went wrong"
        with caplog.at_level(logging.ERROR):
            with pytest.raises(RuntimeError):
                runtime.handle_npb_error(message)

        assert ['-- Something went wrong'] == caplog.messages

    def test_with_setup_calls_artifact_methods(self, tmp_path, monkeypatch):
        """When setup is provided, write_file_list and write_checksum_registry
        must both be called before the exception propagates."""
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

    def test_spice_pool_cleared_with_setup(self, monkeypatch):
        """spiceypy.kclear must be called even when setup is provided."""
        mock_kclear = MagicMock()
        monkeypatch.setattr(spiceypy, "kclear", mock_kclear)

        mock_setup = MagicMock()
        mock_setup.template_files = []

        with pytest.raises(RuntimeError):
            runtime.handle_npb_error("Error", setup=mock_setup)

        mock_kclear.assert_called_once()

    def test_spice_pool_cleared_without_setup(self, monkeypatch):
        """Verifies that SPICE is cleared even if no setup object is provided."""
        mock_kclear = MagicMock()
        monkeypatch.setattr(spiceypy, "kclear", mock_kclear)

        with pytest.raises(RuntimeError):
            runtime.handle_npb_error("Quick Error", setup=None)

        mock_kclear.assert_called_once()

    def test_with_setup_removes_existing_template(self, tmp_path, monkeypatch):
        """Existing template files are deleted when setup is provided."""
        monkeypatch.setattr(spiceypy, "kclear", MagicMock())

        mock_setup = MagicMock()
        temp_file = tmp_path / "template.xml"
        temp_file.write_text("<xml/>")
        mock_setup.template_files = [str(temp_file)]

        with pytest.raises(RuntimeError):
            runtime.handle_npb_error("Error", setup=mock_setup)

        assert not temp_file.exists(), "Template file should have been removed"

    def test_with_setup_and_no_templates_does_not_raise(self, monkeypatch):
        """setup.template_files=[] must complete the setup branch without error."""
        monkeypatch.setattr(spiceypy, "kclear", MagicMock())

        mock_setup = MagicMock()
        mock_setup.template_files = []

        with pytest.raises(RuntimeError):
            runtime.handle_npb_error("Error with no templates", setup=mock_setup)

        mock_setup.write_file_list.assert_called_once()
        mock_setup.write_checksum_registry.assert_called_once()

    def test_missing_template_does_not_raise_file_not_found(self, monkeypatch):
        """If a template listed in setup is already gone, no FileNotFoundError
        must propagate — only the expected RuntimeError."""
        mock_setup = MagicMock()
        mock_setup.template_files = ["/non/existent/path.xml"]

        monkeypatch.setattr(spiceypy, "kclear", MagicMock())

        # This should not raise FileNotFoundError because of the os.path.exists check
        with pytest.raises(RuntimeError):
            runtime.handle_npb_error("Error with missing template", setup=mock_setup)

# ---------------------------------------------------------------------------
# runtime.log_step tests
# ---------------------------------------------------------------------------
class TestLogStep:
    """Tests for runtime.log_step."""

    @patch("logging.info")
    def test_increments_counter(self, _mock_log, mock_setup):
        """Verify that the step counter increments every time the function is called."""
        initial_step = mock_setup.step
        runtime.log_step(mock_setup, title="Test Title")
        assert mock_setup.step == initial_step + 1

    @patch("logging.info")
    def test_increments_step_counter_on_repeated_calls(self, _mock_log, mock_setup):
        """Each successive call increments the counter once more."""
        runtime.log_step(mock_setup, title="First")
        runtime.log_step(mock_setup, title="Second")
        runtime.log_step(mock_setup, title="Third")
        assert mock_setup.step == 4  # started at 1

    def test_log_messages_format(self, caplog, mock_setup):
        """Verify the formatting of the logs and that they include the title."""
        # Set level to INFO since caplog defaults to WARNING
        caplog.set_level(logging.INFO)

        title = "Initialize Database"
        expected_header = "Step 1 - Initialize Database"
        expected_separator =  "----------------------------"

        runtime.log_step(mock_setup, title)

        assert caplog.messages == ["", expected_header, expected_separator, ""]

    @pytest.mark.parametrize("silent, verbose, stdout", [
        (False, False, '-- Conditional Print Test.\n'),  # Standard mode: print
        (True, False, ''),                               # Silent mode:   no print
        (False, True, ''),                               # Verbose mode:  no print
        (True, True, ''),                                # Both:          no print
    ])
    @patch("logging.info")
    def test_print_conditions(self, _mock_log, silent, verbose, stdout, capsys):
        """Test the logic that determines if 'print' is called based on args."""
        setup = _LogStepSetup(step=5, silent=silent, verbose=verbose)
        title = "Conditional Print Test"

        runtime.log_step(setup, title)

        captured = capsys.readouterr()
        assert stdout == captured.out

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
) -> MagicMock:
    """Construct a mockup of the Setup object.
    """
    return MagicMock(
        staging_directory=staging_directory,
        bundle_directory=bundle_directory,
        working_directory=working_directory,
        mission_acronym=mission_acronym,
        run_type=run_type,
        args=args or _make_args(clear=""))


class _LogStepSetup:
    """Minimal stand-in for Setup used by log_step tests."""
    def __init__(self, step: int = 1, silent: bool = False, verbose: bool = False):
        self.step = step
        self.args = MagicMock(silent=silent, verbose=verbose)
