import sys
from pathlib import Path
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

PY = Language(tspython.language())
parser = Parser(PY)

Q_TODO = Query(PY, '((comment) @c (#match? @c "TODO|FIXME"))')
Q_FUNC = Query(PY, '(function_definition name: (identifier) @nama) @fungsi')

BATAS_BARIS = 30

SKIP = {"venv", ".venv", ".git", "node_modules", "__pycache__"}

def node_error_pertama(node):
    if node.is_error or node.is_missing:
        return node
    for child in node.children:
        if child.has_error or child.is_error or child.is_missing:
            hasil = node_error_pertama(child)
            if hasil:
                return hasil
    return None

def cek_file(path):
    tree = parser.parse(path.read_bytes())

    # Fitur 1: komentar TODO/FIXME
    for node in QueryCursor(Q_TODO).captures(tree.root_node).get("c", []):
        print(f"{path}:{node.start_point[0] + 1}: TODO: {node.text.decode(errors='replace').strip()}")

        # Fitur 2: fungsi yang lebih dari 30 baris
    for _, cap in QueryCursor(Q_FUNC).matches(tree.root_node):
        fungsi = cap["fungsi"][0]
        jumlah = fungsi.end_point[0] - fungsi.start_point[0] + 1
        if jumlah > BATAS_BARIS:
            nama = cap["nama"][0].text.decode(errors="replace")
            print(f"{path}:{fungsi.start_point[0] + 1}: FUNGSI PANJANG: {nama} ({jumlah} baris)")
            
    # Fitur 3: file yang pohonnya mengandung error
    if tree.root_node.has_error:
        err = node_error_pertama(tree.root_node)
        baris = err.start_point[0] + 1 if err else "?"
        print(f"{path}:{baris}: SINTAKS ERROR")

def main():
    if len(sys.argv) != 2:
        print("Pemakaian: python cek.py <folder>")
        sys.exit(1)
    for path in sorted(Path(sys.argv[1]).rglob("*.py")):
        if SKIP & set(path.parts):
            continue
        cek_file(path)


main()