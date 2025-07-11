import os
import fitz # PyMuPDF for PDF reading
import csv
from openai import OpenAI
from keys import open_ai_api_key # Your OpenAI API key

# Initialize OpenAI client
client = OpenAI(api_key=open_ai_api_key)

# ----------- Paragraph Extraction -----------

def extract_paragraphs(text, client):
    prompt = (
        "Split the following text into paragraphs. "
        "After each paragraph, output the marker <P>.\n\n"
        + text
    )
    paragraphs = []
    buffer = ""

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

    return paragraphs

# ----------- Tone Classification -----------

def classify_tone(paragraph, author_statement, client):
 """Classify the tone of a paragraph with respect to an author statement."""
 prompt = (
 f"Classify the tone of the following paragraph with respect to the statement: {author_statement}\n\n"
 "There are three possible tones:\n"
 "1. Supportive: The paragraph affirms or supports the presence of an effect, relationship, or influence of the keyword.\n"
 "2. Neutral: The paragraph mentions the keyword without taking a stance.\n"
 "3. Opposing: The paragraph indicates no effect or contradictory evidence.\n\n"
 f"Paragraph: {paragraph}\n\n"
 "Respond with: Supportive, Neutral, or Opposing, and explain why."
 )
 response = client.chat.completions.create(
 model="gpt-4o",
 messages=[
 {"role": "system", "content": "You are a helpful academic tone analysis assistant."},
 {"role": "user", "content": prompt}
 ],
 temperature=0
 )
 return response.choices[0].message.content.strip()

# ----------- Main Execution -----------

pdf_path = "PDF 1.pdf"
keyword = "gender"
author_statement = "gender has an impact on the level of cybersickness experienced by users of immersive technology"
output_csv = "paragraphs_with_tone.csv"

doc = fitz.open(pdf_path)
all_paragraphs = []
for page in doc:
    page_text = page.get_text("text")
    paragraphs = extract_paragraphs(page_text, client)
    all_paragraphs.extend(paragraphs)

# Step 1: Filter paragraphs containing the keyword
keyword_paragraphs = [p for p in all_paragraphs if keyword.lower() in p.lower()]
print(f"\nFound {len(keyword_paragraphs)} paragraphs containing the keyword '{keyword}'.")


# Define the output file name
output_txt = "paragraphs_with_tone.txt"

# Delete the old result file if it exists
if os.path.exists(output_txt):
 os.remove(output_txt)

# Step 2: Analyze tone and save to a text file
with open(output_txt, "w", encoding="utf-8") as txtfile:
    txtfile.write("# AUTO-GENERATED TONE ANALYSIS RESULTS\n\n")
    for i, para in enumerate(keyword_paragraphs):
        tone = classify_tone(para, author_statement, client)
        txtfile.write(f"=== PARAGRAPH {i+1} ===\n")
        txtfile.write(f"**Keyword:** {keyword.capitalize()}\n")
        txtfile.write(f"**Paragraph:**\n{para}\n")
        txtfile.write(f"**Tone:** {tone}\n")
        txtfile.write("\n" + "-" * 60 + "\n\n")
        print(f"=== PARAGRAPH {i+1} ===")
        print(f"**Keyword:** {keyword.capitalize()}")
        print(f"**Paragraph:**\n{para}")
        print(f"**Tone:** {tone}")
        print("\n" + "-" * 60 + "\n")

print("\n✅ Analysis complete. Results saved to 'paragraphs_with_tone.txt'.")

