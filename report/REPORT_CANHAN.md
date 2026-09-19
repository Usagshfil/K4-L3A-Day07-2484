# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Thọ Đạt
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:*
> Hai vector embedding có góc định hướng gần như trùng khít trong không gian vector đa chiều ($\theta \approx 0^\circ \implies \cos \theta \approx 1.0$). Điều này phản ánh hai đoạn văn bản có sự đồng nhất rất cao về mặt ngữ nghĩa và nội dung tư tưởng, bất kể chúng có độ dài khác nhau hay sử dụng bộ từ vựng khác nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A:
- Câu B:
- Tại sao tương đồng:
- Câu A: Sinh viên được phép mượn tối đa 3 tài liệu trong thời hạn 14 ngày.
- Câu B: Hạn mức mượn sách cho người học bậc đại học là ba cuốn với thời gian hai tuần.
- Tại sao tương đồng: Dù hai câu sử dụng bộ từ vựng hoàn toàn khác biệt ("sinh viên" vs "người học bậc đại học", "3 tài liệu" vs "ba cuốn", "14 ngày" vs "hai tuần"), chúng cùng truyền tải một quy định học vụ cụ thể. Mô hình embedding nắm bắt được ngữ nghĩa sâu xa thay vì so khớp ký tự nông rỗng.

**Ví dụ có độ tương tự THẤP:**
- Câu A:
- Câu B:
- Tại sao khác:
- Câu A: Sinh viên được phép mượn tối đa 3 tài liệu trong thời hạn 14 ngày.
- Câu B: Khu vực tự học của thư viện trang bị hệ thống máy điều hòa không khí và đèn chiếu sáng đạt tiêu chuẩn.
- Tại sao khác: Mặc dù cả hai câu đều xuất hiện trong bối cảnh thư viện trường đại học, Câu A là điều khoản pháp lý về lưu thông tài liệu mượn trả, còn Câu B mô tả cơ sở hạ tầng vật chất của không gian học tập.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:*
> Khoảng cách Euclid phụ thuộc trực tiếp vào độ lớn (magnitude) của vector — vốn tỉ lệ thuận với độ dài văn bản hoặc tần suất xuất hiện của từ ngữ. Trong khi đó, Cosine similarity chuẩn hóa độ dài vector ($\frac{\vec{a} \cdot \vec{b}}{\|\vec{a}\| \|\vec{b}\|}$) và chỉ đo góc lệch giữa hai hướng, cho phép so sánh sự tương đồng ngữ nghĩa một cách khách quan và công bằng giữa các văn bản có độ dài ngắn khác nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> *Đáp án:*
> Bước dịch chuyển (step) giữa hai chunk liên tiếp là: $step = chunk\_size - overlap = 500 - 50 = 450$ ký tự.
> Điểm bắt đầu của các chunk lần lượt là $0, 450, 900, \dots, 9450, 9900$.
> Áp dụng công thức: $\text{Số chunks} = 1 + \lceil \frac{\text{độ\_dài} - chunk\_size}{step} \rceil = 1 + \lceil \frac{10000 - 500}{450} \rceil = 1 + \lceil 21.11 \rceil = 1 + 22 = 23$.
> (Kiểm chứng bằng code `FixedSizeChunker(500, 50).chunk('a'*10000)` thu được kết quả chính xác 23 chunks).
> *Đáp án:* **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:*
> Khi overlap tăng lên 100, bước dịch chuyển giảm còn $step = 500 - 100 = 400$, số chunk tăng lên thành $1 + \lceil \frac{9500}{400} \rceil = 1 + 24 = 25$ chunks (tăng thêm 2 chunks). Chúng ta muốn độ chồng chéo lớn hơn để bảo toàn tính liền mạch của ngữ cảnh, ngăn chặn hiện tượng một câu văn quan trọng, một con số hoặc một mệnh đề quy định bị cắt đôi giữa hai chunk ranh giới, giúp retrieval tìm kiếm ngữ cảnh đầy đủ hơn cho LLM.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?*
> Sử dụng biểu thức chính quy với positive lookbehind `r'(?<=[.!?])\s+'` để tách sau dấu kết thúc câu (`.`, `!`, `?`, `\n`) mà vẫn bảo tồn nguyên vẹn dấu câu trong văn bản. Gom các câu theo nhóm kích thước `max_sentences_per_chunk` và loại bỏ khoảng trắng thừa bằng `.strip()`. Đã xử lý các edge cases như chuỗi rỗng/chỉ chứa khoảng trắng (trả về `[]`) và câu không kết thúc bằng dấu chấm; đồng thời ghi nhận hạn chế của regex với các từ viết tắt (`TS.`, `v.v.`) hoặc số thập phân (`3.14`).

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?*
> Triển khai thuật toán hai chiều: (1) Đệ quy xuống sâu theo danh sách phân tách ưu tiên `["\n\n", "\n", ". ", " ", ""]`, chỉ hạ tầng khi mảnh văn bản vượt quá `chunk_size`; (2) Gom mảnh liền kề (merging) bằng `_merge_splits` để nối các mẩu nhỏ lại sát ngưỡng `chunk_size`, chống sinh ra các chunk vụn. Base case gồm: chuỗi rỗng trả về `[]`, độ dài $\le chunk\_size$ giữ nguyên, và khi cạn danh sách phân tách (`not remaining_separators`) thì cắt lát cứng theo `chunk_size` để chống treo đệ quy và hỗ trợ trường hợp `separators=[]`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?*

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?*

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?*

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
# Dán kết quả (output) của: pytest tests/ -v
```

**Số lượng bài test vượt qua (pass):** __ / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | cao / thấp | | |
| 2 | | | cao / thấp | | |
| 3 | | | cao / thấp | | |
| 4 | | | cao / thấp | | |
| 5 | | | cao / thấp | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:*

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
