import streamlit as st
import pandas as pd
import numpy as np
import datetime

# 画面設定
st.set_page_config(page_title="だるま夕日シミュレーター", page_icon="🌅", layout="wide")

st.title("🌅 室戸岬 だるま夕日シミュレーター")
st.caption("気象条件を組み合わせて、だるま夕日が見える日を予測してみよう！")

# データの読み込み
try:
    df = pd.read_csv('muroto_history.csv')
    df['日付'] = pd.to_datetime(df['日付']).dt.strftime('%Y-%m-%d')
    df['月'] = pd.to_datetime(df['日付']).dt.month
except Exception as e:
    st.error(f"データファイルが見つかりません: {e}")
    st.stop()

# ==========================================
# 📱 タブを使ってスマホでも見やすく切り替え
# ==========================================
tab1, tab2, tab3 = st.tabs(["⚙️ ① 条件を設定する", "📈 ② 予測結果を見る", "🔎 ③ 日付で調べる"])

# ------------------------------------------
# タブ1：条件設定
# ------------------------------------------
with tab1:
    st.subheader("🛠️ だるま夕日の「発生ルール」を作ろう")
    st.info("💡 3つの項目の「配点（重要度）」を足して、**ぴったり100点**になるように調整してね！")

    st.markdown("---")
    
    # --- ① 温度差 ---
    st.markdown("#### 🌡️ 条件1：海と空気の温度差（下位蜃気楼の条件）")
    st.caption("※温かい海の上に冷たい空気が来ると、光が屈折して「だるま型」に見えます。")
    threshold_temp = st.slider("海水温が気温より何℃以上高いと合格？", 5.0, 15.0, 5.0, 0.5)
    weight_temp = st.select_slider("この条件の重要度（配点）", options=list(range(0, 105, 5)), value=0, key="w_temp")

    st.markdown("---")

    # --- ② 雲量 ---
    st.markdown("#### ☁️ 条件2：空の晴れぐあい（雲の量）")
    st.caption("※夕日が見えるためには、空に雲が少ないことが大切です。")
    threshold_clouds = st.slider("雲の量は何％以下なら合格？", 0, 100, 100, 10)
    weight_clouds = st.select_slider("この条件の重要度（配点）", options=list(range(0, 105, 5)), value=0, key="w_clouds")

    st.markdown("---")

    # --- ③ 風の条件 ---
    st.markdown("#### 🌬️ 条件3：風の強さと向き")
    st.caption("※室戸では、北や北西からの冷たい季節風が吹くと発生しやすくなります。")
    min_wind = st.slider("最低限必要な風の強さ (m/s)", 0.0, 5.0, 0.0, 0.5)
    max_wind = st.slider("これ以上強いと波が立ちすぎる風速 (m/s)", 5.0, 20.0, 20.0, 0.5)
    weight_wind = st.select_slider("この条件の重要度（配点）", options=list(range(0, 105, 5)), value=0, key="w_wind")

    # 配点チェック
    total_weight = weight_temp + weight_clouds + weight_wind
    st.markdown("---")
    if total_weight == 100:
        st.success(f"🎉 現在の合計配点： **{total_weight}点**（OK！「② 予測結果を見る」タブを開いてね）")
    else:
        st.warning(f"⚠️ 現在の合計配点： **{total_weight}点**（あと {100 - total_weight} 点 調整が必要です）")

# ==========================================
# 📊 シミュレーション計算ロジック (既存処理)
# ==========================================
df['温度差'] = df['海水温'] - df['気温']

df['score_temp'] = np.where(df['温度差'] >= threshold_temp, 
                            weight_temp, 
                            np.maximum(0.0, (df['温度差'] / threshold_temp) * weight_temp))

if threshold_clouds == 100:
    df['score_clouds'] = weight_clouds
else:
    df['score_clouds'] = np.where(df['雲量'] <= threshold_clouds, 
                                  weight_clouds, 
                                  np.maximum(0.0, ((100 - df['雲量']) / (100 - threshold_clouds)) * weight_clouds))

df['wind_speed_factor'] = np.where(
    (df['風速'] >= min_wind) & (df['風速'] <= max_wind), 
    1.0,
    np.where(df['風速'] < min_wind, 
             np.maximum(0.0, df['風速'] / np.maximum(0.1, min_wind)),
             np.maximum(0.0, 1.0 - (df['風速'] - max_wind) / 5.0))
)

wind_direction_multipliers = {
    '北西': 1.0, '北北西': 1.0, '北': 1.0, '西北西': 0.7, '北北東': 0.7,
    '西': 0.35, '北東': 0.35, '東北東': 0.0, '東': 0.0, '東南東': 0.0,
    '南東': 0.0, '南南東': 0.0, '南': 0.0, '南南西': 0.0, '南西': 0.0, '西南西': 0.0
}
df['wind_dir_factor'] = df['風向'].map(wind_direction_multipliers).fillna(0.0)
df['score_wind'] = df['wind_speed_factor'] * df['wind_dir_factor'] * weight_wind

df['予測スコア'] = df['score_temp'] + df['score_clouds'] + df['score_wind']

if total_weight == 100:
    threshold_score = 80.0
    df['発生予測'] = np.where(df['予測スコア'] >= threshold_score, 1, 0)
else:
    df['発生予測'] = 0

total_days = len(df)
predicted_days = int(df['発生予測'].sum())
avg_yearly_days = predicted_days / 5.0

# ------------------------------------------
# タブ2：予測結果
# ------------------------------------------
with tab2:
    st.subheader("📈 シミュレーション結果")
    
    # 指標をスマホでも見やすくカード表示
    m1, m2 = st.columns(2)
    m1.metric("5年間の予想発生日数", f"{predicted_days} 日")
    m2.metric("年間平均", f"{avg_yearly_days:.1f} 日 / 年")

    st.markdown("#### 🤖 AIアドバイザーの判定")
    has_zero_weight = (weight_temp == 0 or weight_clouds == 0 or weight_wind == 0)
    is_initial_condition = (threshold_temp == 5.0 or threshold_clouds == 100 or min_wind == 0.0 or max_wind == 20.0)

    if total_weight != 100:
        st.info("💡 まずは「① 条件を設定する」タブで、合計配点をぴったり100点にしてみよう！")
    elif has_zero_weight:
        st.warning("📋 配点が0点の項目があります。だるま夕日は温度・雲・風のバランスが大切です！")
    elif is_initial_condition:
        st.warning("🔍 条件の基準（スライダー）が初期設定のままのようです。少し絞り込んでみましょう！")
    elif predicted_days == 0:
        st.warning("⚠️ 発生予測が0日になりました。条件が少し厳しすぎるかもしれません。")
    elif 75 <= predicted_days <= 400:
        st.success("🟢 【素晴らしい！】実際の室戸岬の出現頻度にかなり近い、リアルなシミュレーションモデルです！")
    elif predicted_days < 75:
        st.warning(f"💡 年間 {avg_yearly_days:.1f} 日の予測です。実際の室戸より少し基準が厳しめかもしれません。")
    else:
        st.error(f"🔺 年間 {avg_yearly_days:.1f} 日の予測です。基準が少しゆるく、見誤りが多いかもしれません。")

    st.markdown("---")
    st.markdown("#### 📅 月別の発生予想（5年間の合計）")
    monthly_summary = df.groupby('月')['発生予測'].sum().reset_index().set_index('月')
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
        
        # スマホで見やすいメトリクス表示
        col_a, col_b = st.columns(2)
        col_a.metric("気温 / 海水温", f"{row['気温']}℃ / {row['海水温']}℃")
        col_a.metric("温度差", f"{row['温度差']:.1f}℃")
        col_b.metric("風", f"{row['風向']} {row['風速']}m/s")
        col_b.metric("雲量", f"{row['雲量']}％")

        st.markdown("---")
        if total_weight != 100:
            st.warning("合計配点を100点に設定すると、この日のスコア判定が表示されます。")
        elif row['発生予測'] == 1:
            st.success(f"🎉 **発生可能性【大】** （判定スコア: {row['予測スコア']:.1f}点 / 合格点: 80.0点）")
        else:
            st.error(f"❄️ **発生可能性【低】** （判定スコア: {row['予測スコア']:.1f}点 / 合格点: 80.0点）")
    else:
        st.warning("この日付のデータはありません。")