import streamlit as st
from PIL import Image, ImageEnhance
import numpy as np
import cv2
import io
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

# 撮影されたフレームを保存する変数
captured_frame = None

# フレームを処理するクラス
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

# Streamlitアプリの構築
st.title("写真撮影＆加工ツール")

# 写真の撮影またはアップロード
st.header("写真をアップロードまたは撮影してください")

tab1, tab2 = st.tabs(["📤 写真をアップロード", "📷 カメラで撮影"])

# アップロードタブ
with tab1:
    uploaded_file = st.file_uploader("写真を選択してください", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)

# 撮影タブ
with tab2:
    st.write("カメラを使用して写真を撮影")
    webrtc_streamer(key="camera", video_transformer_factory=VideoTransformer)
    if st.button("📸 撮影する"):
        if captured_frame is not None:
            image = Image.fromarray(cv2.cvtColor(captured_frame, cv2.COLOR_BGR2RGB))
        else:
            st.warning("カメラの映像がキャプチャできませんでした")

# 加工とダウンロード
if 'image' in locals():
    st.header("加工オプション")
    options = ["無加工", "逆光補正", "シャープ強め", "グレースケール"]
    processed_images = {}

    for option in options:
        st.subheader(option)
        processed_image = process_image(image, option)
        processed_images[option] = processed_image
        st.image(processed_image, caption=option, use_column_width=True)

        # ダウンロードボタン
        buf = io.BytesIO()
        processed_image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        st.download_button(
            label=f"{option}をダウンロード",
            data=byte_im,
            file_name=f"{option}.png",
            mime="image/png",
        )
else:
    st.info("写真をアップロードまたは撮影してください")
