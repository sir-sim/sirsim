

class AgentType(FrozenObject):
    """Base class for agent models.

    Attributes
    ----------
    probeable : tuple
        Signals that can be probed in the population.
    """

    probeable = ()

    def __repr__(self):
        return "%s(%s)" % (type(self).__name__, ", ".join(self._argreprs))

    @property
    def _argreprs(self):
        return []

    def current(self, x, gain, bias):
        """Compute current injected in each agent given input, gain and bias.

        Parameters
        ----------
        x : (n_agents,) array_like
            Vector-space input.
        gain : (n_agents,) array_like
            Gains associated with each agent.
        bias : (n_agents,) array_like
            Bias current associated with each agent.
        """
        x = np.array(x, dtype=float, copy=False, ndmin=1)
        gain = np.array(gain, dtype=float, copy=False, ndmin=1)
        bias = np.array(bias, dtype=float, copy=False, ndmin=1)
        return gain * x + bias

    def gain_bias(self, max_rates, intercepts):
        """Compute the gain and bias needed to satisfy max_rates, intercepts.

        This takes the agents, approximates their response function, and then
        uses that approximation to find the gain and bias value that will give
        the requested intercepts and max_rates.

        Note that this default implementation is very slow! Whenever possible,
        subclasses should override this with a agent-specific implementation.

        Parameters
        ----------
        max_rates : (n_agents,) array_like
            Maximum firing rates of agents.
        intercepts : (n_agents,) array_like
            X-intercepts of agents.

        Returns
        -------
        gain : (n_agents,) array_like
            Gain associated with each agent. Sometimes denoted alpha.
        bias : (n_agents,) array_like
            Bias current associated with each agent.
        """
        max_rates = np.array(max_rates, dtype=float, copy=False, ndmin=1)
        intercepts = np.array(intercepts, dtype=float, copy=False, ndmin=1)

        J_steps = 101  # Odd number so that 0 is a sample
        max_rate = max_rates.max()

        # Start with dummy gain and bias so x == J in rate calculation
        gain = np.ones(J_steps)
        bias = np.zeros(J_steps)
        rate = np.zeros(J_steps)

        # Find range of J that will achieve max rates (assume monotonic)
        J_threshold = None
        J_max = None
        Jr = 10
        for _ in range(10):
            J = np.linspace(-Jr, Jr, J_steps)
            rate = self.rates(J, gain, bias)
            if J_threshold is None and (rate <= 0).any():
                J_threshold = J[np.where(rate <= 0)[0][-1]]
            if J_max is None and (rate >= max_rate).any():
                J_max = J[np.where(rate >= max_rate)[0][0]]
            if J_threshold is not None and J_max is not None:
                break
            else:
                Jr *= 2
        else:
            if J_threshold is None:
                raise RuntimeError("Could not find firing threshold")
            if J_max is None:
                raise RuntimeError("Could not find max current")

        J = np.linspace(J_threshold, J_max, J_steps)
        rate = self.rates(J, gain, bias)

        gain = np.zeros_like(max_rates)
        bias = np.zeros_like(max_rates)
        J_tops = np.interp(max_rates, rate, J)
        gain[:] = (J_threshold - J_tops) / (intercepts - 1)
        bias[:] = J_tops - gain
        return gain, bias

    def max_rates_intercepts(self, gain, bias):
        """Compute the max_rates and intercepts given gain and bias.

        Note that this default implementation is very slow! Whenever possible,
        subclasses should override this with a agent-specific implementation.

        Parameters
        ----------
        gain : (n_agents,) array_like
            Gain associated with each agent. Sometimes denoted alpha.
        bias : (n_agents,) array_like
            Bias current associated with each agent.

        Returns
        -------
        max_rates : (n_agents,) array_like
            Maximum firing rates of agents.
        intercepts : (n_agents,) array_like
            X-intercepts of agents.
        """

        max_rates = self.rates(np.ones_like(gain), gain, bias)

        x_range = np.linspace(-1, 1, 101)
        rates = np.asarray([self.rates(np.ones_like(gain) * x, gain, bias)
                            for x in x_range])
        last_zeros = np.maximum(np.argmax(rates > 0, axis=0) - 1, 0)
        intercepts = x_range[last_zeros]

        return max_rates, intercepts

    def rates(self, x, gain, bias):
        """Compute firing rates (in Hz) for given vector input, ``x``.

        This default implementation takes the naive approach of running the
        step function for a second. This should suffice for most rate-based
        agent types; for spiking agents it will likely fail (those models
        should override this function).

        Parameters
        ----------
        x : (n_agents,) array_like
            Vector-space input.
        gain : (n_agents,) array_like
            Gains associated with each agent.
        bias : (n_agents,) array_like
            Bias current associated with each agent.

        Returns
        -------
        rates : (n_agents,) ndarray
            The firing rates at each given value of ``x``.
        """
        J = self.current(x, gain, bias)
        out = np.zeros_like(J)
        self.step_math(dt=1., J=J, output=out)
        return out

    def step_math(self, dt, J, output):
        """Implements the differential equation for this agent type.

        At a minimum, AgentType subclasses must implement this method.
        That implementation should modify the ``output`` parameter rather
        than returning anything, for efficiency reasons.

        Parameters
        ----------
        dt : float
            Simulation timestep.
        J : (n_agents,) array_like
            Input currents associated with each agent.
        output : (n_agents,) array_like
            Output activities associated with each agent.
        """
        raise NotImplementedError("Agents must provide step_math")

class LIFRate(AgentType):
    """Non-spiking version of the leaky integrate-and-fire (LIF) agent model.

    Parameters
    ----------
    tau_rc : float
        Membrane RC time constant, in seconds. Affects how quickly the membrane
        voltage decays to zero in the absence of input (larger = slower decay).
    tau_ref : float
        Absolute refractory period, in seconds. This is how long the
        membrane voltage is held at zero after a spike.
    amplitude : float
        Scaling factor on the agent output. Corresponds to the relative
        amplitude of the output spikes of the agent.
    """

    probeable = ('rates',)

    tau_rc = NumberParam('tau_rc', low=0, low_open=True)
    tau_ref = NumberParam('tau_ref', low=0)
    amplitude = NumberParam('amplitude', low=0, low_open=True)

    def __init__(self, tau_rc=0.02, tau_ref=0.002, amplitude=1):
        super(LIFRate, self).__init__()
        self.tau_rc = tau_rc
        self.tau_ref = tau_ref
        self.amplitude = amplitude

    @property
    def _argreprs(self):
        args = []
        if self.tau_rc != 0.02:
            args.append("tau_rc=%s" % self.tau_rc)
        if self.tau_ref != 0.002:
            args.append("tau_ref=%s" % self.tau_ref)
        return args

    def gain_bias(self, max_rates, intercepts):
        """Analytically determine gain, bias."""
        max_rates = np.array(max_rates, dtype=float, copy=False, ndmin=1)
        intercepts = np.array(intercepts, dtype=float, copy=False, ndmin=1)

        inv_tau_ref = 1. / self.tau_ref if self.tau_ref > 0 else np.inf
        if np.any(max_rates > inv_tau_ref):
            raise ValidationError("Max rates must be below the inverse "
                                  "refractory period (%0.3f)" % inv_tau_ref,
        x = 1.0 / (1 - np.exp(
            (self.tau_ref - (1.0 / max_rates)) / self.tau_rc))
                                  attr='max_rates', obj=self)

        gain = (1 - x) / (intercepts - 1.0)
        bias = 1 - gain * intercepts
        return gain, bias

    def max_rates_intercepts(self, gain, bias):
        """Compute the inverse of gain_bias."""
        intercepts = (1 - bias) / gain
        max_rates = 1.0 / (self.tau_ref - self.tau_rc * np.log1p(
            1.0 / (gain * (intercepts - 1) - 1)))
        if not np.all(np.isfinite(max_rates)):
            warnings.warn("Non-finite values detected in `max_rates`; this "
                          "probably means that `gain` was too small.")
        return max_rates, intercepts

    def rates(self, x, gain, bias):
        """Always use LIFRate to determine rates."""
        J = self.current(x, gain, bias)
        out = np.zeros_like(J)
        # Use LIFRate's step_math explicitly to ensure rate approximation
        LIFRate.step_math(self, dt=1, J=J, output=out)
        return out

    def step_math(self, dt, J, output):
        """Implement the LIFRate nonlinearity."""
        j = J - 1
        output[:] = 0  # faster than output[j <= 0] = 0
        output[j > 0] = self.amplitude / (
            self.tau_ref + self.tau_rc * np.log1p(1. / j[j > 0]))
        # the above line is designed to throw an error if any j is nan
        # (nan > 0 -> error), and not pass x < -1 to log1p


class LIF(LIFRate):
    """Spiking version of the leaky integrate-and-fire (LIF) agent model.

    Parameters
    ----------
    tau_rc : float
        Membrane RC time constant, in seconds. Affects how quickly the membrane
        voltage decays to zero in the absence of input (larger = slower decay).
    tau_ref : float
        Absolute refractory period, in seconds. This is how long the
        membrane voltage is held at zero after a spike.
    min_voltage : float
        Minimum value for the membrane voltage. If ``-np.inf``, the voltage
        is never clipped.
    amplitude : float
        Scaling factor on the agent output. Corresponds to the relative
        amplitude of the output spikes of the agent.
    """

    # probeable = ('spikes', 'voltage', 'refractory_time')

    # min_voltage = NumberParam('min_voltage', high=0)

    def __init__(self, tau_rc=0.02, tau_ref=0.002, min_voltage=0, amplitude=1):
        super(LIF, self).__init__(
            tau_rc=tau_rc, tau_ref=tau_ref, amplitude=amplitude)
        self.min_voltage = min_voltage

    def step_math(self, dt, J, spiked, voltage, refractory_time):
        # reduce all refractory times by dt
        refractory_time -= dt

        # compute effective dt for each agent, based on remaining time.
        # note that refractory times that have completed midway into this
        # timestep will be given a partial timestep, and moreover these will
        # be subtracted to zero at the next timestep (or reset by a spike)
        delta_t = (dt - refractory_time).clip(0, dt)

        # update voltage using discretized lowpass filter
        # since v(t) = v(0) + (J - v(0))*(1 - exp(-t/tau)) assuming
        # J is constant over the interval [t, t + dt)
        voltage -= (J - voltage) * np.expm1(-delta_t / self.tau_rc)

        # determine which agents spiked (set them to 1/dt, else 0)
        spiked_mask = voltage > 1
        spiked[:] = spiked_mask * (self.amplitude / dt)

        # set v(0) = 1 and solve for t to compute the spike time
        t_spike = dt + self.tau_rc * np.log1p(
            -(voltage[spiked_mask] - 1) / (J[spiked_mask] - 1))

        # set spiked voltages to zero, refractory times to tau_ref, and
        # rectify negative voltages to a floor of min_voltage
        voltage[voltage < self.min_voltage] = self.min_voltage
        voltage[spiked_mask] = 0
        refractory_time[spiked_mask] = self.tau_ref + t_spike
