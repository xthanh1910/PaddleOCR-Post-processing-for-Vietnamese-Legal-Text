import streamlit as st
import os
import torch
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="OCR & Tiếng Việt Correction", layout="wide")

# --- ĐƯỜNG DẪN MODEL ---
PROJECT_PATH = r"D:\2_BK\NAM_4\HK1\DA2-v2"
MODEL_DIR = os.path.join(PROJECT_PATH, "checkpoint-34125")
MODEL_PREFIX = "correction:  "

# --- CSS TÙY CHỈNH ---
st.markdown("""
    <style>
    .centered-image {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
    }
    .stTextArea textarea {
        font-size: 15px;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    .result-header {
        text-align: center;
        color: #1f77b4;
        font-size: 24px;
        font-weight: bold;
        margin: 2rem 0 1rem 0;
    }
    /* Nút màu xanh lá */
    .stButton > button[kind="primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #218838 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- HÀM CACHE ĐỂ TỐI ƯU TỐC ĐỘ (Chỉ load 1 lần) ---
@st.cache_resource
def load_models():
    ocr = PaddleOCR(use_angle_cls=True, lang='vi', show_log=False)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, use_fast=False)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_DIR) 
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.eval() 
    return ocr, model, tokenizer

# --- HÀM XỬ LÝ CHÍNH ---
def process_correction(raw_text, model, tokenizer):
    if not raw_text.strip():
        return ""
    input_text = MODEL_PREFIX + raw_text
    device = model.device
    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512
    ).to(device)
    with torch.no_grad():
        outputs = model.generate(
            inputs["input_ids"],
            max_length=512,
            num_beams=5,
            early_stopping=True
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# --- GIAO DIỆN CHÍNH ---
def main():
    st.title("Hệ thống hậu xử lý OCR văn bản pháp luật")
    st.markdown("---")
    # Sidebar thông tin
    st.sidebar.header("Cấu hình hệ thống")
    st.sidebar.info(
        f"Model: ViT5-Base\nCheckpoint: 34125\nThiết bị: {'GPU' if torch.cuda.is_available() else 'CPU'}"
    )
    # Nạp model
    with st.spinner("Đang khởi tạo model AI..."):
        ocr, model, tokenizer = load_models()
    # Tải ảnh lên
    uploaded_file = st.file_uploader(
        "Chọn ảnh văn bản cần quét OCR (JPG, PNG, JPEG)...",
        type=["jpg", "png", "jpeg"]
    )
    if uploaded_file is not None:
        image = Image.open(uploaded_file)      
        st.markdown("<h3 style='text-align: center;'>Ảnh văn bản cần quét OCR</h3>", unsafe_allow_html=True)
        col_left, col_center, col_right = st.columns([0.5, 3, 0.5])
        with col_center:
            st.image(image, use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        col_btn_left, col_btn_center, col_btn_right = st.columns([1.5, 1, 1.5])
        with col_btn_center:
            process_button = st.button(
                "Bắt đầu quét OCR và sửa lỗi",
                use_container_width=True,
                type="primary"
            )
        if process_button:
            img_array = np.array(image.convert('RGB'))
            with st.status("Đang thực hiện...", expanded=True) as status:
                st.write("Đang nhận diện văn bản bằng PaddleOCR ...")
                result = ocr.ocr(img_array, cls=True)
                if not result or result[0] is None:
                    st.error("Không tìm thấy chữ trong ảnh!")
                    return
                raw_lines = [line[1][0] for line in result[0]]
                raw_text = " ".join(raw_lines)
                st.write("Đang sửa lỗi của PaddleOCR ...")
                final_output = process_correction(raw_text, model, tokenizer)
                status.update(
                    label="Xử lý hoàn tất!",
                    state="complete",
                    expanded=False
                )
            st.markdown("<br>", unsafe_allow_html=True)
            col_ocr, col_corrected = st.columns(2)
            with col_ocr:
                st.markdown("### Văn bản từ PaddleOCR (gốc)")
                st.text_area(
                    label="Kết quả từ PaddleOCR",
                    value=raw_text,
                    height=300,
                    key="raw_output",
                    label_visibility="collapsed"
                )
                st.caption(f"Độ dài: {len(raw_text)} ký tự")
            with col_corrected:
                st.markdown("### Văn bản đã sửa lỗi")
                st.text_area(
                    label="Kết quả sau khi sửa",
                    value=final_output,
                    height=300,
                    key="corrected_output",
                    label_visibility="collapsed"
                )
                st.caption(f"Độ dài: {len(final_output)} ký tự")
            st.markdown("---")
            col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 1])
            with col_dl2:
                st.download_button(
                    label="Tải kết quả đã sửa về máy (.txt)",
                    data=final_output,
                    file_name="corrected_text.txt",
                    mime="text/plain",
                    use_container_width=True
                )
    else:
        st.info("Vui lòng tải lên một ảnh chứa văn bản tiếng Việt để bắt đầu")
        st.markdown("### Hướng dẫn sử dụng:")
        st.markdown("""
        1. Upload ảnh: Chọn file ảnh (JPG/PNG) chứa văn bản cần xử lý
        2. Xem ảnh: Ảnh hiển thị ở giữa màn hình
        3. Nhấn nút xử lý: Hệ thống sẽ OCR và sửa lỗi tự động
        4. Xem kết quả:
           - Bên trái: Văn bản OCR
           - Bên phải: Văn bản đã sửa lỗi
        5. Tải xuống: Lưu kết quả về máy dưới dạng file .txt
        """)

if __name__ == "__main__":
    main()