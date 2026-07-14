import sqlite3

def export_dosen():
    db_path = r"E:\Project\fisipol-hub-backend\fisipol_hub.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # It might be the 'authors' table or 'researchers'
    # Let's check schema
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in c.fetchall()]
    
    if 'researchers' in tables:
        c.execute("SELECT name FROM researchers")
        names = [row[0] for row in c.fetchall()]
    else:
        # Check authors table
        c.execute("SELECT name FROM authors")
        names = [row[0] for row in c.fetchall()]
        
    conn.close()
    
    # Sort names and write to file
    names = sorted(list(set(names)))
    with open('176_dosen_fisipol.txt', 'w', encoding='utf-8') as f:
        for name in names:
            f.write(name + "\n")
            
    print(f"Exported {len(names)} names to 176_dosen_fisipol.txt")

if __name__ == '__main__':
    export_dosen()
