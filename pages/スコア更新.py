from pathlib import Path

import streamlit as st
from PIL import Image
from streamlit_image_select import image_select

import utils

IMG_FOLDER = "_images"
st.title("スコア更新用")

df, df_team, current_frame, df_conf, now, open_result, stop_update = (
    utils.read_origin_score()
)

if stop_update:
    st.info("事務局確認中のため更新できません。結果発表をお待ちください。")
    exit()

df = df[df.columns[:-21]]


# 拠点に関するフィルター
# session_stateの問題で拠点、チーム、名前は関数化せずそれぞれ処理
def update_area():
    st.session_state["area"] = st.session_state["new_area"]
    utils.clear_ss_score_update()


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
    utils.clear_ss_score_update()


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
    utils.clear_ss_score_update()


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
selected_game = st.selectbox(
    "何ゲーム目かを選択してください",
    (1, 2),
    idx,
    on_change=utils.clear_ss_score_update,
)
st.session_state["game"] = selected_game - 1
if selected_game == 1:
    df = df[df.columns[:-21]]
else:
    df = df[list(df.columns[:3]) + list(df.columns[24:])]


# フレームの選択
def update_frame():
    st.session_state["frame"] = st.session_state["new_frame"]
    utils.clear_ss_score_update()


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
df = df.sort_index()
df["index"] = df.index
idx_min, idx_ma = df["index"].min(), df["index"].max()
df = df.set_index("名前")
df = df[df.columns[2:]]

if "df" in st.session_state:
    edited_df = st.session_state["df"]
else:
    edited_df = df.copy()
if "rc" not in st.session_state:
    row, col = 0, 0
else:
    row, col = st.session_state["rc"]
    if row >= df.shape[0] or col >= df.shape[1]:
        row, col = 0, 0


if st.button(":arrow_double_up:"):
    row = max(0, row - 1)
if st.button(":arrow_double_down:"):
    row = min(df.shape[0] - 1, row + 1)
if st.button(":rewind:"):
    col = max(0, col - 1)
if st.button(":fast_forward:"):
    col = min(df.shape[1] - 1, col + 1)
st.session_state["rc"] = (row, col)

for i, tab in enumerate(
    st.tabs(
        (
            "  ",
            " 0",
            " 1",
            " 2",
            " 3",
            " 4",
            " 5",
            " 6",
            " 7",
            " 8",
            " 9",
            "10",
            " X",
            " /",
            " G",
            " ‐",
        )
    )
):
    with tab:
        if i:
            n = [
                -1,
                0,
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                "X",
                "/",
                "G",
                "-",
            ][i]
        if st.button(":white_check_mark:", key=i):
            edited_df.iat[row, col] = n

st.dataframe(
    edited_df[edited_df.columns[:-1]].style.apply(
        utils.highlight_specific_cell, axis=None, row=row, col=col
    )
)  # [df.columns[:-1]])
st.session_state["df"] = edited_df

# img = image_select(
#     label="",
#     images=[Image.open(image).convert("RGB").resize((5, 5)) for image in images],
#     index=-1,
#     use_container_width=False,
#     return_value="index",
# )
# st.write(img)
if st.button("確認"):
    st.dataframe(edited_df.style.apply(utils.style_diff, target=df, axis=0))
    st.write("赤色部分のデータを更新します。よろしいですか？")
    st.write(
        "(ダメな場合はページ切り替えればとりあえずはOKです。おかしな数字（足して10超えるとか）の確認は未了です。)。チームと拠点は色がついていても更新されません。"
    )


if st.button("更新"):
    client = utils.connect_spread_sheet()
    # スプレッドシートを開く
    try:
        ws = client.open("スコア表").worksheet("data")
    except AttributeError:
        utils.connect_spread_sheet.clear()
        client = utils.connect_spread_sheet()
        ws = client.open("スコア表").worksheet("data")
    if selected_game == 1:
        cells = ws.range(f"D{idx_min+2}:X{idx_ma+2}")
    else:
        cells = ws.range(f"Y{idx_min+2}:AS{idx_ma+2}")
    cells_update = []
    for idx, row_before, row_after in zip(
        df["index"], df.itertuples(), edited_df.itertuples()
    ):
        idx %= idx_min
        for idx2, (v_before, v_after) in enumerate(
            zip(row_before[1:-1], row_after[1:-1])
        ):
            if v_before == v_after:
                continue
            else:
                cell = cells[idx * 21 + (start - 1) * 2 + idx2]
                cell.value = v_after
                cells_update.append(cell)
    if not cells_update:
        st.warning("更新対象データがありませんでした")
    else:
        ws.update_cells(cells_update)
        st.success("更新しました")
        utils.balloons_or_snows()
        # 再読み込み
        utils.read_origin_score.clear()
        df, df_team, current_frame, df_conf, now, open_result, stop_update = (
            utils.read_origin_score()
        )
