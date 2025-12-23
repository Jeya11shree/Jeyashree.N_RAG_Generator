# Architecture & Design

## Overview
High-level architecture for RAG multimodal system: ingestion -> vector store -> hybrid retrieval -> LLM generation.

## Tradeoffs
- Local vs cloud embeddings
- Vector DB choice (Chroma/FAISS) vs managed

## Prompt design
- Provide structured JSON schema output
- Include evidence citations (source, score)

## Safety notes
- Sanitize user inputs
- Evidence threshold before asserting facts
- Rate-limit LLM usage
