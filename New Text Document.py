import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
import streamlit.components.v1 as components
import random

# --- 1. CẤU HÌNH TRANG (MỞ RỘNG TOÀN MÀN HÌNH) ---
st.set_page_config(layout="wide", page_title="Stock Advisor Super Pro", page_icon="🚀")

st.markdown("""
<style>
    /* Nền và font chữ tổng thể */
    .stApp { background-color: #0E1117; color: #FFFFFF; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
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
    div[data-baseweb="input"] > input { color: white !important; font-weight: bold; text-align: center;}
    label { color: #B0BEC5 !important; font-weight: bold !important; font-size: 0.95rem !important; }

    /* Nút Button */
    div.stFormSubmitButton > button {
        background-color: #1A1D24; border: 1px solid #333;
        color: white; font-weight: bold; height: 50px; font-size: 1.1rem; transition: 0.3s;
        border-radius: 6px; margin-top: 5px;
    }
    div.stFormSubmitButton > button:hover { border-color: #00E676; color: #00E676; background-color: #121418; box-shadow: 0 0 10px rgba(0,230,118,0.2); }

    /* Khối Kết Quả Tín Hiệu */
    .result-box { padding: 30px 20px; border-radius: 12px; margin-top: 10px; text-align: center; box-shadow: 0 8px 20px rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1); }
    .bg-buy { background: linear-gradient(135deg, #00C853, #1B5E20); }
    .bg-sell { background: linear-gradient(135deg, #D50000, #880E4F); }
    .bg-warn { background: linear-gradient(135deg, #FF6D00, #E65100); }
    .bg-neutral { background: linear-gradient(135deg, #0D47A1, #1565C0); }
    
    .signal-text { font-size: 2.5rem; font-weight: 900; color: white; margin-bottom: 8px; text-shadow: 0 2px 5px rgba(0,0,0,0.5); text-transform: uppercase;}
    .reason-text { font-size: 1.1rem; color: #FAFAFA; font-style: italic; font-weight: 500;}

    /* Khối Giao diện Backtest So Sánh */
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
    .bt-hold { font-size: 0.85rem; color: #FFF; background-color: rgba(0,230,118,0.1); border: 1px solid rgba(0,230,118,0.3); padding: 4px 12px; border-radius: 20px; display: inline-block; font-weight: 500; margin: 3px;}
    .bt-hold-sl { font-size: 0.85rem; color: #FFF; background-color: rgba(255,82,82,0.1); border: 1px solid rgba(255,82,82,0.3); padding: 4px 12px; border-radius: 20px; display: inline-block; font-weight: 500; margin: 3px;}
    .bt-divider { width: 1px; background-color: #546E7A; height: 130px; margin: 0 20px; opacity: 0.5; }
    .opt-badge { background-color: #00E5FF; color: #000; padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 900; margin-left: 8px; vertical-align: middle; box-shadow: 0 0 10px rgba(0, 229, 255, 0.4); letter-spacing: 0.5px;}

    /* Khối Thẻ Chỉ số Mới Cân Bằng */
    .metric-card {
        background-color: #1E272C; border: 1px solid #37474F; border-radius: 12px;
        padding: 15px 15px; text-align: center; box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        height: 320px;
        display: flex; flex-direction: column;
        margin-bottom: 15px; transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-3px); border-color: #546E7A; }
    
    .m-section { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; }
    .m-label { font-size: 0.85rem; color: #90A4AE; font-weight: bold; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.5px;}
    .m-val { font-size: 2.4rem; font-weight: 900; color: white; margin-bottom: 6px; line-height: 1.1;}
    .m-val-text { font-size: 1.6rem; font-weight: 900; color: #00E5FF; margin-bottom: 6px; line-height: 1.1;}
    
    .m-sub-up { background-color: rgba(0,230,118,0.15); color: #00E676; padding: 5px 12px; border-radius: 6px; font-size: 0.85rem; font-weight: bold; display: inline-block;}
    .m-sub-down { background-color: rgba(255,82,82,0.15); color: #FF5252; padding: 5px 12px; border-radius: 6px; font-size: 0.85rem; font-weight: bold; display: inline-block;}
    .m-sub-neu { background-color: rgba(255,255,255,0.1); color: #FFF; padding: 5px 12px; border-radius: 6px; font-size: 0.85rem; font-weight: bold; display: inline-block;}
    .m-divider { width: 70%; height: 1px; background-color: #37474F; margin: 0 auto; flex-shrink: 0; }

    @media (max-width: 600px) {
        .bt-container { flex-direction: column; padding: 20px; }
        .bt-divider { width: 100%; height: 1px; margin: 20px 0; }
        .bt-val { font-size: 2.2rem; }
        .metric-card { height: auto; }
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo Session State
if 'analysis_done' not in st.session_state:
    st.session_state['analysis_done'] = False
if 'results' not in st.session_state:
    st.session_state['results'] = {}

# --- 2. GIAO DIỆN HEADER ---
st.markdown("<div class='main-title'>STOCK ADVISOR SUPER PRO</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Hệ thống Tối ưu hóa Kép</div>", unsafe_allow_html=True)

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

def run_state_machine_simulation(close_arr, buy_triggers, sell_triggers, sl_val):
    in_trade = False
    entry_price = 0.0
    cum_ret = 1.0
    
    tp_hold_days_list = [] 
    sl_hold_days_list = [] 
    total_trades = 0       
    sl_trades = 0          
    current_hold = 0

    for i in range(1, len(close_arr)):
        if not in_trade:
            if buy_triggers[i-1]:
                in_trade = True
                entry_price = close_arr[i]
                current_hold = 1
        else:
            current_hold += 1
            if sl_val > 0 and (close_arr[i] - entry_price) / entry_price <= -sl_val:
                cum_ret *= (1 - sl_val)
                in_trade = False
                sl_hold_days_list.append(current_hold)
                total_trades += 1
                sl_trades += 1
                current_hold = 0
            elif sell_triggers[i-1]:
                trade_ret = (close_arr[i] - entry_price) / entry_price
                cum_ret *= (1 + trade_ret)
                tp_hold_days_list.append(current_hold)
                total_trades += 1
                in_trade = False
                current_hold = 0

    if in_trade:
        trade_ret = (close_arr[-1] - entry_price) / entry_price
        cum_ret *= (1 + trade_ret)

    total_return = cum_ret - 1
    
    avg_tp_hold = np.mean(tp_hold_days_list) if len(tp_hold_days_list) > 0 else 0
    avg_sl_hold = np.mean(sl_hold_days_list) if len(sl_hold_days_list) > 0 else 0
    sl_rate = (sl_trades / total_trades * 100) if total_trades > 0 else 0.0
    
    return total_return, avg_tp_hold, avg_sl_hold, sl_rate

def optimize_ma_sl_advanced(df, user_sl, sector_rsi_series):
    close_arr = df['Close'].values
    rsi_arr = df['RSI'].values
    sec_rsi_arr = sector_rsi_series.reindex(df.index).ffill().values
    
    ma_windows = np.arange(5, 210, 5)
    sl_levels = np.arange(0.03, 0.105, 0.005)
    
    best_ma_idx = 5
    best_sl = 0.03
    max_cum_return = -np.inf
    
    best_avg_tp_hold = 0
    best_avg_sl_hold = 0
    best_sl_rate = 0.0
    
    for w in ma_windows:
        ma_line = df['Close'].rolling(w).mean().values
        
        # ĐIỀU KIỆN MUA MỚI: Giá < MA & RSI Mã < 30 & Ngành từ 35 đến 65
        buy_triggers = (close_arr < ma_line) & (rsi_arr < 30) & (sec_rsi_arr >= 35) & (sec_rsi_arr <= 65)
        
        # ĐIỀU KIỆN BÁN MỚI:
        # 1. Bán bình thường: Giá > MA & RSI Mã > 70 & Ngành từ 35 đến 65
        # 2. Chốt lời sớm: Giá > MA & RSI Mã >= 65 & Ngành < 35 (Ngành downtrend)
        sell_triggers = (close_arr > ma_line) & (
            ((rsi_arr > 70) & (sec_rsi_arr >= 35) & (sec_rsi_arr <= 65)) |
            ((rsi_arr >= 65) & (sec_rsi_arr < 35))
        )
        
        for sl in sl_levels:
            ret, tp_hold, sl_hold, sl_rate = run_state_machine_simulation(close_arr, buy_triggers, sell_triggers, sl)
            if ret > max_cum_return:
                max_cum_return = ret
                best_ma_idx = w
                best_sl = sl
                best_avg_tp_hold = tp_hold
                best_avg_sl_hold = sl_hold
                best_sl_rate = sl_rate

    # Tính cho User
    opt_ma_series = df['Close'].rolling(best_ma_idx).mean()
    ma_line_best = opt_ma_series.values
    buy_triggers_best = (close_arr < ma_line_best) & (rsi_arr < 30) & (sec_rsi_arr >= 35) & (sec_rsi_arr <= 65)
    sell_triggers_best = (close_arr > ma_line_best) & (
        ((rsi_arr > 70) & (sec_rsi_arr >= 35) & (sec_rsi_arr <= 65)) |
        ((rsi_arr >= 65) & (sec_rsi_arr < 35))
    )
    
    user_sl_decimal = float(user_sl) / 100.0
    user_ret, user_avg_tp_hold, user_avg_sl_hold, user_sl_rate = run_state_machine_simulation(close_arr, buy_triggers_best, sell_triggers_best, user_sl_decimal)
    
    try: days_total = (df.index[-1] - df.index[0]).days
    except: days_total = len(df)
        
    years = days_total / 365.25 if days_total > 0 else 1
    best_ann_ret = max_cum_return / years
    user_ann_ret = user_ret / years
    
    return best_ma_idx, best_sl * 100, best_ann_ret * 100, user_ann_ret * 100, best_avg_tp_hold, user_avg_tp_hold, best_avg_sl_hold, user_avg_sl_hold, best_sl_rate, user_sl_rate, opt_ma_series

# --- 4. FORM NHẬP LIỆU ---
col_pad1, col_main, col_pad2 = st.columns([1, 2, 1])

with col_main:
    with st.form(key='search_form'):
        f_col1, f_col2 = st.columns([2, 1])
        with f_col1:
            ticker_input = st.text_input("Mã cổ phiếu:", placeholder="VD: HPG, CEO...").upper().strip()
        with f_col2:
            sl_input = st.number_input("SL mong muốn (%):", min_value=3.0, max_value=10.0, value=7.0, step=0.5, format="%.1f")
        
        submit_btn = st.form_submit_button("🚀 PHÂN TÍCH & SIÊU TỐI ƯU", use_container_width=True)

results_placeholder = st.empty()

if submit_btn:
    js_hack = f"""<script>
    function forceBlur(){{
        const activeElement=window.parent.document.activeElement;
        if(activeElement){{activeElement.blur();}}
        window.parent.document.body.focus();
    }}
    forceBlur(); setTimeout(forceBlur, 100); setTimeout(forceBlur, 500);
    </script><div style="display:none;">{random.random()}</div>"""
    components.html(js_hack, height=0)
    
    results_placeholder.empty()

# --- 5. LỘ TRÌNH THỰC THI DỮ LIỆU ---
if submit_btn:
    if not ticker_input:
        st.warning("⚠️ Vui lòng nhập mã cổ phiếu!")
        st.stop()
        
    db_nganh = load_sector_database()
    if db_nganh is None:
        st.error("❌ Không tìm thấy file `database_nganh.csv`. Bạn cần có file này trước!")
        st.stop()
        
    ticker_info = db_nganh[db_nganh['Ticker'] == ticker_input]
    if ticker_info.empty:
        st.error(f"❌ Mã {ticker_input} không tồn tại trong Database Ngành. Hãy kiểm tra lại file CSV của bạn.")
        st.stop()
        
    sector_name = ticker_info.iloc[0]['Sector']
    
    # CHỈ LẤY CÁC MÃ HOSE ĐỂ TÍNH RSI NGÀNH CHO CHUẨN XÁC
    if 'Exchange' in db_nganh.columns:
        peers_hose = db_nganh[(db_nganh['Sector'] == sector_name) & (db_nganh['Exchange'] == 'HOSE')]['Ticker'].tolist()
    else:
        peers_hose = db_nganh[db_nganh['Sector'] == sector_name]['Ticker'].tolist()
    
    with st.spinner(f"🔍 Đang phân tích mã {ticker_input} và {len(peers_hose)} mã HOSE cùng ngành '{sector_name}'..."):
        main_vn = f"{ticker_input}.VN"
        main_hn = f"{ticker_input}.HN"
        
        yf_tickers = list(set([f"{t}.VN" for t in peers_hose] + [main_vn, main_hn]))
        
        data = yf.download(yf_tickers, period="max", interval="1d", progress=False)
        
        if data.empty:
            st.error("❌ Mạng lỗi hoặc không tải được dữ liệu.")
            st.stop()
            
        if isinstance(data.columns, pd.MultiIndex):
            close_data = data['Close']
        else:
            if 'Close' in data.columns:
                close_data = pd.DataFrame({yf_tickers[0]: data['Close']})
            else:
                close_data = pd.DataFrame()
            
        main_ticker_yf = None
        for candidate in [main_vn, main_hn]:
            if candidate in close_data.columns and not close_data[candidate].dropna().empty:
                main_ticker_yf = candidate
                break
                
        if not main_ticker_yf:
            st.error(f"❌ Mã {ticker_input} hiện không có dữ liệu trên Yahoo Finance.")
            st.stop()

        rsi_df = pd.DataFrame(index=close_data.index)
        for t in close_data.columns:
            if not close_data[t].dropna().empty:
                rsi_df[t] = calculate_rsi(close_data[t])
            
        hose_peer_cols = [f"{t}.VN" for t in peers_hose]
        valid_hose_cols = [c for c in hose_peer_cols if c in rsi_df.columns]
        
        if valid_hose_cols:
            sector_rsi_series = rsi_df[valid_hose_cols].mean(axis=1).dropna()
        else:
            sector_rsi_series = pd.Series(50.0, index=close_data.index)
            
        current_sector_rsi = sector_rsi_series.iloc[-1] if not sector_rsi_series.empty else 50.0
        
        df_main = pd.DataFrame({'Close': close_data[main_ticker_yf].dropna()})
        
        if len(df_main) < 30:
            st.error(f"❌ Mã {ticker_input} có quá ít lịch sử giao dịch ({len(df_main)} ngày) để áp dụng siêu tối ưu. Vui lòng chọn mã khác.")
            st.stop()
            
        df_main['RSI'] = calculate_rsi(df_main['Close'])
        
        opt_ma, opt_sl, best_ret, user_ret, best_avg_tp_hold, user_avg_tp_hold, best_avg_sl_hold, user_avg_sl_hold, best_sl_rate, user_sl_rate, ma_series = optimize_ma_sl_advanced(df_main, sl_input, sector_rsi_series)
        df_main['MA_Opt'] = ma_series
        
        current_price = df_main['Close'].iloc[-1]
        current_rsi = df_main['RSI'].iloc[-1]
        current_ma_val = ma_series.iloc[-1]
        
        # --- MA TRẬN TÍN HIỆU LÕI MỚI CHUẨN XÁC ---
        signal = "QUAN SÁT (WAIT)"
        output_msg = f"Giá và RSI chưa đạt điều kiện lý tưởng. Tiếp tục theo dõi."
        bg_class = "bg-neutral"
        
        # KIỂM TRA MUA BẮT ĐÁY
        if current_price < current_ma_val and current_rsi < 30:
            if current_sector_rsi < 35:
                signal = "KHOAN MUA"
                output_msg = "Mã rớt về vùng quá bán, nhưng Ngành đang Downtrend (RSI < 35) -> KHOAN MUA."
                bg_class = "bg-warn"
            elif 35 <= current_sector_rsi <= 65:
                signal = "MUA BÌNH THƯỜNG"
                output_msg = "Mã rớt về vùng quá bán, Ngành đang ổn định -> Điểm MUA BẮT ĐÁY tuyệt vời."
                bg_class = "bg-buy"
            elif current_sector_rsi > 65:
                signal = "KHOAN HÃY MUA"
                output_msg = "Ngành đang bay cao (RSI > 65) nhưng mã này cắm đầu -> Có vấn đề nội bộ, KHOAN MUA."
                bg_class = "bg-sell"
                
        # KIỂM TRA BÁN CHỐT LỜI
        elif current_price > current_ma_val:
            if current_rsi > 70 and current_sector_rsi > 65:
                signal = "KHOAN BÁN"
                output_msg = "Mã quá mua nhưng sóng Ngành đang rất mạnh (RSI > 65) -> KHOAN BÁN để bắt trọn sóng."
                bg_class = "bg-buy" 
            elif current_rsi > 70 and 35 <= current_sector_rsi <= 65:
                signal = "BÁN BÌNH THƯỜNG"
                output_msg = "Mã chạm đỉnh ngắn hạn, sóng Ngành bình thường -> BÁN CHỐT LỜI an toàn."
                bg_class = "bg-sell"
            elif current_rsi >= 65 and current_sector_rsi < 35:
                signal = "CHỐT LỜI SỚM"
                output_msg = "Ngành đang Downtrend (RSI < 35) -> Hạ tiêu chuẩn, CHỐT LỜI SỚM khi RSI mã chớm đạt 65."
                bg_class = "bg-sell"

        st.session_state['results'] = {
            'signal': signal, 'output_msg': output_msg, 'bg_class': bg_class,
            'user_ret': user_ret, 'best_ret': best_ret, 'sl_input': sl_input, 'opt_sl': opt_sl,
            'best_avg_tp_hold': best_avg_tp_hold, 'user_avg_tp_hold': user_avg_tp_hold, 
            'best_avg_sl_hold': best_avg_sl_hold, 'user_avg_sl_hold': user_avg_sl_hold,
            'best_sl_rate': best_sl_rate, 'user_sl_rate': user_sl_rate,
            'current_price': current_price, 'current_rsi': current_rsi,
            'opt_ma': opt_ma, 'current_ma_val': current_ma_val, 'sector_name': sector_name,
            'current_sector_rsi': current_sector_rsi, 'df_main': df_main
        }
        st.session_state['analysis_done'] = True

# --- 6. HIỂN THỊ KẾT QUẢ KHI ĐÃ CÓ DỮ LIỆU ---
if st.session_state.get('analysis_done', False):
    with results_placeholder.container():
        res = st.session_state['results']
        
        df_full = res.get('df_main', None)
        if df_full is None:
            st.info("🔄 Hệ thống vừa cập nhật. Vui lòng ấn **🚀 PHÂN TÍCH & SIÊU TỐI ƯU** một lần nữa!")
            st.stop()
            
        # 6.1 Box Tín Hiệu
        st.markdown(f"""
        <div class='result-box {res['bg_class']}'>
            <div class='signal-text'>{res['signal']}</div>
            <div class='reason-text'>💡 {res['output_msg']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 6.2 Box Backtest
        u_color = "#00E676" if res['user_ret'] > 0 else "#FF5252"
        o_color = "#00E5FF" 
        sl_text_user = f"{res['sl_input']:.1f}%"
        sl_text_opt = f"{res['opt_sl']:.1f}%"
        
        st.markdown(f"""
        <div class='bt-container'>
            <div class='bt-col'>
                <div class='bt-label'>CHIẾN LƯỢC CỦA BẠN (SL {sl_text_user})</div>
                <div class='bt-val' style='color:{u_color}'>{res['user_ret']:+.1f}%<span style='font-size:1.4rem'>/năm</span></div>
                <div class='bt-note'>Hiệu quả lợi nhuận trung bình</div>
                <div class='bt-hold'>✅ Gồng lời trung bình: {res['user_avg_tp_hold']:.0f} ngày</div>
                <div class='bt-hold-sl'>❌ Phải cắt lỗ trung bình sau: {res['user_avg_sl_hold']:.0f} ngày</div>
                <div class='bt-note' style='margin-top:8px;'>Tỷ lệ số lệnh phải cắt lỗ: <b>{res['user_sl_rate']:.1f}%</b></div>
            </div>
            <div class='bt-divider'></div>
            <div class='bt-col'>
                <div class='bt-label'>TỐI ƯU NHẤT <span class='opt-badge'>RECOMMENDED</span></div>
                <div class='bt-val' style='color:{o_color}'>{res['best_ret']:+.1f}%<span style='font-size:1.4rem'>/năm</span></div>
                <div class='bt-note'>Với mức Stoploss <b>{sl_text_opt}</b></div>
                <div class='bt-hold'>✅ Gồng lời trung bình: {res['best_avg_tp_hold']:.0f} ngày</div>
                <div class='bt-hold-sl'>❌ Phải cắt lỗ trung bình sau: {res['best_avg_sl_hold']:.0f} ngày</div>
                <div class='bt-note' style='margin-top:8px;'>Tỷ lệ số lệnh phải cắt lỗ: <b>{res['best_sl_rate']:.1f}%</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- 7. BẢNG CHỈ SỐ KỸ THUẬT ---
        col_m1, col_m2 = st.columns(2, gap="large")
        
        with col_m1:
            rsi_val = res['current_rsi']
            rsi_class = "m-sub-down" if rsi_val > 70 else ("m-sub-up" if rsi_val < 30 else "m-sub-neu")
            rsi_text = "🔥 Quá mua" if rsi_val > 70 else ("🧊 Quá bán" if rsi_val < 30 else "⚖️ Trung tính")
            
            st.markdown(f"""
            <div class='metric-card'>
                <div class='m-section'>
                    <div class='m-label'>🏷️ GIÁ HIỆN TẠI</div>
                    <div class='m-val'>{res['current_price']:,.0f}</div>
                </div>
                <div class='m-divider'></div>
                <div class='m-section'>
                    <div class='m-label'>⚡ RSI CỔ PHIẾU</div>
                    <div class='m-val'>{rsi_val:.1f}</div>
                    <div class='{rsi_class}'>{rsi_text}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_m2:
            sec_rsi = res['current_sector_rsi']
            if sec_rsi < 35:
                trend_val = "Downtrend"
                trend_class = "m-sub-down"
            elif sec_rsi > 65:
                trend_val = "Uptrend"
                trend_class = "m-sub-up"
            else:
                trend_val = "Bình thường"
                trend_class = "m-sub-neu"
            
            st.markdown(f"""
            <div class='metric-card'>
                <div class='m-section'>
                    <div class='m-label'>🎯 HỖ TRỢ/KHÁNG CỰ ĐỘNG</div>
                    <div class='m-val' style='color:#FF9800;'>MA {res['opt_ma']}</div>
                    <div class='m-sub-neu'>Mốc giá: {res['current_ma_val']:,.0f}</div>
                </div>
                <div class='m-divider'></div>
                <div class='m-section'>
                    <div class='m-label'>🏢 XU HƯỚNG NGÀNH ({res['sector_name']})</div>
                    <div class='m-val-text'>{trend_val}</div>
                    <div class='{trend_class}'>RSI Ngành: {sec_rsi:.1f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- 8. BIỂU ĐỒ TRỰC QUAN ---
        time_range = st.radio(
            "⏳ Chọn khung thời gian hiển thị biểu đồ:",
            ["1 Tuần", "1 Tháng", "3 Tháng", "6 Tháng", "1 Năm", "3 Năm", "Toàn bộ"],
            horizontal=True,
            index=3
        )
        
        js_blur_radio = f"""
        <script>
            setTimeout(function() {{
                const active = window.parent.document.activeElement;
                if(active && active.tagName === 'INPUT') {{
                    active.blur();
                }}
            }}, 50);
        </script>
        <div style="display:none;">{random.random()}</div>
        """
        components.html(js_blur_radio, height=0)

        if time_range == "1 Tuần": df_plot = df_full.iloc[-5:] 
        elif time_range == "1 Tháng": df_plot = df_full.iloc[-22:] 
        elif time_range == "3 Tháng": df_plot = df_full.iloc[-65:]
        elif time_range == "6 Tháng": df_plot = df_full.iloc[-130:]
        elif time_range == "1 Năm": df_plot = df_full.iloc[-252:]
        elif time_range == "3 Năm": df_plot = df_full.iloc[-756:]
        else: df_plot = df_full
        
        st.markdown("<h4 style='color:#00E5FF; margin-top:10px; margin-bottom:10px;'>📈 DIỄN BIẾN GIÁ & HỖ TRỢ/KHÁNG CỰ ĐỘNG</h4>", unsafe_allow_html=True)
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Close'], name='Đường Giá', line=dict(color='#FFFFFF', width=2.5)))
        fig1.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MA_Opt'], name=f"MA {res['opt_ma']}", line=dict(color='#FF9800', width=2, dash='solid')))
        fig1.update_layout(
            template='plotly_dark', margin=dict(l=0, r=0, t=20, b=0), height=400,
            legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.2)',
            xaxis=dict(showgrid=True, gridcolor='#333'), yaxis=dict(showgrid=True, gridcolor='#333')
        )
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown("<br><hr style='border-top: 1px dashed #444; margin: 10px 0;'><br>", unsafe_allow_html=True)
        
        st.markdown("<h4 style='color:#00E676; margin-top:0px; margin-bottom:10px;'>⚡ CHỈ BÁO ĐỘNG LƯỢNG (RSI 14)</h4>", unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_plot.index, y=df_plot['RSI'], name='RSI', line=dict(color='#00E5FF', width=2)))
        fig2.add_hline(y=70, line_dash='dash', line_color='#FF5252')
        fig2.add_hline(y=30, line_dash='dash', line_color='#00E676')
        
        if len(df_plot) > 5:
            anno_x = df_plot.index[int(len(df_plot)*0.05)]
            fig2.add_annotation(x=anno_x, y=75, text="Quá Mua (70)", showarrow=False, font=dict(color="#FF5252"))
            fig2.add_annotation(x=anno_x, y=25, text="Quá Bán (30)", showarrow=False, font=dict(color="#00E676"))
        
        fig2.update_layout(
            template='plotly_dark', margin=dict(l=0, r=0, t=20, b=10), height=300,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.2)',
            xaxis=dict(showgrid=True, gridcolor='#333'), yaxis=dict(showgrid=True, gridcolor='#333', range=[10, 90])
        )
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
