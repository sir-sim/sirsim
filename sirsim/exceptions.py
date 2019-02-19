import inspect


class SirsimException(Exception):
    """Base class for Sirsim exceptions.

    SirsimException instances should not be created; this base class exists so
    that all exceptions raised by Sirsim can be caught in a try / except block.
    """


class SirsimWarning(Warning):
    """Base class for Sirsim warnings."""


class ValidationError(SirsimException, ValueError):
    """A ValueError encountered during validation of a parameter."""

    def __init__(self, msg, attr, obj=None):
        self.attr = attr
        self.obj = obj
        super(ValidationError, self).__init__(msg)

    def __str__(self):
        if self.obj is None:
            return "{}: {}".format(
                self.attr, super(ValidationError, self).__str__())
        klassname = (self.obj.__name__ if inspect.isclass(self.obj)
                     else type(self.obj).__name__)
        return "{}.{}: {}".format(
            klassname, self.attr, super(ValidationError, self).__str__())


class ReadonlyError(ValidationError):
    """A ValidationError occurring because a parameter is read-only."""

    def __init__(self, attr, obj=None, msg=None):
        if msg is None:
            msg = "%s is read-only and cannot be changed" % attr
        super(ReadonlyError, self).__init__(msg, attr, obj)


class BuildError(SirsimException, ValueError):
    """A ValueError encountered during the build process."""


class ObsoleteError(SirsimException):
    """A feature that has been removed in a backwards-incompatible way."""

    def __init__(self, msg, since=None, url=None):
        self.since = since
        self.url = url
        super(ObsoleteError, self).__init__(msg)

    def __str__(self):
        return "Obsolete%s: %s%s" % (
            "" if self.since is None else " since %s" % self.since,
            super(ObsoleteError, self).__str__(),
            "\nFor more information, please visit %s" % self.url
            if self.url is not None else "")


class ConfigError(SirsimException, ValueError):
    """A ValueError encountered in the config system."""


class SpaModuleError(SirsimException, ValueError):
    """An error in how SPA keeps track of modules."""


class SpaParseError(SirsimException, ValueError):
    """An error encountered while parsing a SPA expression."""


class SimulatorClosed(SirsimException):
    """Raised when attempting to run a closed simulator."""


class SimulationError(SirsimException, RuntimeError):
    """An error encountered during simulation of the model."""


class SignalError(SirsimException, ValueError):
    """An error dealing with Signals in the builder."""


class FingerprintError(SirsimException, ValueError):
    """An error in fingerprinting an object for cache identification."""


class NetworkContextError(SirsimException, RuntimeError):
    """An error with the Network context stack."""


class Unconvertible(SirsimException, ValueError):
    """Raised a requested network conversion cannot be done."""


class CacheIOError(SirsimException, IOError):
    """An IO error in reading from or writing to the decoder cache."""


class TimeoutError(SirsimException):
    """A timeout occurred while waiting for a resource."""


class NotAddedToNetworkWarning(SirsimWarning):
    """A SirsimObject has not been added to a network."""

    def __init__(self, obj):
        self.obj = obj
        super(NotAddedToNetworkWarning, self).__init__()

    def __str__(self):
        return (
            "{obj} was not added to the network. When copying objects, "
            "use the copy method on the object instead of Python's copy "
            "module. When unpickling objects, they have to be added to "
            "networks manually.".format(obj=self.obj))


class CacheIOWarning(SirsimWarning):
    """A non-critical issue in accessing files in the cache."""
