import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import utils

# カラースケールを拡張
colors = (
    px.colors.qualitative.Light24
    + px.colors.qualitative.Alphabet
    + px.colors.qualitative.Dark24
)

df, df_team, current_frame, df_conf = utils.read_origin_score()

# if "width_tmp" in st.session_state and st.sidebar.button(
#     "保存(フィルター等の設定を保存)"
# ):
#     st.session_state["width"] = st.session_state["width_tmp"]


# if "width" in st.session_state and st.sidebar.button("読込(フィルター等の設定を読込)"):
#     width = st.session_state["width"]
# else:
#     width = 600


def sidebar_select(df, df_team, colname, multi):
    selected_elements = "ALL"
    st.sidebar.title(f"{colname}選択")
    if colname != "名前":
        labels = ["ALL"] + sorted(df_team[colname].unique())
    else:
        labels = ["ALL"] + sorted(df[colname].unique())

    if not multi:
        selected_elements = set()
        selected_elements.add(
            st.sidebar.selectbox(f"{colname}を選択してください", labels)
        )
    else:
        selected_elements = set(
            st.sidebar.multiselect(f"{colname}を選択してください", labels, labels[0])
        )

    if "ALL" not in selected_elements:
        df = df[df[colname].isin(selected_elements)]
        if colname != "名前":
            df_team = df_team[df_team[colname].isin(selected_elements)]
    return df, df_team, selected_elements


df, df_team, _ = sidebar_select(df, df_team, "拠点", False)
df, df_team, _ = sidebar_select(df, df_team, "チーム", True)
df, df_team, selected_elements = sidebar_select(df, df_team, "名前", True)

current_frame = st.sidebar.slider(
    label="フレームを選択してください", min_value=1, max_value=20, value=current_frame
)

# width = st.sidebar.slider("グラフの幅を選択", 300, 700, step=100, value=width)


# データを表示
if st.button("順位更新"):
    # 再読み込み
    utils.read_origin_score.clear()
    df, df_team, current_frame, df_conf = utils.read_origin_score()

if "ALL" in selected_elements:
    st.title("チーム順位表")

    st.dataframe(
        df_team[["順位", str(current_frame), "メンバー", "拠点"]].rename(
            columns={str(current_frame): "得点"}
        ),
        hide_index=True,
    )
    st.write("※人数の少ないチームの得点は、多いチームと合うように補正しています。")

    if "width_team" not in st.session_state:
        st.session_state["width_team"] = 700
    fig_team = go.Figure()

    for index, row in df_team.iterrows():
        color_index = index % len(colors)
        fig_team.add_trace(
            go.Scatter(
                x=list(range(1, current_frame + 1)),
                y=row[3 : 3 + current_frame],
                mode="lines+markers",
                name=row["メンバー"],
                marker=dict(color=colors[color_index]),
            )
        )

    fig_team.update_layout(
        xaxis_title="フレーム",
        yaxis_title="スコア",
        legend_title="メンバー",
        xaxis=dict(tickmode="linear"),
        yaxis=dict(rangemode="tozero"),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            x=0.5,
            y=1,
            xanchor="center",
            yanchor="bottom",
        ),
        dragmode="pan",
        # width=width,
    )

    st.plotly_chart(fig_team)


else:
    st.write("個人が選択されているため、チーム順位表は表示していません")

st.title("個人順位表")

st.dataframe(
    df[["順位", str(current_frame), "名前", "拠点", "チーム"]].rename(
        columns={str(current_frame): "得点"}
    ),
    hide_index=True,
)

fig = go.Figure()

for index, row in df.iterrows():
    color_index = index % len(colors)
    fig.add_trace(
        go.Scatter(
            x=list(range(1, current_frame + 1)),
            y=row[45 : 45 + current_frame],
            mode="lines+markers",
            name=row["名前"],
            marker=dict(color=colors[color_index]),
        )
    )

fig.update_layout(
    xaxis_title="フレーム",
    yaxis_title="スコア",
    legend_title="名前",
    xaxis=dict(tickmode="linear"),
    yaxis=dict(rangemode="tozero"),
    hovermode="x unified",
    legend=dict(
        orientation="h",
        x=0.5,
        y=1,
        xanchor="center",
        yanchor="bottom",
    ),
    dragmode="pan",
    # width=width,
)

st.plotly_chart(fig)


# st.session_state["width_tmp"] = width
