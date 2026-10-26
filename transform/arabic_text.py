import re

DIACRITICS = re.compile(r"[\u064B-\u0652\u0670\u0640]")   # tashkeel + superscript alef + tatweel


LETTER_MAP = {
    "\u06cc": "\u064a",   # Persian yeh -> Arabic yeh
    "\u06a9": "\u0643",   # add kaf here
    "\u0623" :"\u0627",   
    "\u0622" :"\u0627",   # Those three the variants of الالف ا
    "\u0625": "\u0627"
    
}


DIGIT_MAP = {}
for i in range(10):
    DIGIT_MAP[chr(0x0660 + i)] = str(i)   # Arabic-Indic
    DIGIT_MAP[chr(0x06F0 + i)] = str(i)   # persian

CHAR_TABLE = str.maketrans({**LETTER_MAP, **DIGIT_MAP})


def normalize(text: str) -> str:
    text = text.translate(CHAR_TABLE)
    text = DIACRITICS.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text