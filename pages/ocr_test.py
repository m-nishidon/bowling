import pytesseract
import streamlit as st
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
st.title("画像認識のテスト")

# 画像アップロード
uploaded_file = st.file_uploader(
    "スコア表の写真をアップロードしてください", type=["jpg", "png", "jpeg"]
)

if uploaded_file is not None:
    # 画像を表示
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # OCR処理
    st.write("Extracted Text:")
    text = pytesseract.image_to_string(image, lang="jpn")
    st.text(text)
