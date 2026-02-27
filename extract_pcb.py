import sys
import os
import logging
from datetime import datetime

# === 日志配置 ===
log_file = "build_RAG.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_file, encoding='utf-8')]
)
logger = logging.getLogger(__name__)

logger.info("=" * 60)
logger.info("🚀 开始构建 RAG 向量库（使用原生 Chroma）")
logger.info(f"工作目录: {os.getcwd()}")
logger.info(f"Python 解释器: {sys.executable}")
logger.info(f"Python 版本: {sys.version}")

# === 导入模块 ===
try:
    from langchain_community.document_loaders import DirectoryLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.embeddings import OllamaEmbeddings
    import chromadb
    from chromadb.utils import embedding_functions
    import uuid

    logger.info("✅ 成功导入所需模块")

except Exception as e:
    logger.error(f"❌ 模块导入失败: {e}")
    sys.exit(1)


def build_vector_db(doc_dir="./docs", persist_dir="./chroma_db"):
    # === 1. 加载文档 ===
    if not os.path.exists(doc_dir):
        logger.error(f"❌ 文档目录不存在: {os.path.abspath(doc_dir)}")
        return False

    txt_files = [f for f in os.listdir(doc_dir) if f.endswith('.txt')]
    if not txt_files:
        logger.error(f"❌ 目录中无 .txt 文件: {os.listdir(doc_dir)}")
        return False

    logger.info(f"📄 找到 {len(txt_files)} 个文件: {txt_files}")

    loader = DirectoryLoader(doc_dir, glob="*.txt")
    docs = loader.load()
    logger.info(f"✅ 加载 {len(docs)} 个文档")

    if not docs:
        logger.error("❌ 文档内容为空")
        return False

    # === 2. 分割文本 ===
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", " ", ""]
    )
    splits = text_splitter.split_documents(docs)
    logger.info(f"✅ 切分为 {len(splits)} 个文本块")

    if not splits:
        logger.error("❌ 分割结果为空")
        return False

    # === 3. 初始化嵌入模型（用于生成向量）===
    logger.info("🧠 初始化 Ollama 嵌入模型 (nomic-embed-text)...")
    ollama_emb = OllamaEmbeddings(model="nomic-embed-text")

    # 测试嵌入是否可用
    try:
        test_vec = ollama_emb.embed_query("test")
        logger.info(f"✅ 嵌入模型正常，向量维度: {len(test_vec)}")
    except Exception as e:
        logger.error(f"❌ 嵌入模型调用失败: {e}")
        logger.error("💡 请确保 Ollama 正在运行: ollama serve")
        return False

    # === 4. 使用原生 Chroma 构建向量库 ===
    logger.info("📦 使用原生 Chroma API 构建向量库...")

    # 创建持久化客户端
    client = chromadb.PersistentClient(path=persist_dir)

    # 删除旧集合（避免冲突）
    collection_name = "kicad_docs"
    try:
        client.delete_collection(name=collection_name)
        logger.info(f"🧹 删除旧集合: {collection_name}")
    except ValueError:
        pass  # 不存在则忽略

    # 创建新集合（注意：这里不使用 embedding_function，因为我们自己提供 embeddings）
    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}  # 可选：设置相似度度量
    )

    # 准备数据
    documents = []
    metadatas = []
    ids = []
    embeddings = []

    for i, doc in enumerate(splits):
        doc_id = str(uuid.uuid4())
        text = doc.page_content
        meta = doc.metadata or {}
        meta["source"] = str(meta.get("source", "unknown"))

        # 生成嵌入
        emb = ollama_emb.embed_query(text)

        ids.append(doc_id)
        documents.append(text)
        metadatas.append(meta)
        embeddings.append(emb)

    # 添加到 Chroma
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    logger.info(f"✅ 成功添加 {len(ids)} 个向量到集合 '{collection_name}'")
    logger.info(f"📁 向量库存储路径: {os.path.abspath(persist_dir)}")
    return True


if __name__ == "__main__":
    success = build_vector_db()
    if success:
        logger.info("🎉 RAG 向量库构建成功！")
    else:
        logger.error("💥 构建失败！")

    logger.info("🔚 脚本结束")
    logger.info("=" * 60)