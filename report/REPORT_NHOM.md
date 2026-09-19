# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy định & Dịch vụ Thư viện Đại học VinUniversity (VinUniversity Library Policies & Services)

**Tại sao nhóm chọn chủ đề này?**
> Thư viện VinUniversity là trung tâm học liệu hiện đại với hệ thống quy định được chuẩn hóa theo chuẩn quốc tế (Cornell/UPenn), phục vụ đa dạng nhóm độc giả trong khuôn viên trường. Điểm đặc sắc nhất của chủ đề này là sự phân cấp đặc quyền mượn tài liệu cực kỳ rõ rệt giữa các nhóm đối tượng (Sinh viên đại học mượn tối đa 3 cuốn/2 tuần, Học viên cao học mượn 5 cuốn/1 tháng, trong khi Giảng viên được mượn 5 cuốn/lên đến 6 tháng). Sự phân định rõ rệt này là kịch bản hoàn hảo nhất để kiểm chứng vai trò của siêu dữ liệu (`metadata_filter={"audience": "student"}`) trong việc ngăn chặn lẫn lộn thông tin giữa các nhóm độc giả.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | vinuni-lib-undergraduate.md | https://library.vinuni.edu.vn/services/borrow-and-request/undergraduate-and-staff/ | 2026-09-19 / 2026.1 | 1799 | audience: student, department: library, category: circulation |
| 2 | vinuni-lib-faculty.md | https://library.vinuni.edu.vn/services/borrow-and-request/graduate-faculty-and-instructors/ | 2026-09-19 / 2026.1 | 1578 | audience: faculty, department: library, category: circulation |
| 3 | vinuni-lib-graduate.md | https://library.vinuni.edu.vn/borrowing-priviledge/ | 2026-09-19 / 2026.1 | 1488 | audience: student, department: library, category: circulation |
| 4 | vinuni-lib-staff.md | https://library.vinuni.edu.vn/services/borrow-and-request/undergraduate-and-staff/ | 2026-09-19 / 2026.1 | 1502 | audience: staff, department: library, category: circulation |
| 5 | vinuni-lib-equipment.md | https://library.vinuni.edu.vn/services/equipment-loan/ | 2026-09-19 / 2026.1 | 1749 | audience: all, department: library, category: equipment |
| 6 | vinuni-lib-study-rooms.md | https://library.vinuni.edu.vn/room-booking/ | 2026-09-19 / 2026.1 | 1997 | audience: student, department: library, category: facilities |
| 7 | vinuni-lib-fines-reserves.md | https://library.vinuni.edu.vn/fine-and-other-charges/ | 2026-09-19 / 2026.1 | 1878 | audience: all, department: library, category: fines |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | str | `vinuni-lib-undergraduate` | Định danh duy nhất cho từng tài liệu thư viện, phục vụ truy vết xuất xứ và lệnh xóa (`delete_document`). |
| `title` | str | `Chính sách mượn trả tài liệu cho sinh viên...` | Tiêu đề văn bản giúp người dùng nhận biết ngay quy định tương ứng khi agent phản hồi. |
| `audience` | str | `student`, `faculty`, `staff`, `all` | **Trường cốt lõi để lọc trước (pre-filtering)**: giúp phân biệt hạn mức mượn giữa sinh viên (2 tuần) vs giảng viên (6 tháng) vs nhân viên. |
| `department` | str | `library` | Xác định đơn vị quản lý nghiệp vụ, phục vụ mở rộng hệ thống RAG đa phòng ban trong toàn trường. |
| `category` | str | `circulation`, `equipment`, `facilities`, `fines` | Khoanh vùng danh mục dịch vụ thư viện (lưu thông tài liệu, thiết bị, phòng học nhóm, xử lý phạt). |
| `source_url` | str | `https://library.vinuni.edu.vn/...` | Link tham chiếu chính thức trên trang thư viện VinUni để kiểm chứng tính xác thực (Grounding). |
| `retrieved_at` | str | `2026-09-19` | Quản lý thời điểm lấy dữ liệu, đảm bảo tài liệu phản ánh đúng quy định thư viện mới nhất. |
| `document_version` | str | `2026.1` | Quản lý phiên bản quy chế áp dụng cho năm học hiện hành. |
| `language` | str | `vi` | Định danh ngôn ngữ để hỗ trợ tiền xử lý và nhúng vector đa ngữ. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:*

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
