from service import *
from sdk.model.action.action import *

from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":

    '''
    Main file is excecuted within the docker Container and starts the service.
    The service will listen to the Message-Queue and listen to messages from the digital farm. 
    '''
    
    service = MyService()
    service.run()
