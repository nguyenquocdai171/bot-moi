import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import os
import time

# --- 1. CẤU HÌNH TRANG & CSS GIAO DIỆN ---
st.set_page_config(layout="centered", page_title="Stock Advisor", page_icon="🚀")

st.markdown("""
<style>
    /* Nền và font chữ tổng thể */
    .stApp { background-color: #121418; color: #FFFFFF; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Header */
    .main-title {
        text-align: center; font-weight: 900; font-size: 3.2rem;
        color: #00E676; letter-spacing: 2px; margin-bottom: 5px; text-transform: uppercase;
        text-shadow: 0px 0px 20px rgba(0, 230, 118, 0.3);
    }
    .sub-title { text-align: center; color: #A0AAB5; font-size: 1.1rem; margin-bottom: 30px; font-weight: 500; }

    /* Disclaimer Box (Giống hệt ảnh) */
    .disclaimer-box {
        background-color: #1E1E1E; border: 1px solid #333; border-radius: 8px;
        padding: 20px; margin: 0 auto 40px auto; text-align: center; max-width: 750px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }
    .disclaimer-title { color: #FF5252; font-weight: bold; font-size: 1.05rem; margin-bottom: 12px; text-transform: uppercase; }
    .d-text-1 { color: #A0AAB5; font-size: 0.95rem; margin-bottom: 6px; }
    .d-text-2 { color: #FFFFFF; font-size: 1rem; font-weight: bold; margin-bottom: 6px; text-decoration: underline; text-decoration-color: #555;}
    .d-text-3 { color: #78838E; font-size: 0.85rem; font-style: italic; }

    /* Inputs Override */
    div[data-baseweb="input"] { background-color: #262730; border-color: #41424C; border-radius: 6px; }
    div[data-baseweb="input"] > input { color: white !important; font-weight: bold; }
    label { color: #B0BEC5 !important; font-weight: bold !important; font-size: 0.9rem !important; }

    /* Nút Button */
    div.stButton > button {
        width: 100%; background-color: #1A1D24; border: 1px solid #333;
        color: white; font-weight: bold; height: 50px; font-size: 1.1rem; transition: 0.3s;
        border-radius: 6px; margin-top: 15px;
    }
    div.stButton > button:hover { border-color: #00E676; color: #00E676; background-color: #121418; box-shadow: 0 0 10px rgba(0,230,118,0.2); }

    /* Kết quả Box */
    .result-box { padding: 25px; border-radius: 10px; margin-top: 20px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .bg-buy { background: linear-gradient(135deg, #1b5e20, #2e7d32); border: 1px solid #4CAF50;}
    .bg-sell { background: linear-gradient(135deg, #b71c1c, #c62828); border: 1px solid #FF5252;}
    .bg-warn { background: linear-gradient(135deg, #e65100, #ef6c00); border: 1px solid #FF9800;}
    .bg-neutral { background: linear-gradient(135deg, #263238, #37474F); border: 1px solid #546E7A;}
    
    .signal-text { font-size: 2.2rem; font-weight: 900; color: white; margin-bottom: 10px; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
    .reason-text { font-size: 1.1rem; color: #EEE; font-style: italic; }
</style>
""", unsafe_allow_html=True)

# --- 2. GIAO DIỆN HEADER ---
st.markdown("<div class='main-title'>STOCK ADVISOR</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Hệ thống Tối ưu hóa Kép (MA & Stoploss)</div>", unsafe_allow_html=True)

st.markdown("""
<div class='disclaimer-box'>
    <div class='disclaimer-title'>⚠️ TUYÊN BỐ MIỄN TRỪ TRÁCH NHIỆM</div>
    <div class='d-text-1'>Công cụ tự động tối ưu hóa tham số quá khứ.</div>
    <div class='d-text-2'>KHÔNG phải lời khuyên đầu tư tài chính chính thức.</div>
    <div class='d-text-3'>Người dùng tự chịu trách nhiệm.</div>
</div>
""", unsafe_allow_html=True)

# --- 3. HÀM XỬ LÝ DỮ LIỆU & THUẬT TOÁN ---
@st.cache_data
def load_sector_database():
    # Lấy đường dẫn thư mục chứa file app.py hiện tại
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Kịch bản 1: File nằm trong thư mục con 'data' (chuẩn nhất)
    path_1 = os.path.join(current_dir, 'data', 'database_nganh.csv')
    
    # Kịch bản 2: File bị up thẳng lên thư mục gốc (cùng chỗ với app.py)
    path_2 = os.path.join(current_dir, 'database_nganh.csv')
    
    if os.path.exists(path_1):
        return pd.read_csv(path_1)
    elif os.path.exists(path_2):
        return pd.read_csv(path_2)
    
    # Nếu vẫn không thấy, trả về None để báo lỗi
    return None

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).ewm(span=period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(span=period, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def run_simulation(strategy_returns, sl_level):
    """Tính toán lợi nhuận dựa trên 1 mảng return và 1 mức Stoploss"""
    if sl_level == 0:
        return np.prod(1 + strategy_returns) - 1
    adj_ret = np.where(strategy_returns < -sl_level, -sl_level, strategy_returns)
    return np.prod(1 + adj_ret) - 1

def optimize_ma_sl(df, user_sl):
    """Tối ưu hóa MA (5->205) và SL (0% -> 10%)"""
    close_arr = df['Close'].values
    returns = np.diff(close_arr) / close_arr[:-1]
    returns = np.insert(returns, 0, 0)
    
    # Mảng MA từ 5 đến 205, bước nhảy 5
    ma_windows = np.arange(5, 210, 5)
    ma_matrix = np.array([df['Close'].rolling(w).mean().values for w in ma_windows])
    
    # Tín hiệu Mua khi Giá vượt MA
    signals = (close_arr > ma_matrix).astype(int)
    signals = np.roll(signals, 1, axis=1) # Tránh look-ahead bias
    signals[:, 0] = 0
    strategy_returns = signals * returns
    
    # Mảng Stoploss từ 0.0% đến 10.0%, bước nhảy 0.1% (0.001)
    sl_levels = np.arange(0.0, 0.101, 0.001)
    
    best_ma_idx, best_sl, max_cum_return = 0, 0.0, -np.inf

    # Tìm bộ tham số tối ưu nhất
    for i, ma_ret in enumerate(strategy_returns):
        for sl in sl_levels:
            cum_return = run_simulation(ma_ret, sl)
            if cum_return > max_cum_return:
                max_cum_return = cum_return
                best_ma_idx = i
                best_sl = sl

    opt_ma_window = ma_windows[best_ma_idx]
    opt_ma_series = df['Close'].rolling(opt_ma_window).mean()
    
    # Tính lợi nhuận theo thông số SL của user trên đường MA tối ưu đó
    user_sl_decimal = float(user_sl) / 100.0
    user_cum_return = run_simulation(strategy_returns[best_ma_idx], user_sl_decimal)
    
    return opt_ma_window, best_sl * 100, max_cum_return * 100, user_cum_return * 100, opt_ma_series

# --- 4. FORM NHẬP LIỆU ---
col1, col2 = st.columns([2, 1])
with col1:
    ticker_input = st.text_input("Mã cổ phiếu:", placeholder="VD: HPG, VNM...").upper().strip()
with col2:
    sl_input = st.number_input("SL mong muốn (%):", min_value=0.0, max_value=20.0, value=7.0, step=0.1, format="%.1f")

submit_btn = st.button("🚀 PHÂN TÍCH & SIÊU TỐI ƯU")

# --- 5. LỘ TRÌNH THỰC THI CHÍNH ---
if submit_btn:
    if not ticker_input:
        st.warning("⚠️ Vui lòng nhập mã cổ phiếu!")
        st.stop()
        
    db_nganh = load_sector_database()
    if db_nganh is None:
        st.error("❌ Không tìm thấy file `database_nganh.csv`. Vui lòng chạy file `prepare_sectors.py` trước!")
        st.stop()
        
    # Xác định ngành
    ticker_info = db_nganh[db_nganh['Ticker'] == ticker_input]
    if ticker_info.empty:
        st.error(f"❌ Mã {ticker_input} không tồn tại trong Database Ngành. Vui lòng kiểm tra lại.")
        st.stop()
        
    sector_name = ticker_info.iloc[0]['Sector']
    peers = db_nganh[db_nganh['Sector'] == sector_name]['Ticker'].tolist()
    
    with st.spinner(f"🔍 Đang thu thập dữ liệu ngành '{sector_name}' ({len(peers)} mã)..."):
        # Tải Batch từ yfinance
        yf_tickers = [f"{t}.VN" for t in peers]
        data = yf.download(yf_tickers, period="2y", interval="1d", progress=False)
        
        if data.empty or 'Close' not in data:
            st.error("❌ Mạng lỗi hoặc không tải được dữ liệu từ Yahoo Finance.")
            st.stop()
            
        # Xử lý format MultiIndex của yfinance bản mới
        if isinstance(data.columns, pd.MultiIndex):
            close_data = data['Close']
        else:
            close_data = data
            
        if isinstance(close_data, pd.Series): # Ngành chỉ có 1 mã
            close_data = close_data.to_frame(name=f"{ticker_input}.VN")
            
        main_ticker_yf = f"{ticker_input}.VN"
        if main_ticker_yf not in close_data.columns:
            st.error(f"❌ Mã {ticker_input} không có dữ liệu giao dịch gần đây.")
            st.stop()

        # Tính RSI Trung bình Ngành
        rsi_df = pd.DataFrame(index=close_data.index)
        for t in close_data.columns:
            rsi_df[t] = calculate_rsi(close_data[t])
            
        sector_rsi_series = rsi_df.mean(axis=1).dropna()
        current_sector_rsi = sector_rsi_series.iloc[-1]
        
        # Xác định Trend Ngành
        if current_sector_rsi < 35: sector_trend = "Downtrend"
        elif current_sector_rsi > 65: sector_trend = "Uptrend"
        else: sector_trend = "Bình thường"
            
        # Trích xuất dữ liệu Cổ phiếu chính
        df_main = pd.DataFrame({'Close': close_data[main_ticker_yf].dropna()})
        df_main['RSI'] = calculate_rsi(df_main['Close'])
        
        # Chạy thuật toán siêu tối ưu
        opt_ma, opt_sl, best_ret, user_ret, ma_series = optimize_ma_sl(df_main, sl_input)
        
        current_price = df_main['Close'].iloc[-1]
        current_rsi = df_main['RSI'].iloc[-1]
        current_ma_val = ma_series.iloc[-1]
        
        # --- 6. MA TRẬN TÍN HIỆU (Logic Lõi) ---
        signal = "QUAN SÁT (Giữ vị thế)"
        output_msg = "Chưa có tín hiệu Mua/Bán đặc biệt."
        bg_class = "bg-neutral"
        
        # TÍN HIỆU MUA
        if current_price < current_ma_val and current_rsi < 30:
            if sector_trend == "Uptrend":
                signal = "KHÔNG MUA"
                output_msg = "CẢNH BÁO: Ngành tăng nhưng mã rớt thảm. Có rủi ro nội tại -> KHÔNG MUA"
                bg_class = "bg-warn"
            elif sector_trend == "Downtrend":
                signal = "CÂN NHẮC MUA"
                output_msg = "Có thể Mua bắt đáy, nhưng Ngành đang rớt -> Rủi ro cao"
                bg_class = "bg-warn"
            else:
                signal = "MUA"
                output_msg = "Thỏa mãn điều kiện Giá, RSI và Ngành bình thường -> MUA"
                bg_class = "bg-buy"
                
        # TÍN HIỆU BÁN
        elif current_price > current_ma_val and current_rsi > 70:
            if sector_trend == "Uptrend":
                signal = "CÂN NHẮC BÁN"
                output_msg = "Có thể Bán, nhưng Ngành đang tăng mạnh -> Coi chừng chốt non"
                bg_class = "bg-warn"
            elif sector_trend == "Downtrend":
                signal = "BÁN NGAY"
                output_msg = "Ngôi sao đi ngược thị trường. BÁN NGAY để bảo toàn lực lượng"
                bg_class = "bg-sell"
            else:
                signal = "BÁN NGAY"
                output_msg = "Thỏa mãn điều kiện Giá, RSI và Ngành bình thường -> BÁN NGAY"
                bg_class = "bg-sell"

        # --- 7. HIỂN THỊ KẾT QUẢ ---
        st.markdown(f"""
        <div class='result-box {bg_class}'>
            <div class='signal-text'>{signal}</div>
            <div class='reason-text'>💡 {output_msg}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Bảng Thông Số Kỹ Thuật
        st.markdown("### 📊 CHỈ SỐ KỸ THUẬT")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Giá Hiện Tại", f"{current_price:,.0f}")
        col_m1.metric("RSI Cổ phiếu (14)", f"{current_rsi:.1f}")
        
        col_m2.metric(f"Đường MA Tối Ưu", f"MA {opt_ma}", delta=f"{current_ma_val:,.0f}", delta_color="off")
        col_m2.metric("Stoploss Tối Ưu", f"{opt_sl:.1f}%")
        
        col_m3.metric(f"Ngành: {sector_name}", f"RSI: {current_sector_rsi:.1f}")
        col_m3.metric("Xu hướng Ngành", sector_trend, delta="↓" if sector_trend=="Downtrend" else ("↑" if sector_trend=="Uptrend" else "-"), delta_color="inverse" if sector_trend=="Downtrend" else "normal")

        st.divider()
        
        # Bảng So sánh Backtest
        st.markdown("### 🏆 SO SÁNH HIỆU QUẢ LỢI NHUẬN LỊCH SỬ")
        col_b1, col_b2 = st.columns(2)
        
        with col_b1:
            st.info(f"**CỦA BẠN (SL {sl_input}%)**\n\nLợi nhuận ước tính: **{user_ret:+.1f}%**")
        with col_b2:
            st.success(f"**TỐI ƯU NHẤT (SL {opt_sl:.1f}%)**\n\nLợi nhuận tối đa: **{best_ret:+.1f}%**")
