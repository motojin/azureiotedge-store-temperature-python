# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import time
import os
import sys
import asyncio
from six.moves import input
import threading
from azure.iot.device.aio import IoTHubModuleClient
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError

# Global configurations
STORAGE_CONNECTION_STRING = "< Local BLOB STORAGE CONNECTION STRING >"
STORAGE_CONTAINER_NAME = "localblobstorage"
STORAGE_LOCAL_PATH = "./UploadBlob"

async def main():
    try:
        if not sys.version >= "3.5.3":
            raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
        print ( "IoT Hub Client for Python" )

        # The client object is used to interact with your Azure IoT hub.
        module_client = IoTHubModuleClient.create_from_edge_environment()

        # connect the client.
        await module_client.connect()

        # initialize the local blob storage
        def init_local_blob():
            global STORAGE_CONNECTION_STRING
            global STORAGE_CONTAINER_NAME
            global STORAGE_LOCAL_PATH

            # Create BlobServiceClient from a Connection String
            blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)

            # Creates a new container
            try:
                new_container = blob_service_client.create_container(STORAGE_CONTAINER_NAME)
                properties = new_container.get_container_properties()
            except ResourceExistsError:
                print("Container already exists")
            
            # Make a local path for the blob to store temporarily
            os.makedirs(STORAGE_LOCAL_PATH, exist_ok=True)

            return blob_service_client 

        # upload input messages to the local blob storage
        def store_message_to_local_blob(blob_service_client, input_message):
            global STORAGE_CONTAINER_NAME
            global STORAGE_LOCAL_PATH

            # Create a file in your local folder to upload to a blob.
            local_filename = "MessageContents_" + str(datetime.now().strftime("%Y-%m-%dT%f")) + ".txt"
            upload_file_path = os.path.join(STORAGE_LOCAL_PATH, local_filename)            

            # Open the file and write the input message to it
            file = open(upload_file_path, 'w')
            file.write(input_message)
            file.close()

            # Create a blob client using the local file name as the name for the blob
            blob_client = blob_service_client.get_blob_client(container=STORAGE_CONTAINER_NAME, blob=local_filename)

            # Upload the created file
            with open(upload_file_path, "rb") as data:
                blob_client.upload_blob(data)
                print("uploaded blob : " + local_filename)

        # define behavior for receiving an input message on input1
        async def input1_listener(module_client):
            while True:
                input_message = await module_client.receive_message_on_input("input1")  # blocking call
                print("the data in the message received on input1 was ")
                print(input_message.data)
                print("custom properties are")
                print(input_message.custom_properties)
                print("forwarding mesage to output1")
                await module_client.send_message_to_output(input_message, "output1")
                # storing the message to the local blob
                store_message_to_local_blob(
                    blob_service_client,
                    str(input_message.data)
                )

        # define behavior for halting the application
        def stdin_listener():
            while True:
                try:
                    selection = input("Press Q to quit\n")
                    if selection == "Q" or selection == "q":
                        print("Quitting...")
                        break
                except:
                    time.sleep(10)

        # initialize the local blob
        blob_service_client = init_local_blob()
        
        # Schedule task for C2D Listener
        listeners = asyncio.gather(input1_listener(module_client))

        print ( "The sample is now waiting for messages. ")

        # Run the stdin listener in the event loop
        loop = asyncio.get_event_loop()
        user_finished = loop.run_in_executor(None, stdin_listener)

        # Wait for user to indicate they are done listening for messages
        await user_finished

        # Cancel listening
        listeners.cancel()

        # Finally, disconnect
        await module_client.disconnect()

    except Exception as e:
        print ( "Unexpected error %s " % e )
        raise

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

    # If using Python 3.7 or above, you can use following code instead:
    # asyncio.run(main())