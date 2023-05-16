from flask import Flask, request, jsonify
import uuid
from datetime import datetime
import re
import logging
import math

app = Flask(__name__)

receipts = [] # in mem stored receipts


def calculate_points(receipt):
    '''
    Calculate points for a receipt based on the following rules:
        1. One point for every alphanumeric character in the retailer name.
        2. 50 points if the total is a round dollar amount with no cents.
        3. 25 points if the total is a multiple of 0.25.
        4. 5 points for every two items on the receipt.
        5. If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 and round up to the nearest integer. The result is the number of points earned.
        6. 6 points if the day in the purchase date is odd.
        7. 10 points if the time of purchase is after 2:00pm and before 4:00pm.
    Args:
        receipt (dict): Receipt object
    Returns:
        int: Points earned
    '''
    points = 0
    retailer = receipt.get("retailer")
    total = receipt.get("total")
    items = receipt.get("items")
    purchase_date = datetime.strptime(receipt.get("purchaseDate"), "%Y-%m-%d") # "2022-01-01"
    purchase_time = datetime.strptime(receipt.get("purchaseTime"), "%H:%M") # "13:01"

    points += sum(c.isalnum() for c in retailer)
    app.logger.debug("rule1 %d", points)
    total = float(total)  
    if total.is_integer():
        points += 50
        app.logger.debug("rule2 %d", points)
    if total % 0.25 == 0:
        points += 25
        app.logger.debug("rule3 %d", points)
    points += (len(items) // 2) * 5 
    app.logger.debug("rule4 %d", points)
    for item in items:
        if len(item.get("shortDescription").strip()) % 3 == 0:
            points += math.ceil(float(item.get("price")) * 0.2)
            app.logger.debug("rule5 %d", points)
    if purchase_date.day % 2 == 1:
        points += 6
        app.logger.debug("rule6 %d", points)
    if 14 <= purchase_time.hour <= 16: # 2pm - 4pm
        points += 10
        app.logger.debug("rule7 %d", points)
    return points

def validate(request):
    '''
    Validate the request matched the api.yml spec.
    1. Validate the request is valid json.
    2. Validate the required properties are present.
    3. Validate the property types.
    4. Validate the items are valid.
    Args:
        request (flask.request): The request object
    Returns:
        bool: True if the request is valid, False otherwise
    '''
    #validate json
    try:
       receipt = request.json 
    except Exception as e:
        app.logger.debug("request %s not valid json", request, e)
        return False
    # validate required properties
    for field in ["retailer", "purchaseDate", "purchaseTime", "items", "total"]:
        if field not in receipt:
            app.logger.debug("field %s not in receipt", field)
            return False
    # validate the property' types
    if type(receipt["retailer"]) != str or not bool(re.match("^\\S+$", receipt["retailer"])):
        app.logger.debug("retailer %s not valid", receipt["retailer"])
        return False
    if type(receipt["purchaseDate"]) != str:
        app.logger.debug("purchaseDate %s not valid str", receipt["purchaseDate"])
        return False
    else: 
        try:
            datetime.strptime(receipt["purchaseDate"], "%Y-%m-%d")
        except Exception:
            app.logger.debug("purchaseDate %s not valid", receipt["purchaseDate"])
            return False
    if type(receipt["purchaseTime"]) != str: 
        app.logger.debug("purchaseTime %s not valid str", receipt["purchaseTime"])
        return False
    else:
        try:
            datetime.strptime(receipt["purchaseTime"], "%H:%M")
        except Exception:
            app.logger.debug("purchaseTime %s not valid", receipt["purchaseTime"])
            return False
    if type(receipt["total"]) != str or not bool(re.match("^\\d+\\.\\d{2}$", receipt["total"])):
        app.logger.debug("total %s not valid", receipt["total"])
        return False
    # validate item
    items = receipt["items"]
    if len(items) < 1:
        app.logger.debug("items %s <1", items)
        return False
    else:
        try:
            item_itr = iter(items)
            while True:
                try:
                    item = next(item_itr)
                    for field in ["shortDescription", "price"]:
                        if field not in item:
                            app.logger.debug("field %s not in item", field)
                            return False
                    if type(item) != dict:
                        app.logger.debug("item %s not valid dict", item)
                        return False
                    if type(item["shortDescription"]) != str or not bool(re.match("^[\\w\\s\\-]+$", item["shortDescription"])):
                        app.logger.debug("shortDescription %s not valid", item["shortDescription"])
                        return False
                    if type(item["price"]) != str or not bool(re.match("^\\d+\\.\\d{2}$", item["price"])):
                        app.logger.debug("price %s not valid", item["price"])
                        return False
                except StopIteration:
                    break
        except Exception as e:
            app.logger.debug("items %s not valid", items, e)
            return False
    return True
            

@app.route('/receipts/process', methods=['POST'])
def process_receipt():
    '''
    This method handles POST /receipts/process endpoint and return the receipt id.
    This method validates the request and calculates the points as well.
    Args:
        None
    Returns:
        flask.Response: The response object is a json containing the receipt id or error messages
    '''
    if not validate(request):
        return jsonify({"error": "The receipt is invalid"}), 400
    receipt = request.json
    receipt_id = str(uuid.uuid4())
    points = calculate_points(receipt)
    receipts.append({"id": receipt_id, "points": points})
    return jsonify({"id": receipt_id}), 200

@app.route('/receipts/<id>/points', methods=['GET'])
def get_points(id):
    '''
    This method handles GET /receipts/<id>/points endpoint and return the points for the receipt id
    Args:
        id (str): The receipt id
    Returns:
        flask.Response: The response object is a json containing the points or error messages 
    '''
    for receipt in receipts:
        if receipt["id"] == id:
            return jsonify({"points": receipt["points"]}), 200
    return jsonify({"error": "No receipt found for that id"}), 404

if __name__ == '__main__':
    # start the server on port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
