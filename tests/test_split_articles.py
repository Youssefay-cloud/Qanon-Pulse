from transform.split_articles import split_law_into_articles


def numbers(text):
    """Split a fake law and return only its article numbers."""
    return [a["article_number"] for a in split_law_into_articles(1, 2025, text)]


def test_heading_forms_and_digit_normalization():
    text = (
        "( المادة الأولى )\nنص الأولى.\n"
        "مادة (۲)\nنص الثانية.\n"        # Persian digit
        "مادة (٣)\nنص الثالثة.\n"        # Arabic-Indic digit
    )
    assert numbers(text) == ["الاولى", "2", "3"]


def test_compound_ordinal_is_not_cut():
    text = (
        "( المادة الثانية )\nنص.\n"
        "( المادة الثانية عشرة )\nنص آخر.\n"
    )
    assert numbers(text) == ["الثانية", "الثانية عشرة"]   # no duplicate "الثانية"


def test_cross_reference_is_not_a_heading():
    text = (
        "مادة (143) : لا يجوز الخصم اكثر من خمسة ايام وفقا لاحكام\n"
        "المادة 143 من هذا القانون . ويعتبر ذلك مخالفة.\n"
    )
    articles = split_law_into_articles(1, 2025, text)
    assert len(articles) == 1
    assert articles[0]["article_number"] == "143"