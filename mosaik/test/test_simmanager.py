from unittest import mock

from example_sim.mosaik import ExampleSim
import pytest

from mosaik import simmanager
from mosaik.exceptions import ScenarioError


sim_config = {
    'ExampleSimA': {
        'python': 'example_sim.mosaik:ExampleSim',
    },
    'ExampleSimB': {
        'cmd': 'example_sim %(addr)s',
        'cwd': '.',
    },
    'ExampleSimC': {
        'connect': 'host:port',
        'slots': 1,
    },
    'ExampleSimD': {
    },
}


@pytest.mark.xfail
def test_start():
    assert 0


def test_start_inproc():
    """Test starting an in-proc simulator."""
    sp = simmanager.start('ExampleSimA', sim_config, 'ExampleSim-0',
                          {'step_size': 2})
    assert sp.sid == 'ExampleSim-0'
    assert isinstance(sp._inst, ExampleSim)
    assert sp._inst.step_size == 2


@pytest.mark.xfail
def test_start_proc():
    """Test starting a simulator as external process."""
    assert 0


@pytest.mark.xfail
def test_start_connect():
    """Test connecting to an already running simulator."""
    assert 0


@pytest.mark.parametrize(('sim_config', 'err_msg'), [
    ({}, 'Not found in sim_config'),
    ({'spam': {}}, 'Invalid configuration'),
    ({'spam': {'python': 'eggs'}}, 'Malformed Python class name: Expected '
                                   '"module:Class"'),
    ({'spam': {'python': 'eggs:Bacon'}}, 'Could not import module'),
    ({'spam': {'python': 'example_sim:Bacon'}}, 'Class not found in module'),
])
def test_start__error(sim_config, err_msg):
    """Test failure at starting an in-proc simulator."""
    with pytest.raises(ScenarioError) as exc_info:
        simmanager.start('spam', sim_config, '', {})
    assert str(exc_info.value) == ('Simulator "spam" could not be started: ' +
                                   err_msg)


def test_sim_proxy():
    es = ExampleSim()
    sp = simmanager.InternalSimProxy('ExampleSim-0', es)
    assert sp.sid == 'ExampleSim-0'
    assert sp._inst is es
    assert sp.meta is es.meta
    assert sp.last_step == float('-inf')
    assert sp.next_step == 0
    assert sp.step_required is None


def test_internal_sim_proxy_meth_forward():
    sp = simmanager.InternalSimProxy('', mock.Mock())
    meths = [
        ('create', (object(), object(), object())),
        ('step', (object(), {})),
        ('get_data', (object(),)),
    ]
    for meth, args in meths:
        ret = getattr(sp, meth)(*args)
        assert ret is getattr(sp._inst, meth).return_value
        assert getattr(sp._inst, meth).call_args == mock.call(*args)
