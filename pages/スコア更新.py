import streamlit as st

import utils

st.title("スコア更新用")


df, df_team, current_frame, df_conf = utils.read_origin_score()

df = df[df.columns[:-21]]


def select(df, colname, multi, selected_past):
    if not selected_past:
        selected_elements = "ALL"

    st.subheader(f"{colname}選択")
    labels = ["ALL"] + sorted(df[colname].unique())

    if not multi:
        if selected_past:
            selected_item = selected_past.pop()
            idx = labels.index(selected_item)
        else:
            idx = 0
        selected_elements = set()
        selected_elements.add(st.selectbox(f"{colname}を選択してください", labels, idx))
    else:
        selected_elements = set(
            st.multiselect(
                f"{colname}を選択してください",
                labels,
                selected_past if selected_past else labels[0],
            )
        )

    if "ALL" not in selected_elements:
        df = df[df[colname].isin(selected_elements)]
    return df, selected_elements


selected_items = []
for key in ["area", "team", "name"]:
    if key in st.session_state:
        selected_items.append(st.session_state[key])
    else:
        selected_items.append(None)
selected_area, selected_team, selected_name = selected_items

df, st.session_state["area"] = select(df, "拠点", False, selected_area)
df, st.session_state["team"] = select(df, "チーム", True, selected_team)
df, st.session_state["name"] = select(df, "名前", True, selected_name)
st.subheader("ゲーム選択")
idx = st.session_state["game"] if "game" in st.session_state else 0
selected_game = st.selectbox("何ゲーム目かを選択してください", (1, 2), idx)
st.session_state["game"] = selected_game - 1
if selected_game == 1:
    df = df[df.columns[:-21]]
else:
    df = df[list(df.columns[:3]) + list(df.columns[24:])]
start, end = st.slider(
    "何フレーム目を更新するか選んでください", min_value=1, max_value=10, value=(1, 10)
)
if end == 10:
    df = df[list(df.columns[:3]) + list(df.columns[3 + (start - 1) * 2 :])]
else:
    df = df[
        list(df.columns[:3])
        + list(df.columns[3 + (start - 1) * 2 : -(3 + (9 - end) * 2)])
    ]
edited_df = st.data_editor(df)


st.write(
    "前回のフィルター条件の保存(バグってます…)、変な数字の確認、2ゲーム目しない場合"
)
