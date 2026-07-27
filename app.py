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
    df['日付'] = pd.to_datetime(df['日付'], format='mixed', errors='coerce').dt.strftime('%Y-%m-%d')
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
# 📊 シミュレーション計算ロジック
# ==========================================
df['温度差'] = df['海水温'] - df['気温']

# ① 温度差：基準より1.5℃低い範囲までで減点（それ以下は0点）
temp_margin = 1.5
df['score_temp'] = np.where(
    df['温度差'] >= threshold_temp,
    float(weight_temp),
    np.maximum(0.0, weight_temp * (1.0 - (threshold_temp - df['温度差']) / temp_margin))
)

# ② 雲量：基準+10%を超えたら急速に0点化
cloud_margin = 10.0
df['score_clouds'] = np.where(
    df['雲量'] <= threshold_clouds,
    float(weight_clouds),
    np.maximum(0.0, weight_clouds * (1.0 - (df['雲量'] - threshold_clouds) / cloud_margin))
)

# ③ 風条件：風向きによる減点をメリハリ化（北〜北西以外は厳しく評価）
wind_speed_score = np.where(
    (df['風速'] >= min_wind) & (df['風速'] <= max_wind),
    1.0,
    np.where(
        df['風速'] < min_wind,
        np.maximum(0.0, 1.0 - (min_wind - df['風速']) / 0.5),
        np.maximum(0.0, 1.0 - (df['風速'] - max_wind) / 2.0)
    )
)

wind_direction_multipliers = {
    '北西': 1.0, '北北西': 1.0, '北': 1.0,
    '西北西': 0.75, '北北東': 0.75,
    '西': 0.5, '北東': 0.5,
    '東北東': 0.1, '東': 0.1, '東南東': 0.1,
    '南東': 0.1, '南南東': 0.1, '南': 0.1, '南南西': 0.1, '南西': 0.1, '西南西': 0.1
}
df['wind_dir_factor'] = df['風向'].map(wind_direction_multipliers).fillna(0.1)
df['score_wind'] = wind_speed_score * df['wind_dir_factor'] * weight_wind

# 合計スコア
df['予測スコア'] = df['score_temp'] + df['score_clouds'] + df['score_wind']

# 💡 合格ラインを 90.0 点に引き上げて厳格化！
threshold_score = 90.0

if total_weight == 100:
    df['発生予測'] = np.where(df['予測スコア'] >= threshold_score, 1, 0)
else:
    df['発生予測'] = 0

total_days = len(df)
predicted_days = int(df['発生予測'].sum())

# 2021年10月〜2025年3月の4シーズン（4年間）データのため 4.0 で割る
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
    elif has_zero_weight:
        st.warning("📋 配点が0点の項目があります。だるま夕日は温度・雲・風のバランスが大切です！")
    elif is_initial_condition:
        st.warning("🔍 条件の基準（スライダー）が初期設定のままのようです。少し絞り込んでみましょう！")
    elif predicted_days == 0:
        st.warning("⚠️ 発生予測が0日になりました。条件が少し厳しすぎるかもしれません。")
    # 4年間で 20日〜80日（年間 5日〜20日相当）を適正基準に設定
    elif 20 <= predicted_days <= 80:
        st.success(f"🟢 【素晴らしい！】年間 {avg_yearly_days:.1f} 日の予測です。実際の室戸岬の年間発生数（10〜20回前後）に極めて近いリアルな条件設定です！")
    elif predicted_days < 20:
        st.warning(f"💡 年間 {avg_yearly_days:.1f} 日の予測です。かなり厳しい条件ですが、完璧な「本物のだるま夕日」に絞った条件と言えます。")
    else:
        st.error(f"🔺 年間 {avg_yearly_days:.1f} 日の予測です。発生数が多すぎます！もう少し「温度差」や「風向き」「雲量」の合格ラインを厳しく設定してみましょう。")

    st.markdown("---")
    st.markdown("#### 📅 月別の発生予想（4シーズンの合計）")
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
        
        # メトリクス表示
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
