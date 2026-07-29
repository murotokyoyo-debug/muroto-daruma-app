import streamlit as st
import pandas as pd
import numpy as np
import datetime
import calendar

# ------------------------------------------
# 📱 画面基本設定
# ------------------------------------------
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
        🌅 室戸だるま夕日シュミレーター
    </h1>
""", unsafe_allow_html=True)

st.caption("気象条件を組み合わせて、だるま夕日が見える日を予測してみよう！")

# データの読み込み
try:
    df = pd.read_csv('muroto_history.csv')
    df['日付'] = pd.to_datetime(df['日付'], format='mixed', errors='coerce').dt.strftime('%Y-%m-%d')
    df['月'] = pd.to_datetime(df['日付']).dt.month
except Exception as e:
    st.error(f"データファイルが見つかりません: {e}")
    st.stop()

# ==========================================
# 📱 タブ構成
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "⚙️ ① 条件を設定する", 
    "📈 ② 予測結果を見る", 
    "🔎 ③ 日付で調べる",
    "🔮 ④ 今日の夕日予報（実践モード）"
])

# ------------------------------------------
# タブ1：条件設定
# ------------------------------------------
with tab1:
    st.subheader("🛠️ だるま夕日の「発生ルール」を作ろう")
    st.info("💡 3つの項目の「配点（重要度）」を足して、**ぴったり100点**になるように調整してね！")

    st.markdown("---")
    
    # ==========================================
    # --- ① 温度差 ---
    # ==========================================
    st.markdown("### 🌡️ 条件1：海と空気の温度差（下位蜃気楼の条件）")
    st.caption("※温かい海の上に冷たい空気が来ると、光が屈折して「だるま型」に見えます。")
    
    col1_temp, col2_temp = st.columns([7, 3])
    
    with col1_temp:
        with st.container(border=True):
            st.markdown("##### 🎯 合格基準（条件設定）")
            st.markdown("""
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: bold; margin-bottom: 4px;">
                    <span style="color: #60a5fa;">🔵 差が小さい (発生しにくい)</span>
                    <span style="color: #f87171;">🔴 差が大きい (発生しやすい) ➔</span>
                </div>
                <div style="height: 8px; background: linear-gradient(to right, #2563eb, #3b82f6, #f97316, #dc2626); border-radius: 4px; margin-bottom: 12px;"></div>
            """, unsafe_allow_html=True)
            threshold_temp = st.slider("海水温が気温より何℃以上高いと合格？", 0.0, 15.0, 0.0, 0.5)

    with col2_temp:
        with st.container(border=True):
            st.markdown("##### ⚖️ 重要度（配点）")
            weight_temp = st.select_slider("この条件の配点", options=list(range(0, 105, 5)), value=0, key="w_temp_v13")
            st.markdown(f"<div style='text-align: center; font-size: 1.4rem; font-weight: bold; color: #f59e0b; margin-top: 4px;'>{weight_temp} 点 / 100点</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ==========================================
    # --- ② 雲量 ---
    # ==========================================
    st.markdown("### ☁️ 条件2：空の晴れぐあい（雲の量）")
    st.caption("※夕日が見えるためには、空に雲が少ないことが大切です。")
    
    col1_clouds, col2_clouds = st.columns([7, 3])
    
    with col1_clouds:
        with st.container(border=True):
            st.markdown("##### 🎯 合格基準（条件設定）")
            st.markdown("""
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: bold; margin-bottom: 4px;">
                    <span style="color: #ff7849;">🌅 0% 快晴 (絶好の夕日)</span>
                    <span style="color: #94a3b8;">☁️ 100% 曇り (見えない) ➔</span>
                </div>
                <div style="height: 8px; background: linear-gradient(to right, #ff5722, #ff9800, #9e9e9e, #546e7a); border-radius: 4px; margin-bottom: 12px;"></div>
            """, unsafe_allow_html=True)
            threshold_clouds = st.slider("雲の量は何％以下なら合格？", 0, 100, 100, 10)

    with col2_clouds:
        with st.container(border=True):
            st.markdown("##### ⚖️ 重要度（配点）")
            weight_clouds = st.select_slider("この条件の配点", options=list(range(0, 105, 5)), value=0, key="w_clouds_v13")
            st.markdown(f"<div style='text-align: center; font-size: 1.4rem; font-weight: bold; color: #f59e0b; margin-top: 4px;'>{weight_clouds} 点 / 100点</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ==========================================
    # --- ③ 風の条件（グループ別チェックボックス） ---
    # ==========================================
    st.markdown("### 🌬️ 条件3：風の強さと向き")
    st.caption("※室戸では、風の向きや強さによって水平線付近の空気の状態が変わります。")
    
    col1_wind, col2_wind = st.columns([7, 3])
    
    with col1_wind:
        with st.container(border=True):
            st.markdown("##### 🎯 合格基準（条件設定）")
            st.markdown("""
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: bold; margin-bottom: 4px;">
                    <span style="color: #facc15;">🍃 0m/s 無風</span>
                    <span style="color: #4ade80;">🍃 5m/s 適風</span>
                    <span style="color: #22c55e;">💨 20m/s 強風 ➔</span>
                </div>
                <div style="height: 8px; background: linear-gradient(to right, #facc15 0%, #a3e635 25%, #16a34a 100%); border-radius: 4px; margin-bottom: 12px;"></div>
            """, unsafe_allow_html=True)
            
            min_wind, max_wind = st.slider(
                "適正な風の強さの範囲 (m/s)",
                min_value=0.0,
                max_value=20.0,
                value=(0.0, 20.0),
                step=0.5,
                help="※風が弱すぎても温床が作られず、強すぎても波で水平線が崩れてしまいます。"
            )

            st.markdown("---")
            st.markdown("**🧭 合格（満点）とする風向きを選択**")
            st.caption("※だるま夕日が発生しずらくなる風向きを選ぶと大きく減点されます。")

            cb_land = st.checkbox("🍃 陸からの風 (北・北北西・北西・西北西)")
            cb_west = st.checkbox("🌊 西寄りの風 (西・西南西)")
            cb_sea  = st.checkbox("☁️ 沖・海からの風 (南西・南南西・南・南南東・南東)")
            cb_east = st.checkbox("💨 東寄りの風 (東南東・東・東北東・北東・北北東)")

            selected_wind_dirs = []
            if cb_land: selected_wind_dirs.extend(["北", "北北西", "北西", "西北西"])
            if cb_west: selected_wind_dirs.extend(["西", "西南西"])
            if cb_sea:  selected_wind_dirs.extend(["南西", "南南西", "南", "南南東", "南東"])
            if cb_east: selected_wind_dirs.extend(["東南東", "東", "東北東", "北東", "北北東"])

    with col2_wind:
        with st.container(border=True):
            st.markdown("##### ⚖️ 重要度（配点）")
            weight_wind = st.select_slider("この条件の配点", options=list(range(0, 105, 5)), value=0, key="w_wind_v13")
            st.markdown(f"<div style='text-align: center; font-size: 1.4rem; font-weight: bold; color: #f59e0b; margin-top: 4px;'>{weight_wind} 点 / 100点</div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("##### 💡 風向きを考えるヒント")
            st.markdown("""
            * **陸からの風（山越えの風）**  
              四国山地を越えて届くため、冷たく乾いた空気の層を海の上に作りやすくなります。
            * **沖・海からの風**  
              太平洋から湿った風が吹き込むため、水蒸気で雲や霧が発生しやすくなります。
            """)

    # 配点チェック
    total_weight = weight_temp + weight_clouds + weight_wind
    st.markdown("---")
    if total_weight == 100:
        st.success(f"🎉 現在の合計配点： **{total_weight}点**（OK！「② 予測結果を見る」タブを開いてね）")
    else:
        st.warning(f"⚠️ 現在の合計配点： **{total_weight}点**（あと {100 - total_weight} 点 調整が必要です）")

# ==========================================
# 📊 気象物理モデルに基づく計算ロジック
# ==========================================
df['温度差'] = df['海水温'] - df['気温']

# ① 温度差判定
temp_margin = 1.0
df['score_temp'] = np.where(
    df['温度差'] >= threshold_temp,
    float(weight_temp),
    np.maximum(0.0, weight_temp * (1.0 - (threshold_temp - df['温度差']) / temp_margin))
)

# ② 雲量判定
cloud_margin = 5.0
df['score_clouds'] = np.where(
    df['雲量'] <= threshold_clouds,
    float(weight_clouds),
    np.maximum(0.0, weight_clouds * (1.0 - (df['雲量'] - threshold_clouds) / cloud_margin))
)

# ③ 風条件判定（補正モデル）
wind_speed_score = np.where(
    (df['風速'] >= min_wind) & (df['風速'] <= max_wind),
    1.0,
    np.where(
        df['風速'] < min_wind,
        np.maximum(0.0, 1.0 - (min_wind - df['風速']) / 0.5),
        np.maximum(0.0, 1.0 - (df['風速'] - max_wind) / 1.5)
    )
)

df['wind_dir_match'] = df['風向'].isin(selected_wind_dirs)
df['wind_dir_factor'] = np.where(df['wind_dir_match'], 1.0, 0.3)
df['score_wind'] = wind_speed_score * df['wind_dir_factor'] * weight_wind

# 総合スコアと判定
df['予測スコア'] = df['score_temp'] + df['score_clouds'] + df['score_wind']
threshold_score = 92.0

if total_weight == 100 and len(selected_wind_dirs) > 0:
    df['発生予測'] = np.where(df['予測スコア'] >= threshold_score, 1, 0)
else:
    df['発生予測'] = 0

total_days = len(df)
predicted_days = int(df['発生予測'].sum())
avg_yearly_days = predicted_days / 4.0

# ------------------------------------------
# タブ2：予測結果
# ------------------------------------------
with tab2:
    st.subheader("📈 シミュレーション結果")
    
    m1, m2 = st.columns(2)
    m1.metric("4シーズン合計発生日数", f"{predicted_days} 日", help="データ対象期間：2021年10月1日〜2025年3月31日（10月〜3月×4年分）")
    m2.metric("年間平均", f"{avg_yearly_days:.1f} 日 / 年")

    st.markdown("#### 🤖 AIアドバイザーの判定")
    
    # 状態判定用フラグ
    has_zero_weight = (weight_temp == 0 or weight_clouds == 0 or weight_wind == 0)
    is_initial_condition = (threshold_temp == 0.0 or threshold_clouds == 100 or min_wind == 0.0 or max_wind == 20.0)

    is_only_land = cb_land and not (cb_west or cb_sea or cb_east)
    is_sea_or_west = (cb_west or cb_sea) and not cb_land
    is_east_only = cb_east and not (cb_land or cb_west or cb_sea)
    is_all_wind = cb_land and cb_west and cb_sea and cb_east

    # --- 判定ロジック ---
    if total_weight != 100:
        st.info("💡 まずは「① 条件を設定する」タブで、合計配点をぴったり100点にしてみよう！")
    elif len(selected_wind_dirs) == 0:
        st.warning("🧭 条件3の「風向き」のチェックが1つも入っていません。1つ以上選んでみよう！")
    elif has_zero_weight:
        st.warning("📋 配点が0点の項目があります。だるま夕日は温度・雲・風のバランスが大切です！")
    elif is_initial_condition:
        st.warning("🔍 条件の基準（スライダー）が初期設定のままのようです。少し絞り込んでみましょう！")

    # 🧭 風向きの気象学的検証アドバイス
    elif is_all_wind:
        st.info("💡 すべての風向きが選ばれています。室戸岬でだるま夕日が見えやすい『決まった風向き』が無いか考えて絞り込んでみよう！")

    elif is_sea_or_west:
        st.warning(f"🤔 年間平均 {avg_yearly_days:.1f} 日の計算結果になりましたが、太平洋（海）からの風は湿気を含んで西の水平線に雲が出やすくなります。『陸からの風』と発生日数を比べてみよう！")

    elif is_east_only:
        st.warning(f"🤔 年間平均 {avg_yearly_days:.1f} 日の計算結果ですが、東寄りの風は低気圧が近づいて天気が下り坂（雨や曇り）になる時によく吹く風です。『陸からの風』と比べてみよう！")

    # 📊 指定文言に基づくフィードバック判定
    elif predicted_days == 0:
        st.warning("⚠️ 発生予測が0日になりました。条件（特に温度差や風速の範囲）が少し厳しすぎるかもしれません。")

    elif avg_yearly_days > 18.0:
        st.error(f"🔺 **【多いかも？】** 年間平均 {avg_yearly_days:.1f} 日の予測です。発生予測日数が少し多めです。もう少し条件を絞り込んでみよう！")

    elif 15.0 <= avg_yearly_days <= 18.0:
        if is_only_land:
            st.success(f"🟢 **【ちょうどいい感じ！】** 年間平均 {avg_yearly_days:.1f} 日の予測です。より実感に近い発生予測日数！（山を越える『陸からの風』に着目した素晴らしい設定です）")
        else:
            st.success(f"🟢 **【ちょうどいい感じ！】** 年間平均 {avg_yearly_days:.1f} 日の予測です。より実感に近い発生予測日数！")

    elif 10.0 <= avg_yearly_days < 15.0:
        st.success(f"🟢 **【いい感じ！】** 年間平均 {avg_yearly_days:.1f} 日の予測です。実感に近い発生予測日数です！")

    else: # avg_yearly_days < 10.0
        st.warning(f"💡 **【かなり厳しい？】** 年間平均 {avg_yearly_days:.1f} 日の予測です。発生予測日数が年に数回の限定的な設定です。")

    st.markdown("---")
    st.markdown("#### 📅 月別の発生予想（4シーズンの合計）")
    
    season_months = [10, 11, 12, 1, 2, 3]
    monthly_data = df.groupby('月')['発生予測'].sum().reindex(season_months, fill_value=0).reset_index()
    monthly_data['月表示'] = monthly_data['月'].astype(str) + '月'
    monthly_summary = monthly_data.set_index('月表示')
    
    st.bar_chart(monthly_summary['発生予測'])

# ------------------------------------------
# タブ3：日付ピンポイント検索
# ------------------------------------------
with tab3:
    st.subheader("🔎 特定の日のデータを確かめる")
    st.caption("※だるま夕日の観測シーズン（10月〜3月）の日付を選択できます。")

    col_y, col_m, col_d = st.columns(3)
    
    with col_y:
        selected_year = st.selectbox("年を選択", [2021, 2022, 2023, 2024, 2025, 2026], index=0)
        
    with col_m:
        selected_month = st.selectbox(
            "月を選択（シーズン限定）", 
            [10, 11, 12, 1, 2, 3], 
            index=0, 
            format_func=lambda x: f"{x}月"
        )

    _, max_days = calendar.monthrange(selected_year, selected_month)

    with col_d:
        selected_day = st.selectbox(
            "日を選択", 
            list(range(1, max_days + 1)), 
            index=19 if max_days >= 20 else 0,
            format_func=lambda x: f"{x}日"
        )

    selected_date = datetime.date(selected_year, selected_month, selected_day)
    date_str = selected_date.strftime('%Y-%m-%d')
    target_data = df[df['日付'] == date_str]

    st.markdown("---")

    if len(target_data) > 0:
        row = target_data.iloc[0]
        st.write(f"**【{date_str} の室戸岬の観測データ】**")
        
        col_a, col_b = st.columns(2)
        col_a.metric("気温 / 海水温", f"{row['気温']}℃ / {row['海水温']}℃")
        col_a.metric("温度差", f"{row['温度差']:.1f}℃")
        col_b.metric("風", f"{row['風向']} {row['風速']}m/s")
        col_b.metric("雲量", f"{row['雲量']}％")

        st.markdown("---")
        
        # 配点・判定エリア
        if total_weight != 100:
            st.warning("合計配点を100点に設定すると、この日のスコア判定が表示されます。")
        elif len(selected_wind_dirs) == 0:
            st.warning("風向きのチェックを入れてください。")
        
        # 🌅【★★★】絶好のチャンス！（92点以上）
        elif row['予測スコア'] >= threshold_score:
            st.success(f"🌅 **【絶好のチャンス！】だるま夕日指数: ★★★** （判定スコア: {row['予測スコア']:.1f}点 / 合格点: {threshold_score}点）\n\n設定した合格ルールをクリアしている絶好の日です！")
            if not row['wind_dir_match']:
                st.info(f"💡 **ワンポイント**: 風向「{row['風向']}」は設定外のため風の配点が減点されていますが、温度差や晴れぐあいが非常に優れているため合格判定となりました！")
        
        # ⛅【★★☆】ワンチャンスあり（80点以上 92点未満）
        elif row['予測スコア'] >= 80.0:
            st.warning(f"⛅ **【ワンチャンスあり】だるま夕日指数: ★★☆** （判定スコア: {row['予測スコア']:.1f}点 / 合格点: {threshold_score}点）\n\n**とても運が良ければだるま夕日が見られるかも！？** 合格ボーダーまであと一歩の条件です。")
            if not row['wind_dir_match']:
                st.info(f"💡 **惜しい理由**: この日の風向「**{row['風向']}**」は設定した風向きグループに含まれていないため、風のスコアが大きく減点されています。")
            elif row['雲量'] > threshold_clouds:
                st.info(f"💡 **惜しい理由**: 雲量が{row['雲量']}％と少し高めです。日没直前に西の水平線ぎりぎりさえ晴れていれば、見られた可能性があります！")
        
        # 🌧️【★☆☆】難しい（80点未満）
        else:
            st.error(f"🌧️ **【難しい】だるま夕日指数: ★☆☆** （判定スコア: {row['予測スコア']:.1f}点 / 合格点: {threshold_score}点）\n\n設定した合格条件に届いておらず、この日にだるま夕日が見られる可能性は低いです。")
            if not row['wind_dir_match']:
                st.info(f"💡 **ポイント**: この日の風向「**{row['風向']}**」は設定した風向きグループに含まれていないため、風のスコアが大きく減点されています。")
            elif row['score_temp'] >= weight_temp * 0.8 and row['雲量'] > threshold_clouds:
                st.info(f"💡 **現地観測のポイント**: 温度差（{row['温度差']:.1f}℃）や風条件は良好です！雲量は{row['雲量']}％ですが、西の水平線が開けていれば見られた可能性はあります。")
    else:
        st.warning(f"⚠️ **{date_str}** の観測データはファイルに登録されていません。")

# ------------------------------------------
# タブ4：今日の夕日予報（実践モード）
# ------------------------------------------
with tab4:
    st.subheader("🔮 天気予報の数値を入れて「今日の発生確率」を計算しよう！")
    st.caption("「① 条件を設定する」タブで設定したあなたの発生ルールを使って、今日や明日の天気予報から遭遇確率を計算します。")

    st.markdown("---")

    if total_weight != 100:
        st.warning("⚠️ まずは「① 条件を設定する」タブで、合計配点をぴったり100点に設定してください！")
    elif len(selected_wind_dirs) == 0:
        st.warning("⚠️ 「① 条件を設定する」タブで、風向きにチェックを1つ以上入れてください！")
    else:
        c1, c2 = st.columns([5, 5])
        
        with c1:
            with st.container(border=True):
                st.markdown("##### 📝 今日の天気予報数値を入力")
                input_temp = st.number_input("予想気温 (℃)", value=12.0, step=0.5)
                input_sea_temp = st.number_input("推定海水温 (℃)", value=18.0, step=0.5, help="※室戸沖の冬の海水温は17〜20℃前後")
                input_cloud = st.slider("予想雲量 (%)", 0, 100, 15)
                input_wind_dir = st.selectbox(
                    "予想風向", 
                    ["北", "北北西", "北西", "西北西", "西", "西南西", "南西", "南南西", "南", "南南東", "南東", "東南東", "東", "東北東", "北東", "北北東"], 
                    index=2
                )
                input_wind_speed = st.number_input("予想風速 (m/s)", value=3.5, step=0.5)

        # リアルタイムスコア計算
        input_diff = input_sea_temp - input_temp
        
        # ① 温度差スコア
        if input_diff >= threshold_temp:
            s_temp = float(weight_temp)
        else:
            s_temp = max(0.0, float(weight_temp) * (1.0 - (threshold_temp - input_diff) / temp_margin))

        # ② 雲量スコア
        if input_cloud <= threshold_clouds:
            s_cloud = float(weight_clouds)
        else:
            s_cloud = max(0.0, float(weight_clouds) * (1.0 - (input_cloud - threshold_clouds) / cloud_margin))

        # ③ 風スコア（減点補正適用）
        if min_wind <= input_wind_speed <= max_wind:
            w_speed_score = 1.0
        elif input_wind_speed < min_wind:
            w_speed_score = max(0.0, 1.0 - (min_wind - input_wind_speed) / 0.5)
        else:
            w_speed_score = max(0.0, 1.0 - (input_wind_speed - max_wind) / 1.5)

        is_input_wind_match = input_wind_dir in selected_wind_dirs
        w_dir_factor = 1.0 if is_input_wind_match else 0.3
        s_wind = w_speed_score * w_dir_factor * float(weight_wind)

        input_score = s_temp + s_cloud + s_wind

        with c2:
            with st.container(border=True):
                st.markdown("##### 📊 リアルタイムスコア判定")
                
                st.metric("海水温と気温の差", f"{input_diff:.1f} ℃")
                st.metric("本日の判定スコア", f"{input_score:.1f} 点 / 100点", f"合格ボーダー: {threshold_score}点")

                st.markdown("---")
                
                if input_score >= threshold_score:
                    st.success("🌅 **【絶好のチャンス！】今日のだるま夕日指数: ★★★**\n設定した合格ルールをクリアしています！室戸岬へ見に行く価値が大いにあります！")
                elif input_score >= threshold_score * 0.8:
                    st.warning("⛅ **【ワンチャンスあり】今日のだるま夕日指数: ★★☆**\nとても運が良ければ見られるかも！？合格ボーダーまであと一歩の条件です。")
                else:
                    st.error("🌧️ **【難しい】今日のだるま夕日指数: ★☆☆**\n設定した合格条件に届いておらず、本日だるま夕日が見られる可能性は低いです。")

                if not is_input_wind_match:
                    st.caption("※予想風向が選択された合格グループ外のため、風スコアが大きく減点されています。")

                with st.expander("🔍 スコアの内訳を見る"):
                    st.write(f"- 温度差スコア: **{s_temp:.1f}** / {weight_temp}点")
                    st.write(f"- 雲量スコア: **{s_cloud:.1f}** / {weight_clouds}点")
                    st.write(f"- 風条件スコア: **{s_wind:.1f}** / {weight_wind}点 (風向適合: {'適合' if is_input_wind_match else '大きく減点'})")
