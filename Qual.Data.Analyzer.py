import os # Handle files and regular expressions.
import re # Handle files and regular expressions.
import PyPDF2 # PyPDF2 for PDF text extraction.
import nltk # Natural Language Toolkit for text processing.
import fitz  # pip install pymupdf
import ast # for string to list conversion
from openai import OpenAI  # OpenAI client for API calls.
from keys import open_ai_api_key # Import your OpenAI API key from a separate file.
nltk.download('punkt') # Download the punkt tokenizer for sentence tokenization.
from nltk.tokenize import sent_tokenize # Tokenize text into sentences.

# Initialize the OpenAI client with the API key.
client = OpenAI(api_key=open_ai_api_key) 

# Function to extract paragraphs from a PDF using PyMuPDF
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



#
def classify_tone_of_sentence(sentence, author_sentence, client):
    """
    Uses OpenAI to classify the tone of a sentence with respect to an author statement.
    """
    prompt = "".join([
        f"Classify the tone of the following sentence with respect to the statement: {author_sentence}\n\n",
        "There are three possible tones:\n",
        "1. Supportive: The sentence affirms or supports the presence of an effect, relationship, or influence of the keyword. assert or affirm the presence of an effect, relationship, or influence of the keyword on cybersickness. This tone often suggests that the factor matters, has a notable impact, or is a key contributor. Keywords include: significant, critical, affects, influences, predicts, correlated with, plays a role, associated with, linked to, worsens, improves, highly sensitive to, strong relationship, results indicate, was found to contribute, etc\n\n",
        "2. Neutral: The sentence mentions the keyword without taking a stance. Keywords include: measured, included, collected, considered, recorded, examined, controlled for, reported\n\n",
        "3. Opposing: indicates that no effect was found, no significant relationship, or even contradictory evidence between the keyword and cybersickness. The tone suggests the factor does not matter, is inconclusive, or shows inconsistent findings and uses negative phrases such as no significant, not related, was not found, did not affect, no difference, not associated, no clear pattern, mixed results, results were inconclusive, failed to show, inconsistent findings\n",
        sentence,
        "\n\nRespond with: Supportive, Neutral, or Opposing, and explain why."
    ])

    response = client.responses.create(
        model="gpt-4o",
        instructions="You are a helpful academic tone analysis assistant.",
        input=prompt,
        temperature=0
    )

    return response.output_text.strip()


# Hardcoded PDF file and keyword
pdf = "PDF 1"
keyword = "Gender"



# Extract text from the PDF (or load from cache)
if not os.path.exists("text1.txt"):
 text1 = extract_text_pypdf2(pdf)
 with open("text1.txt", "w", encoding="utf-8") as f:
  f.write(text1)
else:
 with open("text1.txt", "r", encoding="utf-8") as f:
  text1 = f.read()


# Use OpenAI to find sentences with the keyword in the extracted text
keyword_sentences = find_sentences_with_keyword_AI(text1, keyword, client)

# Clean and split the AI-extracted sentences
cleaned = clean_pdf_text(keyword_sentences)
sentences = sent_tokenize(cleaned)

# Author's statement for tone analysis
author_sentence = "gender has an impact on the level of cybersickness experienced by users of immersive technology"

# Save sentences with tone analysis to a file
with open("sentences_with_tone.txt", "w", encoding="utf-8") as f:
    for i, sentence in enumerate(sentences):
        print(f"Sentence {i+1}: {sentence}", file=f)
        tone = classify_tone_of_sentence(sentence, author_sentence, client)
        print(tone, "\n", file=f)
        print(f"Sentence {i+1}: {sentence}")
        print(tone, "\n")






