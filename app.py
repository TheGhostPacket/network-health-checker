from flask import Flask, render_template, jsonify, request
import requests
import sqlite3
import json
import time
import threading
from datetime import datetime, timedelta
import os
from urllib.parse import urlparse
import socket

app = Flask(__name__)

# Configuration
DATABASE = 'data/health_data.db'
DEFAULT_HOSTS = [
    'https://google.com',
    'https://github.com',
    'https://stackoverflow.com',
    'https://python.org',
    'https://flask.palletsprojects.com'
]

def init_db():
    """Initialize the database with required tables"""
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host TEXT NOT NULL,
            status TEXT NOT NULL,
            response_time REAL,
            status_code INTEGER,
            error_message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monitored_hosts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host TEXT UNIQUE NOT NULL,
            display_name TEXT,
            is_active INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def check_host_health(host):
    """Check the health of a single host"""
    start_time = time.time()
    
    try:
        # Ensure host has protocol
        if not host.startswith(('http://', 'https://')):
            host = 'https://' + host
        
        # Make request with timeout
        response = requests.get(host, timeout=10, allow_redirects=True)
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Determine status based on response time and status code
        if response.status_code == 200:
            if response_time < 500:
                status = 'online'
            elif response_time < 2000:
                status = 'slow'
            else:
                status = 'very_slow'
        else:
            status = 'error'
            
        return {
            'host': host,
            'status': status,
            'response_time': round(response_time, 2),
            'status_code': response.status_code,
            'error_message': None
        }
        
    except requests.exceptions.Timeout:
        return {
            'host': host,
            'status': 'timeout',
            'response_time': None,
            'status_code': None,
            'error_message': 'Request timeout (>10s)'
        }
    except requests.exceptions.ConnectionError:
        return {
            'host': host,
            'status': 'offline',
            'response_time': None,
            'status_code': None,
            'error_message': 'Connection failed'
        }
    except Exception as e:
        return {
            'host': host,
            'status': 'error',
            'response_time': None,
            'status_code': None,
            'error_message': str(e)
        }

def save_health_check(result):
    """Save health check result to database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO health_checks 
        (host, status, response_time, status_code, error_message)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        result['host'],
        result['status'],
        result['response_time'],
        result['status_code'],
        result['error_message']
    ))
    
    conn.commit()
    conn.close()

def get_monitored_hosts():
    """Get list of monitored hosts"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT host, display_name FROM monitored_hosts WHERE is_active = 1')
    hosts = cursor.fetchall()
    conn.close()
    
    if not hosts:  # If no hosts in database, use defaults
        add_default_hosts()
        return [(host, urlparse(host).netloc) for host in DEFAULT_HOSTS]
    
    return hosts

def add_default_hosts():
    """Add default hosts to the database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    for host in DEFAULT_HOSTS:
        display_name = urlparse(host).netloc
        cursor.execute('''
            INSERT OR IGNORE INTO monitored_hosts (host, display_name)
            VALUES (?, ?)
        ''', (host, display_name))
    
    conn.commit()
    conn.close()

def get_health_history(host, hours=24):
    """Get health check history for a specific host"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT status, response_time, timestamp 
        FROM health_checks 
        WHERE host = ? AND datetime(timestamp) >= datetime('now', '-{} hours')
        ORDER BY timestamp DESC
        LIMIT 100
    '''.format(hours), (host,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [{'status': r[0], 'response_time': r[1], 'timestamp': r[2]} for r in results]

# Routes
@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/health-check')
def api_health_check():
    """API endpoint to check health of all monitored hosts"""
    hosts = get_monitored_hosts()
    results = []
    
    for host, display_name in hosts:
        result = check_host_health(host)
        result['display_name'] = display_name
        
        # Save to database
        save_health_check(result)
        
        results.append(result)
    
    return jsonify({
        'results': results,
        'timestamp': datetime.now().isoformat(),
        'total_hosts': len(results)
    })

@app.route('/api/host-history/<path:host>')
def api_host_history(host):
    """Get health history for a specific host"""
    hours = request.args.get('hours', 24, type=int)
    history = get_health_history(host, hours)
    
    return jsonify({
        'host': host,
        'history': history,
        'period_hours': hours
    })

@app.route('/api/add-host', methods=['POST'])
def api_add_host():
    """Add a new host to monitor"""
    data = request.get_json()
    host = data.get('host', '').strip()
    
    if not host:
        return jsonify({'error': 'Host is required'}), 400
    
    # Add protocol if missing
    if not host.startswith(('http://', 'https://')):
        host = 'https://' + host
    
    display_name = data.get('display_name', urlparse(host).netloc)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO monitored_hosts (host, display_name)
            VALUES (?, ?)
        ''', (host, display_name))
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Host added successfully',
            'host': host,
            'display_name': display_name
        })
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Host already exists'}), 400
    finally:
        conn.close()

@app.route('/api/stats')
def api_stats():
    """Get overall statistics"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get stats from last 24 hours
    cursor.execute('''
        SELECT 
            COUNT(*) as total_checks,
            SUM(CASE WHEN status = 'online' THEN 1 ELSE 0 END) as online_count,
            AVG(CASE WHEN response_time IS NOT NULL THEN response_time END) as avg_response_time
        FROM health_checks 
        WHERE datetime(timestamp) >= datetime('now', '-24 hours')
    ''')
    
    stats = cursor.fetchone()
    conn.close()
    
    total_checks, online_count, avg_response_time = stats
    
    if total_checks > 0:
        uptime_percentage = (online_count / total_checks) * 100
    else:
        uptime_percentage = 0
    
    return jsonify({
        'total_checks': total_checks,
        'uptime_percentage': round(uptime_percentage, 2),
        'average_response_time': round(avg_response_time or 0, 2),
        'period': '24 hours'
    })

# Background monitoring (optional for continuous monitoring)
def background_monitor():
    """Background task to periodically check all hosts"""
    while True:
        try:
            hosts = get_monitored_hosts()
            for host, display_name in hosts:
                result = check_host_health(host)
                save_health_check(result)
            
            # Wait 5 minutes before next check
            time.sleep(300)
        except Exception as e:
            print(f"Background monitoring error: {e}")
            time.sleep(60)  # Wait 1 minute on error

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Start background monitoring in a separate thread (optional)
    # monitoring_thread = threading.Thread(target=background_monitor, daemon=True)
    # monitoring_thread.start()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)