from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# download embedding model
# https://huggingface.co/BAAI/bge-small-en-v1.5
embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)
