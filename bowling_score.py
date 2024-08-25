import gspread
import pandas as pd
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets APIの認証情報を設定
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
# creds = ServiceAccountCredentials.from_json_keyfile_name(
#     r"C:\Users\mnish\Downloads\bowling202409-07ee09797e39.json", scope
# )
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"], scope
)
client = gspread.authorize(creds)


# スプレッドシートのデータを読み込み
@st.cache_data
def read_origin_score():
    # スプレッドシートを開く
    sheet = client.open("スコア表").sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df = df.sort_values("順位")
    return df


def read_updated_score():
    # スプレッドシートを開く
    sheet = client.open("スコア表").sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df


# 初期化時にセッションステートを設定
df = read_origin_score()
# データを表示
st.title("順位表")

if st.button("順位更新"):
    # 再読み込み
    read_origin_score.clear()
    df = read_origin_score()

st.dataframe(df)

st.subheader("データ更新用")
edited_df = st.data_editor(df, num_rows="dynamic")

if st.button("データ更新"):
    sheet = client.open("スコア表").sheet1
    for i, row in edited_df.iterrows():
        for j, col in enumerate(edited_df.columns):
            sheet.update_cell(i + 2, j + 1, str(row[col]))  # セルの更新
    st.success("Data Updated Successfully")

    # 再読み込み
    df2 = read_updated_score()
    st.dataframe(df2)
