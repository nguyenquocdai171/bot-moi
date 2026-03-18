import pandas as pd
import numpy as np
import time
import os
import yfinance as yf
from datetime import datetime, timedelta

def load_sector_database():
    """Đọc danh sách mã và ngành trực tiếp từ file CSV (Không dùng danh sách cứng nữa)"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path_1 = os.path.join(current_dir, 'data', 'database_nganh.csv')
    path_2 = os.path.join(current_dir, 'database_nganh.csv')
    
    if os.path.exists(path_1): return pd.read_csv(path_1)
    elif os.path.exists(path_2): return pd.read_csv(path_2)
    else: raise FileNotFoundError("Không tìm thấy file database_nganh.csv! Hãy chạy prepare_sectors.py trước.")

def calculate_rsi(prices, period=14):
    """Tính RSI sử dụng Vectorization của Pandas."""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).ewm(span=period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(span=period, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def optimize_ma_sl_vectorized(df):
    """
    Backtest Vectorized tìm MA và Stop-loss tối ưu.
    Dùng NumPy Broadcasting cực nhanh, không gây treo máy.
    """
    if len(df) < 210:
        return 50, 0.05, df['Close'].rolling(50).mean()

    close_arr = df['Close'].values
    returns = np.diff(close_arr) / close_arr[:-1]
    returns = np.insert(returns, 0, 0)
    
    ma_windows = np.arange(5, 210, 5)
    ma_matrix = np.array([df['Close'].rolling(w).mean().values for w in ma_windows])
    
    signals = (close_arr > ma_matrix).astype(int)
    signals = np.roll(signals, 1, axis=1)
    signals[:, 0] = 0
    
    strategy_returns = signals * returns
    # Chỉnh lại biên độ Stoploss từ 3.0% đến 10.0%, bước nhảy 0.5% theo đúng UI
    sl_levels = np.arange(0.03, 0.105, 0.005)
    
    best_ma_idx = 0
    best_sl = 0.03
    max_cum_return = -np.inf

    for i, ma_ret in enumerate(strategy_returns):
        for sl in sl_levels:
            adj_ret = np.where(ma_ret < -sl, -sl, ma_ret)
            cum_return = np.prod(1 + adj_ret) - 1
            if cum_return > max_cum_return:
                max_cum_return = cum_return
                best_ma_idx = i
                best_sl = sl

    opt_ma_window = ma_windows[best_ma_idx]
    opt_ma_series = df['Close'].rolling(opt_ma_window).mean()
    
    return opt_ma_window, best_sl, opt_ma_series

def fetch_and_process_market_data():
    """Hàm main: Dùng yfinance tải dữ liệu HÀNG LOẠT (Bulk) cực nhanh để tránh treo máy"""
    db_nganh = load_sector_database()
    tickers = db_nganh['Ticker'].tolist()
    
    print(f"🚀 Bắt đầu crawl dữ liệu {len(tickers)} mã từ file database...")
    
    # Tạo danh sách gom cả đuôi .VN và .HN để quét 1 lần duy nhất (Bulk Download)
    yf_tickers = [f"{t}.VN" for t in tickers] + [f"{t}.HN" for t in tickers]
    
    print("⏳ Đang tải dữ liệu Hàng loạt từ Yahoo Finance (Sẽ mất khoảng 1-2 phút)...")
    # Tải Bulk Download (Nhanh gấp hàng trăm lần so với tải từng mã và dùng time.sleep)
    data = yf.download(yf_tickers, period="2y", interval="1d", progress=True)
    
    if data.empty or 'Close' not in data:
        raise ValueError("❌ Không thể tải dữ liệu từ Yahoo Finance.")
        
    if isinstance(data.columns, pd.MultiIndex):
        close_data = data['Close']
    else:
        close_data = pd.DataFrame({yf_tickers[0]: data['Close']})
        
    all_data = []
    print(f"✅ Tải xong! Đang tính toán ma trận siêu tốc cho từng mã...")
    
    for index, row in db_nganh.iterrows():
        ticker = row['Ticker']
        sector = row['Sector']
        
        main_vn = f"{ticker}.VN"
        main_hn = f"{ticker}.HN"
        
        # Dò tìm Ticker hợp lệ có dữ liệu
        valid_sym = None
        if main_vn in close_data.columns and not close_data[main_vn].dropna().empty:
            valid_sym = main_vn
        elif main_hn in close_data.columns and not close_data[main_hn].dropna().empty:
            valid_sym = main_hn
            
        if not valid_sym:
            continue
            
        # Rút trích dữ liệu của 1 mã
        df_ticker = pd.DataFrame({'Close': close_data[valid_sym].dropna()})
        
        # Cổ phiếu quá mới không đủ để tính toán
        if len(df_ticker) < 30:
            continue
            
        df_ticker['Ticker'] = ticker
        df_ticker['Sector'] = sector
        
        # Tính toán chỉ số & Siêu tối ưu
        df_ticker['RSI'] = calculate_rsi(df_ticker['Close'], 14)
        opt_ma, opt_sl, ma_series = optimize_ma_sl_vectorized(df_ticker)
        df_ticker['Opt_MA_Period'] = opt_ma
        df_ticker['Opt_SL'] = opt_sl
        df_ticker['Opt_MA_Value'] = ma_series
        
        # Định dạng lại cột Date
        df_ticker = df_ticker.reset_index()
        df_ticker.rename(columns={'index': 'Date', 'Date': 'Date'}, inplace=True)
        df_ticker['Date'] = pd.to_datetime(df_ticker['Date']).dt.tz_localize(None)
        
        all_data.append(df_ticker)

    if not all_data:
        raise ValueError("Không có dữ liệu nào được thu thập!")

    print("\n⏳ Đang phân tích Ma trận tín hiệu & Cấp độ ngành theo Luật chuẩn...")
    market_df = pd.concat(all_data, ignore_index=True)
    
    # --- TÍNH TOÁN CẤP ĐỘ NGÀNH (SECTOR TREND) BẰNG VECTORIZATION ---
    market_df['Sector_RSI'] = market_df.groupby(['Date', 'Sector'])['RSI'].transform('mean')
    
    # Cập nhật mốc Trend Ngành (<= 40 là Downtrend, > 60 là Uptrend)
    market_df['Sector_Trend'] = np.select(
        [market_df['Sector_RSI'] <= 40, market_df['Sector_RSI'] > 60],
        ['Downtrend', 'Uptrend'],
        default='Bình thường'
    )
    
    # --- MA TRẬN TÍN HIỆU & CẢNH BÁO LÕI (LOGIC MỚI CHUẨN ĐỒNG BỘ VỚI UI) ---
    cond_buy_base = (market_df['Close'] < market_df['Opt_MA_Value']) & (market_df['RSI'] < 30)
    cond_sell_base = (market_df['Close'] > market_df['Opt_MA_Value']) & (market_df['RSI'] > 70)
    
    # Các điều kiện cắt lớp RSI Ngành
    cond_sec_low = market_df['Sector_RSI'] <= 40
    cond_sec_mid = (market_df['Sector_RSI'] > 40) & (market_df['Sector_RSI'] <= 60)
    cond_sec_high = market_df['Sector_RSI'] > 60
    
    conditions = [
        # TH MUA
        cond_buy_base & cond_sec_low,
        cond_buy_base & cond_sec_mid,
        cond_buy_base & cond_sec_high,
        # TH BÁN
        cond_sell_base & cond_sec_high,
        cond_sell_base & cond_sec_mid,
        cond_sell_base & cond_sec_low
    ]
    
    choices = [
        # TEXT CHO MUA
        "KHOAN MUA (Mã quá bán nhưng Ngành downtrend)",
        "MUA BÌNH THƯỜNG (Giá < MA, RSI < 30, Ngành ổn định)",
        "KHÔNG NÊN MUA (Ngành bay cao nhưng mã cắm đầu)",
        # TEXT CHO BÁN
        "KHOAN BÁN (Mã quá mua nhưng Ngành siêu hưng phấn -> Gồng Lãi)",
        "BÁN BÌNH THƯỜNG (Mã chạm đỉnh, Ngành bình thường)",
        "BÁN NGAY LẬP TỨC (Ngành sụp, mã rướn lên -> Chốt ngay)"
    ]
    
    market_df['Signal'] = np.select(conditions, choices, default="QUAN SÁT (WAIT)")
    
    # Lưu file EOD local cho Streamlit App đọc
    os.makedirs('data', exist_ok=True)
    output_path = 'data/market_data.csv'
    market_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n🎉 [HOÀN THÀNH] Data Pipeline thành công mỹ mãn. Dữ liệu lưu tại: {output_path}")

if __name__ == "__main__":
    fetch_and_process_market_data()
