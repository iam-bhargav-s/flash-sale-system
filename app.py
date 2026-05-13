from flask import Flask, render_template_string
from pymongo import MongoClient

app = Flask(__name__)

# This is the "Skin" of your website (HTML/CSS)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Flash Sale Admin Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #e9ecef; }
        .container { background: white; padding: 20px; border-radius: 10px; shadow: 0px 4px 8px rgba(0,0,0,0.1); }
        h2 { color: #2c3e50; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; border: 1px solid #dee2e6; text-align: left; }
        th { background-color: #4CAF50; color: white; }
        tr:nth-child(even) { background-color: #f8f9fa; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Live Order Audit Trail (NoSQL Results)</h2>
        <p>This table shows successful transactions recorded in the <b>orders</b> collection.</p>
        <table>
            <tr>
                <th>Order ID</th>
                <th>User Reference</th>
                <th>Time of Purchase</th>
            </tr>
            {% for order in orders %}
            <tr>
                <td>{{ order['_id'] }}</td>
                <td>User_{{ order['user_id'] }}</td>
                <td>{{ order['timestamp'].strftime('%H:%M:%S') }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    # Connect to your local MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["flash_sale_db"]
    
    # Get all orders from the 'orders' collection, newest first
    orders = list(db["orders"].find().sort("timestamp", 1))
    
    # Send the data to the HTML template above
    return render_template_string(HTML_TEMPLATE, orders=orders)

if __name__ == '__main__':
    # Start the web server
    print("Website starting at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)