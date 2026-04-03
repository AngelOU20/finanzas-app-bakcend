import os


def tree(dir, prefix="", lines=None):
    if lines is None:
        lines = []
    entries = [
        e
        for e in sorted(os.listdir(dir))
        if e
        not in {
            ".venv",
            "__pycache__",
            ".pytest_cache",
            "migrations",
            ".git",
            "node_modules",
        }
    ]
    for i, entry in enumerate(entries):
        connector = "└── " if i == len(entries) - 1 else "├── "
        lines.append(prefix + connector + entry)
        path = os.path.join(dir, entry)
        if os.path.isdir(path):
            extension = "    " if i == len(entries) - 1 else "│   "
            tree(path, prefix + extension, lines)
    return lines


lines = tree(".")
with open("tree.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("tree.txt generado correctamente")
