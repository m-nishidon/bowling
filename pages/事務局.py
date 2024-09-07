import streamlit as st

import utils

df, df_team, current_frame, df_conf, now, open_result, stop_update = (
    utils.read_origin_score()
)

utils.clear_ss_score_update()

st.title("事務局用")
data_staff = st.secrets["staff"]
password = st.text_input("パスワードを入力してください:", type="password")
if password != data_staff["password"]:
    st.error("事務局用のページです。")
else:
    st.markdown(
        """
    - 練習中:100
    - 大会中:001
    - 結果確認中:011
    - 結果発表以降:111
    """
    )
    df_conf = st.data_editor(df_conf, hide_index=True)
    if st.button("更新"):
        client = utils.connect_spread_sheet()
        # スプレッドシートを開く
        try:
            ws = client.open("スコア表").worksheet("data")
        except AttributeError:
            utils.connect_spread_sheet.clear()
            client = utils.connect_spread_sheet()
            ws = client.open("スコア表").worksheet("data")
        cells = ws.range("AU2:AU4")
        for cell, value in zip(cells, df_conf["値"]):
            cell.value = value
        ws.update_cells(cells)
        # 再読み込み
        utils.read_origin_score.clear()
        df, df_team, current_frame, df_conf, now, open_result, stop_update = (
            utils.read_origin_score()
        )
