import requests
from datetime import datetime, timedelta

def normalize_time(dt):
    # если dt это объект datetime, приводим к строке
    if isinstance(dt, datetime):
        dt = dt.strftime("%Y-%m-%d %H:%M:%S")
    time_part = dt.split()[1]
    if time_part > '23:00:00':
        dt = dt.split()[0] + ' 23:00:00'
    elif time_part < '07:00:00':
        dt = dt.split()[0] + ' 07:00:00'
    return dt


def get_moex_price(ticker: str, dt: str) -> float:
    base_url = "https://iss.moex.com/iss/engines/stock/markets/shares/securities"
    dt_encoded = dt.replace(' ', '%20')
    url = f"{base_url}/{ticker}/candles.json?from={dt_encoded}&till={dt_encoded}&interval=1"
    resp = requests.get(url)
    data = resp.json()
    candles = data.get('candles', {}).get('data', [])
    if not candles:
        return None
    close_idx = data['candles']['columns'].index('close')
    return candles[0][close_idx]

def find_next_trading_day_price(ticker: str, dt: str, max_days=14):
    # Сначала нормализуем время
    t = datetime.strptime(normalize_time(dt), "%Y-%m-%d %H:%M:%S")
    for _ in range(max_days):  # Поиск максимум на 2 недели вперед
        dt_str = t.strftime("%Y-%m-%d %H:%M:%S")
        price = get_moex_price(ticker, dt_str)
        if price is not None:
            return t, price
        t += timedelta(days=1)
    return None, None

def get_prices_with_offsets(ticker: str, dt: str):
    # Находим цену на ближайший торговый день и дату
    nearest_day, nearest_price = find_next_trading_day_price(ticker, dt)
    if nearest_day is None:
        return None, None, None
    # Цены через день и через неделю от найденного дня
    price_day, price1 = find_next_trading_day_price(
        ticker, (nearest_day + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    )
    price_week, price7 = find_next_trading_day_price(
        ticker, (nearest_day + timedelta(weeks=1)).strftime("%Y-%m-%d %H:%M:%S")
    )
    return nearest_price, price1, price7

if __name__ == "__main__":# Пример использования:
    price0, price1, price7 = get_prices_with_offsets('SBER', '2025-9-30 23:55:00')
    print(price0, price1, price7)
