import pdfplumber
import PyPDF2
from django.core.exceptions import ValidationError

class PDFservice:

    @staticmethod
    def extract_text_from_pdf(file_path):
        try:
            #trying pdf plumber to extract text form pdf
            return PDFservice._extract_with_pdfplumber(file_path)
        except Exception as e:
            print(f"pdf plumber failed: {e} trying pypdf2")
            
            try:
                return PDFservice._extract_with_pypdf2(file_path)
            except Exception as e:
                raise(f"pdf plumber failed: {e} trying pypdf2")



    @staticmethod
    def _extract_with_pdfplumber(file_path):
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
        
    # using PYPDF2 to exract text
    @staticmethod
    def _extract_with_pypdf2(file_path):
        pages_data = []
        full_text = ""

        # open file 
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            page_count = len(pdf_reader.pages)
            
            if page_count == 0:
                raise ValidationError("PDF has no pages")
            
            # Check if pdf is enscrypted
            if pdf_reader.is_encrypted:
                raise ValidationError("PDF is password protected")
            
            
            for page_num in range(page_count):
                # Extract text from page
                page = pdf_reader.pages[page_num]
                text = page.extract_text()

                if text:
                    text = text.strip()
                    pages_data.append({
                        "page_number":page_num + 1,
                        "text":text,
                    })
                    full_text += f"\n\n---- page {page_num + 1} ----\n\n{text}"
            if not full_text.strip():
                raise ValidationError("No text could be extract from the pdf")
            return {
                "text":full_text.strip(),
                "page_count":page_count,
                "pages":pages_data,
                
            }


    @staticmethod
    def get_page_count(file_path):
        # Get number of pages in the file
        try:
            with pdfplumber.open(file_path) as pdf:
                return len(pdf.pages)
        except:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages)