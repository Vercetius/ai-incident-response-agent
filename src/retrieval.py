import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class IncidentRetriever:
    def __init__(
        self,
        runbook_dir="data/runbooks",
        historical_path="data/raw/historical_incidents.json",
        model_name="all-MiniLM-L6-v2",
    ):
        self.model = SentenceTransformer(
            model_name
        )

        self.runbooks = self._load_runbooks(
            runbook_dir
        )

        self.historical_incidents = (
            self._load_historical_incidents(
                historical_path
            )
        )

        self.runbook_index = (
            self._build_index(
                [
                    item["content"]
                    for item in self.runbooks
                ]
            )
        )

        self.history_index = (
            self._build_index(
                [
                    item["search_text"]
                    for item
                    in self.historical_incidents
                ]
            )
        )

    def _load_runbooks(
        self,
        directory,
    ):
        directory = Path(directory)

        documents = []

        for path in sorted(
            directory.glob("*.md")
        ):
            content = path.read_text()

            documents.append(
                {
                    "name": path.stem,
                    "path": str(path),
                    "content": content,
                }
            )

        return documents

    def _load_historical_incidents(
        self,
        path,
    ):
        items = json.loads(
            Path(path).read_text()
        )

        for item in items:
            item["search_text"] = (
                f"{item['title']}\n"
                f"Service: {item['service']}\n"
                f"Severity: {item['severity']}\n"
                f"Summary: {item['summary']}\n"
                f"Root cause: {item['root_cause']}\n"
                f"Resolution: {item['resolution']}"
            )

        return items

    def _embed(
        self,
        texts,
    ):
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        return np.asarray(
            embeddings,
            dtype="float32",
        )

    def _build_index(
        self,
        texts,
    ):
        vectors = self._embed(
            texts
        )

        index = faiss.IndexFlatIP(
            vectors.shape[1]
        )

        index.add(
            vectors
        )

        return index

    def _incident_query(
        self,
        incident,
    ):
        messages = " ".join(
            incident.log_messages
        )

        metric_text = " ".join(
            f"{name}: {values}"
            for name, values
            in incident.metrics.items()
        )

        return (
            f"Incident: {incident.title}\n"
            f"Primary service: "
            f"{incident.service}\n"
            f"Services affected: "
            f"{', '.join(incident.services_affected)}\n"
            f"Logs: {messages}\n"
            f"Metrics: {metric_text}"
        )

    def retrieve_runbooks(
        self,
        incident,
        top_k=3,
    ):
        query = self._incident_query(
            incident
        )

        vector = self._embed(
            [query]
        )

        scores, indices = (
            self.runbook_index.search(
                vector,
                min(
                    top_k,
                    len(self.runbooks),
                ),
            )
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):
            item = self.runbooks[
                int(index)
            ]

            results.append(
                {
                    "name": item["name"],
                    "path": item["path"],
                    "score": round(
                        float(score),
                        4,
                    ),
                    "content": item[
                        "content"
                    ],
                }
            )

        return results

    def retrieve_historical(
        self,
        incident,
        top_k=3,
    ):
        query = self._incident_query(
            incident
        )

        vector = self._embed(
            [query]
        )

        scores, indices = (
            self.history_index.search(
                vector,
                min(
                    top_k,
                    len(
                        self.historical_incidents
                    ),
                ),
            )
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):
            item = (
                self.historical_incidents[
                    int(index)
                ]
            )

            results.append(
                {
                    "incident_id": item[
                        "incident_id"
                    ],
                    "title": item[
                        "title"
                    ],
                    "service": item[
                        "service"
                    ],
                    "severity": item[
                        "severity"
                    ],
                    "root_cause": item[
                        "root_cause"
                    ],
                    "resolution": item[
                        "resolution"
                    ],
                    "summary": item[
                        "summary"
                    ],
                    "score": round(
                        float(score),
                        4,
                    ),
                }
            )

        return results

    def retrieve_context(
        self,
        incident,
        top_k_runbooks=3,
        top_k_history=3,
    ):
        return {
            "runbooks": (
                self.retrieve_runbooks(
                    incident,
                    top_k_runbooks,
                )
            ),
            "historical_incidents": (
                self.retrieve_historical(
                    incident,
                    top_k_history,
                )
            ),
        }
