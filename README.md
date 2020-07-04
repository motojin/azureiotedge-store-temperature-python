# Store Temperature module on Azure IoT Edge

## .env

```
CONTAINER_REGISTRY_USERNAME=<USERNAME>
CONTAINER_REGISTRY_PASSWORD=<PASSWORD>
CONTAINER_REGISTRY_ADDRESS=<ADDRESS>.azurecr.io
```

## main.py

```python
# Global configurations
STORAGE_CONNECTION_STRING = "< Local BLOB STORAGE CONNECTION STRING >"
STORAGE_CONTAINER_NAME = "localblobstorage"
STORAGE_LOCAL_PATH = "./UploadBlob"
```

## BlobStorageEdge 

### Environment

```
            "env": {
              "LOCAL_STORAGE_ACCOUNT_KEY": {
                "value": "< LOCAL STORAGE ACCOUNT KEY >"
              },
              "LOCAL_STORAGE_ACCOUNT_NAME": {
                "value": "< LOCAL STORAGE ACCOUNT NAME >"
              }
            }
```

### Desired properties

```
    "BlobStorageEdge":{
      "properties.desired": {
        "deviceAutoDeleteProperties": {
          "deleteOn": true,
          "deleteAfterMinutes": 5,
          "retainWhileUploading": true
        },
        "deviceToCloudUploadProperties": {
          "uploadOn": true,
          "uploadOrder": "OldestFirst",
          "cloudStorageConnectionString": < Cloud Storage Connection String > ,
          "storageContainersForUpload": {
            "localblobstorage": {
              "target": "blobstorageedge"
            }
          },
          "deleteAfterUpload": true
        }
      }
    }
```