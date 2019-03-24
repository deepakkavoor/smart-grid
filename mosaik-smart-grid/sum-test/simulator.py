# simulator.py
"""
This module contains a simple example simulator.

"""
import random
import sys
sys.path.append("../mosaik")

class Model:
    """Simple model that increases its value *val* with some *delta* every
    step.

    You can optionally set the initial value *init_val*. It defaults to ``0``.

    """
    def __init__(self, max_val=2):
        self.max_val = max_val
        self.reading = random.randint(0, self.max_val)
        self.aggregate = self.reading

    def step(self, rec_data=None):
        """Perform a simulation step by adding *delta* to *val*."""
        if rec_data is not None:
            self.aggregate += rec_data
        else:
            self.reading = random.randint(0, self.max_val)
            self.aggregate = self.reading
            print("----- empty, reading= ", self.reading)

class Simulator(object):
    """Simulates a number of ``Model`` models and collects some data."""
    def __init__(self):
        self.models = []
        self.data = []

    def add_model(self, max_val):
        """Create an instances of ``Model`` with *init_val*."""
        model = Model(max_val)
        self.models.append(model)
        self.data.append([])  # Add list for simulation data

    def step(self, rec_data_dict=None):
        """Set new model inputs from *deltas* to the models and perform a
        simulatino step.

        *deltas* is a dictionary that maps model indices to new delta values
        for the model.

        """
        if rec_data_dict:
            # Set new deltas to model instances
            for idx, rec_data in rec_data_dict.items():
                self.models[idx].step(rec_data)

        else:
            for i, model in enumerate(self.models):
                self.models[i].step()

        # Step models and collect data
        for i, model in enumerate(self.models):
            self.data[i].append(model.aggregate)


if __name__ == '__main__':
    # This is how the simulator could be used:
    sim = Simulator()
    for i in range(2):
        sim.add_model(max_val=2)
    sim.step()
    sim.step()
    print('Simulation finished with data:')
    for i, inst in enumerate(sim.data):
        print('%d: %s' % (i, inst))
