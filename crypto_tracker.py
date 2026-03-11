import requests
import sqlite3
import os
import sys


def load_cash_balance():
    try:
        with open('cash_balance.txt', 'r') as file:
            print('Cash balance loaded successfully.')
            return float(file.read().strip())
    except FileNotFoundError:
        print('Error: cash_balance.txt not found.')
        sys.exit(1)  # FIX 1: exit was missing (), it did nothing before
    except ValueError:
        print('Error: cash_balance.txt contains invalid data.')
        sys.exit(1)  # FIX 1: same fix here


def save_cash_balance(balance):
    with open('cash_balance.txt', 'w') as file:  # FIX 2: use context manager instead of bare open()
        file.write(str(balance))


cash_balance = load_cash_balance()

conn = sqlite3.connect('porfolio.sqlite')
cur = conn.cursor()
cur.executescript('''CREATE TABLE IF NOT EXISTS Portfolio (
               coin_id TEXT PRIMARY KEY,
               holdings REAL,
               avg_purchase_price REAL);''')  # FIX 3: renamed to avg_purchase_price to reflect what it actually stores

API_KEY = os.getenv("COINGECKO_API_KEY")

print("Commands: buy <amount> <coin_id> | sell <amount> <coin_id> | show | quit")

while True:
    # FIX 4: removed pointless action = list() line that was immediately overwritten
    user_input = input("\nEnter action: ").strip().lower()
    action = user_input.split()

    if not action:
        continue

    if action[0] == 'quit':
        save_cash_balance(cash_balance)
        conn.close()  # FIX 5: database connection was never closed
        print("Portfolio saved. Goodbye.")
        break

    elif action[0] == 'show':
        cur.execute('SELECT * FROM Portfolio')
        rows = cur.fetchall()
        if not rows:
            print("No holdings found.")
        else:
            print(f"\n{'Coin':<15} {'Holdings':<15} {'Avg Buy Price':<15}")
            print("-" * 45)
            for row in rows:
                print(f"{row[0]:<15} {row[1]:<15.6f} ${row[2]:<15.2f}")
        print(f"\nCash balance: ${cash_balance:.2f} USD")
        continue

    if len(action) < 3:
        print("Invalid command. Use: buy/sell <amount> <coin_id>")
        continue

    try:
        value = float(action[1].replace(',', '.'))
    except ValueError:
        print("Invalid amount. Please enter a number.")
        continue

    url = (
        "https://api.coingecko.com/api/v3/simple/price?ids="
        + action[2]
        + "&vs_currencies=usd&x_cg_demo_api_key="
        + API_KEY
    )
    headers = {"accept": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        continue

    data = response.json()
    if not data or action[2] not in data:
        print("Coin ID not found. Please try again.")
        continue

    current_price = data[action[2]]['usd']
    total_cost = current_price * value

    if action[0] == 'buy':
        if cash_balance >= total_cost:
            cash_balance -= total_cost
            cur.execute('SELECT holdings, avg_purchase_price FROM Portfolio WHERE coin_id = ?', (action[2],))
            existing = cur.fetchone()

            if existing is None:
                cur.execute(
                    '''INSERT INTO Portfolio (coin_id, holdings, avg_purchase_price) VALUES (?, ?, ?)''',
                    (action[2], value, current_price)
                )
            else:
                old_holdings, old_avg_price = existing
                new_holdings = old_holdings + value
                # FIX 6: calculate proper average cost basis instead of ignoring price on additional buys
                new_avg_price = ((old_holdings * old_avg_price) + (value * current_price)) / new_holdings
                cur.execute(
                    '''UPDATE Portfolio SET holdings = ?, avg_purchase_price = ? WHERE coin_id = ?''',
                    (new_holdings, new_avg_price, action[2])
                )

            conn.commit()
            print(f"Bought {value} of {action[2]} at ${current_price:.2f} USD each.")
            print(f"Total spent: ${total_cost:.2f} | Cash remaining: ${cash_balance:.2f}")
        else:
            print(f"Insufficient cash. Need ${total_cost:.2f}, have ${cash_balance:.2f}.")

    elif action[0] == 'sell':
        cur.execute('SELECT holdings FROM Portfolio WHERE coin_id = ?', (action[2],))
        holdings = cur.fetchone()

        if holdings is None or holdings[0] < value:
            print(f"Insufficient holdings. You own {holdings[0] if holdings else 0} of {action[2]}.")
        else:
            cash_balance += total_cost
            new_holdings = holdings[0] - value

            if new_holdings == 0:
                cur.execute('DELETE FROM Portfolio WHERE coin_id = ?', (action[2],))
            else:
                cur.execute(
                    '''UPDATE Portfolio SET holdings = ? WHERE coin_id = ?''',
                    (new_holdings, action[2])
                )
            conn.commit()
            print(f"Sold {value} of {action[2]} at ${current_price:.2f} USD each.")
            print(f"Total received: ${total_cost:.2f} | Cash balance: ${cash_balance:.2f}")

    else:
        print("Unknown command. Use: buy/sell <amount> <coin_id> | show | quit")