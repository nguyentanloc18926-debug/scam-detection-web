import joblib
import pandas as pd
from preprocessing import clean_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

# 1. Đọc dữ liệu
df = pd.read_csv("DATASET_TONG_HOP.csv")
text_col = "text" if "text" in df.columns else df.columns[0]
label_col = "label" if "label" in df.columns else df.columns[1]

# 2. Tiền xử lý
df["clean_text"] = df[text_col].astype(str).apply(clean_text)

# 3. Chia tập dữ liệu
X_train, X_test, y_train, y_test = train_test_split(
    df["clean_text"],
    df[label_col],
    test_size=0.2,
    random_state=42,
    stratify=df[label_col],
)

# 4. TF-IDF Vectorization
vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=3000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# 5. So sánh 2 Mô hình Machine Learning
# Mô hình 1: Logistic Regression
model_lr = LogisticRegression(class_weight="balanced")
model_lr.fit(X_train_vec, y_train)
pred_lr = model_lr.predict(X_test_vec)
acc_lr = accuracy_score(y_test, pred_lr)

# Mô hình 2: Naive Bayes
model_nb = MultinomialNB()
model_nb.fit(X_train_vec, y_train)
pred_nb = model_nb.predict(X_test_vec)
acc_nb = accuracy_score(y_test, pred_nb)

print("=== BẢNG SO SÁNH HIỆU NĂNG MÔ HÌNH ===")
print(f"1. Logistic Regression Accuracy: {acc_lr*100:.2f}%")
print(f"2. Naive Bayes Accuracy:        {acc_nb*100:.2f}%")

# Chọn mô hình Logistic Regression làm mô hình chính
joblib.dump(model_lr, "scam_model.pkl")
joblib.dump(vectorizer, "tfidf_vectorizer.pkl")
print("\n✅ Đã lưu mô hình tốt nhất vào scam_model.pkl!")