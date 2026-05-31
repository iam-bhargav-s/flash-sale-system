from flask import Flask, render_template_string
from pymongo import MongoClient

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>DBMS Comparison: Concurrency Control</title>
    <style>
        body { font-family: sans-serif; display: flex; gap: 20px; padding: 20px; background: #f0f0f0; }
        .box { flex: 1; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
        .bad { border-top: 10px solid #e74c3c; }
        .good { border-top: 10px solid #2ecc71; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="box bad">
        <h2>NO Concurrency Control</h2>
        <p>Expectation: 10 | <b>Actual: {{ bad_orders|length }}</b></p>
        <table>
            <tr><th>User ID</th><th>Time</th></tr>
            {% for o in bad_orders %}
            <tr><td>{{ o.user_id }}</td><td>{{ o.timestamp.strftime('%H:%M:%S.%f')[:-3] }}</td></tr>
            {% endfor %}
        </table>
    </div>

    <div class="box good">
        <h2>WITH Concurrency Control</h2>
        <p>Expectation: 10 | <b>Actual: {{ good_orders|length }}</b></p>
        <table>
            <tr><th>User ID</th><th>Time</th></tr>
            {% for o in good_orders %}
            <tr><td>{{ o.user_id }}</td><td>{{ o.timestamp.strftime('%H:%M:%S.%f')[:-3] }}</td></tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["flash_sale_db"]
    bad = list(db.orders_bad.find().sort("timestamp", 1))
    good = list(db.orders_good.find().sort("timestamp", 1))
    return render_template_string(HTML_TEMPLATE, bad_orders=bad, good_orders=good)

if __name__ == '__main__':
    app.run(debug=True)