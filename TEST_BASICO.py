from perceval.backends.core.git import Git
import json
import os
import subprocess

repo_url = "https://github.com/dmonterog2018/LTAW-Practicas"
repo_dir = "./local_repo"

# Extensiones permitidas (puedes agregar más si necesitas)
allowed_extensions = [".py", ".txt", ".js", ".ts", ".rb", ".java", ".cpp", ".c", ".cs", ".html", ".css"]

# Clonar el repositorio si no existe localmente
if not os.path.exists(repo_dir):
    subprocess.run(["git", "clone", repo_url, repo_dir], check=True)

repo = Git(uri=repo_url, gitpath=repo_dir)

print("Obteniendo commits y detalles del repositorio...")
commits_data = []

try:
    for commit in repo.fetch():
        commit_data = commit.get("data", {})
        commit_hash = commit_data.get("commit")

        result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-status", "-r", commit_hash],
            cwd=repo_dir,
            check=True,
            capture_output=True,
            text=True,
        )

        files = []
        for line in result.stdout.strip().split("\n"):
            parts = line.split("\t")
            if len(parts) == 2:
                status, filename = parts
                files.append({"status": status, "filename": filename})

        commit_info = {
            "hash": commit_hash,
            "author": commit_data.get("Author"),
            "date": commit_data.get("CommitDate"),
            "message": commit_data.get("message", commit_data.get("Message")),
            "files": []
        }

        for file in files:
            filename = file["filename"]
            file_status = file["status"]

            # Filtrar archivos no permitidos por extensión
            if file_status in ["A", "M"] and os.path.splitext(filename)[1].lower() in allowed_extensions:
                try:
                    file_content = subprocess.run(
                        ["git", "show", f"{commit_hash}:{filename}"],
                        cwd=repo_dir,
                        check=True,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="ignore"
                    ).stdout.strip()

                    commit_info["files"].append({"file": filename, "content": file_content})
                except subprocess.CalledProcessError as e:
                    commit_info["files"].append({"file": filename, "content": f"Error obteniendo contenido: {e}"})

        if commit_info["files"]:  # Solo agregar commits que tienen archivos útiles
            commits_data.append(commit_info)

except Exception as e:
    print(f"Error al obtener commits: {e}")

# Guarda los commits obtenidos en un archivo JSON
with open("commits_with_contents.json", "w", encoding="utf-8") as f:
    json.dump(commits_data, f, indent=4, ensure_ascii=False)

print("Datos guardados en commits_with_contents.json")
