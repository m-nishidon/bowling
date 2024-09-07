# %%
import pytesseract
import streamlit as st
from PIL import Image

import utils

utils.clear_ss_score_update()

st.title("画像認識とかのテスト")


st.subheader("カメラテスト")
st.write("撮った写真からOCRするテスト")
picture = st.camera_input("写真を撮ってアップロードできます")
st.write("OCRの精度が微妙なので諦め")

if picture:
    st.image(picture)
    text = pytesseract.image_to_string(picture, lang="jpn")
    st.text(text)

st.subheader("写真テスト")
st.write("アップロードした画像からOCRするテスト")

# 画像アップロード
uploaded_file = st.file_uploader(
    "スコア表の写真をアップロードしてください", type=["jpg", "png", "jpeg"]
)

if uploaded_file:
    # 画像を表示
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # OCR処理
    st.write("Extracted Text:")
    text = pytesseract.image_to_string(image, lang="jpn")
    st.text(text)

st.subheader("連絡用等のチャットのテスト")
st.write("LINEにメッセージを飛ばせます")

name = st.text_input("名前を入力してください。(匿名可)")
message = st.text_area("メッセージを入力してください。")

if st.button("送信"):
    if not message:
        st.error("メッセージが入力されていません。")
    else:
        message = "\n".join(["名前", str(name), message])
        token = st.secrets["LINE"]["token"]
        if not name:
            utils.send_message(message, token)
            st.warning("匿名でメッセージを送信しました。")
        else:
            utils.send_message(message, token)
            st.success("メッセージを送信しました。")
