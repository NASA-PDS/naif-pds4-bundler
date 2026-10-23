"""Integration tests for the KernelList class.

The private helpers of KernelList (``_fill_template``, ``_check_consecutive``,
``_check_badchar``, ``_check_kernel_integrity``, ``_check_binary_endianness``
and ``_check_permissions``) are not mocked here: they run as they are, against
real kernels copied into a sandbox and real list files written to it.
"""
import logging
import os
from pathlib import Path

import pytest

from pds.naif_pds4_bundler.classes.exceptions import NPBError
from pds.naif_pds4_bundler.classes.list import KernelList
from pds.naif_pds4_bundler.classes.setup import Setup

pytestmark = pytest.mark.integration

# Message of the NPBError raised when any product has errors.
CHECK_FATAL_MESSAGE = 'Products listed above require work.'

# Message logged when all the products pass every check.
CHECK_SUCCESS_MESSAGE = '-- All products checks have succeeded.'

# Kernels that match the kernel list patterns of the configuration.
TEXT_KERNEL = 'lsk/naif0012.tls'
BINARY_KERNEL = 'spk/maven_orb_rec_210101_210401_v2.bsp'


def messages(caplog: pytest.LogCaptureFixture, level: int) -> list[str]:
    """Return the messages logged at ``level`` or above."""
    return [record.getMessage() for record in caplog.records
            if record.levelno >= level]


def write_release_list(real_setup: Setup, kernel_list: KernelList,
                       release: int, kernel: str) -> Path:
    """Write the kernel list of a release that contains a single kernel."""
    real_setup.release = f'{release:03d}'
    kernel_list.kernel_list = [kernel]
    kernel_list.write_list()

    return Path(real_setup.working_directory) / kernel_list.list_name


class TestKernelListWriteList:
    """Tests for ``write_list`` through the real ``_fill_template``."""

    def test_write_list_fills_the_template(
            self, kernel_list, install_kernel, sandbox) -> None:
        """A list with one text kernel is written from the real template.

        The header takes its values from the configuration and the kernel
        entry takes its description from the matching kernel list pattern.
        """
        # Put a real LSK in the kernels directory and add it to the list.
        install_kernel(TEXT_KERNEL)
        kernel_list.kernel_list = ['naif0012.tls']

        # Write the list file in the working directory.
        kernel_list.write_list()

        # The first line is the current date, so it is left out; the rest of
        # the file does not change between runs.
        lines = (sandbox.working / kernel_list.list_name
                 ).read_text(encoding='utf-8').splitlines()
        assert lines[1:] == [
            'SPACECRAFT = MAVEN',
            'NAIFER = Marc Costa Sitja',
            'DATASETID = N/A',
            'VOLUMEID = N/A',
            'RELEASE_ID = 0001',
            'RELEASE_DATE = 2021-06-25',
            '$EOH',
            'FILE             = spice_kernels/lsk/naif0012.tls',
            'MAKLABEL_OPTIONS =',
            'DESCRIPTION      = SPICE LSK file incorporating leapseconds up '
            'to 2017-JAN-01, created by NAIF, JPL.']

    def test_write_list_without_template_raises(
            self, kernel_list, install_kernel) -> None:
        """Writing the list without its template raises FileNotFoundError."""
        # Add a kernel to the list, then remove the template file.
        install_kernel(TEXT_KERNEL)
        kernel_list.kernel_list = ['naif0012.tls']
        Path(kernel_list.template).unlink()

        # The template is the first thing write_list needs to read.
        with pytest.raises(FileNotFoundError):
            kernel_list.write_list()


class TestKernelListValidate:
    """Tests for ``validate`` on a list written by ``write_list``."""

    @pytest.mark.parametrize('appended, expected_errors', [
        # A clean list does not log any error.
        ('', []),
        # The written list has 11 lines, so the appended one is the 12th.
        ('NOTE = café\n', ['   NON-ASCII character(s) in line 12:',
                           '   NOTE = café',
                           '             ^'])])
    def test_validate_reports_badchar_in_list_and_continues(
            self, caplog, kernel_list, install_kernel, sandbox, appended,
            expected_errors) -> None:
        """Non-ASCII characters in a list are logged as errors, not raised.

        A clean list logs no error. A list with a non-ASCII line logs the
        line, with a marker under the character, and validate still runs
        its remaining checks.
        """
        # Write a valid list, then add the line to be checked at the end.
        install_kernel(TEXT_KERNEL)
        kernel_list.kernel_list = ['naif0012.tls']
        kernel_list.write_list()
        with open(sandbox.working / kernel_list.list_name, 'a',
                  encoding='utf-8') as f:
            f.write(appended)

        # Validate the list again, now with the extra line.
        with caplog.at_level(logging.INFO):
            kernel_list.validate()

        # Only the bad character is logged as an error. The 'All kernels
        # present' message comes from a check that runs after it.
        assert messages(caplog, logging.ERROR) == expected_errors
        assert '     All kernels present.' in messages(caplog, logging.INFO)


class TestKernelListWriteCompleteList:
    """Tests for ``write_complete_list`` and the consecutive releases."""

    @pytest.mark.parametrize('releases, expected', [
        ([1, 2], []),
        ([1, 3], ['-- Incomplete Kernel lists available: [3, 1]'])])
    def test_write_complete_list_release_enumeration(
            self, caplog, real_setup, kernel_list, install_kernel,
            releases, expected) -> None:
        """Gaps between the release lists are warned about, not raised.

        Releases 1 and 2 are consecutive and log nothing. Releases 1 and 3
        miss release 2, so the incomplete enumeration is logged as a warning.
        """
        # Write one list per release. Each one has a different kernel,
        # otherwise the complete list is rejected because of duplicates.
        kernels = [('lsk/naif0012.tls', 'naif0012.tls'),
                   ('pck/pck00010.tpc', 'pck00010.tpc')]
        for release, (path, name) in zip(releases, kernels):
            install_kernel(path)
            write_release_list(real_setup, kernel_list, release, name)

        # Merge the release lists into the complete list.
        with caplog.at_level(logging.INFO):
            kernel_list.write_complete_list()

        # Other warnings may be logged, only the enumeration one matters.
        incomplete = [message for message in messages(caplog, logging.WARNING)
                      if message.startswith('-- Incomplete')]
        assert incomplete == expected

    def test_write_complete_list_without_release_lists_raises(
            self, kernel_list) -> None:
        """Without any release list there is nothing to merge: NPBError."""
        # The working directory is empty, so no release list exists.
        with pytest.raises(NPBError,
                           match='-- No release kernel lists available.'):
            kernel_list.write_complete_list()


class TestKernelListCheckProducts:
    """Tests for ``check_products`` with the real checks."""

    @pytest.mark.parametrize('kernel', [
        TEXT_KERNEL, 'pck/pck00010.tpc', BINARY_KERNEL])
    def test_check_products_valid_kernel_succeeds(
            self, caplog, kernel_list, install_kernel, kernel) -> None:
        """Valid text and binary kernels pass every check without warnings."""
        # Copy a real kernel to the kernels directory and add it to the list.
        installed = install_kernel(kernel)
        kernel_list.kernel_list = [installed.name]

        # Run all the checks on it.
        with caplog.at_level(logging.INFO):
            kernel_list.check_products()

        # The success message is the last thing logged, followed by a blank
        # line.
        assert messages(caplog, logging.INFO)[-2:] == [
            CHECK_SUCCESS_MESSAGE, '']

    @pytest.mark.parametrize('kernel, name, expected', [
        # Integrity: a CK copied under the extension of an SPK.
        ('ck/insight_ida_enc_200829_201220_v1.bc',
         'insight_ida_enc_200829_201220_v1.bsp',
         '     Kernel insight_ida_enc_200829_201220_v1.bsp type SPK is not '
         'the one expected: CK.'),
        # Endianness: a big endian SPK, the archive requires little endian.
        ('spk/mro_psp60.big.bsp', 'mro_psp60.bsp',
         "     The kernel cannot be loaded because of its endianness. Use "
         "NAIF's utility BINGO to convert the file.")])
    def test_check_products_invalid_binary_kernel_is_fatal(
            self, caplog, kernel_list, install_kernel, kernel, name,
            expected) -> None:
        """A binary kernel with a wrong type or endianness is an error.

        The error is logged and check_products raises NPBError. The type of
        the kernel is read from its extension, so a CK with a 'bsp' extension
        fails the integrity check. A big endian SPK fails the endianness
        check.
        """
        # Copy the kernel to the kernels directory under the name that makes
        # it invalid, and add it to the list.
        install_kernel(kernel, name)
        kernel_list.kernel_list = [name]

        # Run all the checks, they are expected to stop with an error.
        with caplog.at_level(logging.INFO):
            with pytest.raises(NPBError, match=CHECK_FATAL_MESSAGE):
                kernel_list.check_products()

        # The only error is the one of the failed check, followed by the
        # blank line that closes the report.
        assert messages(caplog, logging.ERROR) == [expected, '']

    def test_check_products_badchar_in_kernel_is_a_warning(
            self, caplog, kernel_list, install_kernel) -> None:
        """A non-ASCII character in a text kernel is a warning, not an error.

        The line with the character is reported, but check_products does not
        raise.
        """
        # Add a non-ASCII line at the end of a copy of the LSK. The line
        # number is that of the new last line. The newline is set so that
        # Windows does not write '\r\n', which the EOL check rejects.
        installed = install_kernel(TEXT_KERNEL)
        with open(installed, 'a', encoding='utf-8', newline='\n') as f:
            f.write('café\n')
        line_number = len(installed.read_text(encoding='utf-8').splitlines())
        kernel_list.kernel_list = [installed.name]

        # Run all the checks on the modified kernel.
        with caplog.at_level(logging.INFO):
            kernel_list.check_products()

        # Nothing is logged as an error, the bad line is only a warning.
        assert messages(caplog, logging.ERROR) == []
        assert (f'     NON-ASCII character(s) in line {line_number}:'
                in messages(caplog, logging.WARNING))

    @pytest.mark.skipif(
        not hasattr(os, 'geteuid') or os.geteuid() == 0,
        reason='File permissions do not apply to root nor to Windows.')
    def test_check_products_unreadable_kernel_raises(
            self, kernel_list, install_kernel) -> None:
        """A kernel the account cannot read stops check_products: NPBError."""
        # Copy a kernel and remove every permission from the copy.
        installed = install_kernel(TEXT_KERNEL)
        installed.chmod(0o000)
        kernel_list.kernel_list = [installed.name]

        # The permission check is the first one to run on the kernel.
        with pytest.raises(NPBError, match='is not readable'):
            kernel_list.check_products()
