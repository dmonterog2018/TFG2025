from perceval.backends.core.git import Git

repo_url = "https://github.com/dmonterog2018/LTAW-Practicas"
repo_dir = "./local_repo"

repo = Git(uri=repo_url, gitpath=repo_dir)

print("Obteniendo commits y detalles del repositorio...")
commits = []

try:
    for commit in repo.fetch():
        commits.append(commit)
except Exception as e:
    print(f"Error al obtener commits: {e}")

# Guarda los commits obtenidos en un archivo JSON
import json
with open("commits_with_files.json", "w") as f:
    json.dump(commits, f, indent=4)

print("Datos guardados en commits_with_files.json")