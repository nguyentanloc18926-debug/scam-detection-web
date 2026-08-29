import re
from underthesea import word_tokenize


def clean_text(text):
    if not isinstance(text, str):
        return ""

    # 1. Chuyển thành chữ thường
    text = text.lower()

    # 2. Xóa các đường link URL và email
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\S+@\S+", "", text)

    # 3. Xóa các ký tự đặc biệt, icon emoji, giữ lại chữ cái Tiếng Việt
    text = re.sub(
        r"[^\w\sàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệđìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ]",
        " ",
        text,
    )

    # 4. Xóa khoảng trắng thừa
    text = re.sub(r"\s+", " ", text).strip()

    # 5. Tách từ tiếng Việt (VD: "lừa đảo" -> "lừa_đảo")
    text = word_tokenize(text, format="text")

    return text