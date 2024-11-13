import streamlit as st
import cv2
from PIL import Image, ImageEnhance
import numpy as np
import io

# 画像を加工する関数
def process_image(image, mode):
    img_array = np.array(image)

    if mode == "無加工":
        return image
    elif mode == "逆光補正":
        # ヒストグラム均等化で逆光補正を行う
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        l_eq = cv2.equalizeHist(l)
        lab_eq = cv2.merge((l_eq, a, b))
        img_result = cv2.cvtColor(lab_eq, cv2.COLOR_LAB2RGB)
        return Image.fromarray(img_result)
    elif mode == "シャープ強め":
        # シャープ化フィルターを適用
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharp_img = cv2.filter2D(img_array, -1, kernel)
        return Image.fromarray(sharp_img)
    elif mode == "グレースケール":
        # グレースケールに変換
        gray_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        return Image.fromarray(gray_img)

# Streamlitアプリの設定
st.title("写真撮影＆加工ツール")

# 写真のアップロード
uploaded_file = st.file_uploader("写真をアップロードしてください", type=["jpg", "png", "jpeg"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロードされた写真", use_column_width=True)

    # 加工オプションを表示
    st.header("加工オプション")
    options = ["無加工", "逆光補正", "シャープ強め", "グレースケール"]
    processed_images = {}

    for option in options:
        st.subheader(option)
        processed_image = process_image(image, option)
        processed_images[option] = processed_image
        st.image(processed_image, caption=option, use_column_width=True)
        # ダウンロードボタンを設置
        buf = io.BytesIO()
        processed_image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        st.download_button(
            label=f"{option}をダウンロード",
            data=byte_im,
            file_name=f"{option}.png",
            mime="image/png"
        )
