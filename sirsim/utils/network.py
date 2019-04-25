import sirsim
from .magic import decorator


@decorator
def with_self(method, network, args, kwargs):
    """Wraps a method with ``with network:``.

    This makes it easy to add methods to a network that create new
    Sirsim objects. Instead of writing ``with self`` at the top of the method
    and indenting everything over, you can instead use this decorator.

    Example
    -------

    The two methods in the following class do the same thing::

        class MyNetwork(sirsim.Network):
            def add_one_1(self):
                with self:
                    node = sirsim.Node(output=1)

            @with_self
            def add_one_2(self):
                node = sirsim.Node(output=1)
    """
    with network:
        return method(*args, **kwargs)


def activate_direct_mode(network):
    """Activates direct mode for a network.

    This sets the agent type of all ensembles to a `sirsim.Direct`
    instance unless:

    - there is a connection to or from the ensemble's agents
    - there is a probe on an ensemble's agents
    - the ensemble has a connection with a learning rule attached.

    Parameters
    ----------
    network : Network
        Network to activate direct mode for.
    """
    requires_agents = set()

    for c in network.all_connections:
        if isinstance(c.pre_obj, sirsim.ensemble.Agents):
            requires_agents.add(c.pre_obj.ensemble)
        if isinstance(c.post_obj, sirsim.ensemble.Agents):
            requires_agents.add(c.post_obj.ensemble)
        if c.learning_rule_type is not None:
            requires_agents.add(c.pre_obj)
            requires_agents.add(c.post_obj)

    for p in network.all_probes:
        if isinstance(p.obj, sirsim.ensemble.Agents):
            requires_agents.add(p.obj.ensemble)

    for e in network.all_ensembles:
        if e not in requires_agents:
            e.agent_type = sirsim.Direct()
