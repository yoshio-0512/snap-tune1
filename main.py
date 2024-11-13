import streamlit as st
from PIL import Image
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import io

# 撮影されたフレームを保存する変数
captured_frame = None

# カメラ映像をキャプチャするクラス
class VideoTransformer(VideoTransformerBase):
    def transform(self, frame):
        global captured_frame
        captured_frame = frame.to_ndarray(format="bgr24")
        return captured_frame

# 画像加工関数
def process_image(image, mode):
    img_array = np.array(image)

    if mode == "無加工":
        return image
    elif mode == "逆光補正":
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        l_eq = cv2.equalizeHist(l)
        lab_eq = cv2.merge((l_eq, a, b))
        img_result = cv2.cvtColor(lab_eq, cv2.COLOR_LAB2RGB)
        return Image.fromarray(img_result)
    elif mode == "シャープ強め":
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharp_img = cv2.filter2D(img_array, -1, kernel)
        return Image.fromarray(sharp_img)
    elif mode == "グレースケール":
        gray_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        return Image.fromarray(gray_img)

# ダウンロードリンク生成
def generate_download_button(processed_image, label):
    buf = io.BytesIO()
    processed_image.save(buf, format="PNG")
    byte_im = buf.getvalue()
    st.download_button(
        label=f"{label}をダウンロード",
        data=byte_im,
        file_name=f"{label}.png",
        mime="image/png",
    )

# Streamlitアプリ
st.set_page_config(page_title="写真編集ツール", layout="wide")

st.title("写真撮影＆加工ツール")

# タブで操作を切り替え
tab1, tab2 = st.tabs(["写真をアップロード", "カメラで撮影"])

uploaded_image = None

# アップロードタブ
with tab1:
    uploaded_file = st.file_uploader("写真をアップロードしてください", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        uploaded_image = Image.open(uploaded_file)
        st.image(uploaded_image, caption="アップロードされた写真", use_column_width=True)

# カメラタブ
with tab2:
    webrtc_streamer(key="camera", video_transformer_factory=VideoTransformer)
    if st.button("撮影する"):
        if captured_frame is not None:
            captured_image = Image.fromarray(cv2.cvtColor(captured_frame, cv2.COLOR_BGR2RGB))
            uploaded_image = captured_image
            st.image(uploaded_image, caption="撮影した写真", use_column_width=True)
        else:
            st.warning("カメラから映像が取得できませんでした")

# 画像加工とダウンロード
if uploaded_image is not None:
    st.header("加工オプション")
    options = ["無加工", "逆光補正", "シャープ強め", "グレースケール"]

    col1, col2 = st.columns(2)
    for index, option in enumerate(options):
        with col1 if index % 2 == 0 else col2:
            processed_image = process_image(uploaded_image, option)
            st.image(processed_image, caption=option, use_column_width=True)
            generate_download_button(processed_image, option)
else:
    st.info("写真をアップロードするか、カメラで撮影してください")
