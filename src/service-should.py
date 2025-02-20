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

        # Store data
        self.save_result(output_file)
