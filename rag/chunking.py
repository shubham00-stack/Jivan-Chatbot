from typing import List, Dict

class RecursiveCharacterChunker:
    """
    Recursively splits text using paragraph, sentence, and word delimiters
    while respecting chunk size and chunk overlap constraints.
    """
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be strictly less than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", "! ", "? ", "; ", " ", ""]

    def split_text(self, text: str) -> List[str]:
        if not text:
            return []
        return self._split(text, self.separators)

    def _split(self, text: str, separators: List[str]) -> List[str]:
        final_chunks: List[str] = []
        separator = separators[-1]
        new_separators = []
        for i, sep in enumerate(separators):
            if sep == "":
                separator = ""
                break
            if sep in text:
                separator = sep
                new_separators = separators[i + 1:]
                break

        splits = text.split(separator) if separator else list(text)
        good_splits = []

        for s in splits:
            if not s:
                continue
            if len(s) < self.chunk_size:
                good_splits.append(s)
            else:
                if good_splits:
                    merged = self._merge_splits(good_splits, separator)
                    final_chunks.extend(merged)
                    good_splits = []
                if not new_separators:
                    final_chunks.append(s[:self.chunk_size])
                else:
                    other_chunks = self._split(s, new_separators)
                    final_chunks.extend(other_chunks)

        if good_splits:
            merged = self._merge_splits(good_splits, separator)
            final_chunks.extend(merged)

        return final_chunks

    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        docs: List[str] = []
        current_doc: List[str] = []
        total_len = 0

        for s in splits:
            s_len = len(s) + (len(separator) if current_doc else 0)
            if total_len + s_len > self.chunk_size and current_doc:
                doc = separator.join(current_doc)
                docs.append(doc)
                # Keep overlap
                while current_doc and total_len > self.chunk_overlap:
                    removed = current_doc.pop(0)
                    total_len -= len(removed) + len(separator)
            current_doc.append(s)
            total_len += s_len

        if current_doc:
            docs.append(separator.join(current_doc))
        return [d.strip() for d in docs if d.strip()]

    def chunk_document(self, text: str) -> List[Dict[str, any]]:
        raw_chunks = self.split_text(text)
        return [{"index": i, "content": chunk} for i, chunk in enumerate(raw_chunks)]

