import requests
import sqlite3
import os
def load_cash_balance():
    try:
        with open('cash_balance.txt', 'r') as file:
            print('Cash balance loaded successfully.')
            return float(file.read().strip())
    except FileNotFoundError:
        print('File not found.')
        exit
    except ValueError:
        print('Value Error')
        exit
cash_balance = load_cash_balance()
conn = sqlite3.connect('porfolio.sqlite')
cur = conn.cursor()
cur.executescript('''CREATE TABLE IF NOT EXISTS Portfolio (
               coin_id TEXT PRIMARY KEY,
               holdings REAL,
               purchase_price REAL);''')


API_KEY = os.getenv("COINGECKO_API_KEY")
#url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&x_cg_demo_api_key=" + API_KEY
while True:    
    action = list()
    action = input("Enter action: ")
    action = action.split()
    
    if action[0] == 'quit':
        open('cash_balance.txt', 'w').write(str(cash_balance))
        break
    elif action[0] == 'show':
        cur.execute('SELECT * FROM Portfolio')
        rows = cur.fetchall()
        if not rows:
            print("No holdings found.")
        else:
            for row in rows:
                print(f"Coin ID: {row[0]}, Holdings: {row[1]}, Purchase Price: {row[2]} USD")
        continue
    
    if len(action) < 3:
        print("Invalid command. Use: BUY/SELL <amount> <coin_id>")
        continue
    
    value = float(action[1].replace(',', '.'))    
    url = "https://api.coingecko.com/api/v3/simple/price?ids=" + action[2] + "&vs_currencies=usd&x_cg_demo_api_key=" + API_KEY
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.json() == {}:
        print("Coin ID not found. Please try again.")
        continue
    else:
        #print("Price of", action[2], "is", response.json()[action[2]]['usd'], "USD")
        price = response.json()[action[2]]['usd'] * value
        if action[0] == 'buy':
            if cash_balance >= price:
                cash_balance -= price
                cur.execute('SELECT holdings FROM Portfolio WHERE coin_id = ?', (action[2], ))
                existing = cur.fetchone()
                if existing is None:
                    cur.execute('''INSERT INTO Portfolio (coin_id, holdings, purchase_price) 
                                   VALUES (?, ?, ?)''', (action[2], value, response.json()[action[2]]['usd']))
                else:
                    cur.execute('''UPDATE Portfolio SET holdings = holdings + ? WHERE coin_id = ?''', (value, action[2]))
                conn.commit()
                print(f"Bought {value} of {action[2]} at {response.json()[action[2]]['usd']} USD each.")
            else:
                print("Insufficient cash balance.")
        elif action[0] == 'sell':
            cur.execute('SELECT holdings FROM Portfolio WHERE coin_id = ?', (action[2], ))
            holdings = cur.fetchone()
            if holdings is None or holdings[0] < value:
                print("Insufficient holdings to sell.")
            else:
                cash_balance += price
                new_holdings = holdings[0] - value
                if new_holdings == 0:
                    cur.execute('DELETE FROM Portfolio WHERE coin_id = ?', (action[2], ))
                    conn.commit()
                else:
                    cur.execute('''UPDATE Portfolio SET holdings = holdings - ? WHERE coin_id = ?''', (value, action[2]))
                    conn.commit()
                print(f"Sold {value} of {action[2]} at {response.json()[action[2]]['usd']} USD each.")
        print(f"Current cash balance: {cash_balance} USD")
    