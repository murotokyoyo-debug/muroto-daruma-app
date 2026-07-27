# ------------------------------------------
# タブ4：今日の夕日予報（実践モード）
# ------------------------------------------
with tab4:
    st.subheader("🔮 天気予報の数値を入れて「今日の発生確率」を計算しよう！")
    st.caption("「① 条件を設定する」タブで設定したあなたの発生ルールを使って、今日や明日の天気予報から遭遇確率を計算します。")

    st.markdown("---")

    if total_weight != 100:
        st.warning("⚠️ まずは「① 条件を設定する」タブで、合計配点をぴったり100点に設定してください！")
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

        # 入力値に対するリアルタイムスコア計算
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

        # ③ 風スコア
        if min_wind <= input_wind_speed <= max_wind:
            w_speed_score = 1.0
        elif input_wind_speed < min_wind:
            w_speed_score = max(0.0, 1.0 - (min_wind - input_wind_speed) / 0.5)
        else:
            w_speed_score = max(0.0, 1.0 - (input_wind_speed - max_wind) / 1.5)

        w_dir_factor = 1.0 if input_wind_dir in selected_wind_dirs else 0.0
        s_wind = w_speed_score * w_dir_factor * float(weight_wind)

        # 総合予測スコア
        input_score = s_temp + s_cloud + s_wind

        with c2:
            with st.container(border=True):
                st.markdown("##### 📊 リアルタイムスコア判定")
                
                st.metric("海水温と気温の差", f"{input_diff:.1f} ℃")
                st.metric("本日の判定スコア", f"{input_score:.1f} 点 / 100点", f"合格ボーダー: {threshold_score}点")

                st.markdown("---")
                
                # 判定メッセージ（st.balloons() を削除してスマートに表示）
                if input_score >= threshold_score:
                    st.success("🌅 **【絶好のチャンス！】今日のだるま夕日指数: ★★★**\n設定した合格ルールをクリアしています！室戸岬へ見に行く価値が大いにあります！")
                elif input_score >= threshold_score * 0.8:
                    st.warning("⛅ **【ワンチャンスあり】今日のだるま夕日指数: ★★☆**\n合格ボーダーまであと一歩です！西の空の雲が抜ければ見られる可能性があります。")
                else:
                    st.error("🌧️ **【難しい】今日のだるま夕日指数: ★☆☆**\n設定した合格条件に届いておらず、本日だるま夕日が見られる可能性は低いです。")

                # 得点内訳の可視化
                with st.expander("🔍 スコアの内訳を見る"):
                    st.write(f"- 温度差スコア: **{s_temp:.1f}** / {weight_temp}点")
                    st.write(f"- 雲量スコア: **{s_cloud:.1f}** / {weight_clouds}点")
                    st.write(f"- 風条件スコア: **{s_wind:.1f}** / {weight_wind}点")
