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

with st.expander("データ更新説明", expanded=False):
    st.markdown(
        """
    - エラーが起きても落ち着いてページを切り替えたら戻ります
    - 上にある矢印4つは基本的には使わない（詳細は後述）
    - 黄色の箇所に数字が入力される（タップした赤い箇所ではない点注意）
    - 数字は横一列に並んだ0~-を選択した状態でチェックボックスをタップで黄色の箇所に入力される
    - 黄色の箇所は右が下に動くため、また数字を選択してチェックボックスをタップ
    - 2投分(10フレーム目は3投分)入力してから次の人を入力することを想定しているため黄色はZ字状に動く
    - それ以外の箇所に入力したい場合は上部の矢印4つをクリックして動かす（スマホだと横に並べるのがしんどい…）
        - ただページ切り替えでリセットした方が早い場合が多い
    - 確認→更新ボタンでデータ反映
        - 間違えても上書きすればいいので何度でもOK
    """
    )

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
            frame = int(edited_df.columns[col].split("_")[0]) % 10
            if not frame:
                frame = 10
            if n == "X":
                if frame == 10:
                    if not col % 2:
                        n = 10
                    else:
                        if 1 <= edited_df.iat[row, col - 1] <= 9:
                            st.error("倒せるピンが10本残っていません。")
                            continue
                        else:
                            n = 10
                else:
                    if not col % 2:
                        n = 10
                    else:
                        if 1 <= edited_df.iat[row, col - 1] <= 10:
                            st.error("倒せるピンが10本残っていません")
                            continue
                        else:
                            n = 10
            elif n == "/":
                if not col % 2:
                    st.error("2投目以外でスペアにはなりません")
                    continue
                else:
                    n = 10 - edited_df.iat[row, col - 1]
            elif n == "G" or n == "-":
                n = 0

            elif col % 2:
                if edited_df.iat[row, col - 1] + n > 10:
                    if frame < 10 or edited_df.iat[row, col - 1] != 10:
                        st.error("1投目との合計が10を超えています")
                        continue
            if edited_df.columns[col].split("_")[1] == "3":
                if (
                    edited_df.iat[row, col - 1] + edited_df.iat[row, col - 2] < 10
                    and n != 0
                ):
                    st.error("3投目はありません")
                    continue
            edited_df.iat[row, col] = n
            if col % 2:
                if frame == 10:
                    col += 1
                elif row == edited_df.shape[0] - 1:
                    col = min(col + 1, edited_df.shape[1] - 2)
                    row = 0
                else:
                    col -= 1
                    row += 1
            else:
                if frame == 10 and col == edited_df.shape[1] - 2:
                    col -= 2
                    row = min(row + 1, edited_df.shape[0] - 1)
                elif col < edited_df.shape[1] - 2:
                    col += 1
                else:
                    row = min(row + 1, edited_df.shape[0] - 1)

            st.session_state["rc"] = (row, col)


st.dataframe(
    edited_df[edited_df.columns[:-1]].style.apply(
        utils.highlight_specific_cell, axis=None, row=row, col=col
    ),
    use_container_width=True,
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
    st.dataframe(
        edited_df[edited_df.columns[:-1]].style.apply(
            utils.style_diff, target=df, axis=0
        ),
        use_container_width=True,
    )
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
