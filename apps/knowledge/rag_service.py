import logging

import chromadb
from decouple import config
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore


OPENAI_API_KEY = config("OPENAI_API_KEY")
logger = logging.getLogger(__name__)
COLLECTION_NAME = "rag_chunks"

class RAG_Service:

    @staticmethod
    def _get_chroma_client():
        host = config("CHROMADB_HOST", default="localhost")
        port = config("CHROMADB_PORT", default="8001")
        return chromadb.HttpClient(host=host, port=port)

    @staticmethod
    def _get_chroma_collection():
        client = RAG_Service._get_chroma_client()
        return client.get_or_create_collection(
            COLLECTION_NAME,
            metadata={"description": "Coleção para chunks de documentos RAG"},
        )

    @staticmethod
    def ingest_pdf(file_path: str, user_id: str, title: str):
        try:

            reader = SimpleDirectoryReader(input_files=[file_path])
            docs = reader.load_data()
            del reader

            if len(docs) == 0:
                logger.warning("Nenhum documento foi carregado do PDF")
                return 0

            for d in docs:
                d.metadata["user_id"] = str(user_id)
                d.metadata["title"] = title

            chroma_collection = RAG_Service._get_chroma_collection()

            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)

            index = VectorStoreIndex.from_documents(
                docs,
                storage_context=storage_context,
                embed_model=OpenAIEmbedding(
                    model="text-embedding-3-small",
                    api_key=OPENAI_API_KEY,
                ),
                show_progress=True,
            )

            return len(docs)

        except Exception as e:
            logger.error(f"Erro ao fazer ingestão do PDF: {e}", exc_info=True)
            raise

    @staticmethod
    def answer_question(question: str, user_id: str):
        try:
            chroma_collection = RAG_Service._get_chroma_collection()
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)

            index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                storage_context=storage_context,
                embed_model=OpenAIEmbedding(
                    model="text-embedding-3-small",
                    api_key=OPENAI_API_KEY,
                ),
            )

            filters = MetadataFilters(
                filters=[
                    ExactMatchFilter(key="user_id", value=str(user_id))
                ]
            )

            query_engine = index.as_query_engine(
                llm=OpenAI(
                    model="gpt-4o-mini",
                    api_key=OPENAI_API_KEY,
                ),
                similarity_top_k=5,
                filters=filters,
            )

            response = query_engine.query(question)

            response_str = ""
            if hasattr(response, "response") and response.response:
                response_str = str(response.response)

            if not response_str:
                response_str = str(response) if response else ""

            if not response_str or response_str.strip() in ("", "Empty Response"):
                response_str = (
                    "Desculpe, não encontrei informações relevantes para responder "
                    "sua pergunta nos documentos disponíveis."
                )
            return response_str

        except Exception as e:
            logger.error(f"Erro ao responder pergunta: {e}", exc_info=True)
            raise