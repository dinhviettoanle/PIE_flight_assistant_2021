"""
Training of the Snips-NLU Engine
You only need to modify the .yaml file. The .json and the .snips files are automatically generated.
"""
from snips_nlu import SnipsNLUEngine
from snips_nlu.default_configs import CONFIG_EN
import io
import json
import os


nlu_engine_filename = "./nlu/engine.snips"
yaml_filename = "./nlu/requests_datasets.yaml"
json_filename = "./nlu/requests_datasets.json"


def fit_engine():
    with io.open(json_filename) as f:
        sample_dataset = json.load(f)

    nlu_engine = SnipsNLUEngine(config=CONFIG_EN)
    
    print("Training...")
    nlu_engine = nlu_engine.fit(sample_dataset)

    print("Exporting to .snips")
    engine_bytes = nlu_engine.to_byte_array()
    with open(nlu_engine_filename,'wb') as f:
        f.write(engine_bytes)



if __name__ == '__main__':
    print("Generating JSON file")
    os.system(f'snips-nlu generate-dataset en {yaml_filename} > {json_filename}')
    fit_engine()