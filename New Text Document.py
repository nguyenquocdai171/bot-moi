import pandas as pd
import numpy as np
import time
import os
import yfinance as yf
from datetime import datetime, timedelta

# --- MAP NGÀNH CỐ ĐỊNH ---
# Khai báo sẵn ngành giúp loại bỏ hoàn toàn việc gọi API lấy thông tin công ty
# Tránh 100% rủi ro bị ban IP / Rate limit từ các nguồn cấp dữ liệu
SECTOR_MAP = {
    'SSI': 'Chứng khoán', 'VND': 'Chứng khoán', 'HCM': 'Chứng khoán', 'VCI': 'Chứng khoán', 'FTS': 'Chứng khoán',
    'VCB': 'Ngân hàng', 'TCB': 'Ngân hàng', 'MBB': 'Ngân hàng', 'VPB': 'Ngân hàng', 'STB': 'Ngân hàng', 'CTG': 'Ngân hàng', 'BID': 'Ngân hàng',
    'HPG': 'Thép', 'HSG': 'Thép', 'NKG': 'Thép',
    'FPT': 'Công nghệ', 'MWG': 'Bán lẻ', 'PNJ': 'Bán lẻ', 'MSN': 'Tiêu dùng', 'VNM': 'Tiêu dùng',
    'VHM': 'Bất động sản', 'VIC': 'Bất động sản', 'VRE': 'Bất động sản', 'NVL': 'Bất động sản', 'DIG': 'Bất động sản', 'DXG': 'Bất động sản'
}

def get_target_tickers():
    """Lấy danh sách mã chứng khoán từ Map có sẵn"""
    return list(SECTOR_MAP.keys())

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
    sl_levels = np.arange(0.0, 0.101, 0.001)
    
    best_ma_idx = 0
    best_sl = 0.0
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
    """Hàm main: Dùng yfinance cào data chậm rãi, chống Ban IP"""
    tickers = get_target_tickers()
    all_data = []
    
    print(f"🚀 Bắt đầu crawl dữ liệu {len(tickers)} mã bằng YFINANCE (Chống Ban IP)...")
    
    for ticker in tickers:
        symbol = f"{ticker}.VN" # Thêm đuôi .VN cho chứng khoán VN trên yfinance
        try:
            # Lấy data lịch sử 2 năm
            df = yf.download(symbol, period="2y", interval="1d", progress=False)
            
            if df is None or df.empty:
                print(f"⚠️ Bỏ qua {ticker}: Không tìm thấy dữ liệu trên yfinance")
                continue
            
            # Xử lý MultiIndex columns nếu dùng yfinance bản mới
            if isinstance(df.columns, pd.MultiIndex): 
                df.columns = df.columns.get_level_values(0)
            
            # Reset index để biến 'Date' thành 1 cột
            df = df.reset_index()
            df.rename(columns={'Date': 'Date', 'Close': 'Close', 'Volume': 'Volume'}, inplace=True, errors='ignore')
            
            # Chuẩn hóa múi giờ để dễ lưu file CSV
            df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
            df.sort_values('Date', inplace=True)
            
            # Gán ngành tĩnh (Cực kỳ an toàn, không cần gọi API)
            sector = SECTOR_MAP.get(ticker, 'Unknown')
            df['Sector'] = sector
            df['Ticker'] = ticker
            
            # Các tính toán cốt lõi
            df['RSI'] = calculate_rsi(df['Close'], 14)
            opt_ma, opt_sl, ma_series = optimize_ma_sl_vectorized(df)
            df['Opt_MA_Period'] = opt_ma
            df['Opt_SL'] = opt_sl
            df['Opt_MA_Value'] = ma_series
            
            all_data.append(df)
            
            # Sleep 1.5 giây cho chắc cú, yfinance cho phép lấy nhanh hơn nhưng chậm cho bền
            time.sleep(1.5) 
            print(f"✅ Đã xử lý: {ticker} | Ngành: {sector} | Opt MA: {opt_ma} | Opt SL: {opt_sl:.1%}")
            
        except Exception as e:
            print(f"❌ Lỗi tại mã {ticker}: {e}")
            time.sleep(3) # Nghỉ lâu hơn nếu bị lỗi
            continue

    if not all_data:
        raise ValueError("Không có dữ liệu nào được thu thập!")

    print("\n⏳ Đang phân tích Ma trận tín hiệu & Cấp độ ngành...")
    market_df = pd.concat(all_data, ignore_index=True)
    
    # --- TÍNH TOÁN CẤP ĐỘ NGÀNH (SECTOR TREND) BẰNG VECTORIZATION ---
    market_df['Sector_RSI'] = market_df.groupby(['Date', 'Sector'])['RSI'].transform('mean')
    
    # Cập nhật mốc Trend Ngành (<= 40 là Downtrend, > 60 là Uptrend)
    market_df['Sector_Trend'] = np.select(
        [market_df['Sector_RSI'] <= 40, market_df['Sector_RSI'] > 60],
        ['Downtrend', 'Uptrend'],
        default='Bình thường'
    )
    
    # --- MA TRẬN TÍN HIỆU & CẢNH BÁO LÕI (LOGIC MỚI CHUẨN) ---
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
