import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import faiss

from app.core.config import settings
from app.core.logger import logger

EMBEDDING_DIM = 384


def generate_embedding(text: str, dim: int = EMBEDDING_DIM) -> np.ndarray:
    """
    Generate a 384-dimensional normalized dense embedding for FAISS index search.
    Uses sentence-transformers if available, with a deterministic word-hash vectorizer fallback.
    """
    try:
        from sentence_transformers import SentenceTransformer
        # Singleton cache for sentence transformer model if installed
        if not hasattr(generate_embedding, "_model"):
            generate_embedding._model = SentenceTransformer("all-MiniLM-L6-v2")
        vec = generate_embedding._model.encode(text, convert_to_numpy=True)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.astype(np.float32)
    except Exception:
        # Fallback: Deterministic term-frequency & n-gram feature hashing to 384-dim dense vector
        vec = np.zeros(dim, dtype=np.float32)
        words = [w.lower().strip(".,!?;:()[]") for w in text.split() if w.strip()]
        
        for word in words:
            if not word:
                continue
            # Hash word to feature bucket
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h % dim
            val = 1.0 + (h % 3) * 0.5
            vec[idx] += val
            
            # Character trigram hashes for semantic subword overlap
            for i in range(len(word) - 2):
                tri = word[i:i+3]
                tri_h = int(hashlib.md5(tri.encode("utf-8")).hexdigest(), 16)
                vec[tri_h % dim] += 0.3

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.astype(np.float32)


class VectorDocument:
    def __init__(self, doc_id: str, text: str, metadata: Dict[str, Any], vector: Optional[np.ndarray] = None):
        self.doc_id = doc_id
        self.text = text
        self.metadata = metadata
        self.vector = vector if vector is not None else generate_embedding(text)


class PatientVectorStore:
    """
    FAISS-powered vector store for indexing medical report chunks and clinical guidelines
    with strict patient_id metadata boundary isolation.
    """

    def __init__(self, dim: int = EMBEDDING_DIM, storage_dir: Optional[str] = None):
        self.dim = dim
        self._storage_dir = Path(storage_dir or settings.VECTOR_STORE_DIR)
        self._index_path = self._storage_dir / "patient_reports.faiss"
        self._metadata_path = self._storage_dir / "patient_reports.json"
        self._index = faiss.IndexFlatIP(self.dim)  # Flat Inner Product (cosine similarity for normalized vectors)
        self._doc_records: List[VectorDocument] = []
        if not self._load():
            self._seed_medical_knowledge()

    def _load(self) -> bool:
        if not self._index_path.exists() or not self._metadata_path.exists():
            return False
        try:
            index = faiss.read_index(str(self._index_path))
            records = json.loads(self._metadata_path.read_text(encoding="utf-8"))
            if index.d != self.dim or index.ntotal != len(records):
                raise ValueError("FAISS index and metadata record counts do not match")
            self._index = index
            self._doc_records = [
                VectorDocument(
                    doc_id=record["doc_id"],
                    text=record["text"],
                    metadata=record["metadata"],
                    vector=np.zeros(self.dim, dtype=np.float32),
                )
                for record in records
            ]
            logger.info("Loaded %d persistent FAISS records.", len(self._doc_records))
            if not any(doc.doc_id.startswith("kb_") for doc in self._doc_records):
                self._seed_medical_knowledge()
            return True
        except Exception as exc:
            logger.warning("Persistent FAISS load failed; rebuilding knowledge index: %s", exc)
            self._index = faiss.IndexFlatIP(self.dim)
            self._doc_records = []
            return False

    def _save(self) -> None:
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(self._index_path))
        records = [
            {"doc_id": doc.doc_id, "text": doc.text, "metadata": doc.metadata}
            for doc in self._doc_records
        ]
        self._metadata_path.write_text(json.dumps(records, ensure_ascii=True), encoding="utf-8")

    def _seed_medical_knowledge(self) -> None:
        """Seed clinical guidelines with patient_id = None (accessible as general reference)."""
        kb_articles = [
            {
                "doc_id": "kb_who_hb",
                "text": "WHO Hemoglobin Normal Reference Range: Adult Males 13.5 to 17.5 g/dL. Adult Females 12.0 to 15.5 g/dL. Low hemoglobin indicates anemia or iron deficiency.",
                "metadata": {"source_type": "clinical_knowledge", "title": "WHO Hemoglobin Normal Range Guidelines (Adults)", "patient_id": None}
            },
            {
                "doc_id": "kb_anemia_eval",
                "text": "Evaluating Low Hemoglobin: Microcytic anemia is associated with low MCV and iron deficiency. Persistent low hemoglobin requires longitudinal trend evaluation and physician consultation.",
                "metadata": {"source_type": "clinical_knowledge", "title": "MedlinePlus Anemia & Hematology Evaluation", "patient_id": None}
            },
            {
                "doc_id": "kb_rbc_wbc",
                "text": "Red Blood Cell (RBC) count carries oxygen through hemoglobin. White Blood Cell (WBC) count evaluates immune response with normal range 4,000 to 11,000 /uL.",
                "metadata": {"source_type": "clinical_knowledge", "title": "Clinical Hematology Parameter Reference", "patient_id": None}
            }
        ]
        for article in kb_articles:
            self.add_document(article["doc_id"], article["text"], article["metadata"])

    def add_document(self, doc_id: str, text: str, metadata: Dict[str, Any]) -> None:
        """Add a document chunk to the FAISS vector index."""
        doc = VectorDocument(doc_id=doc_id, text=text, metadata=metadata)
        vec_2d = np.array([doc.vector], dtype=np.float32)
        self._index.add(vec_2d)
        self._doc_records.append(doc)
        self._save()
        logger.debug(f"Added document '{doc_id}' to FAISS vector index (total size: {self._index.ntotal})")

    def index_report(
        self,
        patient_id: str,
        analysis_id: str,
        parsed_json: Dict[str, Any],
        raw_text: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> int:
        """
        Dynamically chunk and index a parsed patient report into FAISS with patient_id and user_id metadata.
        Returns the number of chunks added.
        """
        chunks_added = 0
        labs = parsed_json.get("lab_results") or parsed_json.get("lab_facts") or []
        meta = parsed_json.get("patient_metadata") or {}

        # 1. Index Patient Summary metadata chunk
        patient_desc = f"Patient metadata: Gender: {meta.get('sex', 'Unknown')}, Age: {meta.get('age', 'N/A')}, Report Date: {meta.get('report_date', 'N/A')}."
        self.add_document(
            doc_id=f"{analysis_id}_meta",
            text=patient_desc,
            metadata={
                "patient_id": patient_id,
                "user_id": user_id,
                "analysis_id": analysis_id,
                "source_type": "patient_report_metadata",
                "title": "Patient Metadata Summary"
            }
        )
        chunks_added += 1

        # 2. Index individual Lab Results as granular chunks
        for idx, lab in enumerate(labs):
            test_name = lab.get("test_name", "Lab Test")
            value = lab.get("value")
            unit = lab.get("unit", "")
            ref_range = lab.get("reference_range") or lab.get("normal_range") or "N/A"
            status = lab.get("finding_status") or lab.get("status") or "Normal"

            chunk_text = (
                f"Lab Finding for patient: {test_name} measured at {value} {unit}. "
                f"Reference Normal Range: {ref_range}. Evaluation Status: {status}."
            )
            doc_id = f"{analysis_id}_lab_{idx}_{test_name.lower().replace(' ', '_')}"
            self.add_document(
                doc_id=doc_id,
                text=chunk_text,
                metadata={
                    "patient_id": patient_id,
                    "user_id": user_id,
                    "analysis_id": analysis_id,
                    "test_name": test_name,
                    "value": value,
                    "unit": unit,
                    "status": status,
                    "source_type": "patient_lab_fact",
                    "title": f"Lab Fact: {test_name}"
                }
            )
            chunks_added += 1

        # 3. Index raw text segments if provided
        if raw_text and len(raw_text.strip()) > 50:
            lines = [line.strip() for line in raw_text.split("\n") if len(line.strip()) > 30]
            for i in range(0, len(lines), 3):
                paragraph = " ".join(lines[i:i+3])
                if len(paragraph) > 40:
                    self.add_document(
                        doc_id=f"{analysis_id}_raw_{i}",
                        text=paragraph,
                        metadata={
                            "patient_id": patient_id,
                            "user_id": user_id,
                            "analysis_id": analysis_id,
                            "source_type": "patient_raw_text",
                            "title": f"Report Narrative Excerpt {i+1}"
                        }
                    )
                    chunks_added += 1

        logger.info(f"Indexed {chunks_added} report chunks for patient {patient_id} in FAISS vector store.")
        return chunks_added

    def search(
        self,
        query: str,
        patient_id: Optional[str] = None,
        user_id: Optional[str] = None,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Search FAISS vector store, restricting patient report chunks strictly to matching patient_id (and user_id if present).
        Clinical guidelines with patient_id = None are accessible as general knowledge.
        """
        if self._index.ntotal == 0:
            return []

        query_vec = generate_embedding(query)
        query_2d = np.array([query_vec], dtype=np.float32)

        # Retrieve extra candidate neighbors from FAISS to allow for patient filtering
        fetch_k = self._index.ntotal
        scores, indices = self._index.search(query_2d, k=fetch_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self._doc_records):
                continue

            doc = self._doc_records[idx]
            doc_patient_id = doc.metadata.get("patient_id")
            doc_user_id = doc.metadata.get("user_id")

            # Strict Patient Data Isolation Enforcement:
            # If chunk is from a patient report (doc_patient_id is present), it MUST match requested patient_id!
            if doc_patient_id is not None and doc_patient_id != patient_id:
                continue

            # Strict User Isolation:
            # If user_id is provided and doc has a user_id, it must match!
            if doc_user_id is not None and user_id is not None and doc_user_id != user_id:
                continue

            results.append({
                "doc_id": doc.doc_id,
                "text": doc.text,
                "metadata": doc.metadata,
                "score": float(round(score, 4))
            })

            if len(results) >= top_k:
                break

        return results


# Global singleton instance of FAISS Patient Vector Store
vector_store = PatientVectorStore()
