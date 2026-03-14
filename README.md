# Crypto Portfolio Tracker

A command-line Python application that tracks cryptocurrency investments using the CoinGecko API and an SQLite database.
The program allows users to simulate buying and selling cryptocurrencies while maintaining a persistent portfolio and cash balance.

---

## Features

* Buy and sell cryptocurrency using real-time prices
* Fetch live market prices from the CoinGecko API
* Track cryptocurrency holdings in a SQLite database
* Maintain persistent cash balance across sessions
* Display current portfolio holdings with purchase prices
* Simple command-line interface for managing transactions

---

## Technologies Used

* Python
* SQLite
* REST API (CoinGecko API)
* Requests Library
* Environment Variables for secure API key storage

---

## Project Structure

```
crypto-portfolio-tracker
│
├── crypto_tracker.py      # Main application script
├── portfolio.sqlite       # SQLite database storing holdings
├── cash_balance.txt       # File storing current cash balance
├── README.md              # Project documentation
└── .gitignore             # Files excluded from GitHub
```

---

## Installation

1. Clone the repository

```
git clone https://github.com/yourusername/crypto-portfolio-tracker.git
```

2. Navigate to the project folder

```
cd crypto-portfolio-tracker
```

3. Install required libraries

```
pip install requests
```

---

## API Key Setup

The project uses the CoinGecko API.
Store your API key locally using environment variables.

Example (Windows):

```
set COINGECKO_API_KEY=your_api_key_here
```

The script reads the key using:

```
API_KEY = os.getenv("COINGECKO_API_KEY")
```

This keeps sensitive credentials secure and prevents them from being exposed in GitHub.

---

## Usage

Run the program:

```
python crypto_tracker.py
```

Example commands:

```
buy 0.5 bitcoin
sell 0.2 ethereum
show
quit
```

---

## Example Output

```
Enter action: buy 0.5 bitcoin
Bought 0.5 of bitcoin at 45000 USD each.

Enter action: show
Coin ID: bitcoin, Holdings: 0.5, Purchase Price: 45000 USD

Current cash balance: 7750 USD
```

---

## Future Improvements

* Portfolio profit/loss tracking
* Historical price analysis
* Data visualization of portfolio performance
* Web dashboard interface
* Support for multiple currencies

---

## Author

Amartya
B.Tech Engineering Physics
IIT Dharwad
