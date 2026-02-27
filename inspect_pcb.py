import json
import os
import chromadb
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate




def load_pcb_data(json_file="pcb_data.json"):
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"PCB 数据文件不存在: {os.path.abspath(json_file)}")

    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze_with_rag(pcb_data, model_name="qwen3:4b"):
    persist_dir = "./chroma_db"
    collection_name = "kicad_docs"

    if not os.path.exists(persist_dir):
        raise FileNotFoundError(f"向量库不存在，请先运行 build_vector_db.py: {os.path.abspath(persist_dir)}")

    try:
        # === 关键修改：使用 PersistentClient 加载向量库 ===
        client = chromadb.PersistentClient(path=persist_dir)
        embedding_model = OllamaEmbeddings(model="nomic-embed-text")

        vectorstore = Chroma(
            client=client,
            collection_name=collection_name,
            embedding_function=embedding_model
        )

        # 测试是否能检索
        test_results = vectorstore.similarity_search("test", k=1)
        print(f"✅ 向量库加载成功，测试检索返回 {len(test_results)} 个结果")

    except Exception as e:
        print(f"❌ 向量库加载失败: {e}")
        print("💡 请确保:")
        print("   1. 已用新版 build_vector_db.py 成功构建向量库")
        print("   2. Ollama 正在运行（ollama serve）")
        print("   3. 模型已下载: ollama pull nomic-embed-text 和 ollama pull qwen3:4b")
        raise e

    # 初始化 LLM
    llm = Ollama(model=model_name, temperature=0.1)

    # 构造设计摘要
    min_track = min([t["width_mm"] for t in pcb_data["tracks"]]) if pcb_data["tracks"] else 0
    design_summary = f"""
当前 PCB 设计摘要：
- 最小走线宽度: {min_track:.3f} mm
- 元件数量: {len(pcb_data['components'])}
- 走线数量: {len(pcb_data['tracks'])}

请根据公司规范检查：
1. 走线宽度是否合规？
2. 是否存在去耦电容缺失风险？
3. 其他潜在问题？

请逐条列出，并引用规范条款。
"""

    # 定义 Prompt
    prompt_template = """
你是一位资深硬件工程师，请严格基于以下规范回答。

规范内容：
{context}

设计数据：
{question}

要求：
- 仅基于上述内容回答
- 若不确定，回答“无法判断”
- 用中文清晰列出问题
"""
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    # 构建 RAG 链
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
        chain_type="stuff",
        chain_type_kwargs={"prompt": PROMPT}
    )

    print("🔍 正在分析...\n")
    response = qa_chain.invoke({"query": design_summary})
    return response["result"]


if __name__ == "__main__":
    try:
        print("📋 开始 PCB 智能分析...")
        pcb_data = load_pcb_data()
        print(f"✅ 加载 PCB 数据: {len(pcb_data['tracks'])} 条走线, {len(pcb_data['components'])} 个元件")

        report = analyze_with_rag(pcb_data, model_name="qwen3:4b")
        print("\n" + "=" * 50)
        print("📋 PCB 智能检查报告:")
        print("=" * 50)
        print(report)

        # 保存报告
        with open("pcb_analysis_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n✅ 报告已保存到: {os.path.abspath('pcb_analysis_report.txt')}")

    except Exception as e:
        error_msg = f"❌ 错误: {e}"
        print(error_msg)
        with open("error.log", "w", encoding="utf-8") as f:
            f.write(error_msg)
        raise