import json, math

with open('data/unified_publications.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

total   = len(data)
n_parts = 3
size    = math.ceil(total / n_parts)

for i in range(n_parts):
    chunk = data[i*size : (i+1)*size]
    out   = f'data/unified_part_{i+1}.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(chunk, f, ensure_ascii=False)
    print(f'  {out}: {len(chunk):,} records')

print(f'Total: {total:,} records dalam {n_parts} file')
