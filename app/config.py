from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- LLM: Ollama + Qwen3 ---
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="qwen3:8b", alias="OLLAMA_MODEL")

    # --- Embeddings: Google Gemini (text-embedding-004, API gratuita) ---
    # Qwen3 via Ollama no expone un endpoint de embeddings compatible con LangChain,
    # por eso seguimos usando Gemini solo para embeddings.
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_embedding_model: str = Field(default="text-embedding-004", alias="GEMINI_EMBEDDING_MODEL")

    # --- Vector Store ---
    vector_store: str = Field(default="chroma", alias="VECTOR_STORE")
    chroma_path: str = Field(default="./data/chroma_db", alias="CHROMA_PATH")
    chroma_collection: str = Field(default="documents", alias="CHROMA_COLLECTION")

    # --- Chunking ---
    chunk_size: int = Field(default=1000, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, alias="CHUNK_OVERLAP")
    retrieval_top_k: int = Field(default=4, alias="RETRIEVAL_TOP_K")

    # --- Rutas locales ---
    upload_path: str = Field(default="./data/uploads", alias="UPLOAD_PATH")
    log_path: str = Field(default="./data/query_log.jsonl", alias="LOG_PATH")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "populate_by_name": True,
    }


settings = Settings()
