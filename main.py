import fitz 
import pytesseract
import io
import os

from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Create an instance of the OpenAI class
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), organization=os.environ.get("OPENAI_ORGANIZATION"))

# Path to your tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def process_file(pdf_path):
    # Open the PDF file
    file_name = os.path.basename(pdf_path).split('.')[0]
    pdf_document = fitz.open(pdf_path)

    # Loop through the pages
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        
        # Get the image data from the page
        pix = page.get_pixmap(matrix=fitz.Matrix(5.0, 5.0))

        # Convert the image data to a PIL Image object
        img = Image.open(io.BytesIO(pix.tobytes()))
        
        # Read text from the image
        text = pytesseract.image_to_string(img, lang='tur')
        
        # Send the text to the OpenAI API
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={
                "type": "json_object"
            },
            messages=[
                {"role": "system", "content": 
                    "Sen, yemek menüsü içeren metinleri JSON formatına dönüştüren bir asistansın."
                    "Bu menülerde yemeklerin dışında bazı yazılar da bulunabilir."
                    "Sen sadece yemekleri bulacak, bunları Türkçe ve İngilizce olarak kategorize edecek ve JSON formatına çevireceksin."
                    "Her menü, 'Dilediğiniz Zaman' ve 'İnişten Önce' olmak üzere iki ana kategoriye ayrılmaktadır."
                    "Bu kategoriler altındaki yemekleri ise 'Başlangıç', 'Ana Yemek', 'Tatlılar' ve 'Ekstralar' olmak üzere dört farklı başlık altında değerlendireceksin."
                    "Yemekler büyük harflerle yazılmıştır ve sonrasında içerikleri Pascal notasyonu ile belirtilmiştir."
                    "Taze Ekmek, Kruvasan ve danish benzeri ürünler Ekstralar başlığında bulunmaktadır."
                    "JSON objesi öncelikle dil (Türkçe ve English) ve sonrasında ana kategoriyi içermelidir."},
                {"role": "user", "content": text}
            ]
        )
        msg = completion.choices[0].message
        
        # Save content to a JSON file with page name as the filename
        with open(f'output/{file_name}.json', 'w', encoding='utf-8') as file:
            file.write(msg.content)

    pdf_document.close()
    
# Process PDF files in the input folder
if __name__ == '__main__':
    for file in os.listdir('input'):
        if file.endswith('.pdf'):
            print(f'Processing {file}')
            process_file(f'input/{file}')
    
    print('All files processed successfully.')