"""Unit tests for the doorstop.vcs plugin modules."""

import unittest
from unittest.mock import patch, Mock, call

from doorstop.core.vcs import load


class BaseTestCase(unittest.TestCase):  # pylint: disable=R0904

    """Base TestCase for tests that need a working copy."""

    DIRECTORY = None

    path = "path/to/mock/file.txt"
    dirpath = "path/to/mock/directory/"
    message = "A commit message"

    def setUp(self):
        with patch('os.listdir', Mock(return_value=[self.DIRECTORY])):
            self.wc = load(None)

    def lock(self):
        """Lock a file in the working copy."""
        self.wc.lock(self.path)

    def save(self):
        """Save all files in the working copy."""
        self.wc.save(self.message)


@patch('subprocess.call')  # pylint: disable=R0904
class TestGit(BaseTestCase):

    """Tests for the Git plugin."""

    DIRECTORY = '.git'

    def test_lock(self, mock_call):
        """Verify Git can (fake) lock files."""
        self.lock()
        calls = [call(("git", "pull"))]
        mock_call.assert_has_calls(calls)

    def test_save(self, mock_call):
        """Verify Git can save files."""
        self.save()
        calls = [call(("git", "commit", "--all", "--message", self.message)),
                 call(("git", "push"))]
        mock_call.assert_has_calls(calls)


@patch('subprocess.call')  # pylint: disable=R0904
class TestMockVCS(BaseTestCase):

    """Tests for the placeholder VCS plugin."""

    DIRECTORY = '.mockvcs'

    def test_lock(self, mock_call):
        """Verify the placeholder VCS does not lock files."""
        self.lock()
        calls = []
        mock_call.assert_has_calls(calls)

    def test_save(self, mock_call):
        """Verify the placeholder VCS does not  save files."""
        self.save()
        calls = []
        mock_call.assert_has_calls(calls)


@patch('subprocess.call')  # pylint: disable=R0904
class TestSubversion(BaseTestCase):

    """Tests for the Subversion plugin."""

    DIRECTORY = '.svn'

    def test_lock(self, mock_call):
        """Verify Subversion can lock files."""
        self.lock()
        calls = [call(("svn", "update")),
                 call(("svn", "lock", self.path))]
        mock_call.assert_has_calls(calls)

    def test_save(self, mock_call):
        """Verify Subversion can save files."""
        self.save()
        calls = [call(("svn", "commit", "--message", self.message))]
        mock_call.assert_has_calls(calls)


@patch('subprocess.call')  # pylint: disable=R0904
class TestVeracity(BaseTestCase):

    """Tests for the Veracity plugin."""

    DIRECTORY = '.sgdrawer'

    def test_lock(self, mock_call):
        """Verify Veracity can lock files."""
        self.lock()
        calls = [call(("vv", "pull")),
                 call(("vv", "update"))]
        mock_call.assert_has_calls(calls)

    def test_save(self, mock_call):
        """Verify Veracity can save files."""
        self.save()
        calls = [call(("vv", "commit", "--message", self.message)),
                 call(("vv", "push"))]
        mock_call.assert_has_calls(calls)
