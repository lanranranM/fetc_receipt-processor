# fetch-receipt-processor
## Introduction
The recipt processor API has GET and POST methods. See [details here](https://github.com/fetch-rewards/receipt-processor-challenge) or api.yml in the directory.

## How to start
The API depends on Python>=3.8 and Flask >=2.3.2.  
1. build the image. For details, please refer to the Dockerfile. 
```
docker build -t receipt-processor .
```
2. run the image. This command map container's port 5000 to host's 5000. 
```
docker run -p 5000:5000 receipt-processor
```
to run the image in testing mode (unit testers)
```
docker run -e APP_MODE=test receipt-processor
```  
3. Since there is not frontend implementation, you can manually test the API via Postman or curl command line tool. Please refer to the testing section below.
4. To stop the running container: press ctrl+C or ```docker stop <container_id>```

## Manually Testing  
For simplicity, I use ```curl``` command line tool to test the API.   
Keep the container with webserver running, and in a new terminal session: 
- Test Post  

Valid case:  
```  
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{
      "retailer": "Target",
      "purchaseDate": "2022-01-01",
      "purchaseTime": "13:01",
      "items": [
        {
          "shortDescription": "Mountain Dew 12PK",
          "price": "6.49"
        },
        {
          "shortDescription": "Emils Cheese Pizza",
          "price": "12.25"
        },
        {
          "shortDescription": "Knorr Creamy Chicken",
          "price": "1.26"
        },
        {
          "shortDescription": "Doritos Nacho Cheese",
          "price": "3.35"
        },
        {
          "shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ",
          "price": "12.00"
        }
      ],
      "total": "35.35"
    }' \
  http://localhost:5000/receipts/process >> post_output.txt
  ```
  Expected output:
  ```
  { "id": "7fb1377b-b223-49d9-a31a-5a02701dd310" }
  with status code 200
  ```
  Invalid case:  
  ```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{
    "retailer": "target",
    "purchaseDate": "2022-01-02",
    "purchaseTime": "13:13",
    "total": "1.25.2",
    "items": [
        {"shortDescription": "Pepsi - 12-oz", "price": "1.25"}
    ]
}' \
  http://localhost:5000/receipts/process > post_output.txt
  ```
Expected Output:  
```
{"error": "The receipt is invalid"}
with status code 400
```

  - Test Get  

  Valid: case:
  ```
  curl http://localhost:5000/receipts/{id}/points >> get_output.txt
  ```
  Expected output:  
  ```
  { "points": 32 }
  with status code 200
  ```  
  Invalid case:
  ```
curl http://localhost:5000/receipts/{invalid-id}/points >> get_output.txt
   ```
   Expected output:
   ```
   {
  "error": "No receipt found for that id"
   }
   with status code 404
   ```

## What's next?
- Frontend implementation
- Store the data in the dataset for future sake. The data is stored in memory now. 
- how to handle existing receipt? now we handle each post request as a new receipt. 
