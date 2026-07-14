import sqlite3
import re

def clean_title(name):
    # Split by comma first, taking the first part which is usually the name
    name = name.split(',')[0]
    
    # Remove known prefixes
    prefixes = ['prof.', 'prof ', 'dr.', 'dr ', 'drs.', 'drs ', 'ir.', 'ir ', 'dra.', 'dra ', 'h.', 'h ', 'hj.', 'hj ']
    lower_name = name.lower()
    
    for prefix in prefixes:
        if lower_name.startswith(prefix):
            name = name[len(prefix):]
            lower_name = name.lower()
            
    # Clean up double spaces and strip
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def main():
    db_path = r"E:\Project\fisipol-hub-backend\fisipol_hub.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("SELECT name FROM researchers")
    names = [row[0] for row in c.fetchall()]
    conn.close()
    
    cleaned_names = []
    for orig in names:
        cln = clean_title(orig)
        cleaned_names.append(cln)
        
    cleaned_names = sorted(list(set(cleaned_names)))
    
    with open('176_dosen_fisipol_clean.txt', 'w', encoding='utf-8') as f:
        for name in cleaned_names:
            f.write(name + "\n")
            
    print(f"Exported {len(cleaned_names)} cleaned names to 176_dosen_fisipol_clean.txt")
    for i, n in enumerate(cleaned_names[:20]):
        print(f"{i+1}. {n}")

if __name__ == '__main__':
    main()
