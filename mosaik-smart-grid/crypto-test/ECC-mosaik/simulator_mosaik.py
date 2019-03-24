# simulator_mosaik.py
"""
Mosaik interface for the example simulator.

"""
import sys
import simulator
sys.path.append("../../mosaik")
sys.path.append("../crypto")
from ECC.additive_point_utils import *
import mosaik_api


with open("server public key.txt", "r") as keyFile:
    keys = keyFile.read().split("\n")
    P_public = Point(X = int(keys[0]), Y = int(keys[1]), curve = P256)


META = {
    'models': {
        'ExampleModel': {
            'public': True,
            'params': ['max_val'],
            'attrs': ['reading', 'aggregate'],
        },
        'ExampleModel2': {
            'public': True,
            'params': ['max_val'],
            'attrs': ['reading', 'aggregate'],
        },
    },
}


class ExampleSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.simulator = simulator.Simulator()
        self.eid_prefix = 'Model_'
        self.sid = ''
        self.entities = {}  # Maps EIDs to model indices in self.simulator

    def init(self, sid=None, eid_prefix=None):
        if eid_prefix is not None:
            self.eid_prefix = eid_prefix

        if sid is not None:
            self.sid = sid

        return self.meta

    def create(self, num, model, max_val):
        next_eid = len(self.entities)
        entities = []

        for i in range(next_eid, next_eid + num):
            eid = '%s_%s%d' % (self.sid, self.eid_prefix, i)
            self.simulator.add_model(max_val)
            self.entities[eid] = i
            entities.append({'eid': eid, 'type': model})

        return entities

    def step(self, time, inputs):
        # Get inputs
        rec_data_dict = {}
        print("step called in ", self.sid)
        # print(inputs)

        # if inputs is None:
        #     self.simulator.step()
        #     return time + 60

        for eid, attrs in inputs.items():
            for attr, values in attrs.items():
                model_idx = self.entities[eid]
                rec_data_list = [stringToCipher(value) for value in values.values()]   #-----------changed here-----------
                new_rec_data = rec_data_list[0] if len(rec_data_list) == 1 else add_ciphertexts(rec_data_list[0], rec_data_list[1], P_public, Base)
                for data_idx in range(2, len(rec_data_list)):
                    new_rec_data = add_ciphertexts(new_rec_data, rec_data_list[data_idx], P_public, Base)

                # print("new received data is ", new_rec_data)
                rec_data_dict[model_idx] = new_rec_data

        # Perform simulation step
        self.simulator.step(rec_data_dict)

        return time + 60  # Step size is 1 minute

    def get_data(self, outputs):
        models = self.simulator.models
        data = {}
        for eid, attrs in outputs.items():
            model_idx = self.entities[eid]
            data[eid] = {}
            for attr in attrs:
                if attr not in self.meta['models']['ExampleModel']['attrs']:
                    raise ValueError('Unknown output attribute: %s' % attr)

                # Get model.val or model.delta:
                data[eid][attr] = getattr(models[model_idx], attr) if attr=='reading' else cipherToString(getattr(models[model_idx], attr))  #----------changed here----------

        return data


def main():
    return mosaik_api.start_simulation(ExampleSim())


if __name__ == '__main__':
    main()
