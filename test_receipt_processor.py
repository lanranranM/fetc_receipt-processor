import unittest
import json
from receipt_processor import *
import logging

class ReceiptProcessorTestCases(unittest.TestCase):
    '''
    Test Cases for Receipt Processor API

    This class implements unit tests for the Receipt Processor API. Each method in the class
    represents a test case, and tests a specific functionality of the API, 
    including validation and calculation.
    '''

    def setUp(self):
        self.app = app
        self.client = self.app.test_client

    def test_post_valid(self):
        '''
        Test POST /receipts/process endpoint with valid payload
        
        This test case sends a POST request to correct endpoints with a valid payload, 
        and expects a 200 response code.
        '''
        correct_payload = {
            "retailer": "Target",
            "purchaseDate": "2022-01-01",
            "purchaseTime": "13:01",
            "items": [
                {
                    "shortDescription": "Mountain Dew 12PK",
                    "price": "6.49"
                }
            ],
            "total": "6.49"
        }

        response = self.client().post('/receipts/process', data=json.dumps(correct_payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_post_invalid_rule1(self):
        '''
        Test POST /receipts/process endpoint with invalid payload (non json data).
        '''

        response = self.client().post('/receipts/process', data="invalid_json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json().get('error', None), "The receipt is invalid")

    def test_post_invalid_rule2(self):
        response = self.client().post('/receipts/process', json={"invalid_field": "value"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json().get('error', None), "The receipt is invalid")
        
    def test_post_invalid_rule3(self):
        '''
        Test POST /receipts/process endpoint with invalid payload (invalid total).
        '''
        
        invalid_payload = {
            "retailer": "Target", 
            "purchaseDate": "2022-01-01", 
            "purchaseTime": "13:01", 
            "items": [{"shortDescription": "Mountain Dew 12PK", "price": "6.49"}],
            "total": "1.2.00"
        }
        response = self.client().post('/receipts/process', data=json.dumps(invalid_payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json().get('error', None), "The receipt is invalid")
        
    def test_post_invalid_rule4(self):
        '''
        Test POST /receipts/process endpoint with invalid payload (invalid item).
        '''
        
        invalid_items_payload = {
            "retailer": "", 
            "purchaseDate": "2022-01-01", 
            "purchaseTime": "13:01", 
            "items": [{"no_shortdescription": "Mountain Dew 12PK", "price": "6.49"}],
            "total": "1.2.00"
        }
        response = self.client().post('/receipts/process', data=json.dumps(invalid_items_payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json().get('error', None), "The receipt is invalid")
    
    def test_post_calculate_points_rule1(self):
        '''
        Test calculate_points_rule1 function with valid retailer name.
        '''
        
        receipt = {
            "retailer": "Target",
        }
        self.assertEqual(calculate_points_rule1(receipt), 6)
    
    def test_post_calculate_points_rule2(self):
        '''
        Test calculate_points_rule2 function with compliant or noncompliant total.
        '''
        
        receipt = {
            "total": "100.00",
        }
        receipt_noncompliant = {
            "total": "99.99",
        }
        self.assertEqual(calculate_points_rule2(receipt), 50)
        self.assertEqual(calculate_points_rule2(receipt_noncompliant), 0)
    
    def test_post_calculate_points_rule3(self):
        '''
        Test calculate_points_rule3 function with compliant or noncompliant total.
        '''
        
        receipt = {
            "total": "5.00",
        }
        receipt_noncompliant = {
            "total": "4.99",
        }
        self.assertEqual(calculate_points_rule3(receipt), 25)
        self.assertEqual(calculate_points_rule3(receipt_noncompliant), 0)
        
    def test_post_calculate_points_rule4(self):
        '''
        Test calculate_points_rule4 function with items.
        '''
        
        receipt = {
            "items": [
                {"shortDescription": "Item1", "price": "1.00"},
                {"shortDescription": "Item2", "price": "1.00"},
                {"shortDescription": "Item3", "price": "1.00"},
            ],
        }
        self.assertEqual(calculate_points_rule4(receipt), 5)
        
    def test_post_calculate_points_rule5(self):
        '''
        Test calculate_points_rule5 function with compliant or noncompliant items' short description.
        '''
        
        receipt = {
            "items": [
                {"shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ", "price": "12.00"}
            ],
        }
        receipt_noncompliant = {
            "items": [
                {"shortDescription": "Doritos Nacho Cheese", "price": "12.00"}
            ]
        }
        self.assertEqual(calculate_points_rule5(receipt), 3)
        self.assertEqual(calculate_points_rule5(receipt_noncompliant), 0)
        
    def test_post_calculate_points_rule6(self):
        '''
        Test calculate_points_rule6 function with compliant or noncompliant purchase date.
        '''
        
        receipt = {
            "purchaseDate": "2022-01-01",
        }
        receipt_noncompliant = {
            "purchaseDate": "2022-01-02",
        }
        self.assertEqual(calculate_points_rule6(receipt), 6)
        self.assertEqual(calculate_points_rule6(receipt_noncompliant), 0)
    
    def test_post_calculate_points_rule7(self):
        '''
        Test calculate_points_rule7 function with compliant or noncompliant purchase time.
        '''
        
        receipt = {
            "purchaseTime": "14:00",
        }
        receipt_noncompliant = {
            "purchaseTime": "08:13",
        }
        self.assertEqual(calculate_points_rule7(receipt), 10)
        self.assertEqual(calculate_points_rule7(receipt_noncompliant), 0)
    
    def test_post_calculate_points(self):
        '''
        Test calculate_points function with valid receipt.
        '''
        
        receipt = {
            "retailer": "M&M Corner Market",
            "purchaseDate": "2022-03-20",
            "purchaseTime": "14:33",
            "items": [
                {
                "shortDescription": "Gatorade",
                "price": "2.25"
                },{
                "shortDescription": "Gatorade",
                "price": "2.25"
                },{
                "shortDescription": "Gatorade",
                "price": "2.25"
                },{
                "shortDescription": "Gatorade",
                "price": "2.25"
                }
            ],
            "total": "9.00"
        }
        self.assertEqual(calculate_points(receipt), 109)
    
    def test_get_invalid(self):
        '''
        Test GET /receipts/<id>/points endpoint with invalid id.
        '''
        
        response = self.client().get('/receipts/fake_id/points')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json().get('error', None), "No receipt found for that id")
    

if __name__ == "__main__":
    print("!Running unit tests...")
    app.logger.debug("Running unit tests...")
    unittest.main()
