from flask import Flask, request
import json
from config import COINBASE_COMMERCE_API_KEY

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if 'event' in data:
        event = data['event']
        if event['type'] == 'charge:confirmed':
            order_id = event['data']['metadata']['order_id']
            # Mark the order as paid in your system
            # Use the order_id to update the status in the orders list
            for order in orders:
                if order['order_id'] == order_id:
                    order['status'] = 'paid'
            save_orders()

    return "OK"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
