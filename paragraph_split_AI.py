import fitz  # pip install pymupdf
from openai import OpenAI  # pip install openai --upgrade
from keys import open_ai_api_key  # you must enter your OpenAI API key in a file called keys.py
import ast # for string to list conversion

client = OpenAI(
    api_key=open_ai_api_key
)

def find_paragraphs_AI(text, client, file_path):
    prompt = (
        "For the following text, extract all paragraphs with more than 25 words. Omit paragraphs that contain https://doi.org/"
        "After each paragraph, output the marker <P>. Do not output a list or any Python code, just the paragraphs and <P> markers.\n\n"
        + text
    )
    paragraphs = []
    buffer = ""
    # Streaming response
    with client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        temperature=0
    ) as stream:
        for chunk in stream:
            if hasattr(chunk, "choices") and chunk.choices:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    buffer += delta.content
                    while "<P>" in buffer:
                        para, buffer = buffer.split("<P>", 1)
                        para = para.strip()
                        if para:
                            paragraphs.append(para)
                            print(".", end="", flush=True)
                            with open(file_path, "a", encoding="utf-8") as f:
                                f.write(para + "\n\n")
    return paragraphs


doc = fitz.open("PDF 1.pdf")
#delete the old output file 
all_paras = []
fname = "paragraphs2.txt"
for page in doc:
        page = page.get_text("text")
        paras = find_paragraphs_AI(page, client, fname)
        all_paras.extend(paras)  # append the string directly,  

print(f"Extracted {len(all_paras)} paragraphs from the document.")

