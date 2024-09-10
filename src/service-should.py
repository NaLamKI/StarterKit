import dataclasses
import json
import shutil
from sdk.service import NaLamKIService
from sdk.model.output_data import *
from sdk.model.encoder import NaLamKIDataEncoder
import io

class MyService(NaLamKIService):
    def __init__(self):
        super().__init__()

    def init_model(self):
        '''
        Initialize the Model and return the model. 
        Model can be accessed via self.model
        '''
        return None

    def process_data(self):
        '''
        Main Function
        Proces Data and store output in GeoOutputData
        '''

        # convert the output data into the json output template format
        output_data = GeoOutputData(type="bla", features=[]) 
        output_json = json.dumps(dataclasses.asdict(output_data), cls=NaLamKIDataEncoder)
        print(output_json)
        # create File from JSON String
        output_file = io.StringIO(output_json)
        output_file.name = 'results.json'

        # Store File
        self.save_data([output_file])
