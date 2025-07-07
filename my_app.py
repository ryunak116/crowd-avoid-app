
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

# データ読み込み（BOM付きUTF-8対応）
spots_df = pd.read_csv("spots.csv", encoding="utf-8-sig")
congestion_df = pd.read_csv("congestion.csv", encoding="utf-8-sig")

# 列名クリーンアップ
congestion_df.columns = congestion_df.columns.str.strip()
if "混雑度（0〜100）" not in congestion_df.columns:
    for col in congestion_df.columns:
        if "混雑度" in col:
            congestion_df.rename(columns={col: "混雑度（0〜100）"}, inplace=True)

# 天気取得関数
def get_weather(city_name, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&lang=ja&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"{weather}（{temp}℃）"
    else:
        return "天気情報の取得に失敗しました"

# OpenWeatherMap APIキー
API_KEY = "cdf89abd438b578afc512bac8551faf7"

# Streamlitの画面構成
st.set_page_config(page_title="混雑回避アプリ", layout="wide")
st.title("🌞 混雑を避けて観光しよう！")

# 検索欄
search = st.text_input("🔍 行きたい場所を入力してください")

# 検索処理
if search:
    matched_spots = spots_df[spots_df["スポット名"].str.contains(search, na=False, case=False)]
else:
    matched_spots = spots_df

# 地図表示
map_df = matched_spots.rename(columns={"緯度": "latitude", "経度": "longitude"})
st.map(map_df)

# スポット選択
if not matched_spots.empty:
    selected_spot = st.selectbox("表示するスポットを選んでください", matched_spots["スポット名"].unique())

    # スポット情報
    st.subheader(f"📍 {selected_spot}")
    city = matched_spots[matched_spots["スポット名"] == selected_spot]["都市名"].values[0]
    st.markdown(f"### ☁ 天気：{get_weather(city, API_KEY)}")

    # 混雑度グラフ
    df = congestion_df[congestion_df["スポット名"] == selected_spot]
    if not df.empty:
        fig, ax = plt.subplots()
        ax.plot(df["時間帯"], df["混雑度（0〜100）"], marker="o")
        ax.set_title("⏰ 時間帯別混雑度")
        ax.set_xlabel("時間帯")
        ax.set_ylabel("混雑度（0〜100）")
        st.pyplot(fig)

    # 代替スポットの表示
    alt = matched_spots[matched_spots["スポット名"] == selected_spot]["代替スポット"].values[0]
    st.markdown(f"### 🧭 代替案：{alt}")

    df_alt = congestion_df[congestion_df["スポット名"] == alt]
    if not df_alt.empty:
        fig2, ax2 = plt.subplots()
        ax2.plot(df_alt["時間帯"], df_alt["混雑度（0〜100）"], marker="x", color="gray")
        ax2.set_title(f"{alt} の混雑度グラフ")
        st.pyplot(fig2)
