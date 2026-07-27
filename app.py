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
# タブ1：条件設定（グラデーション評価モデル）
# ------------------------------------------
with tab1:
    st.subheader("🛠️ だるま夕日の「科学的発生規則」を設定しよう")
    st.info("💡 だるま夕日は「下位蜃気楼」という物理現象です。条件にぴったり当てはまらなくても、数値に応じて連続的（滑らか）に確率が変化します！")

    st.markdown("---")
    
    # === ① 温度差（連続評価モデル） ===
    st.markdown("### 🌡️ 条件1：海水温と気温の差（目標温度差）")
    st.markdown("""
    > **⚠️ 理科のポイント：** 温かい海の上に冷たい空気の層ができることで、光が屈折します。  
    > **海水温が気温より低い（0℃以下）と物理的に蜃気楼は発生しません**が、目標温度差より少し低くても、条件に応じて確率が滑らかに付与されます。
    """)
    
    col1_temp, col2_temp = st.columns([6, 4])
    with col1_temp:
        threshold_temp = st.slider(
            "理想的な海水温と気温の差 (℃)", 
            min_value=0.5, max_value=8.0, value=3.0, step=0.5,
            help="※一般的に2〜3℃以上の差があると綺麗に見えやすくなります。"
        )
    with col2_temp:
        st.success(f"""
        🎯 **判定ルール:**  
        * **0℃ 以下:** 蜃気楼が起きないため **0点**
        * **0℃ ～ {threshold_temp}℃:** 温度差に応じて **0〜100点（グラデーション）**
        * **{threshold_temp}℃ 以上:** 満点（**100点**）
        """)

    st.markdown("---")

    # === ② 雲量 ===
    st.markdown("### ☁️ 条件2：空の晴れぐあい（許容する雲量）")
    st.markdown("""
    > **⚠️ 理科のポイント：** だるま夕日は西の水平線が見えることが大切です。雲量が目標を少し超えても、徐々に確率が下がる仕組みになっています。
    """)
    
    col1_clouds, col2_clouds = st.columns([6, 4])
    with col1_clouds:
        threshold_clouds = st.slider(
            "理想的な雲量は何％以下？ (%)", 
            min_value=0, max_value=100, value=30, step=5,
            help="※雲量が少ないほど高得点になります。"
        )
    with col2_clouds:
        st.info(f"🎯 **判定ルール:**  \n雲量が **{threshold_clouds}% 以下** であれば100点。超えた分だけ滑らかに減点されます。")

    st.markdown("---")

    # === ③ 風の条件 ===
    st.markdown("### 🌬️ 条件3：風向と風速（空気層の安定度）")
    st.markdown("""
    > **⚠️ 理科のポイント：** 四国山地を越えて吹く「冷たく乾いた陸風」は海上に安定した温度差を作ります。強風すぎると温床が乱れてしまいます。
    """)
    
    col1_wind, col2_wind = st.columns([6, 4])
    with col1_wind:
        st.markdown("**🧭 風向きグループの選択**")
        wind_group = st.radio(
            "発生しやすい風向きのタイプを選んでね：",
            [
                "🍃 陸風メイン（北・北西・西北西など：山越えの冷たく乾いた風）",
                "🌊 海風メイン（南・南東・東など：太平洋からの湿った風）",
                "🌐 全方向 OK（すべての風向きを許可）"
            ],
            index=0
        )
        
        if "陸風" in wind_group:
            selected_wind_dirs = ["北", "北北西", "北西", "西北西", "西", "東北東", "北東", "北北東"]
        elif "海風" in wind_group:
            selected_wind_dirs = ["南", "南南東", "南東", "東南東", "東", "西南西", "南西", "南南西"]
        else:
            selected_wind_dirs = ["北", "北北西", "北西", "西北西", "西", "西南西", "南西", "南南西", 
                                  "南", "南南東", "南東", "東南東", "東", "東北東", "北東", "北北東"]

        min_wind, max_wind = st.slider(
            "適正な風速の範囲 (m/s)",
            min_value=0.0, max_value=15.0, value=(1.0, 8.0), step=0.5
        )

    with col2_wind:
        st.success(f"""
        🎯 **風向き・風速設定:**  
        * 対象風向: {', '.join(selected_wind_dirs[:4])}... 等  
        * 適正風速: **{min_wind}m/s ～ {max_wind}m/s**
        """)

    st.markdown("---")
    
    # === ④ 総合判定のボーダー ===
    st.markdown("### 🎯 総合発生判定のボーダーライン")
    threshold_prob = st.slider("発生予測とする総合確率の境界値 (%)", 40, 90, 65, 5, help="※この計算確率以上で『発生予測あり（1）』と判定します。")

# ------------------------------------------
# 計算ロジック（グラデーション確率モデル）
# ------------------------------------------
def calculate_prediction(data_df):
    if data_df is None or len(data_df) == 0:
        return data_df
    
    res = data_df.copy()
    
    # 1. 物理的大前提：海水温 > 気温（0℃以下は蜃気楼が原理的に不成立）
    is_mirage_possible = res['温度差'] > 0.0
    
    # 2. 温度差スコア（目標値に対する割合で0〜100点へ滑らかに変化）
    temp_ratio = res['温度差'] / threshold_temp if threshold_temp > 0 else 1.0
    score_temp = np.where(is_mirage_possible, np.clip(temp_ratio * 100.0, 0.0, 100.0), 0.0)
    
    # 3. 雲量スコア（目標以下は100点、超えた分だけ滑らかに減点）
    cloud_diff = np.maximum(0.0, res['雲量'] - threshold_clouds)
    score_cloud = np.maximum(0.0, 100.0 - cloud_diff * 2.0)
    
    # 4. 風条件スコア（風向・風速）
    wind_dir_ok = res['風向'].isin(selected_wind_dirs)
    wind_speed_ok = (res['風速'] >= min_wind) & (res['風速'] <= max_wind)
    
    score_wind = np.where(
        wind_dir_ok & wind_speed_ok, 100.0,
        np.where(wind_dir_ok | wind_speed_ok, 50.0, 10.0)
    )
    
    # 5. 総合確率（温度差 <= 0℃ の場合は一律 0%）
    raw_prob = (score_temp * 0.4) + (score_cloud * 0.4) + (score_wind * 0.2)
    res['発生確率'] = np.where(is_mirage_possible, raw_prob, 0.0)
    
    # 6. 発生予測判定
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
            st.error("❌ **気象的矛盾:** 海風（沖からの風）は水蒸気を含み、空気層を乱すため不向きです。「陸風メイン」に設定してみましょう！")
        elif predicted_days == 0:
            st.warning("⚠️ **条件が厳しすぎます:** 発生予測が0日になりました。確率ボーダー値や温度差スライダーを少し緩めてみましょう。")
        elif 10 <= avg_yearly_days <= 25:
            st.success(f"🎉 **【理想的な設定！】** 年間 {avg_yearly_days:.1f} 日の予測です。実際の室戸岬での観測数（年間約10〜20日）と美しく一致しています！")
        elif avg_yearly_days < 10:
            st.info(f"💡 年间 {avg_yearly_days:.1f} 日の予測です。条件が厳しめで、完璧な「本物のだるま夕日」に絞り込んだ設定です。")
        else:
            st.error(f"🔺 年間 {avg_yearly_days:.1f} 日の予測です。発生数が少し多めです。条件をもう少し厳しく見直してみましょう。")

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
            col_a.metric("温度差", f"{row['温度差']:.1f}℃")
            
            col_b.metric("風向・風速", f"{row['風向']} {row['風速']}m/s")
            col_b.metric("雲量", f"{row['雲量']}％")
            
            col_c.metric("計算された発生確率", f"{row['発生確率']:.1f}％")

            st.markdown("---")
            if row['発生予測'] == 1:
                st.success(f"🎉 **発生可能性【高】** （計算確率: {row['発生確率']:.1f}% / ボーダー: {threshold_prob}%）")
            else:
                st.error(f"❄️ **発生可能性【低】** （計算確率: {row['発生確率']:.1f}% / ボーダー: {threshold_prob}%）")
                
                # 不成立の分析
                reasons = []
                if row['温度差'] <= 0:
                    reasons.append(f"・【蜃気楼不成立】海水温より気温が高いため（温度差 {row['温度差']:.1f}℃）、屈折が起きません。")
                elif row['温度差'] < threshold_temp:
                    reasons.append(f"・【温度差不足】温度差（{row['温度差']:.1f}℃）が目標（{threshold_temp}℃）より低いため低得点です。")
                if row['雲量'] > threshold_clouds:
                    reasons.append(f"・【雲量超過】雲量（{row['雲量']}%）が多く、夕日が見えにくい状態です。")
                if not row['風向'].isin(selected_wind_dirs):
                    reasons.append(f"・【風向不適合】風向（{row['風向']}）が対象グループ外です。")
                
                if reasons:
                    st.info("**【理科的アドバイス】**\n" + "\n".join(reasons))
        else:
            st.warning("この日付のデータはありません。")

# ------------------------------------------
# タブ4：今日・明日の夕日予報（実践モード）
# ------------------------------------------
with tab4:
    st.subheader("🔮 天気予報データから「今日のだるま夕日」を予報しよう！")
    st.caption("天気予報（気象庁やウェザーニュース等）で調べた今日の予想数値を入力して、リアルタイム遭遇確率を計算してみよう。")

    st.markdown("---")
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("##### 📝 今日の天気予報数値を入力")
        input_temp = st.number_input("予想気温 (℃)", value=12.0, step=0.5)
        input_sea_temp = st.number_input("推定海水温 (℃)", value=18.0, step=0.5, help="※室戸沖の冬の海水温は17〜20℃前後")
        input_cloud = st.slider("予想雲量 (%)", 0, 100, 15)
        input_wind_dir = st.selectbox("予想風向", ["北", "北北西", "北西", "西北西", "西", "西南西", "南西", "南南西", "南", "南南東", "南東", "東南東", "東", "東北東", "北東", "北北東"], index=2)
        input_wind_speed = st.number_input("予想風速 (m/s)", value=3.5, step=0.5)

    # リアルタイムグラデーション計算
    input_diff = input_sea_temp - input_temp
    is_possible = input_diff > 0.0
    
    # スコア計算
    s_temp = np.clip((input_diff / threshold_temp) * 100.0, 0.0, 100.0) if is_possible else 0.0
    s_cloud = np.maximum(0.0, 100.0 - np.maximum(0.0, input_cloud - threshold_clouds) * 2.0)
    
    d_ok = input_wind_dir in selected_wind_dirs
    w_ok = min_wind <= input_wind_speed <= max_wind
    s_wind = 100.0 if (d_ok and w_ok) else (50.0 if (d_ok or w_ok) else 10.0)
    
    calc_prob = (s_temp * 0.4 + s_cloud * 0.4 + s_wind * 0.2) if is_possible else 0.0

    with c2:
        st.markdown("##### 📊 リアルタイム予報判定")
        
        st.metric("海水温と気温の差", f"{input_diff:.1f} ℃", delta="蜃気楼の発生条件あり" if is_possible else "温度差なし（不成立）", delta_color="normal" if is_possible else "inverse")
        st.metric("今日のだるま夕日 遭遇確率", f"{calc_prob:.1f} ％")
        
        if calc_prob >= threshold_prob:
            st.balloons()
            st.success("🌅 **【絶好のチャンス！】今日のだるま夕日指数: ★★★**\n素晴らしい気象条件です！室戸岬の海岸へ向かう価値が大いにあります。")
        elif calc_prob >= 40:
            st.warning("⛅ **【ワンチャンスあり】今日のだるま夕日指数: ★★☆**\n条件の一部が少し惜しいですが、西の空の雲が抜ければ見られる可能性があります！")
        else:
            st.error("🌧️ **【難しい】今日のだるま夕日指数: ★☆☆**\n気象条件が整っておらず、だるま型になる可能性は非常に低いです。")
