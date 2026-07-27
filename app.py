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
tab1, tab2, tab3 = st.tabs(["⚙️ ① 条件を設定する", "📈 ② 予測結果を見る", "🔎 ③ 日付で調べる"])

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
    
    # 左：合格基準カード
    with col1_temp:
        with st.container(border=True):
            st.markdown("##### 🎯 合格基準（合格ライン）")
            st.markdown("""
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: bold; margin-bottom: 4px;">
                    <span style="color: #60a5fa;">🔵 差が小さい (発生しにくい)</span>
                    <span style="color: #f87171;">🔴 差が大きい (発生しやすい) ➔</span>
                </div>
                <div style="height: 8px; background: linear-gradient(to right, #2563eb, #3b82f6, #f97316, #dc2626); border-radius: 4px; margin-bottom: 12px;"></div>
            """, unsafe_allow_html=True)
            # 初期値を 5.0 ℃に設定
            threshold_temp = st.slider("海水温が気温より何℃以上高いと合格？", 5.0, 15.0, 5.0, 0.5)

    # 右：配点カード（初期値 0点）
    with col2_temp:
        with st.container(border=True):
            st.markdown("##### ⚖️ 重要度（配点）")
            weight_temp = st.select_slider("この条件の配点", options=list(range(0, 105, 5)), value=0, key="w_temp")
            st.markdown(f"<div style='text-align: center; font-size: 1.4rem; font-weight: bold; color: #f59e0b; margin-top: 4px;'>{weight_temp} 点 / 100点</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ==========================================
    # --- ② 雲量 ---
    # ==========================================
    st.markdown("### ☁️ 条件2：空の晴れぐあい（雲の量）")
    st.caption("※夕日が見えるためには、空に雲が少ないことが大切です。")
    
    col1_clouds, col2_clouds = st.columns([7, 3])
    
    # 左：合格基準カード
    with col1_clouds:
        with st.container(border=True):
            st.markdown("##### 🎯 合格基準（合格ライン）")
            st.markdown("""
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: bold; margin-bottom: 4px;">
                    <span style="color: #ff7849;">🌅 0% 快晴 (絶好の夕日)</span>
                    <span style="color: #94a3b8;">☁️ 100% 曇り (見えない) ➔</span>
                </div>
                <div style="height: 8px; background: linear-gradient(to right, #ff5722, #ff9800, #9e9e9e, #546e7a); border-radius: 4px; margin-bottom: 12px;"></div>
            """, unsafe_allow_html=True)
            # 初期値を 100% に設定
            threshold_clouds = st.slider("雲の量は何％以下なら合格？", 0, 100, 100, 10)

    # 右：配点カード（初期値 0点）
    with col2_clouds:
        with st.container(border=True):
            st.markdown("##### ⚖️ 重要度（配点）")
            weight_clouds = st.select_slider("この条件の配点", options=list(range(0, 105, 5)), value=0, key="w_clouds")
            st.markdown(f"<div style='text-align: center; font-size: 1.4rem; font-weight: bold; color: #f59e0b; margin-top: 4px;'>{weight_clouds} 点 / 100点</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ==========================================
    # --- ③ 風の条件 ---
    # ==========================================
    st.markdown("### 🌬️ 条件3：風の強さと向き")
    st.caption("※室戸では、風の向きや強さによって水平線付近の空気の状態が変わります。")
    
    col1_wind, col2_wind = st.columns([7, 3])
    
    # 左：合格基準カード
    with col1_wind:
        with st.container(border=True):
            st.markdown("##### 🎯 合格基準（合格ライン）")
            st.markdown("""
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: bold; margin-bottom: 4px;">
                    <span style="color: #facc15;">🍃 0m/s 無風</span>
                    <span style="color: #4ade80;">🍃 5m/s 適風</span>
                    <span style="color: #22c55e;">💨 20m/s 強風 ➔</span>
                </div>
                <div style="height: 8px; background: linear-gradient(to right, #facc15 0%, #a3e635 25%, #16a34a 100%); border-radius: 4px; margin-bottom: 12px;"></div>
            """, unsafe_allow_html=True)
            
            # 初期値を 0.0〜20.0 m/s に設定
            min_wind, max_wind = st.slider(
                "適正な風の強さの範囲 (m/s)",
                min_value=0.0,
                max_value=20.0,
                value=(0.0, 20.0),
                step=0.5,
                help="※風が弱すぎても温床が作られず、強すぎても波で水平線が崩れてしまいます。"
            )

            st.markdown("---")
            st.markdown("**🧭 合格とする風向きを選択（チェックを入れてね）**")

            # 初期値は全てチェックなし
            default_wind_dirs = []
            selected_wind_dirs = []

            wc1, wc2, wc3, wc4 = st.columns(4)

            with wc1:
                if st.checkbox("北", value=("北" in default_wind_dirs)): selected_wind_dirs.append("北")
                if st.checkbox("北北西", value=("北北西" in default_wind_dirs)): selected_wind_dirs.append("北北西")
                if st.checkbox("北西", value=("北西" in default_wind_dirs)): selected_wind_dirs.append("北西")
                if st.checkbox("西北西", value=("西北西" in default_wind_dirs)): selected_wind_dirs.append("西北西")

            with wc2:
                if st.checkbox("西", value=("西" in default_wind_dirs)): selected_wind_dirs.append("西")
                if st.checkbox("西南西", value=("西南西" in default_wind_dirs)): selected_wind_dirs.append("西南西")
                if st.checkbox("南西", value=("南西" in default_wind_dirs)): selected_wind_dirs.append("南西")
                if st.checkbox("南南西", value=("南南西" in default_wind_dirs)): selected_wind_dirs.append("南南西")

            with wc3:
                if st.checkbox("南", value=("南" in default_wind_dirs)): selected_wind_dirs.append("南")
                if st.checkbox("南南東", value=("南南東" in default_wind_dirs)): selected_wind_dirs.append("南南東")
                if st.checkbox("南東", value=("南東" in default_wind_dirs)): selected_wind_dirs.append("南東")
                if st.checkbox("東南東", value=("東南東" in default_wind_dirs)): selected_wind_dirs.append("東南東")

            with wc4:
                if st.checkbox("東", value=("東" in default_wind_dirs)): selected_wind_dirs.append("東")
                if st.checkbox("東北東", value=("東北東" in default_wind_dirs)): selected_wind_dirs.append("東北東")
                if st.checkbox("北東", value=("北東" in default_wind_dirs)): selected_wind_dirs.append("北東")
                if st.checkbox("北北東", value=("北北東" in default_wind_dirs)): selected_wind_dirs.append("北北東")

    # 右：配点カード（初期値 0点） ＋ ヒントコラム
    with col2_wind:
        with st.container(border=True):
            st.markdown("##### ⚖️ 重要度（配点）")
            weight_wind = st.select_slider("この条件の配点", options=list(range(0, 105, 5)), value=0, key="w_wind")
            st.markdown(f"<div style='text-align: center; font-size: 1.4rem; font-weight: bold; color: #f59e0b; margin-top: 4px;'>{weight_wind} 点 / 100点</div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("##### 💡 風向きを考えるヒント")
            st.markdown("""
            * **陸側から吹く風（山越えの風）**  
              四国山地を越えて届くため、冷たく乾いた空気の層を海の上に作りやすくなります。
            * **海側から吹く風（沖からの風）**  
              太平洋から湿った暖かい風が吹き込むため、水蒸気で雲や霧が発生しやすくなります。
            """)

    # 配点チェック
    total_weight = weight_temp + weight_clouds + weight_wind
    st.markdown("---")
    if total_weight == 100:
        st.success(f"🎉 現在の合計配点： **{total_weight}点**（OK！「② 予測結果を見る」タブを開いてね）")
    else:
        st.warning(f"⚠️ 現在の合計配点： **{total_weight}点**（あと {100 - total_weight} 点 調整が必要です）")

# ==========================================
# 📊 気象物理モデルに基づくリアル計算ロジック
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

# ③ 風条件判定（風速 ✕ チェックされた風向）
wind_speed_score = np.where(
    (df['風速'] >= min_wind) & (df['風速'] <= max_wind),
    1.0,
    np.where(
        df['風速'] < min_wind,
        np.maximum(0.0, 1.0 - (min_wind - df['風速']) / 0.5),
        np.maximum(0.0, 1.0 - (df['風速'] - max_wind) / 1.5)
    )
)

# チェックされた風向に含まれていれば 1.0、無効なら 0.0
df['wind_dir_factor'] = np.where(df['風向'].isin(selected_wind_dirs), 1.0, 0.0)
df['score_wind'] = wind_speed_score * df['wind_dir_factor'] * weight_wind

# 合計スコア計算
df['予測スコア'] = df['score_temp'] + df['score_clouds'] + df['score_wind']

# 合格判定ライン（92.0点）
threshold_score = 92.0

if total_weight == 100:
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
    
    # 指標カード表示
    m1, m2 = st.columns(2)
    m1.metric("4シーズン合計発生日数", f"{predicted_days} 日", help="データ対象期間：2021年10月1日〜2025年3月31日（10月〜3月×4年分）")
    m2.metric("年間平均", f"{avg_yearly_days:.1f} 日 / 年")

    st.markdown("#### 🤖 AIアドバイザーの判定")
    has_zero_weight = (weight_temp == 0 or weight_clouds == 0 or weight_wind == 0)
    is_initial_condition = (threshold_temp == 5.0 or threshold_clouds == 100 or min_wind == 0.0 or max_wind == 20.0)

    if total_weight != 100:
        st.info("💡 まずは「① 条件を設定する」タブで、合計配点をぴったり100点にしてみよう！")
    elif len(selected_wind_dirs) == 0:
        st.warning("🧭 条件3の「風向き」のチェックが1つも入っていません。風向きを1つ以上選んでみよう！")
    elif has_zero_weight:
        st.warning("📋 配点が0点の項目があります。だるま夕日は温度・雲・風のバランスが大切です！")
    elif is_initial_condition:
        st.warning("🔍 条件の基準（スライダー）が初期設定のままのようです。少し絞り込んでみましょう！")
    elif predicted_days == 0:
        st.warning("⚠️ 発生予測が0日になりました。条件が少し厳しすぎるかもしれません。")
    elif 20 <= predicted_days <= 80:
        st.success(f"🟢 【素晴らしい！】年間 {avg_yearly_days:.1f} 日の予測です。実際の室戸岬の年間発生数（10〜20回前後）に極めて近いリアルな条件設定です！")
    elif predicted_days < 20:
        st.warning(f"💡 年間 {avg_yearly_days:.1f} 日の予測です。かなり厳しい条件ですが、完璧な「本物のだるま夕日」に絞った条件と言えます。")
    else:
        st.error(f"🔺 年間 {avg_yearly_days:.1f} 日の予測です。発生数が多すぎます！もう少し「温度差」や「風向き」「雲量」の合格ラインを厳しく設定してみましょう。")

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
    selected_date = st.date_input("日付を選択", value=datetime.date(2021, 10, 20))
    date_str = selected_date.strftime('%Y-%m-%d')
    target_data = df[df['日付'] == date_str]

    if len(target_data) > 0:
        row = target_data.iloc[0]
        st.write(f"**【{date_str} の室戸岬の観測データ】**")
        
        col_a, col_b = st.columns(2)
        col_a.metric("気温 / 海水温", f"{row['気温']}℃ / {row['海水温']}℃")
        col_a.metric("温度差", f"{row['温度差']:.1f}℃")
        col_b.metric("風", f"{row['風向']} {row['風速']}m/s")
        col_b.metric("雲量", f"{row['雲量']}％")

        st.markdown("---")
        if total_weight != 100:
            st.warning("合計配点を100点に設定すると、この日のスコア判定が表示されます。")
        elif row['発生予測'] == 1:
            st.success(f"🎉 **発生可能性【大】** （判定スコア: {row['予測スコア']:.1f}点 / 合格点: {threshold_score}点）")
        else:
            st.error(f"❄️ **発生可能性【低】** （判定スコア: {row['予測スコア']:.1f}点 / 合格点: {threshold_score}点）")
    else:
        st.warning("この日付のデータはありません。")
