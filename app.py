from flask import Flask, render_template_string
from pymongo import MongoClient

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DBMS Enterprise Architecture Lab</title>
    <style>
        :root {
            --bg: #0f172a;
            --card-bg: #1e293b;
            --text: #f1f5f9;
            --danger: #ef4444;
            --success: #22c55e;
            --accent: #38bdf8;
            --waitlist: #f59e0b;
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
        .stat-label { font-size: 0.8rem; text-transform: uppercase; opacity: 0.7; }
        
        /* Upgraded to a 3-Column Grid Layout */
        .grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
        
        .card { 
            background: var(--card-bg); 
            padding: 20px; 
            border-radius: 16px; 
            border: 1px solid #334155;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        .card.bad { border-top: 6px solid var(--danger); }
        .card.good { border-top: 6px solid var(--success); }
        .card.queue { border-top: 6px solid var(--waitlist); }
        
        h2 { margin-top: 0; display: flex; justify-content: space-between; align-items: center; font-size: 1.3rem; }
        .badge { font-size: 0.8rem; padding: 4px 12px; border-radius: 20px; }
        .bad .badge { background: #450a0a; color: #f87171; }
        .good .badge { background: #064e3b; color: #4ade80; }
        .queue .badge { background: #78350f; color: #fbbf24; }

        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th { text-align: left; padding: 10px; border-bottom: 2px solid #334155; font-size: 0.8rem; opacity: 0.8; }
        td { padding: 10px; border-bottom: 1px solid #334155; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; }
        tr:hover { background: rgba(255,255,255,0.03); }
        
        .summary { font-size: 0.85rem; margin-top: 5px; opacity: 0.9; }
        .highlight { font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Flash Sale Concurrency & Traffic Flow Lab</h1>
        <p>Comparative Analysis of Lost Updates against Thread-Safe Atomic Queues</p>
    </div>

    <div class="stats-bar">
        <div class="stat-item">
            <span class="stat-val">100</span>
            <span class="stat-label">Total Simulated Users</span>
        </div>
        <div class="stat-item">
            <span class="stat-val" style="color: var(--danger)">{{ "%.2f"|format(bad_avg_lat) }} ms</span>
            <span class="stat-label">Avg Latency (Non-Atomic)</span>
        </div>
        <div class="stat-item">
            <span class="stat-val" style="color: var(--success)">{{ "%.2f"|format(good_avg_lat) }} ms</span>
            <span class="stat-label">Avg Latency (Atomic)</span>
        </div>
        <div class="stat-item">
            <span class="stat-val" style="color: var(--waitlist)">{{ waitlist_orders|length }}</span>
            <span class="stat-label">Users Queued Safely</span>
        </div>
    </div>

    <div class="grid">
        <div class="card bad">
            <h2>Non-Atomic <span class="badge">Unsafe</span></h2>
            <div class="summary">
                Expectation: <span class="highlight">10</span> | Actual Sales: <span class="highlight" style="color:var(--danger)">{{ bad_orders|length }}</span>
            </div>
            <table>
                <thead>
                    <tr><th>User ID</th><th>DB Latency</th></tr>
                </thead>
                <tbody>
                    {% for o in bad_orders %}
                    <tr>
                        <td>User_{{ o.user_id }}</td>
                        <td style="color: var(--danger)">{{ "%.2f"|format(o.get('latency_ms', 0)) }} ms</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="card good">
            <h2>Atomic Update <span class="badge">Secured (10)</span></h2>
            <div class="summary">
                Expectation: <span class="highlight">10</span> | Actual Sales: <span class="highlight" style="color:var(--success)">{{ good_orders|length }}</span>
            </div>
            <table>
                <thead>
                    <tr><th>User ID</th><th>DB Latency</th></tr>
                </thead>
                <tbody>
                    {% for o in good_orders %}
                    <tr>
                        <td>User_{{ o.user_id }}</td>
                        <td style="color: var(--success)">{{ "%.2f"|format(o.get('latency_ms', 0)) }} ms</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="card queue">
            <h2>Diverted Queue <span class="badge" style="letter-spacing: 0.5px;">Waitlist</span></h2>
            <div class="summary">
                Total Overflow: <span class="highlight" style="color:var(--waitlist)">{{ waitlist_orders|length }} Users</span>
            </div>
            <table>
                <thead>
                    <tr><th>User ID</th><th>Queue Position</th></tr>
                </thead>
                <tbody>
                    {% for o in waitlist_orders %}
                    <tr>
                        <td>User_{{ o.user_id }}</td>
                        <td style="color: var(--waitlist)">#{{ o.queue_number }}</td>
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
    pipeline = [{"$group": {"_id": None, "avg_latency": {"$avg": "$latency_ms"}}}]
    result = list(collection.aggregate(pipeline))
    return result[0]["avg_latency"] if result else 0.0

@app.route('/')
def index():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["flash_sale_db"]
    
    bad = list(db.orders_bad.find().sort("timestamp", 1))
    good = list(db.orders_good.find().sort("timestamp", 1))
    waitlist = list(db.orders_waitlist.find().sort("queue_number", 1)) # Pull waitlist data
    
    bad_avg = get_avg_latency(db.orders_bad)
    good_avg = get_avg_latency(db.orders_good)
    
    client.close()
    return render_template_string(
        HTML_TEMPLATE, 
        bad_orders=bad, 
        good_orders=good, 
        waitlist_orders=waitlist,
        bad_avg_lat=bad_avg, 
        good_avg_lat=good_avg
    )

if __name__ == '__main__':
    app.run(debug=True)