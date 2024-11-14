#!/usr/bin/env python3
from flask import Flask, render_template, request
import requests
import json
from datetime import datetime
from dataclasses import dataclass
import time

app = Flask(__name__)

@dataclass
class NetworkStats:
    hashrate_gh: float
    difficulty: int
    daily_workshares: int
    quai_per_workshare: float
    daily_quai: float
    last_updated: str

@dataclass
class EstimatedReward:
    daily: float
    weekly: float
    monthly: float

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

    def get_block_number(self):
        result = self.make_rpc_call("quai_blockNumber")
        return int(result['result'], 16)

    def get_block_info(self, block_number):
        result = self.make_rpc_call("quai_getBlockByNumber", [hex(block_number), True])
        return result['result']

    def calculate_network_hashrate(self, block_info):
        difficulty = int(block_info['difficulty'], 16)
        hashrate = difficulty / 5  # Assuming 5-second block time
        return hashrate

    def get_network_stats(self):
        latest_block = self.get_block_number()
        blocks_to_analyze = 10  # Use last 10 blocks for average
        total_hashrate = 0
        samples = 0
        
        for block_num in range(latest_block, latest_block - blocks_to_analyze, -1):
            try:
                block_info = self.get_block_info(block_num)
                hashrate = self.calculate_network_hashrate(block_info)
                total_hashrate += hashrate
                samples += 1
            except Exception as e:
                print(f"Error processing block {block_num}: {str(e)}")
                continue
        
        if samples > 0:
            avg_network_hashrate = total_hashrate / samples
            latest_block_info = self.get_block_info(latest_block)
            current_difficulty = int(latest_block_info['difficulty'], 16)
            
            daily_quai = self.WORKSHARES_PER_DAY * self.QUAI_PER_WORKSHARE
            
            return NetworkStats(
                hashrate_gh=avg_network_hashrate / 1e9,
                difficulty=current_difficulty,
                daily_workshares=self.WORKSHARES_PER_DAY,
                quai_per_workshare=self.QUAI_PER_WORKSHARE,
                daily_quai=daily_quai,
                last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        return None

    def calculate_rewards(self, hashrate_gh, network_stats):
        network_hashrate_gh = network_stats.hashrate_gh
        proportion = hashrate_gh / network_hashrate_gh
        daily_reward = proportion * network_stats.daily_quai
        
        return EstimatedReward(
            daily=daily_reward,
            weekly=daily_reward * 7,
            monthly=daily_reward * 30
        )

# Initialize analyzer
analyzer = QuaiNetworkAnalyzer()

@app.route('/')
def index():
    network_stats = analyzer.get_network_stats()
    
    # Example rewards for different hashrates
    example_hashrates = [1, 5, 10, 50, 100]
    example_rewards = []
    
    for hashrate in example_hashrates:
        reward = analyzer.calculate_rewards(hashrate, network_stats)
        example_rewards.append({
            'hashrate': hashrate,
            'reward': reward.daily
        })
    
    return render_template('index.html', 
                         network_stats=network_stats,
                         example_rewards=example_rewards)

@app.route('/calculate', methods=['POST'])
def calculate():
    network_stats = analyzer.get_network_stats()
    hashrate = float(request.form['hashrate'])
    estimated_reward = analyzer.calculate_rewards(hashrate, network_stats)
    
    example_hashrates = [1, 5, 10, 50, 100]
    example_rewards = []
    
    for h in example_hashrates:
        reward = analyzer.calculate_rewards(h, network_stats)
        example_rewards.append({
            'hashrate': h,
            'reward': reward.daily
        })
    
    return render_template('index.html',
                         network_stats=network_stats,
                         estimated_reward=estimated_reward,
                         example_rewards=example_rewards)

if __name__ == '__main__':
    print("Starting Quai Network Mining Calculator...")
    print("Access the web interface at: http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)