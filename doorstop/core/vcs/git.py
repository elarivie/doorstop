"""Plug-in module to store requirements in a Git repository."""

from doorstop import common
from doorstop.core.vcs.base import BaseWorkingCopy

log = common.logger(__name__)


class WorkingCopy(BaseWorkingCopy):

    """Git working copy."""

    DIRECTORY = '.git'
    IGNORES = ('.gitignore',)

    def lock(self, path):
        log.info("git does not support locking: {}".format(path))
        self.call('git', 'pull')

    def save(self, message=None):
        message = message or input("Commit message: ")  # pylint: disable=W0141
        self.call('git', 'commit', '--all', '--message', message)
        self.call('git', 'push')
