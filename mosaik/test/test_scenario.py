from unittest import mock

import pytest

from mosaik import scenario
from mosaik.exceptions import ScenarioError


sim_config = {
    'ExampleSim': {
        'python': 'example_sim.mosaik:ExampleSim',
    },
}


def test_entity():
    sim = object()
    e = scenario.Entity('0', '1', 'spam', [], sim)
    assert e.sid == '0'
    assert e.eid == '1'
    assert e.type == 'spam'
    assert e.rel == []
    assert e.sim is sim
    assert str(e) == 'Entity(0, 1, spam)'
    assert repr(e) == 'Entity(0, 1, spam, [], %r)' % sim


def test_environment():
    sim_config = {'spam': 'eggs'}
    env = scenario.Environment(sim_config)
    assert env.sim_config is sim_config
    assert env.sims == {}
    assert env.simpy_env is None
    assert env.df_graph.nodes() == []
    assert env.df_graph.edges() == []


def test_env_start():
    """Test starting new simulators and getting IDs for them."""
    env = scenario.Environment(sim_config)
    fac = env.start('ExampleSim')
    assert isinstance(fac, scenario.ModelFactory)
    assert env.sims == {'ExampleSim-0': fac._sim}

    env.start('ExampleSim')
    assert list(sorted(env.sims)) == ['ExampleSim-0', 'ExampleSim-1']


def test_env_connect():
    """Test connecting to single entities."""
    env = scenario.Environment(sim_config)
    a = env.start('ExampleSim').A.create(2, init_val=0)
    b = env.start('ExampleSim').B.create(2, init_val=0)
    for i, j in zip(a, b):
        env.connect(i, j, ('val_out', 'val_in'), ('dummy_out', 'dummy_in'))

    assert list(sorted(env.df_graph.nodes())) == ['ExampleSim-0',
                                                  'ExampleSim-1']
    assert env.df_graph.edges() == [('ExampleSim-0', 'ExampleSim-1')]
    assert env._df_outattr == {
        'ExampleSim-0': {
            '0.0': ['val_out', 'dummy_out'],
            '0.1': ['val_out', 'dummy_out']
        },
    }


def test_env_connect_same_simulator():
    """Connecting to entities belonging to the same simulator must fail."""
    env = scenario.Environment(sim_config)
    a = env.start('ExampleSim').A.create(2, init_val=0)
    with pytest.raises(ScenarioError) as err:
        env.connect(a[0], a[1], ('val_out', 'val_out'))
    assert str(err.value) == ('Cannot connect entities sharing the same '
                              'simulator.')
    assert env.df_graph.edges() == []
    assert env._df_outattr == {}


def test_env_connect_cycle():
    """If connecting two entities results in a cycle in the dataflow graph,
    an error must be raised."""
    env = scenario.Environment(sim_config)
    a = env.start('ExampleSim').A(init_val=0)
    b = env.start('ExampleSim').B(init_val=0)
    env.connect(a, b, ('val_out', 'val_in'))
    with pytest.raises(ScenarioError) as err:
        env.connect(b, a, ('val_in', 'val_out'))
    assert str(err.value) == ('Connection from "ExampleSim-1" to '
                              '"ExampleSim-0" introduces cyclic dependencies.')
    assert env.df_graph.edges() == [('ExampleSim-0', 'ExampleSim-1')]
    assert len(env._df_outattr) == 1


def test_env_connect_wrong_attr_names():
    """The entities to be connected must have the listed attributes."""
    env = scenario.Environment(sim_config)
    a = env.start('ExampleSim').A(init_val=0)
    b = env.start('ExampleSim').B(init_val=0)
    err = pytest.raises(ScenarioError, env.connect, a, b, ('val', 'val_in'))
    assert str(err.value) == ('At least on attribute does not exist: '
                              'Entity(ExampleSim-0, 0.0, A).val')
    err = pytest.raises(ScenarioError, env.connect, a, b, ('val_out', 'val'))
    assert str(err.value) == ('At least on attribute does not exist: '
                              'Entity(ExampleSim-1, 0.0, B).val')
    err = pytest.raises(ScenarioError, env.connect, a, b, ('val', 'val_in'),
                        ('dummy_out', 'onoes'))
    assert str(err.value) == ('At least on attribute does not exist: '
                              'Entity(ExampleSim-0, 0.0, A).val, '
                              'Entity(ExampleSim-1, 0.0, B).onoes')
    assert env.df_graph.edges() == []
    assert env._df_outattr == {}


def test_env_run():
    env = scenario.Environment({})
    with mock.patch('mosaik.simulator.run') as run_mock:
        env.run(3)
        assert run_mock.call_args == mock.call(env, 3)


def test_model_factory():
    env = scenario.Environment(sim_config)
    mf = env.start('ExampleSim')
    assert mf.A._name == 'A'
    assert mf.A._sim_id == mf._sim.sid
    assert mf.B._name == 'B'


def test_model_factory_private_model():
    env = scenario.Environment(sim_config)
    mf = env.start('ExampleSim')
    err = pytest.raises(ScenarioError, getattr, mf, 'C')
    assert str(err.value) == 'Model "C" is not public.'


def test_model_factory_unkown_model():
    env = scenario.Environment(sim_config)
    mf = env.start('ExampleSim')
    err = pytest.raises(ScenarioError, getattr, mf, 'D')
    assert str(err.value) == ('Model factory for "ExampleSim-0" has no model '
                              '"D".')
