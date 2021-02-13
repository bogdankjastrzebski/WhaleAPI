from WhaleAlertMessenger import WhaleAlertMessenger
import time
import yaml

with open('./src/properties.yaml', 'r') as f:
    properties = yaml.load(f, Loader=yaml.loader.FullLoader)

if __name__ == '__main__':
    
    # Init Messenger 
    messenger = WhaleAlertMessenger(properties['api_key'],
                                    properties['min_value'],
                                    properties['sec'],
                                    properties['path_transactions'],
                                    properties['webhook'])

    # Run in loop
    while True:
            
        # Start
        start = time.time()
        
        try:
            # Get values
            messenger.get()

            # Post values
            messenger.post()

            # Post
            print(f'[{time.ctime()}] Posted message to discord.')
            
        except Exception as e:
            print(f'[{time.ctime()}] Error: {e}')
        
        # Stop
        stop = time.time()
        
        # Sleep
        time.sleep(properties['sec'] - (stop - start))
    