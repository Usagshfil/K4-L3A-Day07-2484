import os
from dotenv import load_dotenv
from src.chunking import compute_similarity
from src.embeddings import GeminiEmbedder

load_dotenv()
embedder = GeminiEmbedder()

pairs = [
    (
        "Sinh viên đại học được phép mượn tối đa 3 tài liệu trong thời hạn 14 ngày.",
        "Hạn mức mượn sách cho người học bậc cử nhân là ba cuốn với thời gian hai tuần.",
        "cao",
    ),
    (
        "Độc giả làm mất sách phải bồi thường toàn bộ chi phí mua mới kèm theo 100.000 VNĐ phí hành chính.",
        "Trường hợp đánh mất tài liệu thư viện, người mượn phải đền tiền mua sách mới và nộp thêm khoản phụ phí xử lý một trăm nghìn đồng.",
        "cao",
    ),
    (
        "Sinh viên đại học được phép mượn tối đa 3 tài liệu trong thời hạn 14 ngày.",
        "Hệ thống phòng tự học được trang bị máy điều hòa không khí và kết nối internet không dây tốc độ cao.",
        "thấp",
    ),
    (
        "Độc giả không được mang thức ăn có mùi và đồ uống không có nắp vào thư viện.",
        "Bạn đọc phải giữ trật tự chung và không gây ồn ào tại khu vực học tập yên tĩnh.",
        "trung bình / thấp",
    ),
    (
        "Tài liệu dự trữ môn học chỉ được sử dụng tại chỗ tối đa trong 2 giờ.",
        "Giảng viên được mượn tài liệu nghiên cứu về nhà với thời hạn lên tới 6 tháng.",
        "thấp",
    ),
]

print("=== ĐO LƯỜNG 5 CẶP CÂU TƯƠNG ĐỒNG BẰNG GEMINI EMBEDDER ===")
for i, (a, b, pred) in enumerate(pairs, 1):
    va = embedder(a)
    vb = embedder(b)
    sim = compute_similarity(va, vb)
    print(f"Cặp {i}: score = {sim:.4f} | Dự đoán: {pred}")
    print(f"  A: {a}")
    print(f"  B: {b}\n")

