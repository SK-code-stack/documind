def get_chat_prompt(query, context, document_title):
    """
    Generate prompt for Gemini AI
    
    Args:
        query: User's question
        context: Retrieved chunks from document
        document_title: Name of the document
    
    Returns:
        str: Formatted prompt
    """
    
    prompt = f"""You are an intelligent assistant helping users understand their documents.

Document Title: {document_title}

Context from the document:
{context}

User Question: {query}

Instructions:
1. Answer the question based ONLY on the context provided above
2. Be specific and accurate
3. If the context doesn't contain the answer, say "I cannot find this information in the document"
4. Use natural, conversational language
5. Cite page numbers when relevant
6. Keep answers concise but complete

Answer:"""

    return prompt


def get_system_instruction():
    """
    System instruction for Gemini model
    
    Returns:
        str: System instruction
    """
    
    return """You are a helpful AI assistant that answers questions about documents. 
You provide accurate, concise answers based only on the provided context. 
You cite sources with page numbers when possible.
You are honest when information is not available in the context."""