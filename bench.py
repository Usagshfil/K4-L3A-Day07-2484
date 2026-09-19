from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

from src.chunking import FixedSizeChunker, RecursiveChunker, SentenceChunker
from src.embeddings import (
    EMBEDDING_PROVIDER_ENV,
    GEMINI_EMBEDDING_MODEL,
    GeminiEmbedder,
    MockEmbedder,
)
from src.models import Document
from src.store import EmbeddingStore


class SectionChunker:
    """
    Split Markdown text by headings (e.g. ## Điều ...), keeping semantic units intact.
    If a section exceeds max_chunk_size, fallback to RecursiveChunker while prefixing
    the heading title to each sub-chunk to preserve context.
    """

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


BENCHMARK_QUERIES = [
    {
        "id": 1,
        "query": "Hạn mức mượn sách tối đa và thời gian mượn thông thường là bao lâu?",
        "filter": {"audience": "student"},
        "gold_doc_id": "vinuni-lib-undergraduate",
        "expected_keywords": ["3", "14 ngày"],
        "gold_answer": "Sinh viên được mượn tối đa 3 tài liệu trong thời hạn 14 ngày (2 tuần), được gia hạn 1 lần thêm 14 ngày.",
        "requires_filter": True,
    },
    {
        "id": 2,
        "query": "Thời hạn mượn các thiết bị công nghệ như laptop hoặc iPad là bao lâu và sau bao nhiêu ngày quá hạn thì thiết bị bị tính là làm mất?",
        "filter": None,
        "gold_doc_id": "vinuni-lib-equipment",
        "expected_keywords": ["15 phút", "5 ngày"],
        "gold_answer": "Thiết bị mượn trong ngày và phải trả trước giờ đóng cửa 15 phút; quá hạn 5 ngày liên tiếp tính là làm mất và phải đền bù.",
        "requires_filter": False,
    },
    {
        "id": 3,
        "query": "Điều kiện số lượng người tối thiểu để sử dụng phòng học nhóm là bao nhiêu và sau bao lâu không đến nhận phòng thì lượt đặt phòng bị hủy?",
        "filter": None,
        "gold_doc_id": "vinuni-lib-study-rooms",
        "expected_keywords": ["2 người", "10 phút"],
        "gold_answer": "Số lượng tối thiểu là 2 người; vắng mặt sau 10 phút kể từ giờ bắt đầu thì lượt đặt phòng tự động bị hủy (no-show).",
        "requires_filter": False,
    },
    {
        "id": 4,
        "query": "Thời gian mượn tối đa và mức phí phạt quá hạn đối với tài liệu dự trữ môn học (Course Reserves) là bao nhiêu?",
        "filter": None,
        "gold_doc_id": "vinuni-lib-fines-reserves",
        "expected_keywords": ["2 giờ", "10.000"],
        "gold_answer": "Mượn tại chỗ tối đa 2 giờ/lượt; phí phạt quá hạn là 10.000 VNĐ cho mỗi giờ trễ hạn.",
        "requires_filter": False,
    },
    {
        "id": 5,
        "query": "Mức phí phạt mượn sách thông thường quá hạn mỗi ngày là bao nhiêu và làm mất sách thì phải đền bù thế nào?",
        "filter": None,
        "gold_doc_id": "vinuni-lib-fines-reserves",
        "expected_keywords": ["10.000", "100.000"],
        "gold_answer": "Phí phạt trễ hạn sách thông thường là 10.000 VNĐ/ngày/cuốn; làm mất sách phải đền giá mua mới cộng 100.000 VNĐ phí hành chính.",
        "requires_filter": False,
    },
]


def load_corpus(data_dir: Path) -> list[tuple[dict, str, str]]:
    """Load markdown files and parse frontmatter metadata and body."""
    documents_raw = []
    for md_file in sorted(data_dir.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            meta = yaml.safe_load(parts[1]) or {}
            body = parts[2].strip() if len(parts) > 2 else ""
        else:
            meta = {}
            body = text.strip()
        meta.setdefault("doc_id", md_file.stem)
        documents_raw.append((meta, body, md_file.stem))
    return documents_raw


def get_chunker(strategy: str):
    if strategy == "fixed_size":
        return FixedSizeChunker(chunk_size=500, overlap=50)
    elif strategy == "sentence":
        return SentenceChunker(max_sentences_per_chunk=3)
    elif strategy == "section":
        return SectionChunker(max_chunk_size=500)
    elif strategy == "recursive":
        return RecursiveChunker(chunk_size=500)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")


def build_store(documents_raw: list[tuple[dict, str, str]], chunker, embedder) -> tuple[EmbeddingStore, int]:
    store = EmbeddingStore(collection_name="benchmark_store", embedding_fn=embedder)
    chunk_docs: list[Document] = []
    for meta, body, stem in documents_raw:
        chunks = chunker.chunk(body)
        for idx, chunk in enumerate(chunks):
            doc_id = f"{stem}#{idx}"
            chunk_meta = {**meta, "doc_id": stem, "chunk_index": idx}
            chunk_docs.append(Document(id=doc_id, content=chunk, metadata=chunk_meta))
    store.add_documents(chunk_docs)
    return store, len(chunk_docs)


def run_benchmark(strategy: str, data_dir: Path, output_file: str | None = None) -> None:
    load_dotenv(override=False)
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "").strip().lower()

    if (provider == "gemini" or gemini_key) and gemini_key != "your_gemini_api_key_here":
        try:
            embedder = GeminiEmbedder(model_name=os.getenv("GEMINI_EMBEDDING_MODEL", GEMINI_EMBEDDING_MODEL))
            backend_name = "Gemini (gemini-embedding-001, 3072 dims)"
        except Exception as e:
            embedder = MockEmbedder()
            backend_name = f"MockEmbedder (fallback due to {e})"
    else:
        embedder = MockEmbedder()
        backend_name = "MockEmbedder (deterministic mock)"

    chunker = get_chunker(strategy)
    documents_raw = load_corpus(data_dir)
    store, total_chunks = build_store(documents_raw, chunker, embedder)

    lines = []
    lines.append("=" * 70)
    lines.append("BÁO CÁO ĐÁNH GIÁ TRUY XUẤT (BENCHMARK RETRIEVAL REPORT)")
    lines.append(f"Chiến lược chunking (Strategy) : {strategy}")
    lines.append(f"Backend Embedding              : {backend_name}")
    lines.append(f"Số file tài liệu nguồn         : {len(documents_raw)}")
    lines.append(f"Tổng số chunk được tạo ra       : {total_chunks}")
    lines.append("=" * 70)

    total_score = 0
    max_score = len(BENCHMARK_QUERIES) * 2

    for q in BENCHMARK_QUERIES:
        qid = q["id"]
        query_text = q["query"]
        meta_filter = q["filter"]
        gold_doc = q["gold_doc_id"]
        expected_keywords = q["expected_keywords"]

        lines.append(f"\n[CÂU HỎI {qid}]: {query_text}")
        if meta_filter:
            lines.append(f"  * Áp dụng Metadata Filter: {meta_filter}")
        lines.append(f"  * Tài liệu chuẩn (Gold Doc) : {gold_doc}")
        lines.append(f"  * Đáp án chuẩn (Gold Answer): {q['gold_answer']}")

        results = store.search_with_filter(query_text, top_k=3, metadata_filter=meta_filter)

        found_in_rank = None
        has_keywords = False

        for rank, res in enumerate(results, 1):
            doc_id = res["metadata"].get("doc_id")
            score = res["score"]
            content_preview = res["content"].replace("\n", " ")[:100]
            contains_kw = all(kw.lower() in res["content"].lower() for kw in expected_keywords)
            status_tag = []
            if doc_id == gold_doc:
                status_tag.append("GOLD_DOC")
                if found_in_rank is None:
                    found_in_rank = rank
                    has_keywords = contains_kw
            if contains_kw:
                status_tag.append("KEYWORDS_FOUND")

            tag_str = f" [{' | '.join(status_tag)}]" if status_tag else ""
            lines.append(f"  Top-{rank}: [score={score:.4f}] {res['id']}{tag_str}")
            lines.append(f"          Preview: {content_preview}...")

        # Scoring: 2 pts for rank 1 with keywords, 1 pt for rank 2/3 with keywords, 0 otherwise
        if found_in_rank == 1 and has_keywords:
            q_score = 2
            reason = "Chính xác tuyệt đối (Gold doc tại Top-1 và chứa đầy đủ dữ liệu trả lời)"
        elif found_in_rank in (2, 3) and has_keywords:
            q_score = 1
            reason = f"Đạt một phần (Gold doc tại Top-{found_in_rank}, chứa dữ liệu trả lời)"
        elif found_in_rank is not None:
            q_score = 1
            reason = f"Đạt một phần (Gold doc tại Top-{found_in_rank} nhưng thiếu dữ liệu con số cốt lõi)"
        else:
            q_score = 0
            reason = "Thất bại (Không tìm thấy Gold doc trong Top-3)"

        total_score += q_score
        lines.append(f"  => Đánh giá: {q_score}/2 điểm ({reason})")

    lines.append("\n" + "=" * 70)
    lines.append(f"TỔNG KẾT ĐIỂM TRUY XUẤT: {total_score} / {max_score} điểm ({(total_score/max_score)*100:.1f}%)")
    lines.append("=" * 70)

    # A/B Test for Query 1
    lines.append("\n" + "-" * 70)
    lines.append("THỬ NGHIỆM A/B LỌC METADATA CHO CÂU HỎI 1")
    lines.append("Query: Hạn mức mượn sách tối đa và thời gian mượn thông thường là bao lâu?")
    lines.append("-" * 70)

    # Case A: with filter
    res_a = store.search_with_filter(BENCHMARK_QUERIES[0]["query"], top_k=3, metadata_filter={"audience": "student"})
    lines.append("[NHÁNH A - CÓ FILTER audience=student]:")
    for r, item in enumerate(res_a, 1):
        lines.append(f"  Top-{r}: [score={item['score']:.4f}] {item['id']} (audience={item['metadata'].get('audience')})")
        lines.append(f"          {item['content'].replace(chr(10), ' ')[:90]}...")

    # Case B: without filter
    res_b = store.search_with_filter(BENCHMARK_QUERIES[0]["query"], top_k=3, metadata_filter=None)
    lines.append("[NHÁNH B - KHÔNG DÙNG FILTER]:")
    for r, item in enumerate(res_b, 1):
        lines.append(f"  Top-{r}: [score={item['score']:.4f}] {item['id']} (audience={item['metadata'].get('audience')})")
        lines.append(f"          {item['content'].replace(chr(10), ' ')[:90]}...")
    lines.append("-" * 70)

    report_text = "\n".join(lines)
    print(report_text)

    if output_file:
        Path(output_file).write_text(report_text, encoding="utf-8")
        print(f"\n[OK] Đã xuất kết quả ra file: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Chạy benchmark retrieval Lab 07")
    parser.add_argument(
        "--strategy",
        choices=["fixed_size", "sentence", "section", "recursive"],
        default="section",
        help="Chiến lược chunking (mặc định: section)",
    )
    parser.add_argument("--data-dir", default="data/university", help="Thư mục dữ liệu markdown")
    parser.add_argument("--output", default="ket_qua_benchmark.txt", help="File lưu kết quả benchmark")
    args = parser.parse_args()

    run_benchmark(strategy=args.strategy, data_dir=Path(args.data_dir), output_file=args.output)


if __name__ == "__main__":
    main()

