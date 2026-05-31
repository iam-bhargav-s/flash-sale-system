from flask import Flask, render_template_string
from pymongo import MongoClient

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DBMS Concurrency & Telemetry Lab</title>
    <style>
        :root {
            --bg: #0f172a;
            --card-bg: #1e293b;
            --text: #f1f5f9;
            --danger: #ef4444;
            --success: #22c55e;
            --accent: #38bdf8;
            --telemetry: #a855f7;
        }
        body { 
            font-family: 'Inter', -apple-system, sans-serif; 
            background: var(--bg); 
            color: var(--text); 
            margin: 0; padding: 40px; 
        }
        .header { text-align: center; margin-bottom: 40px; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; color: var(--accent); }
        
        .stats-bar {
            background: var(--card-bg);
            padding: 20px;
            border-radius: 12px;
            display: flex;
            justify-content: space-around;
            margin-bottom: 40px;
            border: 1px solid #334155;
        }
        .stat-item { text-align: center; }
        .stat-val { display: block; font-size: 1.8rem; font-weight: bold; color: var(--accent); }
        .stat-val.bad-telemetry { color: var(--danger); }
        .stat-val.good-telemetry { color: var(--success); }
        .stat-label { font-size: 0.8rem; text-transform: uppercase; opacity: 0.7; }
        
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
        .card { 
            background: var(--card-bg); 
            padding: 25px; 
            border-radius: 16px; 
            border: 1px solid #334155;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        .card.bad { border-top: 6px solid var(--danger); }
        .card.good { border-top: 6px solid var(--success); }
        
        h2 { margin-top: 0; display: flex; justify-content: space-between; align-items: center; }
        .badge { font-size: 0.9rem; padding: 4px 12px; border-radius: 20px; }
        .bad .badge { background: #450a0a; color: #f87171; }
        .good .badge { background: #064e3b; color: #4ade80; }

        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th { text-align: left; padding: 12px; border-bottom: 2px solid #334155; font-size: 0.9rem; opacity: 0.8; }
        td { padding: 12px; border-bottom: 1px solid #334155; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; }
        tr:hover { background: rgba(255,255,255,0.03); }
        
        .summary { font-size: 0.9rem; margin-top: 10px; opacity: 0.9; display: flex; justify-content: space-between;}
        .highlight { font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Flash Sale Concurrency & Performance Lab</h1>
        <p>Live System Telemetry: Analyzing Execution Latency under Race Conditions</p>
    </div>

    <div class="stats-bar">
        <div class="stat-item">
            <span class="stat-val">100</span>
            <span class="stat-label">Total Simulated Requests</span>
        </div>
        <div class="stat-item">
            <span class="stat-val bad-telemetry">{{ "%.2f"|format(bad_avg_lat) }} ms</span>
            <span class="stat-label">Avg Latency (Non-Atomic)</span>
        </div>
        <div class="stat-item">
            <span class="stat-val good-telemetry">{{ "%.2f"|format(good_avg_lat) }} ms</span>
            <span class="stat-label">Avg Latency (Atomic)</span>
        </div>
    </div>

    <div class="grid">
        <div class="card bad">
            <h2>Non-Atomic <span class="badge">Unsafe</span></h2>
            <div class="summary">
                <span>Expectation: <span class="highlight">10</span> | Actual Sales: <span class="highlight" style="color:var(--danger)">{{ bad_orders|length }}</span></span>
            </div>
            <table>
                <thead>
                    <tr><th>User ID</th><th>Precise Timestamp</th><th>DB Latency</th></tr>
                </thead>
                <tbody>
                    {% for o in bad_orders %}
                    <tr>
                        <td>User_{{ o.user_id }}</td>
                        <td>{{ o.timestamp.strftime('%H:%M:%S.%f')[:-3] }}</td>
                        <td style="color: var(--danger)">{{ "%.2f"|format(o.get('latency_ms', 0)) }} ms</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="card good">
            <h2>Atomic Update <span class="badge">Thread-Safe</span></h2>
            <div class="summary">
                <span>Expectation: <span class="highlight">10</span> | Actual Sales: <span class="highlight" style="color:var(--success)">{{ good_orders|length }}</span></span>
            </div>
            <table>
                <thead>
                    <tr><th>User ID</th><th>Precise Timestamp</th><th>DB Latency</th></tr>
                </thead>
                <tbody>
                    {% for o in good_orders %}
                    <tr>
                        <td>User_{{ o.user_id }}</td>
                        <td>{{ o.timestamp.strftime('%H:%M:%S.%f')[:-3] }}</td>
                        <td style="color: var(--success)">{{ "%.2f"|format(o.get('latency_ms', 0)) }} ms</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

def get_avg_latency(collection):
    # MongoDB aggregation pipeline to compute average of latency_ms field
    pipeline = [{"$group": {"_id": None, "avg_latency": {"$avg": "$latency_ms"}}}]
    result = list(collection.aggregate(pipeline))
    return result[0]["avg_latency"] if result else 0.0

@app.route('/')
def index():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["flash_sale_db"]
    
    bad = list(db.orders_bad.find().sort("timestamp", 1))
    good = list(db.orders_good.find().sort("timestamp", 1))
    
    bad_avg = get_avg_latency(db.orders_bad)
    good_avg = get_avg_latency(db.orders_good)
    
    client.close()
    return render_template_string(HTML_TEMPLATE, bad_orders=bad, good_orders=good, bad_avg_lat=bad_avg, good_avg_lat=good_avg)

if __name__ == '__main__':
    app.run(debug=True)