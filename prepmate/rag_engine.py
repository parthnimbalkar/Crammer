# rag_engine.py - Using Pinecone Inference API with 384-dimension model
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_groq import ChatGroq
from prompts import (
    TUTOR_SYSTEM_PROMPT,
    TEACHING_PROMPT,
    QA_PROMPT,
    FLASHCARD_PROMPT
)

load_dotenv()

class RAGTutor:
    """RAG-based Tutor System using Pinecone Inference API"""
    
    def __init__(self):
        print("🚀 Initializing RAG Tutor...")
        
        # Connect to Pinecone
        print("Connecting to Pinecone...")
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index = self.pc.Index("crammer")
        print("✅ Connected to Pinecone")
        
        # Initialize LLM
        print("Initializing Groq LLM...")
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.7
        )
        print("✅ Groq LLM ready")
        
        print("✅ RAG Tutor ready! Using Pinecone Inference (multilingual-e5-small, 384d)")
    
    def _get_relevant_context(self, query: str, k: int = 4) -> str:
        """Retrieve relevant chunks from vector store using Pinecone Inference"""
        print(f"🔍 Searching for relevant context (top {k})...")
        
        try:
            # Embed query using Pinecone Inference API
            query_embedding = self.pc.inference.embed(
    model="llama-text-embed-v2",
    inputs=[query],
    parameters={"input_type": "query", "truncate": "END"}
)[0].values
            
            # Search Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=k,
                include_metadata=True
            )
            
            # Extract text from results
            contexts = []
            for match in results.matches:
                text = match.metadata.get("text", "")
                if text:
                    contexts.append(text)
            
            context = "\n\n".join(contexts)
            print(f"✅ Found {len(contexts)} relevant chunks")
            return context
            
        except Exception as e:
            print(f"❌ Error retrieving context: {e}")
            return ""
    
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
        """Generate flashcards for revision"""
        print(f"\n{'='*70}")
        print(f"🗂️ FLASHCARD GENERATION START")
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
        
        print(f"📏 Total response length: {len(response.content)} characters")
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