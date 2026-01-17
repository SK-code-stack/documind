import pdfplumber
from django.core.exceptions import ValidationError

class PDFservice:

    @staticmethod
    def extract_text_from_pdf(file_path):
        try:
            #trying pdf plumber to extract text form pdf
            return PDFservice.extract_with_pdfplumber(file_path)
        except Exception as e:
            print(f"pdf plumber failed: {e} trying pypdf2")
            
            try:
                return PDFservice.extract_with_pypdf2(file_path)
            except Exception as e:
                raise(f"pdf plumber failed: {e} trying pypdf2")



    @staticmethod
    def extract_with_pdfplumber(file_path):
        # extracting using pdf plumber 
        pages_data = []
        full_text = ""

        # open file 
        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)
            
            if page_count == 0:
                raise ValidationError("PDF has no pages")
            
            for page_num, page in enumerate(pdf.pages, start=1):
                # Extract text from page
                text = page.extract_text()

                if text:
                    text = text.strip()
                    pages_data.append({
                        "page_number":page_num,
                        "text":text,
                    })
                    full_text += f"\n\n---- page {page_num} ----\n\n{text}"
            if not full_text.strip():
                raise ValidationError("No text could be extract from the pdf")
            return {
                "text":full_text.strip(),
                "page_count":page_count,
                "pages":pages_data,
                
            }
        
    
    @staticmethod
    def extract_with_pypdf2():
        pass