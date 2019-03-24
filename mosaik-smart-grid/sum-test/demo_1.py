# demo_1.py
import sys
sys.path.append("../mosaik")
import mosaik.util
import mosaik.util.connect


# Sim config. and other parameters
SIM_CONFIG = {
    'ExampleSim': {
        'python': 'simulator_mosaik:ExampleSim',
    },
    'ExampleSim2': {
        'python': 'simulator_mosaik:ExampleSim',
    },
    'Collector': {
        'cmd': 'python collector.py %(addr)s',
    },
}
END = 3 * 60  # 10 minutes

# Create World
world = mosaik.World(SIM_CONFIG)

# Start simulators
examplesim = world.start('ExampleSim', eid_prefix='Model_')
examplesim2 = world.start('ExampleSim2', eid_prefix='Model_')
collector = world.start('Collector', step_size=60)

# Instantiate models
# model1 = examplesim.ExampleModel(max_val=20)
model2 = examplesim2.ExampleModel(max_val=20)
monitor = collector.Monitor()

more_model1 = examplesim.ExampleModel.create(3, max_val=20)

# Connect entities
# world.connect(model, monitor, 'val', 'delta')

mosaik.util.connect.connect_many_to_one(world, more_model1, model2, 'aggregate')
# world.connect(model1, model2,'aggregate')
# world.connect(model1, monitor, 'val', 'delta')
world.connect(model2, monitor, 'reading', 'aggregate')


# Create more entities
# more_models = examplesim.ExampleModel.create(2, init_val=3)
#mosaik.util.connect.connect_many_to_one(world, more_models, monitor, 'val', 'delta')

# Run simulation
world.run(until=END)
