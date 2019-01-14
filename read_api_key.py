import sys  
import os
import json

def readKey(filePath):
    
    print('read file {}'.format(filePath))
    if not os.path.isfile(filePath):
        print("File path {} does not exist. Exiting...".format(filePath))
        sys.exit()
    
    try:
        with open(filePath) as fp:
            result = json.load(fp)
    except Exception as exp:
        print("Can't load json : {}".format(exp))
        print("Program exit")
        sys.exit()

    return result
