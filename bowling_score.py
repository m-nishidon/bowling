import gspread
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

from utils import calc_bowling_score

plt.rcParams["font.family"] = "Meiryo"

# Google Sheets APIの認証情報を設定
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"], scope
)
client = gspread.authorize(creds)


def keisha(row, max_):
    rate = max_ / row["人数"]
    for i in range(1, 11):
        row[str(i)] *= rate
    return row[3:-1]


def make_rank(df):
    df = df.sort_values("10", ascending=False)
    df["順位"] = [i + 1 for i in range(df.shape[0])]
    return df


# スプレッドシートのデータを読み込み
@st.cache_data
def read_origin_score():
    # スプレッドシートを開く
    sheet = client.open("スコア表").worksheet("1ゲーム目")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df[[str(i) for i in range(1, 11)]] = df[df.columns[3:]].apply(
        calc_bowling_score, result_type="expand", axis=1
    )

    df_team = df[list(df.columns[:3]) + list(df.columns[-10:])].copy()
    df_team = df_team.groupby("チーム", as_index=False).agg(
        {
            "名前": lambda x: "  ".join(x),
            "拠点": "first",
            **{
                col: "sum"
                for col in df_team.columns
                if col not in ["チーム", "名前", "拠点"]
            },
        }
    )
    df_team["人数"] = list(df.groupby("チーム")["名前"].count())
    df_team = df_team.rename(columns={"名前": "メンバー"})
    max_ = df_team["人数"].max()
    df_team[[str(i) for i in range(1, 11)]] = df_team.apply(
        keisha, result_type="expand", axis=1, max_=max_
    )
    df_team = make_rank(df_team)
    df = make_rank(df)

    return df, df_team


def read_updated_score():
    # スプレッドシートを開く
    sheet = client.open("スコア表").worksheet("1ゲーム目")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df


df, df_team = read_origin_score()

area = "全拠点"
st.sidebar.title("拠点選択")
labels = ["全拠点"] + list(df_team["拠点"].unique())
area = st.sidebar.selectbox("拠点を選択してください", labels)

if area != "全拠点":
    df = df[df["拠点"] == area]
    df_team = df_team[df_team["拠点"] == area]

# データを表示
st.title("個人順位表")

if st.button("順位更新"):
    # 再読み込み
    read_origin_score.clear()
    df, df_team = read_origin_score()

st.dataframe(
    df[["順位", "10", "名前", "拠点", "チーム"]].rename(columns={"10": "得点"})
)

plt.figure(figsize=(10, 10))

for index, row in df.iterrows():
    # 24-34はフレーム
    plt.plot(range(1, 11), row[24:34], marker="o", label=row["名前"])

plt.xlabel("フレーム")
plt.ylabel("スコア")
plt.title("個人順位表")
plt.legend(title="名前", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.grid(True)
plt.tight_layout()

st.pyplot(plt)


st.title("チーム順位表")

st.dataframe(df_team[["順位", "10", "メンバー", "拠点"]].rename(columns={"10": "得点"}))

plt.figure(figsize=(10, 10))

for index, row in df_team.iterrows():
    # 3-13はフレーム
    plt.plot(range(1, 11), row[3:13], marker="o", label=row["メンバー"])

plt.xlabel("フレーム")
plt.ylabel("スコア")
plt.title("チーム順位表")
plt.legend(title="メンバー", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.grid(True)
plt.tight_layout()

st.pyplot(plt)

st.subheader("データ更新用")
edited_df = st.data_editor(df[df.columns[:-11]], num_rows="dynamic")
