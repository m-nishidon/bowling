import streamlit as st

import utils

df, df_team, current_frame, df_conf, now = utils.read_origin_score()

st.title("事務局用")
data_staff = st.secrets["staff"]
password = st.text_input("パスワードを入力してください:", type="password")
if password != data_staff["password"]:
    st.error("事務局用のページです。")
else:
    st.success("パスワードが正しいです。後続の処理を実行します。")
    st.dataframe(df_conf, hide_index=True)
