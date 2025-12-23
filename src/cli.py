"""CLI entrypoint for ingestion and query."""

import argparse
import json
import logging
from . import ingest, retrieval, generate, guardrails


logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="RAG multimodal CLI")
    sub = parser.add_subparsers(dest="cmd")

    p_ingest = sub.add_parser("ingest", help="Ingest files from sample_data or a folder")
    p_ingest.add_argument("path", nargs="?", default="sample_data")

    p_index = sub.add_parser("index", help="Build or load TF-IDF index from persisted chunks")

    p_query = sub.add_parser("query", help="Query the knowledge base and generate JSON use cases")
    p_query.add_argument("q", help="Query text")
    p_query.add_argument("--top_k", type=int, default=5)
    p_query.add_argument("--debug", action="store_true", help="Show retrieved chunks")

    args = parser.parse_args()

    if args.cmd == "ingest":
        ingest.run(input_path=args.path, persist=True)
        logger.info("Ingest complete.")

    elif args.cmd == "index":
        vec, mat, chunks = retrieval.run_build_index()
        logger.info("Index built/loaded (%d chunks)", len(chunks))

    elif args.cmd == "query":
        vec, mat, _ = retrieval.run_build_index()
        retrieved = retrieval.retrieve(args.q, top_k=args.top_k)
        # optional debug display
        if args.debug:
            for r in retrieved:
                logger.info("[RETRIEVED] score=%.3f source=%s", r["score"], r.get("source"))

        if not guardrails.meets_evidence_threshold(retrieved):
            output = {"clarify": True, "message": "Insufficient evidence; provide more documents or confirm assumptions.", "evidence": retrieved}
            print(json.dumps(output, indent=2))
            return

        out = generate.generate_use_cases(args.q, retrieved, top_k=args.top_k)
        print(json.dumps(out, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
