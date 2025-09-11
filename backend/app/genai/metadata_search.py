from datetime import datetime, timedelta
from chromadb import Client, Collection
from dependencies.chromadb_dependency import get_chroma_client
from utils.parser import metadata_parser  # import your parser

def metadata_query_tool_factory(vectordb:Collection,user_id: str):
    def _run(query: str):
        # --- Step 1: Parse query with LLM parser ---
        parsed_query = metadata_parser(query)
        print("Parsed Query:", parsed_query)
        # Extract structured fields
        status = parsed_query.get("status") 
        duration = parsed_query.get("duration") 
        action = parsed_query.get("action") 

        start_date = parsed_query.get("start_date")
        end_date = parsed_query.get("end_date")
        start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())

    # If same day → set end at 23:59:59
        if start_date == end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
        else:
            # Different day → midnight at start of end_date
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        end_ts = int(end_dt.timestamp())
        filters = [{"user_id": {"$eq": user_id}}]

# If time filtering is desired
        if start_ts and end_ts:
                filters.append({"start_time": {"$gte": start_ts}})
                filters.append({"start_time": {"$lte": end_ts}})


        # Optional filtering
        if status:
            filters.append({"status": {"$eq": status}})
        if duration:
            filters.append({"duration": {"$gte": duration}})
        if len(filters) > 1:
            vector_filter = {"$and": filters}
        else:
            vector_filter = filters[0]
                
        results = vectordb.get(
            where=vector_filter,
            include=["documents", "metadatas"],
            limit=100
        )

        docs = results.get("documents", []) if isinstance(results, dict) else []
        metadatas = results.get("metadatas", []) if isinstance(results, dict) else []
        for metadata in metadatas:
            if 'start_time' in metadata:
                metadata['start_time'] = datetime.fromtimestamp(metadata['start_time']).strftime('%Y-%m-%d %H:%M:%S')
            
            sensitive_keys = ['user_id', 'log_id', 'ace_task_id']
            for key in sensitive_keys:
                if key in metadata:
                    del metadata[key]

        filtered_docs = []
        for doc, meta in zip(docs, metadatas):
            if status and meta.get("status") != status:
                continue
            filtered_docs.append({
                "document": doc,
                "metadata": meta
            })

        if not filtered_docs:
            return "No documents available for this filter."

        if action == "total":
            total = sum(item["metadata"].get("duration", 0) for item in filtered_docs)
            return {
                "total_duration": total,
                "tasks": filtered_docs
            }

        if action == "longest":
            longest = max(filtered_docs, key=lambda x: x["metadata"].get("duration", 0))
            return {
                "longest_task": longest,
                "tasks": filtered_docs
            }
        if action == "list":
            # Return documents mapped with metadata
            return [{"document": doc["document"], "metadata": doc["metadata"]} for doc in filtered_docs]
        
        # Default: just return all filtered docs with metadata
        return filtered_docs


    return _run



# if __name__ == "__main__":
#     # Create Chroma client and collection
#     client = get_chroma_client()
#     vectordb = client.get_or_create_collection("testing")

#     # Example usage
#     tool = metadata_query_tool_factory(vectordb, user_id="8151378e-5a0e-42e1-8a48-d112f2512eb2")
#     query = "give me a summary tasks completed last week that from 1st Sept 2025 to 5th Sept 2025"
#     result = tool(query)

#     print("Query Result:", result)