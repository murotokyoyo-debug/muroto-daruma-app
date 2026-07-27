import streamlit as st
import pandas as pd
import numpy as np
import datetime

# 画面設定
st.set_page_config(page_title="室戸だるま夕日シュミレーター", page_icon="🌅", layout="wide")

# 🌅 夕日グラデーションタイトルの表示
st.markdown("""
    <h1 style="
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ff4e50 0%, #f9d423 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        padding-bottom: 5px;
    ">
        🌅 室戸だるま夕日シュミレーター（理科学習・実践モデル）
    </h1>
""", unsafe_allow_html=True)

st.caption("気象の物理メカニズム（下位蜃気楼）に基づき、室戸岬のだるま夕日発生条件をシミュレーション＆予想しよう！")

# データの読み込み
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('muroto_history.csv')
        df['日付'] = pd.to_datetime(df['日付'], format='mixed', errors='coerce').dt.strftime('%Y-%m-%d')
        df['月'] = pd.to_datetime(df['日付']).dt.month
        df['温度差'] = df['海水温'] - df['気温']
        return df
    except Exception as e:
        return None

df = load_data()

# ==========================================
# 📱 タブ構成（実践モードを含む4タブ）
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "⚙️ ① 発生条件の設定", 
    "📈 ② 過去データ検証", 
    "🔎 ③ 日付ピンポイント検索",
    "🔮 ④ 今日の夕日予報（実践モード）"
])

# ------------------------------------------
# タブ1：条件設定（気象物理メカニズムに基づく）
# ------------------------------------------
with tab1:
    st.subheader("🛠️ だるま夕日の「科学的発生規則」を設定しよう")
    st.info("💡 だるま夕日は「下位蜃気楼」という物理現象です。温度差・雲量・風の条件を正しく設定してみましょう！")

    st.markdown("---")
    
    # === ① 温度差（物理的絶対条件） ===
    st.markdown("### 🌡️ 条件1：【絶対条件】海水温と気温の差（下位蜃気楼の発生メカニズム）")
    st.markdown("""
    > **⚠️ 理科のポイント：** 温かい海の上に冷たい空気の層ができることで、光が下向きに屈折して「だるま型」に見えます。  
    > **海水温が気温より高くならない限り、物理的に蜃気楼は絶対に発生しません（AND条件）。**
    """)
    
    col1_temp, col2_temp = st.columns([6, 4])
    with col1_temp:
        threshold_temp = st.slider(
            "海水温が気温より何℃以上高いことを「必須条件」にする？ (℃)", 
            min_value=0.0, max_value=10.0, value=2.0, step=0.5,
            help="※0℃以下では下位蜃気楼は発生しません。一般的に2℃以上の差が必要とされています。"
        )
    with col2_temp:
        st.warning(f"🎯 **判定ルール:**  \n温度差が **{threshold_temp}℃ 未満** の場合、他の条件がどんなに良くても**発生確率は 0%** になります。")

    st.markdown("---")

    # === ② 雲量 ===
    st.markdown("### ☁️ 条件2：西の天空・水平線の晴れぐあい（雲の量）")
    st.markdown("""
    > **⚠️ 理科のポイント：** だるま夕日は日没時（西の水平線）に見られます。空全体ではなく、**西の空が開けていること**が視認の必須条件です。
    """)
    
    col1_clouds, col2_clouds = st.columns([6, 4])
    with col1_clouds:
        threshold_clouds = st.slider(
            "許容できる雲量は何％以下？ (%)", 
            min_value=0, max_value=100, value=30, step=5,
            help="※雲量が少ないほど夕日が見えやすくなります。"
        )
    with col2_clouds:
        st.info(f"🎯 **判定ルール:**  \n雲量が **{threshold_clouds}% 以下** であれば高スコア。超えると視認確率が低下します。")

    st.markdown("---")

    # === ③ 風の条件 ===
    st.markdown("### 🌬️ 条件3：風向と風速（空気層の安定度）")
    st.markdown("""
    > **⚠️ 理科のポイント：** 四国山地を越えて吹く「冷たく乾いた陸風」は海上に安定した温度差を作ります。風が強すぎると空気が混ざり、波で水平線も乱れてしまいます。
    """)
    
    col1_wind, col2_wind = st.columns([6, 4])
    with col1_wind:
        st.markdown("**🧭 風向きグループの選択**")
        wind_group = st.radio(
            "だるま夕日が発生しやすい風向きタイプを選んでね：",
            [
                "🍃 陸風メイン（北・北西・西北西など：山越えの冷たく乾いた風）",
                "🌊 海風メイン（南・南東・東など：太平洋からの湿った風）",
                "🌐 全方向 OK（すべての風向きを許可）"
            ],
            index=0
        )
        
        # 風向リストの割り当て
        if "陸風" in wind_group:
            selected_wind_dirs = ["北", "北北西", "北西", "西北西", "西", "東北東", "北東", "北北東"]
        elif "海風" in wind_group:
            selected_wind_dirs = ["南", "南南東", "南東", "東南東", "東", "西南西", "南西", "南南西"]
        else:
            selected_wind_dirs = ["北", "北北西", "北西", "西北西", "西", "西南西", "南西", "南南西", 
                                  "南", "南南東", "南東", "東南東", "東", "東北東", "北東", "北北東"]

        min_wind, max_wind = st.slider(
            "適正な風速の範囲 (m/s)",
            min_value=0.0, max_value=15.0, value=(1.0, 8.0), step=0.5,
            help="※弱すぎると暖気の層が作られにくく、強すぎると海水と空気が撹拌されてしまいます。"
        )

    with col2_wind:
        st.success(f"""
        🎯 **選択中の風向き設定:**  
        * 対象風向: {', '.join(selected_wind_dirs[:4])}... 等  
        * 適正風速: **{min_wind}m/s ～ {max_wind}m/s**
        """)

    st.markdown("---")
    
    # === ④ 総合判定のボーダー ===
    st.markdown("### 🎯 総合発生判定のボーダーライン")
    threshold_prob = st.slider("発生予測とする総合確率の境界値 (%)", 50, 90, 70, 5, help="※この確率以上で『だるま夕日発生予測（1）』と判定します。")

# ------------------------------------------
# 共通データ計算ロジック（確率・物理統合モデル）
# ------------------------------------------
def calculate_prediction(data_df):
    if data_df is None or len(data_df) == 0:
        return data_df
    
    res = data_df.copy()
    
    # 1. 必須物理条件（温度差）
    is_temp_ok = res['温度差'] >= threshold_temp
    
    # 2. 温度差スコア (0~100)
    score_temp = np.where(is_temp_ok, 100.0, 0.0)
    
    # 3. 雲量スコア (0~100)
    score_cloud = np.where(
        res['雲量'] <= threshold_clouds,
        100.0,
        np.maximum(0.0, 100.0 - (res['雲量'] - threshold_clouds) * 2.5)
    )
    
    # 4. 風条件スコア (0~100)
    wind_dir_ok = res['風向'].isin(selected_wind_dirs)
    wind_speed_ok = (res['風速'] >= min_wind) & (res['風速'] <= max_wind)
    
    score_wind = np.where(
        wind_dir_ok & wind_speed_ok,
        100.0,
        np.where(
            wind_dir_ok | wind_speed_ok,
            50.0,
            10.0
        )
    )
    
    # 5. 総合確率の計算（必須条件を満たさない場合は強制的に0%）
    raw_prob = (score_temp * 0.4) + (score_cloud * 0.4) + (score_wind * 0.2)
    res['発生確率'] = np.where(is_temp_ok, raw_prob, 0.0)
    
    # 6. 発生予測 (1 or 0)
    res['発生予測'] = np.where(res['発生確率'] >= threshold_prob, 1, 0)
    
    return res

if df is not None:
    df_calc = calculate_prediction(df)
else:
    df_calc = None

# ------------------------------------------
# タブ2：過去データ検証
# ------------------------------------------
with tab2:
    st.subheader("📈 シミュレーション結果（過去データの検証）")
    
    if df_calc is None:
        st.error("⚠️ データファイル（muroto_history.csv）が読み込まれていません。")
    else:
        total_days = len(df_calc)
        predicted_days = int(df_calc['発生予測'].sum())
        avg_yearly_days = predicted_days / 4.0

        m1, m2, m3 = st.columns(3)
        m1.metric("検証対象日数", f"{total_days} 日", "2021-2025（10月〜3月）")
        m2.metric("4シーズン合計発生日数", f"{predicted_days} 日")
        m3.metric("年間平均発生日数", f"{avg_yearly_days:.1f} 日 / 年", "実際の平均: 約10〜20日")

        st.markdown("#### 🤖 AI気象アドバイザーの判定＆学習フィードバック")
        
        if "海風" in wind_group:
            st.error("❌ **気象的矛盾:** 海風（沖からの湿った風）は水蒸気や雲を発生させやすく、冷たい空気層を乱すためだるま夕日には不向きです。「陸風メイン」に変更してみましょう！")
        elif threshold_temp < 1.0:
            st.warning("⚠️ **物理条件が緩すぎます:** 海水温と気温の差が小さすぎると、下位蜃気楼（光の下向き屈折）が不十分になります。2.0℃以上に設定してみましょう。")
        elif threshold_clouds > 60:
            st.warning("☁️ **視認条件が緩すぎます:** 雲量が60%以上あると夕日が雲に隠れて見えません。30%以下に設定するのが一般的です。")
        elif predicted_days == 0:
            st.warning("⚠️ **条件が厳しすぎます:** 発生予測が0日になりました。確率ボーダー値や風速範囲を少し調整してみましょう。")
        elif 10 <= avg_yearly_days <= 25:
            st.success(f"🎉 **【完璧な科学的設定！】** 年間 {avg_yearly_days:.1f} 日の予測です。実際の室戸岬での「本物のだるま夕日」年間観測数（10〜20回前後）に極めて近いリアルな設定になっています！")
        elif avg_yearly_days < 10:
            st.info(f"💡 年間 {avg_yearly_days:.1f} 日の予測です。厳選された「超快晴＋完璧な蜃気楼日」のみを捉えた非常に厳しい設定です。")
        else:
            st.error(f"🔺 年間 {avg_yearly_days:.1f} 日の予測です。発生数が多すぎます！条件（温度差・雲量・風向）をもう少し厳しく見直してみましょう。")

        st.markdown("---")
        st.markdown("#### 📅 月別の発生予想（4シーズンの合計）")
        
        season_months = [10, 11, 12, 1, 2, 3]
        monthly_data = df_calc.groupby('月')['発生予測'].sum().reindex(season_months, fill_value=0).reset_index()
        monthly_data['月表示'] = monthly_data['月'].astype(str) + '月'
        monthly_summary = monthly_data.set_index('月表示')
        
        st.bar_chart(monthly_summary['発生予測'])

# ------------------------------------------
# タブ3：日付ピンポイント検索
# ------------------------------------------
with tab3:
    st.subheader("🔎 特定の日のデータを確かめる")
    
    if df_calc is not None:
        selected_date = st.date_input("日付を選択", value=datetime.date(2021, 10, 20))
        date_str = selected_date.strftime('%Y-%m-%d')
        target_data = df_calc[df_calc['日付'] == date_str]

        if len(target_data) > 0:
            row = target_data.iloc[0]
            st.write(f"**【{date_str} の室戸岬の観測データ】**")
            
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("気温 / 海水温", f"{row['気温']}℃ / {row['海水温']}℃")
            col_a.metric("温度差", f"{row['温度差']:.1f}℃", delta="判定基準クリア" if row['温度差'] >= threshold_temp else "基準未達", delta_color="normal" if row['温度差'] >= threshold_temp else "inverse")
            
            col_b.metric("風向・風速", f"{row['風向']} {row['風速']}m/s")
            col_b.metric("雲量", f"{row['雲量']}％")
            
            col_c.metric("総合発生確率", f"{row['発生確率']:.1f}％")

            st.markdown("---")
            if row['発生予測'] == 1:
                st.success(f"🎉 **だるま夕日 発生期待大！** （計算確率: {row['発生確率']:.1f}% / 判定ボーダー: {threshold_prob}%）")
            else:
                st.error(f"❄️ **発生可能性 低** （計算確率: {row['発生確率']:.1f}% / 判定ボーダー: {threshold_prob}%）")
                
                # 不成立の理由自動分析
                reasons = []
                if row['温度差'] < threshold_temp:
                    reasons.append(f"・【下位蜃気楼の不成立】温度差（{row['温度差']:.1f}℃）が必要条件（{threshold_temp}℃）に達していません。")
                if row['雲量'] > threshold_clouds:
                    reasons.append(f"・【視認不可】雲量（{row['雲量']}%）が多く、夕日が遮られます。")
                if not row['風向'].isin(selected_wind_dirs):
                    reasons.append(f"・【風向不適切】風向（{row['風向']}）が設定した風向きグループに含まれていません。")
                if not (min_wind <= row['風速'] <= max_wind):
                    reasons.append(f"・【風速不適切】風速（{row['風速']}m/s）が適正範囲（{min_wind}〜{max_wind}m/s）外です。")
                
                if reasons:
                    st.info("**【見られない原因の理科的分析】**\n" + "\n".join(reasons))
        else:
            st.warning("この日付のデータはありません。")

# ------------------------------------------
# タブ4：今日・明日の夕日予報（実践モード）
# ------------------------------------------
with tab4:
    st.subheader("🔮 天気予報データから「今日のだるま夕日」を予想しよう！")
    st.caption("天気予報サイトや気象庁発表の数値（予想気温・風向・風速・雲量）を入力して、今日のだるま夕日遭遇確率をリアルタイム計算します。")

    st.markdown("---")
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("##### 📝 今日の気象予報データの入力")
        input_temp = st.number_input("予想気温 (℃)", value=12.0, step=0.5)
        input_sea_temp = st.number_input("推定海水温 (℃)", value=18.0, step=0.5, help="※室戸沖の冬の海水温は17〜20℃前後です")
        input_cloud = st.slider("予想雲量 (0:快晴 〜 100:全天曇り)", 0, 100, 10)
        input_wind_dir = st.selectbox("予想風向", ["北", "北北西", "北西", "西北西", "西", "西南西", "南西", "南南西", "南", "南南東", "南東", "東南東", "東", "東北東", "北東", "北北東"], index=2)
        input_wind_speed = st.number_input("予想風速 (m/s)", value=3.5, step=0.5)

    # リアルタイム計算
    input_diff = input_sea_temp - input_temp
    is_temp_pass = input_diff >= threshold_temp
    
    score_t = 100.0 if is_temp_pass else 0.0
    score_c = 100.0 if input_cloud <= threshold_clouds else max(0.0, 100.0 - (input_cloud - threshold_clouds) * 2.5)
    
    dir_ok = input_wind_dir in selected_wind_dirs
    spd_ok = min_wind <= input_wind_speed <= max_wind
    score_w = 100.0 if (dir_ok and spd_ok) else (50.0 if (dir_ok or spd_ok) else 10.0)
    
    prob = (score_t * 0.4 + score_c * 0.4 + score_w * 0.2) if is_temp_pass else 0.0

    with c2:
        st.markdown("##### 📊 予測判定結果")
        
        st.metric("海水温と気温の差", f"{input_diff:.1f} ℃", delta="下位蜃気楼条件クリア" if is_temp_pass else "温度差不足", delta_color="normal" if is_temp_pass else "inverse")
        st.metric("だるま夕日 遭遇確率", f"{prob:.1f} ％")
        
        if prob >= threshold_prob:
            st.balloons()
            st.success("🌅 **【絶好のチャンス！】今日のだるま夕日指数: ★★★**\n物理条件・気象条件が完璧に整っています！室戸岬へ向かう価値大です。")
        elif prob >= 40:
            st.warning("⛅ **【可能性あり】今日のだるま夕日指数: ★★☆**\n条件の一部が惜しいですが、西の空の開けたタイミングで見られる可能性があります。")
        else:
            st.error("🌧️ **【難しい】今日のだるま夕日指数: ★☆☆**\n気象条件が整っていないため、だるま型になる可能性は非常に低いです。")
