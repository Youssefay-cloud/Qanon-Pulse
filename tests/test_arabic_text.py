from transform.arabic_text import normalize



def test_persian_yeh_becomes_arabic_yeh():
    assert normalize("الجریدة الرسمیة") == "الجريدة الرسمية"

def test_alef_variants():
    assert normalize("أحمد إبراهيم آمن") == "احمد ابراهيم امن"

def test_mixed_digits():
    assert normalize("۲۰۱٧") == "2017"

def test_removes_diacritics():
    assert normalize("مُحَمَّد") == "محمد"

def test_removes_tatweel():
    assert normalize("سـيئر") == "سيئر"

def test_collapses_whitespace():
    assert normalize("  قرار   رئيس\n\nالوزراء ") == "قرار رئيس الوزراء"

def test_is_idempotent():
    s = "مُحَمَّد الجریدة ۲۰۱٧"
    assert normalize(normalize(s)) == normalize(s)

def test_empty_string():
    assert normalize("") == ""