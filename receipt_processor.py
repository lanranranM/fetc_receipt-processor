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

@app.route('/receipts/process', methods=['POST'])
def process_receipt():
    receipt = request.json
    receipt_id = str(uuid.uuid4())
    points = calculate_points(receipt)
    receipts.append({"id": receipt_id, "points": points})
    return jsonify({"id": receipt_id}), 200

@app.route('/receipts/<id>/points', methods=['GET'])
def get_points(id):
    for receipt in receipts:
        if receipt["id"] == id:
            return jsonify({"points": receipt["points"]}), 200
    return jsonify({"error": "Receipt not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
