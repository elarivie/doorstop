"""Shared functions for the `doorstop.cli` package."""

import os
import ast
from argparse import ArgumentTypeError
import logging

from doorstop import common
from doorstop import settings

log = common.logger(__name__)


class capture(object):  # pylint: disable=R0903

    """Context manager to catch :class:`~doorstop.common.DoorstopError`."""

    def __init__(self, catch=True):
        self.catch = catch
        self._success = True

    def __bool__(self):
        return self._success

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type and issubclass(exc_type, common.DoorstopError):
            self._success = False
            if self.catch:
                log.error(exc_value)
                return True


def configure_logging(verbosity=0):
    """Configure logging using the provided verbosity level (0+)."""
    assert common.PRINT_VERBOSITY == 0
    assert common.STR_VERBOSITY == 3
    assert common.MAX_VERBOSITY == 4

    # Configure the logging level and format
    if verbosity == -1:
        level = settings.QUIET_LOGGING_LEVEL
        default_format = settings.DEFAULT_LOGGING_FORMAT
        verbose_format = settings.LEVELED_LOGGING_FORMAT
    elif verbosity == 0:
        level = settings.DEFAULT_LOGGING_LEVEL
        default_format = settings.DEFAULT_LOGGING_FORMAT
        verbose_format = settings.LEVELED_LOGGING_FORMAT
    elif verbosity == 1:
        level = settings.VERBOSE_LOGGING_LEVEL
        default_format = settings.DEFAULT_LOGGING_FORMAT
        verbose_format = settings.LEVELED_LOGGING_FORMAT
    elif verbosity == 2:
        level = settings.VERBOSE2_LOGGING_LEVEL
        default_format = verbose_format = settings.VERBOSE_LOGGING_FORMAT
    elif verbosity == 3:
        level = settings.VERBOSE3_LOGGING_LEVEL
        default_format = verbose_format = settings.VERBOSE_LOGGING_FORMAT
    else:
        level = settings.VERBOSE3_LOGGING_LEVEL
        default_format = verbose_format = settings.VERBOSE2_LOGGING_FORMAT

    # Set a custom formatter
    if not logging.root.handlers:  # pragma: no cover (manual test)
        logging.basicConfig(level=level)
        formatter = common.WarningFormatter(default_format, verbose_format)
        logging.root.handlers[0].setFormatter(formatter)

    # Warn about excessive verbosity
    if verbosity > common.MAX_VERBOSITY:
        msg = "maximum verbosity level is {}".format(common.MAX_VERBOSITY)
        logging.warn(msg)
        common.verbosity = common.MAX_VERBOSITY
    else:
        common.verbosity = verbosity


def configure_settings(args):
    """Update settings based on the command-line options."""
    # Parse common settings
    if args.no_reformat is not None:
        settings.REFORMAT = not args.no_reformat
    if args.reorder is not None:
        settings.REORDER = args.reorder
    if args.no_level_check is not None:
        settings.CHECK_LEVELS = not args.no_level_check
    if args.no_ref_check is not None:
        settings.CHECK_REF = not args.no_ref_check
    if args.no_child_check is not None:
        settings.CHECK_CHILD_LINKS = not args.no_child_check
    if args.no_suspect_check is not None:
        settings.CHECK_SUSPECT_LINKS = not args.no_suspect_check
    if args.no_review_check is not None:
        settings.CHECK_REVIEW_STATUS = not args.no_review_check
    if args.server is not None:
        settings.SERVER_HOST = args.server
    # Parse subcommand settings
    if hasattr(args, 'no_child_links') and args.no_child_links is not None:
        settings.PUBLISH_CHILD_LINKS = not args.no_child_links
    if hasattr(args, 'no_body_levels') and args.no_body_levels is not None:
        settings.PUBLISH_BODY_LEVELS = not args.no_body_levels


def literal_eval(literal, err=None, default=None):
    """Convert an literal to its value.

    :param literal: string to evaulate
    :param err: function to call for errors
    :param default: default value for empty inputs
    :return: Python literal

    >>> literal_eval("False")
    False

    >>> literal_eval("[1, 2, 3]")
    [1, 2, 3]

    """
    try:
        return ast.literal_eval(literal) if literal else default
    except (SyntaxError, ValueError):
        msg = "invalid Python literal: {}".format(literal)
        if err:
            err(msg)
        else:
            log.critical(msg)


def get_ext(args, ext_stdout, ext_file, whole_tree, err):
    """Determine the output file extensions from input arguments.

    :param args: Namespace of CLI arguments
    :param ext_stdout: default extension for standard output
    :param ext_file: default extension for file output
    :param whole_tree: indicates the path is a directory for the whole tree
    :param err: function to call for CLI errors

    :return: chosen extension

    """
    path = args.path if hasattr(args, 'path') else None
    ext = None

    # Get the default argument from a provided output path
    if path:
        if whole_tree:
            ext = ext_file
        else:
            if os.path.isdir(path):
                err("given a prefix, [path] must be a file, not a directory")
            ext = os.path.splitext(path)[-1]
        log.debug("extension based on path: {}".format(ext or None))

    # Override the extension if a format is specified
    for _ext, option in {'.txt': 'text',
                         '.md': 'markdown',
                         '.html': 'html',
                         '.yml': 'yaml',
                         '.csv': 'csv',
                         '.xlsx': 'xlsx'}.items():
        try:
            if getattr(args, option):
                ext = _ext
                log.debug("extension based on override: {}".format(ext))
                break
        except AttributeError:
            continue
    else:
        if not ext:
            if path:
                err("given a prefix, [path] must include an extension")
            else:
                ext = ext_stdout
            log.debug("extension based on default: {}".format(ext))

    return ext


def show(message, flush=False):
    """Print (optionally flushed) text to the display."""
    if common.verbosity >= common.PRINT_VERBOSITY:
        print(message, flush=flush)


def ask(question, default=None):
    """Display a console yes/no prompt.

    :param question: text of yes/no question ending in '?'
    :param default: 'yes', 'no', or None (for no default)

    :return: True = 'yes', False = 'no'

    """
    valid = {"yes": True,
             "y": True,
             "no": False,
             "n": False}
    prompts = {'yes': " [Y/n] ",
               'no': " [y/N] ",
               None: " [y/n] "}

    prompt = prompts.get(default, prompts[None])
    message = question + prompt

    while True:
        try:
            choice = input(message).lower().strip() or default
        except KeyboardInterrupt as exc:
            print()
            raise exc from None
        try:
            return valid[choice]
        except KeyError:
            options = ', '.join(sorted(valid.keys()))
            print("valid responses: {}".format(options))


def positive_int(value):
    """Evaluate a value as positive.

    :param value: passed in value to Evaluate

    :return: value casted to an integer

    """
    exc = ArgumentTypeError("'{}' is not a positive int value".format(value))
    try:
        ival = int(value)
    except ValueError:
        raise exc from None
    else:
        if ival < 1:
            raise exc
        return ival
