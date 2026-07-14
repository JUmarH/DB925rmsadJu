import os

with open('merge_data.py', 'r', encoding='utf-8') as f:
    code = f.read()
    
# 1. Add CANONICAL_DOSEN_MAP initialization at the top
old_globals = """# List of known countries for affiliation cleaning
KNOWN_COUNTRIES = {"""

new_globals = """# Load 176 Canonical Dosen List for OpenRefine-like matching
CANONICAL_DOSEN_MAP = {}
if os.path.exists('176_dosen_fisipol_clean.txt'):
    with open('176_dosen_fisipol_clean.txt', 'r', encoding='utf-8') as f:
        for line in f:
            name = line.strip()
            if name:
                norm = name.lower().replace(" ", "")
                CANONICAL_DOSEN_MAP[norm] = name

# List of known countries for affiliation cleaning
KNOWN_COUNTRIES = {"""

code = code.replace(old_globals, new_globals)

# 2. Add the matching logic inside load_etd
old_etd_logic = """        all_authors = [resolve_initials_to_fullname(a, registry) for a in all_authors]
        all_authors = [a for a in all_authors if a.lower().replace(" ", "") not in IGNORE_DEGREES_NO_SPACES]
        
        # Deduplicate
        all_authors = list(dict.fromkeys(all_authors))
        if not all_authors:
            continue"""
            
new_etd_logic = """        all_authors = [resolve_initials_to_fullname(a, registry) for a in all_authors]
        
        # OpenRefine-like Canonical Matching and Cleanup
        final_authors = []
        for i, a in enumerate(all_authors):
            a_norm = a.lower().replace(" ", "")
            if a_norm in IGNORE_DEGREES_NO_SPACES or len(a_norm) < 3:
                continue
                
            if i > 0: # Check advisors against canonical list
                matched = False
                for can_norm, can_orig in CANONICAL_DOSEN_MAP.items():
                    if can_norm in a_norm:
                        final_authors.append(can_orig)
                        matched = True
                        break
                if matched:
                    continue
                    
            final_authors.append(a)
            
        all_authors = list(dict.fromkeys(final_authors))
        if not all_authors:
            continue"""

code = code.replace(old_etd_logic, new_etd_logic)

with open('merge_data.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("merge_data.py updated with OpenRefine logic.")
