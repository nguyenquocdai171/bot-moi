import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import os

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

    /* Disclaimer Box */
    .disclaimer-box {
        background-color: #1A1D24; border: 1px solid #2D333B; border-radius: 8px;
        padding: 20px; margin: 0 auto 30px auto; text-align: center; max-width: 750px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }
    .disclaimer-title { color: #FF5252; font-weight: bold; font-size: 1.05rem; margin-bottom: 12px; text-transform: uppercase; }
    .d-text-1 { color: #A0AAB5; font-size: 0.95rem; margin-bottom: 6px; }
    .d-text-2 { color: #FFFFFF; font-size: 1rem; font-weight: bold; margin-bottom: 6px; text-decoration: underline; text-decoration-color: #555;}
    .d-text-3 { color: #78838E; font-size: 0.85rem; font-style: italic; }

    /* Inputs Override */
    div[data-baseweb="input"] { background-color: #262730; border-color: #41424C; border-radius: 6px; }
    div[data-baseweb="input"] > input { color: white !important; font-weight: bold; }
    label { color: #B0BEC5 !important; font-weight: bold !important; font-size: 0.95rem !important; }

    /* Nút Button (Nằm trong Form) */
    div.stFormSubmitButton > button {
        background-color: #1A1D24; border: 1px solid #333;
        color: white; font-weight: bold; height: 50px; font-size: 1.1rem; transition: 0.3s;
        border-radius: 6px; margin-top: 5px;
    }
    div.stFormSubmitButton > button:hover { border-color: #00E676; color: #00E676; background-color: #121418; box-shadow: 0 0 10px rgba(0,230,118,0.2); }

    /* Khối Kết Quả Tín Hiệu (Đã làm rực rỡ, giống ảnh 2) */
    .result-box { padding: 30px 20px; border-radius: 12px; margin-top: 10px; text-align: center; box-shadow: 0 8px 20px rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1); }
    .bg-buy { background: linear-gradient(135deg, #00C853, #1B5E20); } /* Xanh lá rực rỡ */
    .bg-sell { background: linear-gradient(135deg, #D50000, #880E4F); } /* Đỏ rực rỡ */
    .bg-warn { background: linear-gradient(135deg, #FF6D00, #E65100); } /* Cam rực rỡ */
    .bg-neutral { background: linear-gradient(135deg, #0D47A1, #1565C0); } /* Xanh dương đậm y hệt ảnh */
    
    .signal-text { font-size: 2.5rem; font-weight: 900; color: white; margin-bottom: 8px; text-shadow: 0 2px 5px rgba(0,0,0,0.5); text-transform: uppercase;}
    .reason-text { font-size: 1.1rem; color: #FAFAFA; font-style: italic; font-weight: 500;}

    /* Khối Giao diện Backtest So Sánh (Chuẩn từ ảnh 2) */
    .bt-container {
        display: flex; justify-content: space-around; align-items: center;
        background: linear-gradient(135deg, #263238 0%, #1E272C 100%);
        border-radius: 12px; padding: 30px 20px; margin-top: 25px; text-align: center;
        border: 1px solid #37474F; box-shadow: 0 6px 15px rgba(0,0,0,0.3);
    }
    .bt-col { flex: 1; text-align: center; }
    .bt-label { color: #B0BEC5; font-size: 0.95rem; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: bold; }
    .bt-val { font-size: 2.8rem; font-weight: 900; line-height: 1.1; margin-bottom: 5px; }
    .bt-note { font-size: 0.9rem; color: #90A4AE; margin-top: 5px; margin-bottom: 12px;}
    .bt-hold { font-size: 0.9rem; color: #FFF; background-color: rgba(255,255,255,0.08); border: 1px solid #455A64; padding: 6px 15px; border-radius: 20px; display: inline-block; font-weight: 500;}
    .bt-divider { width: 1px; background-color: #546E7A; height: 100px; margin: 0 20px; opacity: 0.5; }
    .opt-badge { background-color: #00E5FF; color: #000; padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 900; margin-left: 8px; vertical-align: middle; box-shadow: 0 0 10px rgba(0, 229, 255, 0.4); letter-spacing: 0.5px;}

    /* Reponsive cho điện thoại */
    @media (max-width: 600px) {
        .bt-container { flex-direction: column; padding: 20px; }
        .bt-divider { width: 100%; height: 1px; margin: 20px 0; }
        .bt-val { font-size: 2.2rem; }
    }
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
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path_1 = os.path.join(current_dir, 'data', 'database_nganh.csv')
    path_2 = os.path.join(current_dir, 'database_nganh.csv')
    
    if os.path.exists(path_1): return pd.read_csv(path_1)
    elif os.path.exists(path_2): return pd.read_csv(path_2)
    return None

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).ewm(span=period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(span=period, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def run_simulation(strategy_returns, sl_level):
    if sl_level == 0:
        return np.prod(1 + strategy_returns) - 1
    adj_ret = np.where(strategy_returns < -sl_level, -sl_level, strategy_returns)
    return np.prod(1 + adj_ret) - 1

def optimize_ma_sl(df, user_sl):
    """Tối ưu hóa MA, SL và Trả về cả Số ngày nắm giữ trung bình"""
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
    best_ma_idx, best_sl, max_cum_return = 0, 0.0, -np.inf

    for i, ma_ret in enumerate(strategy_returns):
        for sl in sl_levels:
            cum_return = run_simulation(ma_ret, sl)
            if cum_return > max_cum_return:
                max_cum_return = cum_return
                best_ma_idx = i
                best_sl = sl

    opt_ma_window = ma_windows[best_ma_idx]
    opt_ma_series = df['Close'].rolling(opt_ma_window).mean()
    
    user_sl_decimal = float(user_sl) / 100.0
    user_cum_return = run_simulation(strategy_returns[best_ma_idx], user_sl_decimal)
    
    # Tính số ngày nắm giữ trung bình của chiến lược MA tốt nhất
    best_sig = signals[best_ma_idx]
    trades = np.sum(np.diff(np.insert(best_sig, 0, 0)) == 1)
    total_days_held = np.sum(best_sig)
    avg_hold_days = total_days_held / trades if trades > 0 else 0
    
    # Quy đổi Lợi nhuận ra % theo Năm (%/năm)
    try:
        days_total = (df.index[-1] - df.index[0]).days
    except:
        days_total = len(df)
        
    years = days_total / 365.25 if days_total > 0 else 1
    best_ann_ret = max_cum_return / years
    user_ann_ret = user_cum_return / years
    
    return opt_ma_window, best_sl * 100, best_ann_ret * 100, user_ann_ret * 100, avg_hold_days, opt_ma_series

# --- 4. FORM NHẬP LIỆU (HỖ TRỢ ENTER & NÚT FULL WIDTH) ---
# Wrap toàn bộ bằng st.form để khi nhập xong bấm phím Enter sẽ tự chạy
with st.form(key='search_form'):
    col1, col2 = st.columns([2, 1])
    with col1:
        ticker_input = st.text_input("Mã cổ phiếu:", placeholder="VD: HPG, VNM...").upper().strip()
    with col2:
        sl_input = st.number_input("SL mong muốn (%):", min_value=0.0, max_value=20.0, value=7.0, step=0.1, format="%.1f")
    
    # Nút bấm được set use_container_width=True để trải dài ra nhìn đẹp mắt
    submit_btn = st.form_submit_button("🚀 PHÂN TÍCH & SIÊU TỐI ƯU", use_container_width=True)

# --- 5. LỘ TRÌNH THỰC THI CHÍNH ---
if submit_btn:
    if not ticker_input:
        st.warning("⚠️ Vui lòng nhập mã cổ phiếu!")
        st.stop()
        
    db_nganh = load_sector_database()
    if db_nganh is None:
        st.error("❌ Không tìm thấy file `database_nganh.csv`. Vui lòng chạy file `prepare_sectors.py` trước!")
        st.stop()
        
    ticker_info = db_nganh[db_nganh['Ticker'] == ticker_input]
    if ticker_info.empty:
        st.error(f"❌ Mã {ticker_input} không tồn tại trong Database Ngành. Vui lòng kiểm tra lại.")
        st.stop()
        
    sector_name = ticker_info.iloc[0]['Sector']
    peers = db_nganh[db_nganh['Sector'] == sector_name]['Ticker'].tolist()
    
    with st.spinner(f"🔍 Đang thu thập dữ liệu ngành '{sector_name}' ({len(peers)} mã)..."):
        yf_tickers = [f"{t}.VN" for t in peers]
        data = yf.download(yf_tickers, period="2y", interval="1d", progress=False)
        
        if data.empty or 'Close' not in data:
            st.error("❌ Mạng lỗi hoặc không tải được dữ liệu từ Yahoo Finance.")
            st.stop()
            
        if isinstance(data.columns, pd.MultiIndex):
            close_data = data['Close']
        else:
            close_data = data
            
        if isinstance(close_data, pd.Series): 
            close_data = close_data.to_frame(name=f"{ticker_input}.VN")
            
        main_ticker_yf = f"{ticker_input}.VN"
        if main_ticker_yf not in close_data.columns:
            st.error(f"❌ Mã {ticker_input} không có dữ liệu giao dịch gần đây.")
            st.stop()

        rsi_df = pd.DataFrame(index=close_data.index)
        for t in close_data.columns:
            rsi_df[t] = calculate_rsi(close_data[t])
            
        sector_rsi_series = rsi_df.mean(axis=1).dropna()
        current_sector_rsi = sector_rsi_series.iloc[-1]
        
        if current_sector_rsi < 35: sector_trend = "Downtrend"
        elif current_sector_rsi > 65: sector_trend = "Uptrend"
        else: sector_trend = "Bình thường"
            
        df_main = pd.DataFrame({'Close': close_data[main_ticker_yf].dropna()})
        df_main['RSI'] = calculate_rsi(df_main['Close'])
        
        opt_ma, opt_sl, best_ret, user_ret, avg_hold_days, ma_series = optimize_ma_sl(df_main, sl_input)
        
        current_price = df_main['Close'].iloc[-1]
        current_rsi = df_main['RSI'].iloc[-1]
        current_ma_val = ma_series.iloc[-1]
        
        # --- 6. MA TRẬN TÍN HIỆU LÕI ---
        signal = "QUAN SÁT (WAIT)"
        output_msg = f"Giá dưới MA{opt_ma} (Xu hướng giảm), chờ RSI < 30." if current_price < current_ma_val else f"Giá trên MA{opt_ma} (Xu hướng tăng), chờ RSI > 70."
        bg_class = "bg-neutral"
        
        if current_price < current_ma_val and current_rsi < 30:
            if sector_trend == "Uptrend":
                signal = "KHÔNG MUA"
                output_msg = "Ngành tăng nhưng mã rớt thảm. Có rủi ro nội tại -> KHÔNG MUA"
                bg_class = "bg-warn"
            elif sector_trend == "Downtrend":
                signal = "CÂN NHẮC MUA"
                output_msg = "Có thể Mua bắt đáy, nhưng Ngành đang rớt -> Rủi ro cao"
                bg_class = "bg-warn"
            else:
                signal = "MUA NGAY"
                output_msg = "Thỏa mãn điều kiện Giá, RSI và Ngành bình thường -> MUA"
                bg_class = "bg-buy"
                
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
        
        # 7.1 Box Tín Hiệu (Màu Sắc Rực Rỡ)
        st.markdown(f"""
        <div class='result-box {bg_class}'>
            <div class='signal-text'>{signal}</div>
            <div class='reason-text'>💡 {output_msg}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 7.2 Box Backtest (Sao chép 100% tỷ lệ từ Ảnh 2)
        u_color = "#00E676" if user_ret > 0 else "#FF5252"
        o_color = "#00E5FF" 
        sl_text_user = f"{sl_input}%" if sl_input > 0 else "OFF"
        sl_text_opt = f"{opt_sl:.1f}%" if opt_sl > 0 else "OFF"
        
        html_box = f"""
        <div class='bt-container'>
            <div class='bt-col'>
                <div class='bt-label'>CỦA BẠN (SL {sl_text_user})</div>
                <div class='bt-val' style='color:{u_color}'>{user_ret:+.1f}%<span style='font-size:1.4rem'>/năm</span></div>
                <div class='bt-note'>Hiệu quả lợi nhuận trung bình</div>
                <div class='bt-hold'>⏳ Nắm giữ TB: {avg_hold_days:.0f} ngày</div>
            </div>
            <div class='bt-divider'></div>
            <div class='bt-col'>
                <div class='bt-label'>TỐI ƯU NHẤT <span class='opt-badge'>RECOMMENDED</span></div>
                <div class='bt-val' style='color:{o_color}'>{best_ret:+.1f}%<span style='font-size:1.4rem'>/năm</span></div>
                <div class='bt-note'>Với mức Stoploss <b>{sl_text_opt}</b></div>
                <div class='bt-hold'>⏳ Nắm giữ TB: {avg_hold_days:.0f} ngày</div>
            </div>
        </div>
        """
        st.markdown(html_box, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 7.3 Bảng Thông Số Kỹ Thuật Dưới Cùng
        st.markdown("### 📊 CHỈ SỐ KỸ THUẬT HIỆN TẠI")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Giá Hiện Tại", f"{current_price:,.0f}")
        col_m1.metric("RSI Cổ phiếu (14)", f"{current_rsi:.1f}")
        
        col_m2.metric(f"Đường MA Tối Ưu", f"MA {opt_ma}", delta=f"{current_ma_val:,.0f} (Giá MA)", delta_color="off")
        col_m2.metric("Stoploss Tối Ưu", f"{opt_sl:.1f}%")
        
        col_m3.metric(f"Ngành: {sector_name}", f"RSI: {current_sector_rsi:.1f}")
        col_m3.metric("Xu hướng Ngành", sector_trend, delta="↓" if sector_trend=="Downtrend" else ("↑" if sector_trend=="Uptrend" else "-"), delta_color="inverse" if sector_trend=="Downtrend" else "normal")
