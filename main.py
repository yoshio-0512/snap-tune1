import streamlit as st
from PIL import Image
import io
import base64
import numpy as np
import cv2

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

# JavaScriptでカメラを操作する関数
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
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'image_data';
                input.value = dataURL;
                document.body.appendChild(input);
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '';
                form.appendChild(input);
                document.body.appendChild(form);
                form.submit();
            });
        </script>
    </div>
    """
    return photo_widget_code

# Streamlitアプリ
st.title("写真撮影＆加工ツール")

uploaded_image = None

# アップロードセクション
st.header("写真をアップロードする")
uploaded_file = st.file_uploader("写真を選択してください", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    uploaded_image = Image.open(uploaded_file)
    st.image(uploaded_image, caption="アップロードされた写真", use_column_width=True)

# カメラセクション
st.header("カメラで写真を撮影")
photo_widget_html = webcam_photo_widget()
st.components.v1.html(photo_widget_html, height=350)

# 撮影データの取得
if "image_data" in st.session_state:
    image_data = st.session_state["image_data"]
    image_data = image_data.split(",")[1]
    decoded_data = base64.b64decode(image_data)
    uploaded_image = Image.open(io.BytesIO(decoded_data))
    st.image(uploaded_image, caption="撮影した写真", use_column_width=True)

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
    st.info("写真をアップロードするか、カメラで撮影してください")
