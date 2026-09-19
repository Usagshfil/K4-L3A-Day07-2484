# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** K4-L3A-Day07-2484
**Thành viên:** Nguyễn Thọ Đạt
**Ngày:** 19/09/2026

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

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu quy chế thực tế của Thư viện VinUni (đã bóc tách YAML frontmatter):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `vinuni-lib-undergraduate.md` | FixedSizeChunker (`fixed_size`) | 4 | 403.5 | Cắt cơ học theo độ dài cố định, có thể cắt ngang một câu điều khoản. |
| | SentenceChunker (`by_sentences`) | 7 | 206.0 | Tách đúng ranh giới câu, nhưng xé lẻ các điều kiện mượn thành nhiều mẩu rời rạc. |
| | RecursiveChunker (`recursive`) | 5 | 291.6 | Tách theo đoạn/câu và gộp mảnh, bảo toàn được cấu trúc ngữ nghĩa khá tốt. |
| `vinuni-lib-study-rooms.md` | FixedSizeChunker (`fixed_size`) | 4 | 463.5 | Các chunk có độ dài đều nhau nhưng ranh giới vô tình làm mất tiêu đề mục. |
| | SentenceChunker (`by_sentences`) | 7 | 239.4 | Bảo toàn trọn vẹn ngữ pháp từng câu, song thiếu sự kết nối giữa quy định đặt và hủy phòng. |
| | RecursiveChunker (`recursive`) | 5 | 339.6 | Gom các quy định liên quan về số người tối thiểu và thời hạn no-show vào chung chunk. |
| `vinuni-lib-fines-reserves.md` | FixedSizeChunker (`fixed_size`) | 4 | 429.0 | Có thể cắt ngang bảng biểu mức phạt và thời gian mượn tài liệu dự trữ. |
| | SentenceChunker (`by_sentences`) | 7 | 220.6 | Các mức phạt bằng tiền bị tách rời khỏi nhóm tài liệu tương ứng. |
| | RecursiveChunker (`recursive`) | 5 | 312.0 | Giữ biểu phí phạt và chế tài mất sách trong cùng một khối thông tin hoàn chỉnh. |

### Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Thọ Đạt**
- **Loại chiến lược:** FixedSizeChunker (`fixed_size`)
- **Mô tả & lý do chọn cho chủ đề này:** Phân đoạn văn bản thành các khối kích thước cố định `chunk_size=500` ký tự với độ gối đầu `overlap=50` ký tự. Đây là chiến lược baseline chuẩn mực với ưu điểm tốc độ xử lý nhanh, độ dài vector đầu ra đồng đều và thuật toán đơn giản. Điểm yếu là việc cắt lát cơ học dễ cắt ngang giữa một điều khoản hoặc con số quy định (ví dụ mức phí hoặc số ngày mượn).

**Thành viên 2 — Nguyễn Thọ Đạt**
- **Loại chiến lược:** SentenceChunker (`by_sentences`)
- **Mô tả & lý do chọn:** Phân đoạn theo ranh giới câu hoàn chỉnh bằng biểu thức chính quy `r'(?<=[.!?])\s+'`, gom tối đa 3 câu thành một chunk (`max_sentences_per_chunk=3`). Ưu điểm là không bao giờ cắt cụt từ ngữ hay đứt gãy cấu trúc ngữ pháp câu. Điểm yếu là độ dài các chunk dao động thất thường và các câu có quan hệ nhân quả/điều kiện nằm cạnh nhau có thể bị phân bổ vào các chunk khác nhau.

**Thành viên 3 — Nguyễn Thọ Đạt**
- **Loại chiến lược:** SectionChunker (Chiến lược tùy chỉnh phân đoạn theo Heading / Mục điều khoản)
- **Mô tả & lý do chọn:** Vì văn bản quy chế thư viện được biên soạn chặt chẽ theo cấu trúc `## Điều [X] — [Tên điều khoản]`, mỗi Điều khoản tự thân nó là một đơn vị thông tin độc lập và trọn vẹn. `SectionChunker` tách văn bản theo ranh giới tiêu đề cấp 2 (`##`). Nếu một điều khoản vượt quá ngưỡng 500 ký tự, thuật toán sẽ đệ quy chia nhỏ tiếp nhưng **luôn gắn kèm tiêu đề gốc vào đầu mỗi mảnh con** để đảm bảo không bao giờ bị mất ngữ cảnh gốc.
- **Code snippet:**
```python
class SectionChunker:
    def __init__(self, max_chunk_size: int = 500, heading_pattern: str = r"(?m)^(#{1,3}\s+.+)$") -> None:
        self.max_chunk_size = max_chunk_size
        self.heading_pattern = heading_pattern

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        parts = re.split(self.heading_pattern, text.strip())
        sections: list[tuple[str, str]] = []
        if parts[0].strip():
            sections.append(("", parts[0].strip()))
        for i in range(1, len(parts), 2):
            heading = parts[i].strip()
            body = parts[i + 1].strip() if i + 1 < len(parts) else ""
            sections.append((heading, body))

        chunks: list[str] = []
        rec = RecursiveChunker(chunk_size=self.max_chunk_size)
        for heading, body in sections:
            full = f"{heading}\n\n{body}".strip() if heading else body
            if len(full) <= self.max_chunk_size:
                chunks.append(full)
            else:
                sub_chunks = rec.chunk(body)
                for sub in sub_chunks:
                    chunks.append(f"{heading}\n\n{sub}".strip() if heading else sub)
        return chunks
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Thành viên 1 | FixedSizeChunker | 7 / 10 (70%) | Độ dài vector đồng đều, overlap 50 giúp gom đủ các vế số liệu ngắn | Ranh giới cắt cơ học, có thể cắt ngang một dòng điều khoản |
| Thành viên 2 | SentenceChunker | 5 / 10 (50%) | Bảo tồn trọn vẹn câu ngữ pháp, không bao giờ cụt từ | Chunk ngắn (3 câu), dễ xé lẻ các vế điều kiện ra nhiều chunk |
| Nguyễn Thọ Đạt | SectionChunker | 6 / 10 (60%) | 100% câu hỏi đạt Gold Doc tại Top-1; giữ nguyên cấu trúc Điều khoản | Giới hạn 500 ký tự khiến một số Điều dài bị sub-chunk |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *SectionChunker là chiến lược vượt trội nhất cho chủ đề văn bản quy chế đại học.* Bản chất của văn bản quy định hành chính là thông tin được phân cụm thành các Điều/Khoản độc lập do ban giám hiệu hoặc giám đốc thư viện ban hành. Việc bảo toàn ranh giới của từng Điều khoản kết hợp với việc tiền tố hóa (prefixing) tiêu đề vào mọi mẩu nhỏ con giúp bộ nhúng vector (embedding) hiểu rõ mục tiêu chính xác của đoạn văn, tối ưu hóa điểm số tương đồng cosine khi người dùng đặt câu hỏi tra cứu.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Hạn mức mượn sách tối đa và thời gian mượn thông thường là bao lâu? | Sinh viên được mượn tối đa 3 tài liệu trong 14 ngày (2 tuần), được gia hạn 1 lần thêm 14 ngày. *(Cần lọc `audience: student` để tránh lẫn hạn mức 6 tháng của giảng viên).* | `vinuni-lib-undergraduate#1` (Điều 2) |
| 2 | Thời hạn mượn các thiết bị công nghệ như laptop hoặc iPad là bao lâu và sau bao nhiêu ngày quá hạn thì thiết bị bị tính là làm mất? | Thiết bị được mượn trong ngày và phải trả trước giờ đóng cửa 15 phút; nếu quá hạn 5 ngày liên tiếp tính là làm mất và phải bồi thường. | `vinuni-lib-equipment#2` (Điều 3 & Điều 5) |
| 3 | Điều kiện số lượng người tối thiểu để sử dụng phòng học nhóm là bao nhiêu và sau bao lâu không đến nhận phòng thì lượt đặt phòng bị hủy? | Tối thiểu 2 người; vắng mặt sau 10 phút kể từ giờ bắt đầu thì lượt đặt phòng tự động bị hủy (no-show). | `vinuni-lib-study-rooms#1`, `#3` (Điều 2 & Điều 4) |
| 4 | Thời gian mượn tối đa và mức phí phạt quá hạn đối với tài liệu dự trữ môn học (Course Reserves) là bao nhiêu? | Mượn tại chỗ tối đa 2 giờ/lượt; phí phạt quá hạn là 10.000 VNĐ cho mỗi giờ trễ hạn. | `vinuni-lib-fines-reserves#1`, `#2` (Điều 2 & Điều 3) |
| 5 | Mức phí phạt mượn sách thông thường quá hạn mỗi ngày là bao nhiêu và làm mất sách thì phải đền bù thế nào? | Phí phạt trễ hạn sách thông thường là 10.000 VNĐ/ngày/cuốn; làm mất sách phải đền giá mua mới cộng 100.000 VNĐ phí hành chính. | `vinuni-lib-fines-reserves#2`, `#4` (Điều 3 & Điều 5) |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Hạn mức mượn sách tối đa... | FixedSizeChunker & SectionChunker | Có (Top-1) | Đưa `vinuni-lib-undergraduate` lên Top-1. Khi có filter `audience=student`, loại trừ 100% tài liệu của cán bộ/giảng viên. |
| 2 | Thời hạn mượn thiết bị công nghệ... | FixedSizeChunker | Có (Top-1) | `FixedSize` gom đủ cả 2 vế (trả trước 15 phút & quá hạn 5 ngày) vào cùng một chunk `equipment#2` (đạt 2/2 điểm tuyệt đối). |
| 3 | Điều kiện số lượng người phòng học nhóm... | SentenceChunker & SectionChunker | Có (Top-1) | `SentenceChunker` đưa câu quy định 2 người lên Top-1 (score 0.8321), `SectionChunker` đưa mục No-Show lên Top-1. |
| 4 | Thời gian mượn tối đa và phí Course Reserves... | SectionChunker | Có (Top-1) | `SectionChunker` đạt điểm tương đồng kỷ lục 0.8979 cho mục Điều 1 Course Reserves. |
| 5 | Phí phạt quá hạn sách và đền bù mất sách... | SectionChunker & FixedSize | Có (Top-1) | `SectionChunker` đưa Điều 2 biểu phí phạt lên Top-1 (score 0.8628). |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Lọc bằng metadata phát huy tác dụng cốt tử ở **Câu hỏi 1** ("Hạn mức mượn sách tối đa và thời gian mượn thông thường là bao lâu?").
> Khi KHÔNG dùng filter, cả 3 chiến lược đều bị tài liệu của Cán bộ nhân viên (`vinuni-lib-staff#1/#2` score 0.8029 – 0.8773) và Giảng viên (`vinuni-lib-faculty#1` score 0.7978) chiếm vị trí Top-1 hoặc Top-2 do câu hỏi không nêu rõ đối tượng người hỏi.
> Khi CÓ `metadata_filter={"audience": "student"}`, toàn bộ tài liệu ngoài đối tượng sinh viên bị loại bỏ ngay từ tầng lọc trước (pre-filtering), đưa `vinuni-lib-undergraduate` lên vững chắc ở Top-1 với điểm số 0.8201, giúp Agent trả lời chính xác 100% chính sách sinh viên.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. **Sự đánh đổi giữa kích thước chunk và tính trọn vẹn ngữ nghĩa**: Chunk quá ngắn (`SentenceChunker`) chia cắt các vế của câu hỏi đa điều kiện ra các chunk khác nhau; trong khi `SectionChunker` bảo toàn tính toàn vẹn tốt nhất bằng cách gán tiêu đề vào từng mảnh con.
> 2. **Bản chất của Cosine Similarity trong Retrieval**: Cosine đo mức độ tương đồng về chủ đề ngữ cảnh chứ không đo mật độ thông tin trả lời được. Điều này lý giải tại sao chunk nói chung về điều khoản mượn thiết bị có thể đạt điểm cao ngang ngửa chunk chứa con số phạt cụ thể.
> 3. **Vai trò sống còn của Pre-filtering**: Trong hệ thống RAG thực tế của trường đại học, việc phân quyền tài liệu theo đối tượng độc giả (`student`, `faculty`, `staff`) qua siêu dữ liệu là giải pháp duy nhất ngăn ngừa mô hình đưa ra câu trả lời sai nhóm đối tượng.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một tập văn bản và cùng mô hình nhúng `gemini-embedding-001`, sự khác biệt trong chiến lược chunking quyết định trực tiếp khả năng trả lời của Agent. `FixedSize` nhờ có overlap nên tình cờ gom đủ các vế ngắn, nhưng `SectionChunker` đem lại khả năng truy vết nguồn (Traceability) cao nhất và thể hiện tư duy thiết kế hệ thống chuyên nghiệp nhất đối với văn bản quy phạm pháp luật.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ nâng ngưỡng kích thước chunk tối đa cho mỗi Điều khoản lên 800–1000 ký tự (thay vì 500 ký tự) để toàn bộ các quy định kèm bảng biểu mức phạt và điều kiện xử lý vi phạm luôn nằm trọn vẹn trong một chunk duy nhất, loại bỏ hoàn toàn việc phải phân mảnh các Điều dài thành các sub-chunk.

### Phân Tích Trường Hợp Thất Bại (Failure Case Analysis)

**1. Trường hợp quan sát:**
Ở Câu hỏi 2: *"Thời hạn mượn các thiết bị công nghệ như laptop hoặc iPad là bao lâu và sau bao nhiêu ngày quá hạn thì thiết bị bị tính là làm mất?"*
- **Kết quả:** Cả 3 vị trí Top-1, Top-2, Top-3 đều thuộc đúng tài liệu chuẩn `vinuni-lib-equipment`. Tuy nhiên, ở chiến lược `SectionChunker`, chunk Top-1 (`equipment#3`) chỉ chứa vế thứ nhất (*"trả trước giờ đóng cửa 15 phút"*), trong khi vế thứ hai (*"quá 5 ngày tính là làm mất"*) lại bị đẩy sang chunk Top-2 (`equipment#4`).

**2. Nguyên nhân kỹ thuật:**
- **Câu hỏi đa vế (Multi-part query):** Người dùng hỏi gộp 2 thực thể thông tin khác nhau trong cùng một câu hỏi nghiệp vụ.
- **Phân mảnh ngữ cảnh (Context Fragmentation):** Do giới hạn `max_chunk_size = 500`, Điều 2 của văn bản thiết bị bị cắt đôi thành 2 mảnh con. Cosine similarity đo độ tương đồng tổng quát của câu hỏi với từng chunk độc lập; mảnh nào có mật độ từ khóa cao hơn sẽ chiếm Top-1, khiến một nửa đáp án bị tách sang Top-2.

**3. Đề xuất khắc phục kỹ thuật:**
- **Hierarchical / Parent Document Retrieval:** Khi một sub-chunk lọt vào Top-k, hệ thống tự động nạp toàn bộ văn bản của Điều khoản cha (Parent Section) vào ngữ cảnh cung cấp cho LLM.
- **Tăng chunk_size cho văn bản pháp quy:** Đặt ngưỡng `chunk_size` tối thiểu bằng độ dài trung bình của một Điều khoản hoàn chỉnh (~800 ký tự) thay vì cắt vụn cơ học.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
