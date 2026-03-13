import os
import torch
import numpy as np
from google.colab import drive
from datasets import load_from_disk
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
)

# 1. Kết nối Drive
drive.mount('/content/drive')

# 2. Cấu hình đường dẫn
base_path = "/content/drive/MyDrive/Colab Notebooks/DA2-v3"
processed_path = os.path.join(base_path, "split_data")
checkpoint_path = os.path.join(base_path, "checkpoints")

# 3. Khởi tạo Model và Tokenizer ViT5-base
model_checkpoint = "VietAI/vit5-base"
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint)

# 4. Load dữ liệu đã chia (182k Train / 15k Valid)
train_ds = load_from_disk(os.path.join(processed_path, "train"))
val_ds = load_from_disk(os.path.join(processed_path, "valid"))

# 5. Hàm tiền xử lý (Giữ lại để tạo 'labels' phục vụ tính Loss)
def preprocess_function(examples):
    inputs = ["correction: " + doc for doc in examples["input"]]
    # Mã hóa văn bản đầu vào
    model_inputs = tokenizer(inputs, max_length=128, truncation=True, padding="max_length")
    # Mã hóa nhãn (văn bản chuẩn) - cực kỳ quan trọng cho Seq2Seq
    labels = tokenizer(text_target=examples["corrected_text"], max_length=128, truncation=True, padding="max_length")
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs
print("Đang mã hóa lại dữ liệu với đầy đủ nhãn (labels)...")
tokenized_train = train_ds.map(preprocess_function, batched=True, remove_columns=train_ds.column_names)
tokenized_val = val_ds.map(preprocess_function, batched=True, remove_columns=val_ds.column_names)

# 6. Thiết lập tham số huấn luyện (Chỉ theo dõi Loss)
training_args = Seq2SeqTrainingArguments(
    output_dir=checkpoint_path,
    eval_strategy="epoch",            # Đánh giá Loss sau mỗi epoch (tạo 3 điểm dữ liệu)
    save_strategy="epoch",            # Lưu checkpoint mỗi epoch
    learning_rate=5e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    gradient_accumulation_steps=2,    # Batch size hiệu dụng = 16
    weight_decay=0.01,
    save_total_limit=3,               # Giữ đủ 3 checkpoint cho 3 Epoch
    num_train_epochs=3,
    predict_with_generate=False,
    fp16=True,                        # Tối ưu cho GPU T4
    lr_scheduler_type="cosine",
    warmup_ratio=0.1,                 # Warmup 10% đầu để tránh sốc dữ liệu lớn
    label_smoothing_factor=0.1,
    load_best_model_at_end=False,
    greater_is_better=False,          # Loss càng thấp càng tốt
    logging_steps=500,                # Ghi log Training Loss mỗi 500 steps
    report_to="none"
)

# 7. Khởi tạo Trainer (Không có compute_metrics)
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_val,
    tokenizer=tokenizer,
    data_collator=DataCollatorForSeq2Seq(tokenizer, model=model),
)

# 8. Chạy huấn luyện (Hỗ trợ Resume từ checkpoint nếu hết GPU giữa chừng)
print("Bắt đầu Giai đoạn 1: Huấn luyện 3 Epoch (Chỉ tính Loss)...")
trainer.train(resume_from_checkpoint=False)

# 9. Lưu mô hình cuối cùng
trainer.save_model(os.path.join(base_path, "final_model_loss_only"))
print("Hoàn tất Giai đoạn 1! Checkpoint đã sẵn sàng để tính ROUGE sau.")