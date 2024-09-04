import streamlit as st

import utils

st.title("スコア更新用")


df, df_team, current_frame, df_conf, now = utils.read_origin_score()

df = df[df.columns[:-21]]


# 拠点に関するフィルター
# session_stateの問題で拠点、チーム、名前は関数化せずそれぞれ処理
def update_area():
    st.session_state["area"] = st.session_state["new_area"]


st.subheader("拠点選択")
labels = ["ALL"] + sorted(df["拠点"].unique())
idx = labels.index(st.session_state["area"]) if "area" in st.session_state else 0
selected_area = st.selectbox(
    "拠点を選択してください",
    labels,
    idx,
    key="new_area",
    on_change=update_area,
)
if selected_area != "ALL":
    df = df[df["拠点"] == selected_area]


# チームに関するフィルター
def update_team():
    selected_team = st.session_state["new_team"]
    if "ALL" in selected_team and len(selected_team) >= 2:
        if selected_team[-1] == "ALL":
            selected_team = set({"ALL"})
        else:
            selected_team = set(selected_team)
            selected_team.discard("ALL")
    st.session_state["team"] = selected_team


st.subheader("チーム選択")
labels = ["ALL"] + sorted(df["チーム"].unique())
selected_team = set(
    st.multiselect(
        "チームを選択してください",
        labels,
        st.session_state["team"] if "team" in st.session_state else labels[0],
        key="new_team",
        on_change=update_team,
    )
)
if selected_team != {"ALL"}:
    df = df[df["チーム"].isin(selected_team)]


# 名前に関するフィルター
def update_name():
    selected_name = st.session_state["new_name"]
    if "ALL" in selected_name and len(selected_name) >= 2:
        if selected_name[-1] == "ALL":
            selected_name = set({"ALL"})
        else:
            selected_name = set(selected_name)
            selected_name.discard("ALL")
    st.session_state["name"] = selected_name


st.subheader("名前選択")
labels = ["ALL"] + sorted(df["名前"].unique())
selected_name = set(
    st.multiselect(
        "名前を選択してください",
        labels,
        st.session_state["name"] if "name" in st.session_state else labels[0],
        key="new_name",
        on_change=update_name,
    )
)
if selected_name != {"ALL"}:
    df = df[df["名前"].isin(selected_name)]

# 1ゲーム目2ゲーム目の選択
st.subheader("ゲーム選択")
idx = st.session_state["game"] if "game" in st.session_state else 0
selected_game = st.selectbox("何ゲーム目かを選択してください", (1, 2), idx)
st.session_state["game"] = selected_game - 1
if selected_game == 1:
    df = df[df.columns[:-21]]
else:
    df = df[list(df.columns[:3]) + list(df.columns[24:])]


# フレームの選択
def update_frame():
    st.session_state["frame"] = st.session_state["new_frame"]


start, end = st.slider(
    "何フレーム目を更新するか選んでください",
    min_value=1,
    max_value=10,
    key="new_frame",
    value=st.session_state["frame"] if "frame" in st.session_state else (1, 10),
    on_change=update_frame,
)
if end == 10:
    df = df[list(df.columns[:3]) + list(df.columns[3 + (start - 1) * 2 :])]
else:
    df = df[
        list(df.columns[:3])
        + list(df.columns[3 + (start - 1) * 2 : -(3 + (9 - end) * 2)])
    ]

# インデックスを名前列にする
# 元のインデックスも保存しておく
df["index"] = df.index
df = df.set_index("名前")
edited_df = st.data_editor(df[df.columns[:-1]])
