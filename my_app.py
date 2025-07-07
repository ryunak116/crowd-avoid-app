# Streamlit Crowd Avoidance App Prototype（1ページ構成）
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

# 天気取得関数（OpenWeatherMap API）
def get_weather(city_name, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&lang=ja&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"{weather}（{temp}℃）"
    else:
        return "天気情報取得に失敗"

# APIキー（自分のキーをここに）
API_KEY = "cdf89abd438b578afc512bac8551faf7"

# データ読み込み
spots_df = pd.read_csv("spots.csv", encoding="utf-8")
congestion_df = pd.read_csv("congestion.csv", encoding="utf-8")

# 列名調整
congestion_df.columns = congestion_df.columns.str.strip()
for col in congestion_df.columns:
    if "混雑度" in col and col != "混雑度（0〜100）":
        congestion_df.rename(columns={col: "混雑度（0〜100）"}, inplace=True)

# UI設定
st.set_page_config(page_title="混雑回避観光アプリ", layout="wide")
st.title("🌈 混雑を避けて観光を楽しもう！")

# スポット検索
search = st.text_input("🔍 行きたい観光地を入力してください")
if search:
    filtered = spots_df[spots_df["スポット名"].str.contains(search, case=False, na=False)]
else:
    filtered = spots_df

# 地図表示
map_df = filtered.rename(columns={"緯度": "latitude", "経度": "longitude"})
st.map(map_df)

# スポット選択
spot_names = filtered["スポット名"].unique()
if len(spot_names) > 0:
    selected_spot = st.selectbox("📍 スポットを選んで詳細を表示", spot_names)
    st.subheader(f"🔎 {selected_spot}")

    # 天気
    city = spots_df[spots_df["スポット名"] == selected_spot]["都市名"].values[0]
    st.markdown(f"☁ 現在の天気：{get_weather(city, API_KEY)}")

    # 混雑度グラフ
    df = congestion_df[congestion_df["スポット名"] == selected_spot]
    if not df.empty:
        fig, ax = plt.subplots()
        ax.plot(df["時間帯"], df["混雑度（0〜100）"], marker="o")
        ax.set_title("時間帯別の混雑度予測")
        ax.set_ylabel("混雑度（0〜100）")
        ax.set_xlabel("時間帯")
        st.pyplot(fig)

    # 代替案の提案
    alt_spot = spots_df[spots_df["スポット名"] == selected_spot]["代替スポット"].values[0]
    st.markdown(f"🏞 代替案: {alt_spot}")
    alt_df = congestion_df[congestion_df["スポット名"] == alt_spot]
    if not alt_df.empty:
        fig2, ax2 = plt.subplots()
        ax2.plot(alt_df["時間帯"], alt_df["混雑度（0〜100）"], color="gray", marker="x")
        ax2.set_title(f"{alt_spot} の混雑度")
        st.pyplot(fig2)
else:
    st.warning("該当するスポットが見つかりませんでした。")

# 今空いている場所の提案
st.markdown("---")
st.subheader("✨ 今おすすめのスポット")
current = congestion_df[congestion_df["時間帯"] == "12:00"]
if not current.empty and "混雑度（0〜100）" in current.columns:
    least_crowded = current.sort_values("混雑度（0〜100）").iloc[0]
    st.markdown(f"💡 今一番空いてるのは **{least_crowded['スポット名']}**！")
    st.bar_chart(current.set_index("スポット名")["混雑度（0〜100）"])

