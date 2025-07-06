
# Streamlit Crowd Avoidance App Prototype
import streamlit as st
import pandas as pd
import pandas as pd

# スポットCSVを安全に読み込む関数
def read_spots_csv(path):
    try:
        df = pd.read_csv(path, encoding="utf-8")
        if df.shape[1] == 1:  # 1列しかない場合は読み込みミス
            raise ValueError("列が1つしか読み込まれていません。区切り文字やエンコードを確認してください。")
        return df
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="utf-8-sig")

# データ読み込みにこの関数を使う
spots_df = read_spots_csv("spots.csv")
congestion_df = pd.read_csv("congestion.csv", encoding="utf-8")  # これはそのままでOK

import matplotlib.pyplot as plt
import requests

# 天気取得関数（OpenWeatherMapを利用）
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

# APIキー（自分のキーをここに入れる）
API_KEY = "cdf89abd438b578afc512bac8551faf7"

# 安全なCSV読み込み（エンコーディング対応）
def read_csv_safely(filepath):
    try:
        return pd.read_csv(filepath, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(filepath, encoding="utf-8-sig")

# CSVファイル読み込み
spots_df = read_csv_safely("spots.csv")
congestion_df = read_csv_safely("congestion.csv")

# 列名の整備
congestion_df.columns = congestion_df.columns.str.strip()
if "混雑度（0〜100）" not in congestion_df.columns:
    for col in congestion_df.columns:
        if "混雑度" in col:
            congestion_df.rename(columns={col: "混雑度（0〜100）"}, inplace=True)

# ページ設定
st.set_page_config(page_title="閑散スポット検索", layout="wide")
page = st.sidebar.selectbox("ページ選択", ["ホーム", "スポット詳細", "おすすめ"])

# ホームページ
if page == "ホーム":
    st.title("🌍 空いてる観光地を探そう!")
    search = st.text_input("🔍 行きたい場所を入力")

    # スポット検索
    if search:
        filtered_df = spots_df[spots_df["スポット名"].str.contains(search, case=False, na=False)]
        if not filtered_df.empty:
            map_df = filtered_df.rename(columns={"緯度": "latitude", "経度": "longitude"})
            st.map(map_df)
            st.write("検索結果：", filtered_df["スポット名"].tolist())
        else:
            st.warning("該当するスポットが見つかりませんでした。")
    else:
        map_df = spots_df.rename(columns={"緯度": "latitude", "経度": "longitude"})
        st.map(map_df)

# 詳細ページ
elif page == "スポット詳細":
    st.title("🏠 スポット詳細")
    spot = st.selectbox("スポットを選択", spots_df["スポット名"].unique())
    st.subheader(f"📍 {spot}")

    # 天気情報表示
    city_name = spots_df[spots_df["スポット名"] == spot]["都市名"].values[0]
    weather = get_weather(city_name, API_KEY)
    st.markdown(f"### ☀ 現在の天気：{weather}")

    # 混雑グラフ
    df = congestion_df[congestion_df["スポット名"] == spot]
    if "混雑度（0〜100）" in df.columns:
        fig, ax = plt.subplots()
        ax.plot(df["時間帯"], df["混雑度（0〜100）"], marker="o")
        ax.set_ylabel("混雑度")
        ax.set_xlabel("時間帯")
        ax.set_title("時間帯別混雑予測")
        st.pyplot(fig)

    # 代替スポット提案
    alt = spots_df[spots_df["スポット名"] == spot]["代替スポット"].values[0]
    st.markdown(f"### 代替案の提案: {alt}")
    df_alt = congestion_df[congestion_df["スポット名"] == alt]
    if not df_alt.empty and "混雑度（0〜100）" in df_alt.columns:
        fig2, ax2 = plt.subplots()
        ax2.plot(df_alt["時間帯"], df_alt["混雑度（0〜100）"], marker="x", color="gray")
        ax2.set_title(f"{alt} の混雑度")
        st.pyplot(fig2)

# おすすめページ
elif page == "おすすめ":
    st.title("🤖 今行くならここ！")
    now_df = congestion_df[congestion_df["時間帯"] == "12:00"]
    if "混雑度（0〜100）" in now_df.columns and not now_df.empty:
        least_crowded = now_df.sort_values("混雑度（0〜100）").iloc[0]
        st.subheader(f"👑 おすすめ: {least_crowded['スポット名']}")
        st.markdown("### 理由: 12:00時点で最も空いているスポット")
        st.bar_chart(pd.DataFrame(
            congestion_df[congestion_df["スポット名"] == least_crowded["スポット名"]]["混雑度（0〜100）"].values,
            index=congestion_df[congestion_df["スポット名"] == least_crowded["スポット名"]]["時間帯"],
            columns=["混雑度"]
        ))
        st.write("まったり過ごせそうですね！")
