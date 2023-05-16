# fetch-receipt-processor
## testing  
For simplicity, I use ```curl``` command line tool to test the API.  
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
  ```
  Invalid case:

  - Test Get  

  Valid: case:
  ```
  curl http://localhost:5000/receipts/{id}/points >> get_output.txt

  ```
  Expected output:  
  ```
  { "points": 32 }
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
   ```
