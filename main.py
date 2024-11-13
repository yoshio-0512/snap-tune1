import streamlit as st
from PIL import Image
import cv2
import numpy as np
import io
import base64

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

# JavaScriptでカメラを起動して写真を撮影
def webcam_photo_widget():
    photo_widget_code = """
    <div>
        <video id="video" width="100%" autoplay></video>
        <button id="snap" style="margin-top: 10px;">撮影</button>
        <canvas id="canvas" style="display: none;"></canvas>
        <script>
            const video = document.getElementById('video');
            const canvas = document.getElementById('canvas');
            const snap = document.getElementById('snap');
            const context = canvas.getContext('2d');
            navigator.mediaDevices.getUserMedia({ video: true })
                .then((stream) => {
                    video.srcObject = stream;
                });

            snap.addEventListener('click', () => {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                context.drawImage(video, 0, 0, canvas.width, canvas.height);
                const dataURL = canvas.toDataURL('image/png');
                fetch("/save_photo", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ image: dataURL })
                });
            });
        </script>
    </div>
    """
    return photo_widget_code

# アップロードまたは撮影された画像を取得する
st.title("写真撮影＆加工ツール")

uploaded_image = None

# アップロードセクション
st.header("写真をアップロードする")
uploaded_file = st.file_uploader("写真を選択してください", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    uploaded_image = Image.open(uploaded_file)
    st.image(uploaded_image, caption="アップロードされた写真", use_column_width=True)

# カメラセクション
st.header("カメラを使用して写真を撮影")
photo_widget_html = webcam_photo_widget()
st.components.v1.html(photo_widget_html, height=350)

# 画像加工とダウンロード
if uploaded_image is not None:
    st.header("加工オプション")
    options = ["無加工", "逆光補正", "シャープ強め", "グレースケール"]

    for option in options:
        st.subheader(option)
        processed_image = process_image(uploaded_image, option)
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
    st.info("写真をアップロードするか、撮影してください")
