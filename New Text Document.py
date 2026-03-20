import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
import streamlit.components.v1 as components
import random
import warnings

warnings.filterwarnings('ignore')

# --- 1. CẤU HÌNH TRANG (MỞ RỘNG TOÀN MÀN HÌNH) ---
st.set_page_config(layout="wide", page_title="Stock Advisor Super Pro", page_icon="🚀")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FFFFFF; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .main-title { text-align: center; font-weight: 900; font-size: 3.2rem; color: #00E676; letter-spacing: 2px; margin-bottom: 5px; text-transform: uppercase; text-shadow: 0px 0px 20px rgba(0, 230, 118, 0.3); }
    .sub-title { text-align: center; color: #A0AAB5; font-size: 1.1rem; margin-bottom: 30px; font-weight: 500; }
    .disclaimer-box { background-color: #1A1D24; border: 1px solid #2D333B; border-radius: 8px; padding: 20px; margin: 0 auto 30px auto; text-align: center; max-width: 750px; box-shadow: 0 4px 10px rgba(0,0,0,0.4); }
    .disclaimer-title { color: #FF5252; font-weight: bold; font-size: 1.05rem; margin-bottom: 12px; text-transform: uppercase; }
    .d-text-1 { color: #A0AAB5; font-size: 0.95rem; margin-bottom: 6px; }
    .d-text-2 { color: #FFFFFF; font-size: 1rem; font-weight: bold; margin-bottom: 6px; text-decoration: underline; text-decoration-color: #555;}
    
    div[data-baseweb="input"] { background-color: #262730; border-color: #41424C; border-radius: 6px; }
    div[data-baseweb="input"] > input { color: white !important; font-weight: bold; text-align: center;}
    label { color: #B0BEC5 !important; font-weight: bold !important; font-size: 0.95rem !important; }

    div.stFormSubmitButton > button { background-color: #1A1D24; border: 1px solid #333; color: white; font-weight: bold; height: 50px; font-size: 1.1rem; transition: 0.3s; border-radius: 6px; margin-top: 5px; }
    div.stFormSubmitButton > button:hover { border-color: #00E676; color: #00E676; background-color: #121418; box-shadow: 0 0 10px rgba(0,230,118,0.2); }

    .result-box { padding: 30px 20px; border-radius: 12px; margin-top: 10px; text-align: center; box-shadow: 0 8px 20px rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1); }
    .bg-buy { background: linear-gradient(135deg, #00C853, #1B5E20); }
    .bg-sell { background: linear-gradient(135deg, #D50000, #880E4F); }
    .bg-warn { background: linear-gradient(135deg, #FF6D00, #E65100); }
    .bg-neutral { background: linear-gradient(135deg, #0D47A1, #1565C0); }
    .signal-text { font-size: 2.5rem; font-weight: 900; color: white; margin-bottom: 8px; text-shadow: 0 2px 5px rgba(0,0,0,0.5); text-transform: uppercase;}
    .reason-text { font-size: 1.1rem; color: #FAFAFA; font-style: italic; font-weight: 500;}

    .bt-container { display: flex; justify-content: space-around; align-items: center; background: linear-gradient(135deg, #263238 0%, #1E272C 100%); border-radius: 12px; padding: 30px 20px; margin-top: 25px; text-align: center; border: 1px solid #37474F; box-shadow: 0 6px 15px rgba(0,0,0,0.3); }
    .bt-col { flex: 1; text-align: center; }
    .bt-label { color: #B0BEC5; font-size: 0.95rem; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: bold; }
    .bt-val { font-size: 2.8rem; font-weight: 900; line-height: 1.1; margin-bottom: 5px; }
    .bt-note { font-size: 0.9rem; color: #90A4AE; margin-top: 5px; margin-bottom: 12px;}
    .bt-hold { font-size: 0.85rem; color: #FFF; background-color: rgba(0,230,118,0.1); border: 1px solid rgba(0,230,118,0.3); padding: 4px 12px; border-radius: 20px; display: inline-block; font-weight: 500; margin: 3px;}
    .bt-hold-sl { font-size: 0.85rem; color: #FFF; background-color: rgba(255,82,82,0.1); border: 1px solid rgba(255,82,82,0.3); padding: 4px 12px; border-radius: 20px; display: inline-block; font-weight: 500; margin: 3px;}
    .bt-divider { width: 1px; background-color: #546E7A; height: 130px; margin: 0 20px; opacity: 0.5; }
    .opt-badge { background-color: #00E5FF; color: #000; padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 900; margin-left: 8px; vertical-align: middle; box-shadow: 0 0 10px rgba(0, 229, 255, 0.4); }

    .metric-card { background-color: #1E272C; border: 1px solid #37474F; border-radius: 12px; padding: 15px; text-align: center; box-shadow: 0 6px 12px rgba(0,0,0,0.3); height: 320px; display: flex; flex-direction: column; margin-bottom: 15px; transition: transform 0.2s; }
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

st.markdown("<div class='main-title'>STOCK ADVISOR SUPER PRO</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Phân Tích Dòng Tiền & Tối Ưu Hóa MA Clusters</div>", unsafe_allow_html=True)
st.markdown("""
<div class='disclaimer-box'>
    <div class='disclaimer-title'>⚠️ TUYÊN BỐ MIỄN TRỪ TRÁCH NHIỆM</div>
    <div class='d-text-1'>Phân tích kỹ thuật tự động dựa trên dữ liệu quá khứ.</div>
    <div class='d-text-2'>KHÔNG phải lời khuyên đầu tư tài chính chính thức.</div>
</div>
""", unsafe_allow_html=True)

# --- 3. HÀM XỬ LÝ & THUẬT TOÁN ---
@st.cache_data
def load_sector_database():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path_1 = os.path.join(current_dir, 'data', 'database_nganh.csv')
    path_2 = os.path.join(current_dir, 'database_nganh.csv')
    if os.path.exists(path_1): return pd.read_csv(path_1)
    elif os.path.exists(path_2): return pd.read_csv(path_2)
    return None

def calculate_rsi(series, period=14):
    if isinstance(series, pd.DataFrame): series = series.squeeze()
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).ewm(span=period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(span=period, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_s1_triggers(close_arr, rsi_arr, sec_rsi_arr, ma_line):
    # Logic chuẩn Strategy 1 (RSI Ngành 35 - 65)
    buy = (close_arr < ma_line) & (rsi_arr < 30) & (sec_rsi_arr >= 35) & (sec_rsi_arr <= 65)
    sell = (close_arr > ma_line) & (((rsi_arr > 70) & (sec_rsi_arr >= 35) & (sec_rsi_arr <= 65)) | ((rsi_arr >= 65) & (sec_rsi_arr < 35)))
    return buy, sell

def run_simulation_fast(close_arr, buy_triggers, sell_triggers, sl_val):
    in_trade = False
    entry_price = 0.0
    cum_ret = 1.0
    total_trades = 0
    sl_trades = 0
    hold_sum_tp = 0
    hold_sum_sl = 0
    current_hold = 0

    for i in range(1, len(close_arr)):
        if not in_trade:
            if buy_triggers[i-1]:
                in_trade = True
                entry_price = float(close_arr[i])
                current_hold = 1
        else:
            current_hold += 1
            price_now = float(close_arr[i])
            if sl_val > 0 and (price_now - entry_price) / entry_price <= -sl_val:
                cum_ret *= (1 - sl_val)
                sl_trades += 1
                total_trades += 1
                hold_sum_sl += current_hold
                in_trade = False
                current_hold = 0
            elif sell_triggers[i-1]:
                trade_ret = (price_now - entry_price) / entry_price
                cum_ret *= (1 + trade_ret)
                total_trades += 1
                hold_sum_tp += current_hold
                in_trade = False
                current_hold = 0

    if in_trade:
        trade_ret = (float(close_arr[-1]) - entry_price) / entry_price
        cum_ret *= (1 + trade_ret)

    tp_trades = total_trades - sl_trades
    avg_tp = hold_sum_tp / tp_trades if tp_trades > 0 else 0
    avg_sl = hold_sum_sl / sl_trades if sl_trades > 0 else 0
    sl_rate = (sl_trades / total_trades * 100) if total_trades > 0 else 0
    return cum_ret - 1, avg_tp, avg_sl, sl_rate

def optimize_and_classify_s1(df, sector_rsi_series, user_sl_decimal):
    close_arr = df['Close'].values.flatten()
    rsi_arr = df['RSI'].values.flatten()
    sec_rsi_arr = sector_rsi_series.reindex(df.index).ffill().values.flatten()
    
    ma_windows = np.arange(5, 210, 5)
    sl_levels = np.arange(0.03, 0.105, 0.005)
    years = max((df.index[-1] - df.index[0]).days / 365.25, 1)

    ma_returns = []

    # BƯỚC 1: TÌM LỢI NHUẬN TỐI ƯU CỦA TẤT CẢ MA
    for w in ma_windows:
        ma_line = df['Close'].rolling(w).mean().values.flatten()
        buy_s1, sell_s1 = get_s1_triggers(close_arr, rsi_arr, sec_rsi_arr, ma_line)

        best_w_ret = -999.0
        for sl in sl_levels:
            ret, _, _, _ = run_simulation_fast(close_arr, buy_s1, sell_s1, sl)
            if ret > best_w_ret: 
                best_w_ret = ret
        ma_returns.append((w, best_w_ret))

    # BƯỚC 2: TÌM TOP 5 MA & PHÂN LOẠI
    ma_returns.sort(key=lambda x: x[1], reverse=True)
    top_5_mas = [x[0] for x in ma_returns[:5]]
    best_raw_ma = top_5_mas[0] # MA sinh lời tuyệt đối cao nhất

    short_count = sum(1 for w in top_5_mas if 5 <= w <= 30)
    mid_count = sum(1 for w in top_5_mas if 35 <= w <= 100)
    long_count = sum(1 for w in top_5_mas if 105 <= w <= 205)

    if short_count >= 3:
        trend_label, fixed_ma = "Ngắn hạn", 20
    elif mid_count >= 3:
        trend_label, fixed_ma = "Trung hạn", 50
    elif long_count >= 3:
        trend_label, fixed_ma = "Dài hạn", 200
    else:
        trend_label, fixed_ma = "Không rõ ràng", best_raw_ma

    # BƯỚC 3: TỐI ƯU HÓA LẠI SL CHO ĐƯỜNG MA ĐÃ CHỐT
    ma_line_final = df['Close'].rolling(fixed_ma).mean().values.flatten()
    buy_f, sell_f = get_s1_triggers(close_arr, rsi_arr, sec_rsi_arr, ma_line_final)

    # Tính SL Tối ưu
    best_final = {'ann_ret': -999.0, 'sl': 0.0, 'tp_hold': 0.0, 'sl_hold': 0.0, 'sl_rate': 0.0}
    for sl in sl_levels:
        ret, tp_h, sl_h, sl_r = run_simulation_fast(close_arr, buy_f, sell_f, sl)
        ann_ret = (ret / years) * 100
        if ann_ret > best_final['ann_ret']:
            best_final.update({'ann_ret': ann_ret, 'sl': sl*100, 'tp_hold': tp_h, 'sl_hold': sl_h, 'sl_rate': sl_r})
    
    if best_final['ann_ret'] == -999.0: best_final['ann_ret'] = 0.0

    # Tính lợi nhuận theo SL người dùng nhập
    u_ret, u_tp_h, u_sl_h, u_sl_r = run_simulation_fast(close_arr, buy_f, sell_f, user_sl_decimal)
    u_ann_ret = (u_ret / years) * 100

    return {
        'trend': trend_label, 'ma': fixed_ma, 'ma_series': ma_line_final,
        'opt_ann_ret': best_final['ann_ret'], 'opt_sl': best_final['sl'], 
        'opt_tp_hold': best_final['tp_hold'], 'opt_sl_hold': best_final['sl_hold'], 'opt_sl_rate': best_final['sl_rate'],
        'usr_ann_ret': u_ann_ret, 'usr_tp_hold': u_tp_h, 'usr_sl_hold': u_sl_h, 'usr_sl_rate': u_sl_r
    }

def generate_s1_signal(current_price, current_rsi, current_sec_rsi, current_ma_val):
    signal, output_msg, bg_class = "QUAN SÁT (WAIT)", "Giá và RSI chưa đạt điều kiện. Theo dõi thêm.", "bg-neutral"
    
    if current_price < current_ma_val and current_rsi < 30:
        if current_sec_rsi < 35:
            signal, output_msg, bg_class = "KHOAN MUA", "Mã quá bán nhưng Ngành Downtrend (<35) -> KHOAN MUA.", "bg-warn"
        elif 35 <= current_sec_rsi <= 65:
            signal, output_msg, bg_class = "MUA BÌNH THƯỜNG", "Mã quá bán, Ngành ổn định -> ĐIỂM MUA TỐT.", "bg-buy"
        else:
            signal, output_msg, bg_class = "KHÔNG NÊN MUA", "Ngành uptrend mà mã cắm đầu -> Có lỗi nội tại.", "bg-sell"
    elif current_price > current_ma_val:
        if current_rsi > 70 and current_sec_rsi > 65:
            signal, output_msg, bg_class = "KHOAN BÁN", "Mã quá mua nhưng sóng ngành mạnh (>65) -> GỒNG LÃI.", "bg-buy"
        elif current_rsi > 70 and 35 <= current_sec_rsi <= 65:
            signal, output_msg, bg_class = "BÁN BÌNH THƯỜNG", "Mã chạm đỉnh, Ngành bình thường -> BÁN CHỐT LỜI.", "bg-sell"
        elif current_rsi >= 65 and current_sec_rsi < 35:
            signal, output_msg, bg_class = "CHỐT LỜI SỚM", "Ngành sụp (<35) -> CHỐT LỜI SỚM khi RSI chạm 65.", "bg-sell"
                
    return signal, output_msg, bg_class

# --- 4. FORM NHẬP LIỆU ---
col_pad1, col_main, col_pad2 = st.columns([1, 2, 1])
with col_main:
    with st.form(key='search_form'):
        f_col1, f_col2 = st.columns([2, 1])
        with f_col1: ticker_input = st.text_input("Mã cổ phiếu:", placeholder="VD: HPG, CEO...").upper().strip()
        with f_col2: sl_input = st.number_input("SL mong muốn (%):", min_value=3.0, max_value=10.0, value=7.0, step=0.5, format="%.1f")
        submit_btn = st.form_submit_button("🚀 PHÂN TÍCH & PHÂN LOẠI", use_container_width=True)

results_placeholder = st.empty()

if submit_btn:
    js_hack = f"""<script>
    function forceBlur(){{ const el=window.parent.document.activeElement; if(el) el.blur(); window.parent.document.body.focus(); }}
    forceBlur(); setTimeout(forceBlur, 100); setTimeout(forceBlur, 500);
    </script><div style="display:none;">{random.random()}</div>"""
    components.html(js_hack, height=0)
    results_placeholder.empty()

# --- 5. LỘ TRÌNH THỰC THI ---
if submit_btn:
    if not ticker_input:
        st.warning("⚠️ Vui lòng nhập mã cổ phiếu!")
        st.stop()
        
    db_nganh = load_sector_database()
    if db_nganh is None:
        st.error("❌ Không tìm thấy file `database_nganh.csv`.")
        st.stop()
        
    ticker_info = db_nganh[db_nganh['Ticker'] == ticker_input]
    if ticker_info.empty:
        st.error(f"❌ Mã {ticker_input} không tồn tại trong Database.")
        st.stop()
        
    sector_name = ticker_info.iloc[0]['Sector']
    exchange = ticker_info.iloc[0]['Exchange'] if 'Exchange' in db_nganh.columns else 'HOSE'
    
    peers_hose = db_nganh[(db_nganh['Sector'] == sector_name) & (db_nganh['Exchange'] == 'HOSE')]['Ticker'].tolist()
    
    with st.spinner(f"🔍 Đang quét dữ liệu lịch sử và xác định nhóm MA cho {ticker_input}..."):
        main_vn = f"{ticker_input}.VN"
        main_hn = f"{ticker_input}.HN"
        yf_tickers = list(set([f"{t}.VN" for t in peers_hose] + [main_vn, main_hn]))
        
        data = yf.download(yf_tickers, period="max", interval="1d", progress=False)
        if data.empty:
            st.error("❌ Không tải được dữ liệu.")
            st.stop()
            
        close_data = data['Close'] if isinstance(data.columns, pd.MultiIndex) else pd.DataFrame({yf_tickers[0]: data['Close']})
            
        main_sym = None
        for candidate in [main_vn, main_hn]:
            if candidate in close_data.columns and not close_data[candidate].dropna().empty:
                main_sym = candidate
                break
                
        if not main_sym:
            st.error(f"❌ Mã {ticker_input} chưa có đủ dữ liệu trên Yahoo.")
            st.stop()

        rsi_df = pd.DataFrame(index=close_data.index)
        for t in close_data.columns:
            if not close_data[t].dropna().empty:
                rsi_df[t] = calculate_rsi(close_data[t])
            
        hose_peer_cols = [f"{t}.VN" for t in peers_hose]
        valid_hose_cols = [c for c in hose_peer_cols if c in rsi_df.columns]
        sector_rsi_series = rsi_df[valid_hose_cols].mean(axis=1).dropna() if valid_hose_cols else pd.Series(50.0, index=close_data.index)
            
        current_sector_rsi = sector_rsi_series.iloc[-1] if not sector_rsi_series.empty else 50.0
        df_main = pd.DataFrame({'Close': close_data[main_sym].dropna()})
        
        if len(df_main) < 150:
            st.error(f"❌ Mã {ticker_input} có lịch sử quá ngắn (Dưới 150 ngày) để chạy Backtest.")
            st.stop()
            
        df_main['RSI'] = calculate_rsi(df_main['Close'])
        
        # Chạy thuật toán Backtest S1
        b_data = optimize_and_classify_s1(df_main, sector_rsi_series, sl_input/100)
        df_main['MA_Opt'] = b_data['ma_series']
        
        current_price = float(df_main['Close'].iloc[-1])
        current_rsi = float(df_main['RSI'].iloc[-1])
        current_ma_val = float(b_data['ma_series'][-1])
        
        # Sinh tín hiệu
        signal, output_msg, bg_class = generate_s1_signal(current_price, current_rsi, current_sector_rsi, current_ma_val)

        st.session_state['results'] = {
            'signal': signal, 'output_msg': output_msg, 'bg_class': bg_class,
            'trend': b_data['trend'], 'opt_ma': b_data['ma'], 'sl_input': sl_input,
            
            'opt_ret': b_data['opt_ann_ret'], 'opt_sl': b_data['opt_sl'],
            'opt_tp_hold': b_data['opt_tp_hold'], 'opt_sl_hold': b_data['opt_sl_hold'], 'opt_sl_rate': b_data['opt_sl_rate'],
            
            'usr_ret': b_data['usr_ann_ret'], 'usr_tp_hold': b_data['usr_tp_hold'],
            'usr_sl_hold': b_data['usr_sl_hold'], 'usr_sl_rate': b_data['usr_sl_rate'],
            
            'current_price': current_price, 'current_rsi': current_rsi, 'current_ma_val': current_ma_val,
            'sector_name': sector_name, 'current_sector_rsi': current_sector_rsi, 'df_main': df_main
        }
        st.session_state['analysis_done'] = True

# --- 6. HIỂN THỊ KẾT QUẢ KHI ĐÃ CÓ DỮ LIỆU ---
if st.session_state.get('analysis_done', False):
    with results_placeholder.container():
        res = st.session_state['results']
        
        st.markdown(f"""
        <div class='result-box {res['bg_class']}'>
            <div class='signal-text'>{res['signal']}</div>
            <div class='reason-text'>💡 {res['output_msg']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        u_color = "#00E676" if res['usr_ret'] > 0 else "#FF5252"
        o_color = "#00E5FF" 
        
        st.markdown(f"""
        <div class='bt-container'>
            <div class='bt-col'>
                <div class='bt-label'>CHIẾN LƯỢC CỦA BẠN (SL {res['sl_input']:.1f}%)</div>
                <div class='bt-val' style='color:{u_color}'>{res['usr_ret']:+.1f}%<span style='font-size:1.4rem'>/năm</span></div>
                <div class='bt-note'>Hiệu quả lợi nhuận trung bình</div>
                <div class='bt-hold'>✅ Gồng lời TB: {res['usr_tp_hold']:.0f} ngày</div>
                <div class='bt-hold-sl'>❌ Cắt lỗ TB sau: {res['usr_sl_hold']:.0f} ngày</div>
                <div class='bt-note' style='margin-top:8px;'>Tỷ lệ số lệnh thua: <b>{res['usr_sl_rate']:.1f}%</b></div>
            </div>
            <div class='bt-divider'></div>
            <div class='bt-col'>
                <div class='bt-label'>TỐI ƯU NHẤT <span class='opt-badge'>RECOMMENDED</span></div>
                <div class='bt-val' style='color:{o_color}'>{res['opt_ret']:+.1f}%<span style='font-size:1.4rem'>/năm</span></div>
                <div class='bt-note'>Với mức Stoploss <b>{res['opt_sl']:.1f}%</b></div>
                <div class='bt-hold'>✅ Gồng lời TB: {res['opt_tp_hold']:.0f} ngày</div>
                <div class='bt-hold-sl'>❌ Cắt lỗ TB sau: {res['opt_sl_hold']:.0f} ngày</div>
                <div class='bt-note' style='margin-top:8px;'>Tỷ lệ số lệnh thua: <b>{res['opt_sl_rate']:.1f}%</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
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
            trend_class = "m-sub-down" if sec_rsi < 35 else ("m-sub-up" if sec_rsi > 65 else "m-sub-neu")
            trend_val = "Downtrend" if sec_rsi < 35 else ("Uptrend" if sec_rsi > 65 else "Bình thường")
            
            st.markdown(f"""
            <div class='metric-card'>
                <div class='m-section'>
                    <div class='m-label'>🎯 ĐƯỜNG MA SỬ DỤNG: MA{res['opt_ma']}</div>
                    <div class='m-val' style='color:#FF9800;'>{res['current_ma_val']:,.0f}</div>
                    <div class='m-sub-neu'>Nhóm cổ phiếu: {res['trend']}</div>
                </div>
                <div class='m-divider'></div>
                <div class='m-section'>
                    <div class='m-label'>🏢 SỨC MẠNH NGÀNH ({res['sector_name']})</div>
                    <div class='m-val-text'>{trend_val}</div>
                    <div class='{trend_class}'>RSI Ngành: {sec_rsi:.1f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        time_range = st.radio("⏳ Khung thời gian biểu đồ:", ["1 Tháng", "3 Tháng", "6 Tháng", "1 Năm", "3 Năm", "Toàn bộ"], horizontal=True, index=2)
        components.html(f"""<script>setTimeout(function(){{ const el=window.parent.document.activeElement; if(el && el.tagName==='INPUT') el.blur(); }}, 50);</script><div style="display:none;">{random.random()}</div>""", height=0)

        df_full = res['df_main']
        if time_range == "1 Tháng": df_plot = df_full.iloc[-22:] 
        elif time_range == "3 Tháng": df_plot = df_full.iloc[-65:]
        elif time_range == "6 Tháng": df_plot = df_full.iloc[-130:]
        elif time_range == "1 Năm": df_plot = df_full.iloc[-252:]
        elif time_range == "3 Năm": df_plot = df_full.iloc[-756:]
        else: df_plot = df_full
        
        st.markdown(f"<h4 style='color:#00E5FF;'>📈 DIỄN BIẾN GIÁ & MA{res['opt_ma']}</h4>", unsafe_allow_html=True)
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Close'], name='Đường Giá', line=dict(color='#FFFFFF', width=2.5)))
        fig1.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MA_Opt'], name=f"MA {res['opt_ma']}", line=dict(color='#FF9800', width=2, dash='solid')))
        fig1.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=20, b=0), height=400, legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.2)')
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown("<h4 style='color:#00E676; margin-top:20px;'>⚡ CHỈ BÁO ĐỘNG LƯỢNG (RSI 14)</h4>", unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_plot.index, y=df_plot['RSI'], name='RSI', line=dict(color='#00E5FF', width=2)))
        fig2.add_hline(y=70, line_dash='dash', line_color='#FF5252')
        fig2.add_hline(y=30, line_dash='dash', line_color='#00E676')
        fig2.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=20, b=10), height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.2)', yaxis=dict(range=[10, 90]))
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
