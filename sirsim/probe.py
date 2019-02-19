from sirsim.base import SirsimObject, SirsimObjectParam, ObjView
from sirsim.config import Config
from sirsim.connection import Connection, LearningRule
from sirsim.exceptions import ObsoleteError, ValidationError
from sirsim.params import (
    Default, ConnectionDefault, NumberParam, Parameter, StringParam)
from sirsim.solvers import SolverParam
from sirsim.synapses import SynapseParam


class TargetParam(SirsimObjectParam):
    def coerce(self, probe, target):
        obj = target.obj if isinstance(target, ObjView) else target
        if not hasattr(obj, 'probeable'):
            raise ValidationError("Type %r is not probeable"
                                  % type(obj).__name__,
                                  attr=self.name, obj=probe)

        # do this after; better to know that type is not Probable first
        if isinstance(obj, LearningRule):
            # TODO: this special case should be able to be removed with #1310
            return Parameter.coerce(self, probe, target)
        else:
            return super(TargetParam, self).coerce(probe, target)


class AttributeParam(StringParam):
    coerce_defaults = False

    def coerce(self, probe, attr):
        value = super(AttributeParam, self).coerce(probe, attr)
        if attr in ('decoders', 'transform'):
            raise ObsoleteError("'decoders' and 'transform' are now combined "
                                "into 'weights'. Probe 'weights' instead.",
                                since="v2.1.0")
        if attr not in probe.obj.probeable:
            raise ValidationError("Attribute %r is not probeable on %s.\n"
                                  "Probeable attributes: %s"
                                  % (attr, probe.obj, probe.obj.probeable),
                                  attr=self.name, obj=probe)
        return value


class ProbeSolverParam(SolverParam):
    def coerce(self, conn, solver):
        if solver is ConnectionDefault:
            solver = Config.default(Connection, 'solver')
        solver = super(ProbeSolverParam, self).coerce(conn, solver)
        if solver is not None and solver.weights:
            raise ValidationError("weight solvers only work for ensemble to "
                                  "ensemble connections, not probes",
                                  attr=self.name, obj=conn)
        return solver


class Probe(SirsimObject):
    """A probe is an object that collects data from the simulation.

    This is to be used in any situation where you wish to gather simulation
    data (spike data, represented values, agent voltages, etc.) for analysis.

    Probes do not directly affect the simulation.

    All Sirsim objects can be probed (except Probes themselves).
    Each object has different attributes that can be probed.
    To see what is probeable for each object, print its
    ``probeable`` attribute.

    >>> with sirsim.Network():
    ...     ens = sirsim.Ensemble(10, 1)
    >>> print(ens.probeable)
    ['decoded_output', 'input']

    Parameters
    ----------
    target : Ensemble, Agents, Node, or Connection
        The object to probe.

    attr : str, optional (Default: None)
        The signal to probe. Refer to the target's ``probeable`` list for
        details. If None, the first element in the ``probeable`` list
        will be used.
    sample_every : float, optional (Default: None)
        Sampling period in seconds. If None, the ``dt`` of the simluation
        will be used.
    synapse : Synapse, optional (Default: None)
        A synaptic model to filter the probed signal.
    solver : Solver, optional (Default: ``ConnectionDefault``)
        `~sirsim.solvers.Solver` to compute decoders
        for probes that require them.
    label : str, optional (Default: None)
        A name for the probe. Used for debugging and visualization.
    seed : int, optional (Default: None)
        The seed used for random number generation.

    Attributes
    ----------
    attr : str or None
        The signal that will be probed. If None, the first element of the
        target's ``probeable`` list will be used.
    sample_every : float or None
        Sampling period in seconds. If None, the ``dt`` of the simluation
        will be used.
    solver : Solver or None
        `~sirsim.solvers.Solver` to compute decoders. Only used for probes
        of an ensemble's decoded output.
    synapse : Synapse or None
        A synaptic model to filter the probed signal.
    target : Ensemble, Agents, Node, or Connection
        The object to probe.
    """

    target = TargetParam('target', nonzero_size_out=True)
    attr = AttributeParam('attr', default=None, optional=True)
    sample_every = NumberParam(
        'sample_every', default=None, optional=True, low=1e-10)
    synapse = SynapseParam('synapse', default=None, optional=True)
    solver = ProbeSolverParam('solver', default=ConnectionDefault)

    _param_init_order = ['target']

    def __init__(self, target, attr=None, sample_every=Default,
                 synapse=Default, solver=Default, label=Default, seed=Default):
        super(Probe, self).__init__(label=label, seed=seed)
        self.target = target
        self.attr = attr if attr is not None else self.obj.probeable[0]
        self.sample_every = sample_every
        self.synapse = synapse
        self.solver = solver

    def __repr__(self):
        return "<Probe%s at 0x%x of '%s' of %s>" % (
            "" if self.label is None else ' "%s"' % self.label,
            id(self), self.attr, self.target)

    def __str__(self):
        return "<Probe%s of '%s' of %s>" % (
            "" if self.label is None else ' "%s"' % self.label,
            self.attr, self.target)

    @property
    def obj(self):
        """(Sirsim object) The underlying Sirsim object target."""
        return (self.target.obj if isinstance(self.target, ObjView) else
                self.target)

    @property
    def size_in(self):
        """(int) Dimensionality of the probed signal."""
        return self.target.size_out

    @property
    def size_out(self):
        """(int) Cannot connect from probes, so always 0."""
        return 0

    @property
    def slice(self):
        """(slice) The slice associated with the Sirsim object target."""
        return (self.target.slice if isinstance(self.target, ObjView) else
                None)
