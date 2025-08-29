from flask import Flask, render_template, jsonify, request
import requests
import time
from datetime import datetime
import os

app = Flask(__name__)

# In-memory storage for monitored hosts (simple fix)
MONITORED_HOSTS = [
    {'host': 'https://google.com', 'display_name': 'Google'},
    {'host': 'https://github.com', 'display_name': 'GitHub'},
    {'host': 'https://stackoverflow.com', 'display_name': 'Stack Overflow'},
    {'host': 'https://python.org', 'display_name': 'Python.org'},
    {'host': 'https://flask.palletsprojects.com', 'display_name': 'Flask'}
]

def check_host_health(host):
    """Check the health of a single host"""
    start_time = time.time()
    
    try:
        # Ensure host has protocol
        if not host.startswith(('http://', 'https://')):
            host = 'https://' + host
        
        # Make request with timeout
        response = requests.get(host, timeout=10, allow_redirects=True, 
                              headers={'User-Agent': 'HealthChecker/1.0'})
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

def validate_host(host):
    """Basic host validation"""
    if not host or len(host.strip()) == 0:
        return False, "Host cannot be empty"
    
    host = host.strip()
    
    # Add protocol if missing
    if not host.startswith(('http://', 'https://')):
        host = 'https://' + host
    
    # Basic URL validation
    if '.' not in host:
        return False, "Invalid host format"
    
    return True, host

# Routes
@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/health-check')
def api_health_check():
    """API endpoint to check health of all monitored hosts"""
    results = []
    
    try:
        for host_info in MONITORED_HOSTS:
            host = host_info['host']
            display_name = host_info['display_name']
            
            result = check_host_health(host)
            result['display_name'] = display_name
            results.append(result)
        
        return jsonify({
            'results': results,
            'timestamp': datetime.now().isoformat(),
            'total_hosts': len(results)
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Health check failed: {str(e)}',
            'results': [],
            'timestamp': datetime.now().isoformat(),
            'total_hosts': 0
        }), 500

@app.route('/api/add-host', methods=['POST'])
def api_add_host():
    """Add a new host to monitor"""
    try:
        # Get JSON data
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        host = data.get('host', '').strip()
        display_name = data.get('display_name', '').strip()
        
        # Validate host
        is_valid, processed_host_or_error = validate_host(host)
        if not is_valid:
            return jsonify({'error': processed_host_or_error}), 400
        
        processed_host = processed_host_or_error
        
        # Check if host already exists
        for existing_host in MONITORED_HOSTS:
            if existing_host['host'].lower() == processed_host.lower():
                return jsonify({'error': 'Host already exists'}), 400
        
        # Generate display name if not provided
        if not display_name:
            # Extract domain from URL
            try:
                from urllib.parse import urlparse
                parsed = urlparse(processed_host)
                display_name = parsed.netloc or processed_host
            except:
                display_name = processed_host
        
        # Add host to monitored list
        new_host = {
            'host': processed_host,
            'display_name': display_name
        }
        MONITORED_HOSTS.append(new_host)
        
        return jsonify({
            'success': True,
            'message': 'Host added successfully',
            'host': processed_host,
            'display_name': display_name
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to add host: {str(e)}'
        }), 500

@app.route('/api/remove-host', methods=['POST'])
def api_remove_host():
    """Remove a host from monitoring"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        host = data.get('host', '').strip()
        if not host:
            return jsonify({'error': 'Host is required'}), 400
        
        # Find and remove host
        for i, existing_host in enumerate(MONITORED_HOSTS):
            if existing_host['host'].lower() == host.lower():
                removed_host = MONITORED_HOSTS.pop(i)
                return jsonify({
                    'success': True,
                    'message': 'Host removed successfully',
                    'removed_host': removed_host
                })
        
        return jsonify({'error': 'Host not found'}), 404
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to remove host: {str(e)}'
        }), 500

@app.route('/api/stats')
def api_stats():
    """Get overall statistics (simplified)"""
    try:
        # For demo purposes, return static stats
        # In a real app, this would calculate from stored data
        return jsonify({
            'total_checks': 150,
            'uptime_percentage': 98.5,
            'average_response_time': 245.3,
            'period': '24 hours'
        })
    except Exception as e:
        return jsonify({
            'error': f'Failed to get stats: {str(e)}',
            'total_checks': 0,
            'uptime_percentage': 0,
            'average_response_time': 0,
            'period': '24 hours'
        }), 500

@app.route('/api/hosts')
def api_hosts():
    """Get list of monitored hosts"""
    try:
        return jsonify({
            'hosts': MONITORED_HOSTS,
            'total': len(MONITORED_HOSTS)
        })
    except Exception as e:
        return jsonify({
            'error': f'Failed to get hosts: {str(e)}',
            'hosts': [],
            'total': 0
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('index.html'), 500

@app.errorhandler(405)
def method_not_allowed(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Method not allowed'}), 405
    return render_template('index.html'), 405

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)