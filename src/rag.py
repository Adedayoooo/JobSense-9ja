import chromadb
from sentence_transformers import SentenceTransformer
from src.config import EMBEDDING_MODEL, COLLECTION_NAME, RAG_RESULTS_COUNT

print("Loading embedding model...")
embedder = SentenceTransformer(EMBEDDING_MODEL)
chroma = chromadb.Client()
collection = chroma.get_or_create_collection(COLLECTION_NAME)
print("✅ RAG system ready!")

COMPANY_KNOWLEDGE = [
    {
        "id": "flutterwave_1",
        "text": (
            "Flutterwave is a Nigerian fintech unicorn founded in 2016. "
            "They process payments across Africa. Tech stack heavily involves "
            "Python, Node.js, Kubernetes, and AWS. Known for fast-paced culture. "
            "Interview process: technical screen, system design round, and culture fit. "
            "They value candidates who have shipped production systems, not just academic projects."
        ),
    },
    {
        "id": "flutterwave_2",
        "text": (
            "Flutterwave fraud detection team uses real-time ML scoring on transactions. "
            "They deal with millions of transactions daily. Kafka is used for streaming. "
            "Candidates with any fintech or fraud detection experience get preference. "
            "Remote-friendly for senior roles but most junior/mid roles are hybrid Lagos."
        ),
    },
    {
        "id": "paystack_1",
        "text": (
            "Paystack was acquired by Stripe in 2020. Strong engineering culture, "
            "very high bar for technical quality. Interview includes take-home coding "
            "project (usually 3-5 days). They value clean code and good documentation. "
            "Python and TypeScript primary languages. ML team is small but growing. "
            "Competitive salary, one of the best in Nigeria."
        ),
    },
    {
        "id": "andela_1",
        "text": (
            "Andela connects African engineers with global companies. They shifted from "
            "full-time employment to marketplace model in 2021. Clients are mostly US "
            "companies. Interview involves technical assessment on their platform. Good "
            "for Nigerian engineers wanting remote international exposure. "
            "Pay is in USD which is advantageous given naira devaluation."
        ),
    },
    {
        "id": "kuda_1",
        "text": (
            "Kuda is a Nigerian digital bank. Fast-growing fintech. Data and ML team "
            "works on credit scoring, fraud, and customer behavior models. Python-first. "
            "They value practical ML experience over academic background. "
            "Have faced some regulatory challenges. Hybrid work in Lagos."
        ),
    },
    {
        "id": "general_nigeria_1",
        "text": (
            "Nigerian tech companies generally offer salaries between 200k-800k NGN "
            "monthly for junior-to-mid ML engineers. Senior roles can go higher. "
            "Many companies now offer remote or hybrid. The job market in Nigeria for "
            "ML engineers is competitive but smaller than global market. Having deployed "
            "projects on GitHub and HuggingFace significantly improves callback rates."
        ),
    },
    {
        "id": "general_nigeria_2",
        "text": (
            "For Nigerian engineers applying to remote international roles: Deel and "
            "Remote.com are common payment platforms. Time zones matter — companies in "
            "UK/Europe are easier for Nigeria (WAT is UTC+1). Portfolio projects with "
            "live demos are more important than certifications for ML roles. "
            "GitHub activity and HuggingFace deployments are actively checked by recruiters."
        ),
    },
]

def load_knowledge_base():
    existing_ids = set(collection.get()["ids"])
    new_docs = [d for d in COMPANY_KNOWLEDGE if d["id"] not in existing_ids]

    if not new_docs:
        print("✅ Knowledge base already loaded.")
        return

    texts      = [d["text"] for d in new_docs]
    ids        = [d["id"]   for d in new_docs]
    embeddings = embedder.encode(texts).tolist()

    collection.add(documents=texts, embeddings=embeddings, ids=ids)
    print(f"✅ Added {len(new_docs)} entries to knowledge base.")

def retrieve_company_context(company_name: str, role: str) -> str:
    """
    Semantic search: finds the most relevant knowledge base entries
    for a given company and role.

    Returns combined text string — this goes directly into the
    cover letter prompt as context.
    """
    query           = f"{company_name} {role} culture interview hiring"
    query_embedding = embedder.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=RAG_RESULTS_COUNT
    )

    if results["documents"][0]:
        return "\n\n".join(results["documents"][0])
    return "No specific company information available."

load_knowledge_base()
