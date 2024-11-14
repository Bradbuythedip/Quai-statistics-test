#!/usr/bin/env python3
import http.server
import socketserver
import json
import requests
from datetime import datetime
import urllib.parse

class QuaiNetworkAnalyzer:
    def __init__(self):
        self.base_url = "http://rpc.sandbox.quai.network:9200"
        self.headers = {
            'Content-Type': 'application/json'
        }
        
        # Network constants
        self.QUAI_PER_WORKSHARE = 3.5
        self.WORKSHARES_PER_DAY = 128000
        self.BLOCKS_PER_DAY = 17280  # Assuming 5-second block time

    def make_rpc_call(self, method, params=[]):
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        response = requests.post(self.base_url, headers=self.headers, json=payload)
        return response.json()

    def get_network_stats(self):
        try:
            result = self.make_rpc_call("quai_blockNumber")
            latest_block = int(result['result'], 16)
            
            result = self.make_rpc_call("quai_getBlockByNumber", [hex(latest_block), True])
            latest_block_info = result['result']
            
            difficulty = int(latest_block_info['difficulty'], 16)
            hashrate = difficulty / 5  # Assuming 5-second block time
            
            daily_quai = self.WORKSHARES_PER_DAY * self.QUAI_PER_WORKSHARE
            
            return {
                'hashrate_gh': hashrate / 1e9,
                'difficulty': difficulty,
                'daily_workshares': self.WORKSHARES_PER_DAY,
                'quai_per_workshare': self.QUAI_PER_WORKSHARE,
                'daily_quai': daily_quai,
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            return {'error': str(e)}

class QuaiHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.analyzer = QuaiNetworkAnalyzer()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            with open('templates/index.html', 'r') as f:
                template = f.read()
            
            # Get network stats
            stats = self.analyzer.get_network_stats()
            
            # Generate example rewards
            example_hashrates = [1, 5, 10, 50, 100]
            example_rewards = []
            
            for hashrate in example_hashrates:
                proportion = hashrate / stats['hashrate_gh']
                daily_reward = proportion * stats['daily_quai']
                example_rewards.append({
                    'hashrate': hashrate,
                    'reward': daily_reward
                })
            
            # Replace template variables
            html = template.replace('{{ network_stats.hashrate_gh|round(2) }}', f"{stats['hashrate_gh']:.2f}")
            html = html.replace("{{ '{:,}'.format(network_stats.difficulty) }}", f"{stats['difficulty']:,}")
            html = html.replace("{{ '{:,}'.format(network_stats.daily_workshares) }}", f"{stats['daily_workshares']:,}")
            html = html.replace('{{ network_stats.quai_per_workshare }}', str(stats['quai_per_workshare']))
            html = html.replace("{{ '{:,.2f}'.format(network_stats.daily_quai) }}", f"{stats['daily_quai']:,.2f}")
            html = html.replace('{{ network_stats.last_updated }}', stats['last_updated'])
            
            # Replace example rewards
            example_rows = ""
            for example in example_rewards:
                example_rows += f"""
                <tr>
                    <td>{example['hashrate']} GH/s</td>
                    <td>{example['reward']:,.2f} QUAI</td>
                </tr>"""
            html = html.replace('{% for example in example_rewards %}', '')
            html = html.replace('{% endfor %}', '')
            html = html.replace('<td>{{ example.hashrate }} GH/s</td>', '')
            html = html.replace('<td>{{ \'{:,.2f}\'.format(example.reward) }} QUAI</td>', '')
            
            # Remove Jinja2 conditionals
            html = html.replace('{% if estimated_reward %}', '')
            html = html.replace('{% endif %}', '')
            
            self.wfile.write(html.encode())
        else:
            self.send_error(404)

def run():
    PORT = 8000
    print(f"Starting Quai Network Mining Calculator on port {PORT}...")
    print(f"Access the web interface at: http://127.0.0.1:{PORT}")
    
    with socketserver.TCPServer(("", PORT), QuaiHandler) as httpd:
        print("Server started")
        httpd.serve_forever()

if __name__ == "__main__":
    run()