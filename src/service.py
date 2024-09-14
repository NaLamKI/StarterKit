import io
import os.path
import json

from nalamkisdk.model.action.action import *
from nalamkisdk.service import NaLamKIService
from nalamkisdk.model.output_data import *
from nalamkisdk.model.encoder import *

from model.greendetectionmodel import DummyGreenDetectionModel

from PIL import Image as PilImage
from PIL.ExifTags import TAGS, GPSTAGS


class MyService(NaLamKIService):
    def __init__(self):
        # for local testing only:
        self.model = self.init_model()
        self.s3 = None
        self.action_path = os.path.join("test","action")
        # create output path (only needed in local testing)
        path = os.path.join(self.action_path, "output")
        if not os.path.exists(path):
            os.makedirs(path)

        # else call: super().__init__()

    def init_model(self):
        '''
        Initialize and return the model.
        Model can be accessed via self.model
        '''
        return DummyGreenDetectionModel()

    def process_data(self):
        '''
        Main Function
        Proces Data and store output in GeoOutputData
        '''
        if self.model is None:
            raise Warning("Model not initialized")

        # get list of input files:
        input_files = self.load_inputData()

        # process images, get results
        results = []
        for input_file in input_files:
            if any(f".{ext}" in input_file.name.lower() for ext in self.model.IMAGE_EXTENSIONS):
                result = self.model(input_file)

            else:
                print(f'skip {input_file.name.lower()}')
                continue

            # save image into output folder
            image = PilImage.fromarray(result['image'])
            image.save(os.path.join(self.action_path, 'output', f"green_{result['uri']}"))
            results.append(result)

        # process the results, convert into GeoOutputData
        output_data: GeoOutputData = self._process_results(results)

        # convert it to JSON
        output_json = json.dumps(dataclasses.asdict(output_data), cls=NaLamKIDataEncoder, indent=2)
        # create File from JSON String
        output_file = io.StringIO(output_json)
        output_file.name = 'results.json'


        # store file
        self.save_data([output_file])

    @staticmethod
    def _process_results(results: List[dict]) -> GeoOutputData:
        # process results for images in the input folder into a GeoOutputData object
        features = []
        for result in results:
            image = DataImage(uri=result['uri'])
            coords = result.get('coordinates')
            if coords is None:
                latitude, longitude = [0, 0]
            else:
                latitude, longitude = coords
            p_green = result['green']

            items = TimeSeriesItem(
                timestamp=datetime.now(),
                values=[DataValue(name='Percentage of green values: ', value=p_green)],
                images=[image]
            )

            features.append(
                GeoFeature(
                    type='Feature',
                    geometry=GeoGeometry(
                        type='point',
                        coordinates=GeoCoordinates(latitude=latitude, longitude=longitude)
                    ),
                    property=GeoFeatureProperty(
                        type="BILD",
                        datasets=[Timeseries(name="BILDAUSWERTUNG", items=[items])]
                    )
                )
            )

        output_data = GeoOutputData(
            type='FeatureCollection',
            features=features
        )
        return output_data
