# Quai Network Mining Calculator

A simple and efficient calculator for estimating mining rewards on the Quai Network.

## Features

- Calculate daily, weekly, and monthly mining rewards
- Based on actual network parameters:
  - 3.5 Quai per workshare
  - 128,000 workshares per day
  - Rewards proportional to network hashrate share
- Example rewards table for different hashrate levels
- Simple, clean interface
- No server required - runs entirely in the browser

## Usage

1. Open `index.html` in your web browser
2. Enter your mining hashrate (in GH/s)
3. Enter the current network hashrate (in GH/s)
4. Click "Calculate" to see your estimated rewards

## Calculation Formula

The calculator uses the following formula for reward calculation:
```
Daily Reward = (Your Hashrate / Network Hashrate) * 128,000 * 3.5
```

Where:
- 128,000 is the number of workshares per day
- 3.5 is the Quai reward per workshare

## Example Rewards

The calculator includes example rewards for different hashrate levels, assuming a network hashrate of 400 GH/s:

| Hashrate (GH/s) | Daily Reward (QUAI) |
|-----------------|---------------------|
| 1 GH/s          | 1,120 QUAI         |
| 5 GH/s          | 5,600 QUAI         |
| 10 GH/s         | 11,200 QUAI        |
| 50 GH/s         | 56,000 QUAI        |
| 100 GH/s        | 112,000 QUAI       |

## Files

- `index.html`: The main calculator interface
- `templates/`: Contains the web application templates (if using server version)
- `app.py`: Flask web application (optional server version)
- `simple_server.py`: Simple HTTP server implementation (optional)

## License

MIT License