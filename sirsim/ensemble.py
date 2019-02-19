from sirsim.base import SirsimObject, ObjView, ProcessParam
from sirsim.dists import DistOrArrayParam, Uniform, UniformHypersphere
from sirsim.exceptions import ReadonlyError
from sirsim.agents import LIF, AgentTypeParam, Direct
from sirsim.params import BoolParam, Default, IntParam, NumberParam


class Ensemble(SirsimObject):
    """A group of agents that collectively represent a vector.

    Parameters
    ----------
    n_agents : int
        The number of agents.
    dimensions : int
        The number of representational dimensions.

    radius : int, optional (Default: 1.0)
        The representational radius of the ensemble.
    encoders : Distribution or (n_agents, dimensions) array_like, optional \
               (Default: UniformHypersphere(surface=True))
        The encoders used to transform from representational space
        to agent space. Each row is a agent's encoder; each column is a
        representational dimension.
    intercepts : Distribution or (n_agents,) array_like, optional \
                 (Default: ``sirsim.dists.Uniform(-1.0, 1.0)``)
        The point along each agent's encoder where its activity is zero. If
        ``e`` is the agent's encoder, then the activity will be zero when
        ``dot(x, e) <= c``, where ``c`` is the given intercept.
    max_rates : Distribution or (n_agents,) array_like, optional \
                (Default: ``sirsim.dists.Uniform(200, 400)``)
        The activity of each agent when the input signal ``x`` is magnitude 1
        and aligned with that agent's encoder ``e``;
        i.e., when ``dot(x, e) = 1``.
    eval_points : Distribution or (n_eval_points, dims) array_like, optional \
                  (Default: ``sirsim.dists.UniformHypersphere()``)
        The evaluation points used for decoder solving, spanning the interval
        (-radius, radius) in each dimension, or a distribution from which
        to choose evaluation points.
    n_eval_points : int, optional (Default: None)
        The number of evaluation points to be drawn from the ``eval_points``
        distribution. If None, then a heuristic is used to determine
        the number of evaluation points.
    agent_type : `~sirsim.agents.AgentType`, optional \
                  (Default: ``sirsim.LIF()``)
        The model that simulates all agents in the ensemble
        (see `~sirsim.agents.AgentType`).
    gain : Distribution or (n_agents,) array_like (Default: None)
        The gains associated with each agent in the ensemble. If None, then
        the gain will be solved for using ``max_rates`` and ``intercepts``.
    bias : Distribution or (n_agents,) array_like (Default: None)
        The biases associated with each agent in the ensemble. If None, then
        the gain will be solved for using ``max_rates`` and ``intercepts``.
    noise : Process, optional (Default: None)
        Random noise injected directly into each agent in the ensemble
        as current. A sample is drawn for each individual agent on
        every simulation step.
    normalize_encoders : bool, optional (Default: True)
        Indicates whether the encoders should be normalized.
    label : str, optional (Default: None)
        A name for the ensemble. Used for debugging and visualization.
    seed : int, optional (Default: None)
        The seed used for random number generation.

    Attributes
    ----------
    bias : Distribution or (n_agents,) array_like or None
        The biases associated with each agent in the ensemble.
    dimensions : int
        The number of representational dimensions.
    encoders : Distribution or (n_agents, dimensions) array_like
        The encoders, used to transform from representational space
        to agent space. Each row is a agent's encoder, each column is a
        representational dimension.
    eval_points : Distribution or (n_eval_points, dims) array_like
        The evaluation points used for decoder solving, spanning the interval
        (-radius, radius) in each dimension, or a distribution from which
        to choose evaluation points.
    gain : Distribution or (n_agents,) array_like or None
        The gains associated with each agent in the ensemble.
    intercepts : Distribution or (n_agents) array_like or None
        The point along each agent's encoder where its activity is zero. If
        ``e`` is the agent's encoder, then the activity will be zero when
        ``dot(x, e) <= c``, where ``c`` is the given intercept.
    label : str or None
        A name for the ensemble. Used for debugging and visualization.
    max_rates : Distribution or (n_agents,) array_like or None
        The activity of each agent when ``dot(x, e) = 1``,
        where ``e`` is the agent's encoder.
    n_eval_points : int or None
        The number of evaluation points to be drawn from the ``eval_points``
        distribution. If None, then a heuristic is used to determine
        the number of evaluation points.
    n_agents : int or None
        The number of agents.
    agent_type : AgentType
        The model that simulates all agents in the ensemble
        (see ``sirsim.agents``).
    noise : Process or None
        Random noise injected directly into each agent in the ensemble
        as current. A sample is drawn for each individual agent on
        every simulation step.
    radius : int
        The representational radius of the ensemble.
    seed : int or None
        The seed used for random number generation.
    """

    probeable = ('decoded_output', 'input', 'scaled_encoders')

    n_agents = IntParam('n_agents', low=1)
    dimensions = IntParam('dimensions', low=1)
    radius = NumberParam('radius', default=1.0, low=1e-10)
    encoders = DistOrArrayParam('encoders',
                                default=UniformHypersphere(surface=True),
                                sample_shape=('n_agents', 'dimensions'))
    intercepts = DistOrArrayParam('intercepts',
                                  default=Uniform(-1.0, 1.0),
                                  optional=True,
                                  sample_shape=('n_agents',))
    max_rates = DistOrArrayParam('max_rates',
                                 default=Uniform(200, 400),
                                 optional=True,
                                 sample_shape=('n_agents',))
    eval_points = DistOrArrayParam('eval_points',
                                   default=UniformHypersphere(),
                                   sample_shape=('*', 'dimensions'))
    n_eval_points = IntParam('n_eval_points', default=None, optional=True)
    agent_type = AgentTypeParam('agent_type', default=LIF())
    gain = DistOrArrayParam('gain',
                            default=None,
                            optional=True,
                            sample_shape=('n_agents',))
    bias = DistOrArrayParam('bias',
                            default=None,
                            optional=True,
                            sample_shape=('n_agents',))
    noise = ProcessParam('noise', default=None, optional=True)
    normalize_encoders = BoolParam(
        'normalize_encoders', default=True, optional=True)

    def __init__(self, n_agents, dimensions, radius=Default, encoders=Default,
                 intercepts=Default, max_rates=Default, eval_points=Default,
                 n_eval_points=Default, agent_type=Default, gain=Default,
                 bias=Default, noise=Default, normalize_encoders=Default,
                 label=Default, seed=Default):
        super(Ensemble, self).__init__(label=label, seed=seed)
        self.n_agents = n_agents
        self.dimensions = dimensions
        self.radius = radius
        self.encoders = encoders
        self.intercepts = intercepts
        self.max_rates = max_rates
        self.n_eval_points = n_eval_points
        self.eval_points = eval_points
        self.bias = bias
        self.gain = gain
        self.agent_type = agent_type
        self.noise = noise
        self.normalize_encoders = normalize_encoders

    def __getitem__(self, key):
        return ObjView(self, key)

    def __len__(self):
        return self.dimensions

    @property
    def agents(self):
        """A direct interface to the agents in the ensemble."""
        return Agents(self)

    @agents.setter
    def agents(self, dummy):
        raise ReadonlyError(attr="agents", obj=self)

    @property
    def size_in(self):
        """The dimensionality of the ensemble."""
        return self.dimensions

    @property
    def size_out(self):
        """The dimensionality of the ensemble."""
        return self.dimensions


class Agents(object):
    """An interface for making connections directly to an ensemble's agents.

    This should only ever be accessed through the ``agents`` attribute of an
    ensemble, as a way to signal to `~sirsim.Connection` that the connection
    should be made directly to the agents rather than to the ensemble's
    decoded value, e.g.::

        sirsim.Connection(a.agents, b.agents)
    """

    def __init__(self, ensemble):
        self._ensemble = ensemble

    def __getitem__(self, key):
        return ObjView(self, key)

    def __len__(self):
        return self.ensemble.n_agents

    def __repr__(self):
        return "<Agents at 0x%x of %r>" % (id(self), self.ensemble)

    def __str__(self):
        return "<Agents of %s>" % self.ensemble

    def __eq__(self, other):
        return self.ensemble is other.ensemble

    def __hash__(self):
        return hash(self.ensemble) + 1  # +1 to avoid collision with ensemble

    @property
    def ensemble(self):
        """(Ensemble) The ensemble these agents are part of."""
        return self._ensemble

    @property
    def probeable(self):
        """(tuple) Signals that can be probed in the agent population."""
        return ('output', 'input') + self.ensemble.agent_type.probeable

    @property
    def size_in(self):
        """(int) The number of agents in the population."""
        if isinstance(self.ensemble.agent_type, Direct):
            # This will prevent users from connecting/probing Direct agents
            # (since there aren't actually any agents being simulated).
            return 0
        return self.ensemble.n_agents

    @property
    def size_out(self):
        """(int) The number of agents in the population."""
        if isinstance(self.ensemble.agent_type, Direct):
            # This will prevent users from connecting/probing Direct agents
            # (since there aren't actually any agents being simulated).
            return 0
        return self.ensemble.n_agents
