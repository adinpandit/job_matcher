import re

def clean_text(text:str)->str:
    if not text:
        return ""

    text = text.replace("\t"," ")

    text = re.sub(r"[ ]+"," ",text)

    text = re.sub(r" +\n","\n",text)

    text = re.sub(r"\n{3,}","\n\n",text)

    return text.strip()