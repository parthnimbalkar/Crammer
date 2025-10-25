# clean_install.py - FINAL VERSION
import subprocess
import sys

def run(cmd):
    """Run command and return success"""
    print(f"\n▶ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"⚠️ Warning: {result.stderr[:200]}")
    else:
        print("✅ Done")
    return result.returncode == 0

print("=" * 70)
print("🧹 RAG Tutor - FINAL Clean Installation")
print("=" * 70)

# STEP 1: Aggressive uninstall
print("\n🗑️ STEP 1: Removing ALL langchain packages...")
packages_to_remove = [
    "langchain", "langchain-classic", "langchain-core", "langchain-community",
    "langchain-groq", "langchain-openai", "langchain-pinecone", 
    "langchain-text-splitters", "langgraph", "langgraph-checkpoint",
    "langgraph-prebuilt", "langgraph-sdk", "pinecone-client", "pinecone",
    "pinecone-plugin-assistant", "pinecone-plugin-interface"
]

run(f"pip uninstall -y {' '.join(packages_to_remove)}")

# Verify removal
print("\n🔍 Verifying removal...")
result = subprocess.run("pip list | findstr langchain", shell=True, capture_output=True, text=True)
if result.stdout.strip():
    print("⚠️ WARNING: Some packages still remain:")
    print(result.stdout)
    print("\nTrying to remove them individually...")
    for pkg in packages_to_remove:
        run(f"pip uninstall -y {pkg}")
else:
    print("✅ All langchain packages removed")

# STEP 2: Install compatible 1.0.x versions
print("\n📥 STEP 2: Installing compatible packages...")

installs = [
    "langchain-core==1.0.0",  # NOT 1.0.52!
    "langchain-text-splitters==1.0.0",
    "langchain-community==0.4.0",
    "langchain-groq==1.0.0",
    "langchain-pinecone",  # Latest version
    "pinecone-client",
]

for pkg in installs:
    run(f"pip install {pkg}")

# STEP 3: Verify
print("\n🧪 STEP 3: Testing imports...")
tests = [
    ("langchain_core", "Core"),
    ("langchain_core.pydantic_v1", "Pydantic v1"),
    ("langchain_pinecone", "Pinecone"),
    ("langchain_groq", "Groq"),
    ("langchain_community.embeddings", "Embeddings"),
]

passed = 0
for module, name in tests:
    try:
        __import__(module)
        print(f"  ✅ {name}")
        passed += 1
    except Exception as e:
        print(f"  ❌ {name}: {e}")

print("\n" + "=" * 70)
if passed == len(tests):
    print("🎉 SUCCESS!")
    print("\n✅ Installed versions:")
    subprocess.run("pip list | findstr langchain", shell=True)
    subprocess.run("pip list | findstr pinecone", shell=True)
else:
    print(f"⚠️ Only {passed}/{len(tests)} passed")

print("=" * 70)