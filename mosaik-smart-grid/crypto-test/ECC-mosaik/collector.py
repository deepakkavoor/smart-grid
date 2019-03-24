"""
A simple data collector that prints all data when the simulation finishes.

"""
import collections
import pprint
import sys
sys.path.append("../../mosaik")
sys.path.append("../crypto")
from ECC.additive_point_utils import *
import mosaik_api


privateKey = random.randint(1, P256.P - 1)
P_public = pointMultiply(Base, privateKey)

with open("server public key.txt", "w") as keyFile:
        keyFile.write(str(P_public.getX()) + "\n" + str(P_public.getY()))

table = compute_table(Base, 0, 1000)

META = {
    'models': {
        'Monitor': {
            'public': True,
            'any_inputs': True,
            'params': [],
            'attrs': [],
        },
    },
}


class Collector(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid = None
        self.data = collections.defaultdict(lambda:
                                            collections.defaultdict(list))
        self.step_size = None

    def init(self, sid, step_size):
        self.step_size = step_size
        return self.meta

    def create(self, num, model):
        if num > 1 or self.eid is not None:
            raise RuntimeError('Can only create one instance of Monitor.')

        self.eid = 'Monitor'
        return [{'eid': self.eid, 'type': model}]

    def step(self, time, inputs):
        data = inputs[self.eid]
        for attr, values in data.items():
            for src, value in values.items():
                self.data[src][attr].append(value)

        return time + self.step_size

    def finalize(self):
        print('Collected data:')
        for sim, sim_data in sorted(self.data.items()):
            print('- %s:' % sim)
            for attr, values in sorted(sim_data.items()):
                print('  - %s: %s' % (attr, [additive_decrypt(stringToCipher(value), privateKey, Base, table) for value in values])) if attr == 'aggregate' else print('  - %s: %s' %(attr, values))


if __name__ == '__main__':
    mosaik_api.start_simulation(Collector())
