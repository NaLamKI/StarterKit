import os
import sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
sys.path.append(os.path.join(parent, 'src'))

from service import MyService

from dotenv import load_dotenv
# TODO: implement local initialisation for NaLamKI Service without initializing MQTT Broker
load_dotenv()

if __name__ == "__main__":
    '''
    Locally test Service without receiving messages and downloading files from S3 storage.
    Testdata (Input & Output) can be stored in action folder. Service will use local data for testing.
    '''
    service = MyService()
    service.local_test()
