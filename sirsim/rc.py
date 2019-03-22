r"""Certain features of Sirsim can be configured globally through RC settings.

RC settings can be manipulated either through the ``sirsim.rc`` object,
or through RC configuration files.

The ``sirsim.rc`` object
=======================

The ``sirsim.rc`` object gives programmatic access to
globally configured features of Sirsim.

.. autodata:: sirsim.rc

Configuration files
===================

``sirsim.rc`` is initialized with configuration settings read
from the following files with precedence to those listed first:

1. ``sirsimrc`` in the current directory. This is intended to allow for project
   specific settings without hard coding them in the model script.

2. An operating system specific file in the user's home directory.

   * Windows: ``%userprofile%\.sirsim\sirsimrc``

   * Other (OS X, Linux): ``~/.config/sirsim/sirsimrc``

3. ``INSTALL/sirsim-data/sirsimrc`` (where ``INSTALL`` is the
   installation directory of the Sirsim package).

The RC file is divided into sections by lines containing the section name
in brackets, i.e. ``[section]``. A setting is set by giving the name followed
by a ``:`` or ``=`` and the value. All lines starting with ``#`` or ``;`` are
comments.

For example, to set the size of the decoder cache to 512 MB,
add the following to a configuration file:

.. code-block:: ini

   [decoder_cache]
   size = 512 MB

Configuration options
=====================

All of the configuration options are listed in the example
configuration file, which is included with Sirsim
and copied below.

Commented lines show the default values for each setting.

.. _sirsimrc:

.. include:: ../sirsim-data/sirsimrc
   :literal:
   :start-line: 29

"""

import logging

import sirsim.utils.paths
from sirsim.utils.compat import configparser

logger = logging.getLogger(__name__)

# The default core Sirsim RC settings. Access with
#   sirsim.RC_DEFAULTS[section_name][option_name]
RC_DEFAULTS = {
    'decoder_cache': {
        'enabled': True,
        'readonly': False,
        'size': '512 MB',
        'path': sirsim.utils.paths.decoder_cache_dir,
    },
    'progress': {
        'updater': 'auto',  # Deprecated
        'progress_bar': 'auto',
    },
    'exceptions': {
        'simplified': True,
    },
}

# The RC files in the order in which they will be read.
RC_FILES = [sirsim.utils.paths.sirsimrc['system'],
            sirsim.utils.paths.sirsimrc['user'],
            sirsim.utils.paths.sirsimrc['project']]


class _RC(configparser.SafeConfigParser):
    """Allows reading from and writing to Sirsim RC settings.

    This object is a :class:`configparser.ConfigParser`, which means that
    values can be accessed and manipulated with ``get`` and ``set``::

        oldsize = sirsim.rc.get("decoder_cache", "size")
        sirsim.rc.set("decoder_cache", "size", "2 GB")

    ``get`` and ``set`` return and expect strings. There are also special
    getter methods for booleans, ints, and floats::

        simple = sirsim.rc.getboolean("exceptions", "simplified")

    In addition to the normal :class:`configparser.ConfigParser` methods,
    this object also has a ``reload_rc`` method to reset ``sirsim.rc``
    to default settings::

        sirsim.rc.reload_rc()  # Reads defaults from configuration files
        sirsim.rc.reload_rc(filenames=[])  # Ignores configuration files

    """

    def __init__(self):
        # configparser uses old-style classes without 'super' support
        configparser.SafeConfigParser.__init__(self)
        self.reload_rc()

    def _clear(self):
        self.remove_section(configparser.DEFAULTSECT)
        for s in self.sections():
            self.remove_section(s)

    def _init_defaults(self):
        for section, settings in RC_DEFAULTS.items():
            self.add_section(section)
            for k, v in settings.items():
                self.set(section, k, str(v))

    def read_file(self, fp, filename=None):
        if filename is None:
            if hasattr(fp, 'name'):
                filename = fp.name
            else:
                filename = '<???>'
        logger.info('Reading configuration from {}'.format(filename))
        try:
            return configparser.SafeConfigParser.read_file(self, fp, filename)
        except AttributeError:
            # pylint: disable=deprecated-method
            return configparser.SafeConfigParser.readfp(self, fp, filename)

    def read(self, filenames):
        logger.info('Reading configuration files {}'.format(filenames))
        return configparser.SafeConfigParser.read(self, filenames)

    def reload_rc(self, filenames=None):
        """Resets the currently loaded RC settings and loads new RC files.

        Parameters
        ----------
        filenames: iterable object
            Filenames of RC files to load.
        """
        if filenames is None:
            filenames = RC_FILES

        self._clear()
        self._init_defaults()
        self.read(filenames)


rc = _RC()
