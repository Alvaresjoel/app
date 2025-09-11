from langchain.chains import RetrievalQA,RetrievalQAWithSourcesChain

def semantic_search_tool(retriever, llm):
    """
    retriever is already filtered for user_id
    """
    retrieval_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )   

    def _run(query: str) -> str:
        result = retrieval_chain.invoke({"query": query})
        docs = result["source_documents"]

        # Clean metadata to remove sensitive IDs
        cleaned_metadata = []
        for doc in docs:
            clean_meta = {k: v for k, v in doc.metadata.items() 
                         if k not in ['user_id', 'log_id', 'ace_task_id']}
            cleaned_metadata.append(clean_meta)

        # Metadata summary
        metadata_summary = "\n".join([str(m) for m in cleaned_metadata])

        return f"{result['result']}\n\nMetadata:\n{metadata_summary}"

    return _run
