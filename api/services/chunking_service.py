from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken
from ..models import Document, DocumentChunk

class ChunkingService:

    CHUNK_SIZE = 1000 # characters per chunk
    CHUNK_OVERLAP = 200 # Overlap between chunks
    
    @staticmethod
    def chunk_deocument(document, pdf_data):


        # Delete the existing chunk of document if available
        DocumentChunk.objects.filter(document=document).delete()

        # Initialize text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = ChunkingService.CHUNK_SIZE,
            chunk_overlap = ChunkingService.CHUNK_OVERLAP,
            length_function = len,
            separators = ["\n\n", "\n", ".", " ", ""]
        )

        # Split text into chunks
        text_chunk = text_splitter.split_text(pdf_data['text'])

        # Create chunk report
        chunk_object = []
        for index, chunk_text in enumerate(text_chunk):
            # Finding which page this chunk belongs to 
            page_number = ChunkingService._find_page_number(
                chunk_text,
                pdf_data.get('pages', [])
            )
            # Count token
            token_count = ChunkingService._count_tokens(chunk_text)

            chunk_object.append(
                DocumentChunk(
                    document=document,
                    content=chunk_text,
                    chunk_index=index,
                    page_number=page_number,
                    token_count=token_count,
                )
            )
        
        # Bulk create all chunks 
        DocumentChunk.objects.bulk_create(chunk_object)

        return len(chunk_object)





    @staticmethod
    def _find_page_number(chunk_text, pages):
        chunk_start = chunk_text[:100].strip()
        for page in pages:
            if chunk_start in page['text']:
                return page['page_number']
        return None


    @staticmethod
    def _count_tokens(text):
        try:
            # Use tiktoken for accurate token counting
            encoding = tiktoken.get_encoding('cl100k_base')
            tokens = encoding.encode(text)
            return len(tokens)
        except:
            # Rough estimate of token length 
            return len(text) // 4
        

    @staticmethod
    def get_chunk_statistics(document):
        chunks = DocumentChunk.objects.filter(document=document)

        if not chunks.exists():
            return {
             'total_chunks':0,   
             'total_tokens':0,   
             'avg_tokens_per_chunk':0,   
             'pages_covered':[],   
            }
        
        total_tokens = sum(chunk.token_count for chunk in chunks)
        pages = set(chunk.page_number for chunk in chunks if chunk.page_number)

        return {
            'total_chunks':chunks.count(),   
             'total_tokens':total_tokens,   
             'avg_tokens_per_chunk':total_tokens // chunks.count(),   
             'pages_covered':sorted(list(pages)),
        }