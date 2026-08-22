from rapidfuzz import fuzz

def name_similarity(name1,name2):
    return fuzz.token_sort_ratio(
        name1.strip().lower(),
        name2.strip().lower()
    )
    