from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI, ChatAnthropic
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_core.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from typing import List, Dict, Any, Optional, Callable
import logging
import os
from vector_store import EnhancedPineconeStore

logger = logging.getLogger(__name__)

class LangChainRAG:
    """Advanced RAG system using LangChain."""
    
    def __init__(
        self, 
        openai_api_key: str, 
        anthropic_api_key: str, 
        pinecone_api_key: str, 
        index_name: str,
        organization_id: Optional[str] = None
    ):
        self.openai_api_key = openai_api_key
        self.anthropic_api_key = anthropic_api_key
        self.pinecone_api_key = pinecone_api_key
        self.index_name = index_name
        self.organization_id = organization_id
        
        # Initialize embedding model
        self.embedding_model = OpenAIEmbeddings(
            model="text-embedding-3-large",
            openai_api_key=self.openai_api_key
        )
        
        # Initialize LLM
        self.llm = ChatAnthropic(
            model="claude-3-7-sonnet-20250219",
            anthropic_api_key=self.anthropic_api_key,
            temperature=1
        )
        
        # Initialize vector store
        self.vector_store = EnhancedPineconeStore(
            api_key=self.pinecone_api_key,
            index_name=self.index_name,
            organization_id=self.organization_id
        )
        
        logger.info(f"Initialized LangChainRAG for organization: {organization_id or 'global'}")
    
    def process_document(self, file_path: str, source_id: str, category: str = "general") -> int:
        """Process a document and add it to the vector store."""
        import document_loaders
        import text_splitters
        
        DocumentLoaderFactory = document_loaders.DocumentLoaderFactory
        EnhancedTextSplitter = text_splitters.EnhancedTextSplitter
        
        logger.info(f"Processing document: {source_id}")
        
        try:
            # Load document
            _, metadata, documents = DocumentLoaderFactory.extract_text_and_metadata(file_path)
            
            if not documents:
                logger.warning(f"No content extracted from document: {source_id}")
                return 0
            
            # Add metadata
            for doc in documents:
                doc.metadata.update({
                    "source_id": source_id,
                    "category": category,
                    "organization_id": self.organization_id
                })
            
            # Split into chunks
            chunks = EnhancedTextSplitter.create_document_chunks(documents)
            logger.info(f"Split document into {len(chunks)} chunks")
            
            # Add to vector store
            total_chunks = self.vector_store.add_documents(chunks)
            logger.info(f"Added {total_chunks} chunks to vector store")
            
            return total_chunks
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return 0
    
    def create_retriever(self, category: Optional[str] = None, use_reranking: bool = True):
        """Create an enhanced retriever with optional filtering and reranking."""
        # Create filter dict if category is provided
        filter_dict = {"category": category} if category else None
        
        # Create base retriever
        base_retriever = self.vector_store.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 10,  # Retrieve more candidates for reranking
                "filter": filter_dict
            }
        )
        
        # Add reranking if enabled
        if use_reranking and os.environ.get("COHERE_API_KEY"):
            try:
                compressor = CohereRerank(
                    cohere_api_key=os.environ.get("COHERE_API_KEY"),
                    top_n=5  # Keep top 5 after reranking
                )
                return ContextualCompressionRetriever(
                    base_compressor=compressor,
                    base_retriever=base_retriever
                )
            except Exception as e:
                logger.error(f"Error creating reranker: {str(e)}")
                return base_retriever
        else:
            return base_retriever
    
    def query(
        self, 
        query_text: str, 
        category: Optional[str] = None, 
        history: str = "", 
        stream_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """Query the RAG system with a user question."""
        logger.info(f"Processing query: '{query_text}'")
        
        try:
            # Create retriever
            retriever = self.create_retriever(category)
            
            # Parse conversation history
            chat_history = []
            if history:
                # Simple parsing of history format "Human: ... AI: ..."
                history_parts = history.split("Human: ")
                for part in history_parts:
                    if part.strip():
                        if "AI: " in part:
                            human_msg, ai_msg = part.split("AI: ", 1)
                            chat_history.append((human_msg.strip(), ai_msg.strip()))
                        else:
                            # Incomplete exchange, just add human message
                            chat_history.append((part.strip(), ""))
            
            # Create memory
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
            # Add history to memory
            for human_msg, ai_msg in chat_history:
                if human_msg and ai_msg:
                    memory.chat_memory.add_user_message(human_msg)
                    memory.chat_memory.add_ai_message(ai_msg)
            
            # Create QA chain
            qa_prompt = PromptTemplate.from_template("""
            You are a helpful, knowledgeable, and friendly AI assistant.
            
            Context information:
            {context}
            
            Chat History:
            {chat_history}
            
            User Question: {question}
            
            Guidelines:
            1. Answer the question based on the provided context and conversation history.
            2. If the context does not fully answer the question, supplement with relevant additional knowledge.
            3. Use a warm and personable tone with a friendly greeting.
            4. Structure your response with clear section breaks.
            5. Use bullet points or numbering for clarity.
            6. Conclude with a friendly sign-off.
            
            Answer:
            """)
            
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                memory=memory,
                return_source_documents=True,
                combine_docs_chain_kwargs={"prompt": qa_prompt}
            )
            
            # Execute query
            if stream_callback:
                # For streaming, we need a different approach
                # First get relevant documents
                docs = retriever.get_relevant_documents(query_text)
                
                # Format context
                context_text = "\n\n---\n\n".join([doc.page_content for doc in docs])
                
                # Format chat history
                formatted_history = "\n".join([f"Human: {h}\nAI: {a}" for h, a in chat_history])
                
                # Create prompt
                prompt = qa_prompt.format(
                    context=context_text,
                    chat_history=formatted_history,
                    question=query_text
                )
                
                # Stream response
                response_text = ""
                for chunk in self.llm.stream(prompt):
                    chunk_text = chunk.content
                    response_text += chunk_text
                    stream_callback(chunk_text)
                
                # Format sources
                sources = []
                for i, doc in enumerate(docs):
                    sources.append({
                        "id": doc.metadata.get("source_id", "unknown"),
                        "relevance_score": 1.0 - (i * 0.1)  # Approximate score
                    })
                
                return {
                    "answer": response_text,
                    "sources": sources
                }
            else:
                # Non-streaming response
                result = qa_chain({"question": query_text})
                
                # Format sources
                sources = []
                for i, doc in enumerate(result.get("source_documents", [])):
                    sources.append({
                        "id": doc.metadata.get("source_id", "unknown"),
                        "relevance_score": 1.0 - (i * 0.1)  # Approximate score
                    })
                
                return {
                    "answer": result["answer"],
                    "sources": sources
                }
                
        except Exception as e:
            logger.error(f"Error in query: {str(e)}")
            return {
                "answer": "I encountered an error while processing your query. Please try again.",
                "sources": []
            }
