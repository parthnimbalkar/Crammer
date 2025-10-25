# rag_engine.py - Core RAG functionality with DEBUG LOGGING
import os
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import Pinecone as PineconeVectorStore
from langchain_groq import ChatGroq
from prompts import (
    TUTOR_SYSTEM_PROMPT,
    TEACHING_PROMPT,
    QA_PROMPT,
    FLASHCARD_PROMPT
)

load_dotenv()

class RAGTutor:
    """RAG-based Tutor System"""
    
    def __init__(self):
        # Load embeddings
        print("Loading embedding model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Connect to Pinecone
        print("Connecting to Pinecone...")
        self.vectorstore = PineconeVectorStore(
            index_name="my-rag-index",
            embedding=self.embeddings,
            pinecone_api_key=os.getenv("PINECONE_API_KEY")
        )
        
        # Initialize LLM
        print("Initializing LLM...")
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.7
        )
        
        print(" RAG Tutor ready!")
    
    def _get_relevant_context(self, query: str, k: int = 4) -> str:
        """Retrieve relevant chunks from vector store"""
        docs = self.vectorstore.similarity_search(query, k=k)
        context = "\n\n".join([doc.page_content for doc in docs])
        return context
    
    def teach(self, topic: str) -> dict:
        """Teaching mode - explain a topic"""
        print(f"🧑‍🏫 Teaching: {topic}")
        
        context = self._get_relevant_context(topic, k=5)
        prompt = TEACHING_PROMPT.format(context=context, question=topic)
        
        messages = [
            {"role": "system", "content": TUTOR_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "mode": "teaching",
            "topic": topic,
            "explanation": response.content,
            "sources_used": len(context.split("\n\n"))
        }
    
    def answer_question(self, question: str) -> dict:
        """Q&A mode - answer specific questions"""
        print(f"❓ Answering: {question}")
        
        context = self._get_relevant_context(question, k=3)
        prompt = QA_PROMPT.format(context=context, question=question)
        
        messages = [
            {"role": "system", "content": TUTOR_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "mode": "qa",
            "question": question,
            "answer": response.content,
            "sources_used": len(context.split("\n\n"))
        }
     
    def generate_flashcards(self, topic: str, num_cards: int = 15) -> dict:
        """Generate flashcards for revision - WITH DEBUG LOGGING"""
        print(f"\n{'='*70}")
        print(f" FLASHCARD GENERATION START")
        print(f"{'='*70}")
        print(f"Topic: {topic}")
        print(f"Num cards requested: {num_cards}")
        
        # Get comprehensive context
        print("\n📚 Retrieving context from Pinecone...")
        context = self._get_relevant_context(topic, k=8)
      
        
        # Create prompt
        prompt = FLASHCARD_PROMPT.format(
            context=context,
            num_cards=num_cards
        )
        
        print(f"\n📝 Prompt created: {len(prompt)} characters")
        
        # Add system message
        messages = [
            {"role": "system", "content": "You are a flashcard generator for students."},
            {"role": "user", "content": prompt}
        ]
        
        # Get response
        print("\n🤖 Calling Groq LLM...")
        response = self.llm.invoke(messages)
        print("✅ LLM response received")
        
        # DEBUG: Print the actual LLM response
        print("\n" + "="*70)
        print("🤖 LLM RAW RESPONSE:")
        print("="*70)
        print(response.content[:1500])  # First 1500 characters
        if len(response.content) > 1500:
            print("\n... [truncated] ...")
        print("="*70)
        print(f"📏 Total response length: {len(response.content)} characters")
        
        # Check format
        has_card = "Card 1:" in response.content or "Card 1" in response.content
        has_front = "Front:" in response.content
        has_back = "Back:" in response.content
        
        print(f"\n🔍 Format check:")
        print(f"  - Contains 'Card 1:': {has_card}")
        print(f"  - Contains 'Front:': {has_front}")
        print(f"  - Contains 'Back:': {has_back}")
        
        if has_card and has_front and has_back:
            print("  ✅ Response appears to follow expected format!")
        else:
            print("  ⚠️ WARNING: Response may not follow expected format!")
        
        print("="*70 + "\n")
        
        return {
            "mode": "flashcards",
            "topic": topic,
            "num_cards": num_cards,
            "flashcards": response.content
        }
    
    def chat(self, message: str, chat_history: list = None) -> dict:
        """Interactive chat with context awareness"""
        print(f"💬 Chat: {message}")
        
        context = self._get_relevant_context(message, k=5)
        
        messages = [{"role": "system", "content": TUTOR_SYSTEM_PROMPT}]
        
        if chat_history:
            messages.extend(chat_history)
        
        user_message = f"""Based on this content:
{context}

Student says: {message}"""
        
        messages.append({"role": "user", "content": user_message})
        
        response = self.llm.invoke(messages)
        
        return {
            "mode": "chat",
            "message": message,
            "response": response.content,
            "sources_used": len(context.split("\n\n"))
        }