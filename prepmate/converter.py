# converter.py - Using Pinecone Inference API with llama-text-embed-v2 (1024d)
import os
from typing import List
from fastapi import UploadFile
from io import BytesIO
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from unstructured.partition.auto import partition
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
import time

# Load environment variables
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "crammer"

# Validate API key
if not PINECONE_API_KEY:
    raise ValueError("❌ PINECONE_API_KEY not found! Create a .env file with your API key.")

print(f"✅ API Key loaded: {PINECONE_API_KEY[:10]}...")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create index if it doesn't exist
if INDEX_NAME not in pc.list_indexes().names():
    raise ValueError(f"❌ Index '{INDEX_NAME}' not found! Please create it in Pinecone dashboard first.")
else:
    print(f"✅ Index '{INDEX_NAME}' found!")
    index = pc.Index(INDEX_NAME)
    stats = index.describe_index_stats()
    print(f"  Current vectors: {stats.get('total_vector_count', 0)}")

print("✅ Using Pinecone Inference API (llama-text-embed-v2, 1024d) - No local embeddings!")


def clear_pinecone_index():
    """Delete all vectors from Pinecone index"""
    try:
        print("🗑️ Clearing Pinecone index...")
        index = pc.Index(INDEX_NAME)
        
        stats = index.describe_index_stats()
        vector_count = stats.get('total_vector_count', 0)
        
        if vector_count == 0:
            print("✅ Index already empty")
            return True
        
        print(f"Deleting {vector_count} vectors...")
        index.delete(delete_all=True)
        
        # Verify deletion
        time.sleep(3)
        stats = index.describe_index_stats()
        remaining = stats.get('total_vector_count', 0)
        
        if remaining == 0:
            print("✅ Cleared all vectors from Pinecone")
            return True
        else:
            print(f"⚠️ Still {remaining} vectors remaining")
            return False
        
    except Exception as e:
        print(f"❌ Error clearing Pinecone: {e}")
        return False


async def extract_text_from_files(files: List[UploadFile]) -> str:
    """Extract raw text from multiple uploaded files"""
    print(f"📄 Extracting text from {len(files)} file(s)...")
    all_texts = []

    for file in files:
        print(f"  Processing: {file.filename}")
        file_bytes = await file.read()
        
        try:
            if file.filename.lower().endswith('.pdf'):
                buffer = BytesIO(file_bytes)
                pdf_reader = PdfReader(buffer)
                
                text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += page_text + "\n"
                    print(f"    Page {page_num + 1}: {len(page_text)} characters")
                
                all_texts.append(text)
                print(f"  ✅ Extracted {len(text)} characters from {file.filename}")
            
            else:
                buffer = BytesIO(file_bytes)
                elements = partition(file=buffer)
                text = "\n".join([el.text for el in elements if getattr(el, "text", "")])
                all_texts.append(text)
                print(f"  ✅ Extracted {len(text)} characters from {file.filename}")
        
        except Exception as e:
            print(f"  ❌ Error processing {file.filename}: {e}")

    combined_text = "\n".join(all_texts)
    print(f"📊 Total extracted: {len(combined_text)} characters")
    return combined_text


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into smaller overlapping chunks"""
    print(f"✂️ Chunking text (size={chunk_size}, overlap={overlap})...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )
    chunks = splitter.split_text(text)
    print(f"✅ Created {len(chunks)} chunks")
    return chunks


def store_in_pinecone(chunks: List[str], source_filename: str = "unknown"):
    """
    Converts chunks to embeddings using Pinecone Inference API and uploads to Pinecone
    """
    print(f"\n{'='*60}")
    print(f"🔄 STARTING PINECONE UPLOAD")
    print(f"{'='*60}")
    print(f"  Chunks to upload: {len(chunks)}")
    print(f"  Index name: {INDEX_NAME}")
    print(f"  Embedding model: llama-text-embed-v2 (1024d)")
    print(f"  Source: {source_filename}")
    
    if len(chunks) == 0:
        print("⚠️ No chunks to store!")
        return None
    
    try:
        # Get index reference
        index = pc.Index(INDEX_NAME)
        
        # Check index before upload
        print(f"\n📊 BEFORE UPLOAD:")
        stats_before = index.describe_index_stats()
        vectors_before = stats_before.get('total_vector_count', 0)
        print(f"  Existing vectors: {vectors_before}")
        
        # Upload vectors using Pinecone Inference API
        print(f"\n🚀 UPLOADING WITH PINECONE INFERENCE API...")
        
        # Batch process chunks (96 at a time - llama-text-embed-v2 limit)
        batch_size = 96
        total_uploaded = 0
        
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(chunks) + batch_size - 1) // batch_size
            
            print(f"  Processing batch {batch_num}/{total_batches} ({len(batch_chunks)} chunks)...")
            
            try:
                # Generate embeddings using Pinecone Inference API
                embeddings_response = pc.inference.embed(
                    model="llama-text-embed-v2",
                    inputs=batch_chunks,
                    parameters={"input_type": "passage", "truncate": "END"}
                )
                
                # Prepare vectors for upload
                vectors_to_upsert = []
                for j, (chunk, embedding) in enumerate(zip(batch_chunks, embeddings_response)):
                    vector_id = f"{source_filename}-{i + j}"
                    vectors_to_upsert.append({
                        "id": vector_id,
                        "values": embedding.values,
                        "metadata": {
                            "text": chunk,
                            "source": source_filename,
                            "chunk_index": i + j,
                            "chunk_length": len(chunk)
                        }
                    })
                
                # Upsert to Pinecone
                index.upsert(vectors=vectors_to_upsert)
                total_uploaded += len(vectors_to_upsert)
                print(f"  ✅ Batch {batch_num} uploaded ({total_uploaded}/{len(chunks)} total)")
                
            except Exception as batch_error:
                print(f"  ⚠️ Error in batch {batch_num}: {batch_error}")
                continue
        
        print(f"\n  Upload completed! {total_uploaded} vectors uploaded.")
        
        # Wait and verify
        print(f"\n⏳ VERIFYING UPLOAD (checking every 2 seconds)...")
        max_attempts = 10
        for attempt in range(max_attempts):
            time.sleep(2)
            stats = index.describe_index_stats()
            vectors_now = stats.get('total_vector_count', 0)
            new_vectors = vectors_now - vectors_before
            
            print(f"  Attempt {attempt+1}/{max_attempts}: {vectors_now} total ({new_vectors} new)")
            
            if new_vectors >= total_uploaded:
                print(f"\n✅ SUCCESS! All {new_vectors} vectors uploaded!")
                return True
            elif new_vectors > 0:
                print(f"  ⏳ Partial upload detected, waiting...")
        
        # Final check
        stats_final = index.describe_index_stats()
        total_vectors = stats_final.get('total_vector_count', 0)
        new_vectors = total_vectors - vectors_before
        
        print(f"\n{'='*60}")
        print(f"📊 FINAL STATUS:")
        print(f"  Expected: {len(chunks)} vectors")
        print(f"  Uploaded: {new_vectors} vectors")
        print(f"  Total in index: {total_vectors}")
        print(f"{'='*60}\n")
        
        if total_vectors == 0:
            raise Exception(
                "❌ CRITICAL: No vectors in Pinecone after upload!\n"
                "Possible causes:\n"
                "1. Invalid Pinecone API key\n"
                "2. Wrong index name\n"
                "3. Insufficient permissions\n"
                "Please check your Pinecone dashboard at https://app.pinecone.io"
            )
        elif new_vectors < len(chunks):
            print(f"⚠️ WARNING: Only {new_vectors}/{len(chunks)} vectors uploaded")
        
        return True
    
    except Exception as e:
        print(f"\n❌ ERROR DURING UPLOAD:")
        print(f"  {str(e)}")
        import traceback
        traceback.print_exc()
        raise


async def process_uploaded_files(files: List[UploadFile], clear_existing: bool = True):
    """
    Orchestrates the entire ingestion flow:
    clear (optional) → extract → chunk → embed → store
    """
    print("\n" + "=" * 70)
    print(f"🚀 INGESTION PIPELINE START")
    print(f"   Files: {len(files)}")
    print(f"   Clear existing: {clear_existing}")
    print("=" * 70)
    
    # Step 0: Clear existing vectors if requested
    if clear_existing:
        clear_pinecone_index()
        time.sleep(3)
    
    # Step 1: Extract text
    print("\n📖 STEP 1: EXTRACT TEXT")
    raw_text = await extract_text_from_files(files)
    
    if len(raw_text) == 0:
        print("❌ No text extracted from files!")
        return {
            "message": "No text could be extracted from the files",
            "files_processed": len(files),
            "chunks_created": 0,
            "total_vectors_in_index": 0,
            "index_name": INDEX_NAME
        }

    # Step 2: Chunk
    print("\n✂️ STEP 2: CHUNK TEXT")
    chunks = chunk_text(raw_text)
    
    if len(chunks) == 0:
        print("❌ No chunks created!")
        return {
            "message": "Failed to create chunks",
            "files_processed": len(files),
            "chunks_created": 0,
            "total_vectors_in_index": 0,
            "index_name": INDEX_NAME
        }

    # Step 3: Embed + Store in Pinecone
    print("\n💾 STEP 3: STORE IN PINECONE")
    source_name = files[0].filename if files else "unknown"
    
    try:
        store_in_pinecone(chunks, source_name)
    except Exception as e:
        print(f"❌ Failed to store in Pinecone: {e}")
        return {
            "message": f"Error storing in Pinecone: {str(e)}",
            "files_processed": len(files),
            "chunks_created": len(chunks),
            "total_vectors_in_index": 0,
            "index_name": INDEX_NAME,
            "error": str(e)
        }

    # Step 4: Get final stats
    print("\n📊 STEP 4: FINAL VERIFICATION")
    index = pc.Index(INDEX_NAME)
    stats = index.describe_index_stats()
    total_vectors = stats.get('total_vector_count', 0)
    
    print("=" * 70)
    print(f"✅ INGESTION COMPLETE")
    print(f"   Files processed: {len(files)}")
    print(f"   Chunks created: {len(chunks)}")
    print(f"   Vectors in Pinecone: {total_vectors}")
    print("=" * 70 + "\n")

    return {
        "message": "Files processed successfully!",
        "files_processed": len(files),
        "chunks_created": len(chunks),
        "total_vectors_in_index": total_vectors,
        "index_name": INDEX_NAME,
        "previous_vectors_cleared": clear_existing
    }