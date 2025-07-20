from perceval.backends.core.git import Git
import json
import os
import subprocess
import shutil
from datetime import datetime

## INICIO DE LA HERRAMIENTA CON LA FUNCIÓN PRINCIPAL ##

def analyze_repository(repo_url, allowed_extensions):
    repo_name = repo_url.rstrip("/").split("/")[-1]
    repo_dir = os.path.abspath(f"./{repo_name}_local_repo")

    # CLONAMOS EL REPOSITORIO SI ESTE NO EXISTE O NO ESTA CLONADO CON ANTERIORIDAD
    if not os.path.exists(repo_dir):
        subprocess.run(["git", "clone", "--mirror", repo_url, repo_dir], check=True)

    repo = Git(uri=repo_url, gitpath=repo_dir)

    # OBTENEMOS LOS COMMITS
    print("Obteniendo commits y detalles del repositorio...")
    commits_data = []

    ## BUCLE PARA LA LECTURA DE CADA COMMIT Y SACAR LOS DATOS

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
                "Repository" : repo_name,                                                   # NOMBRE DEL REPO
                "hash": commit_hash,                                                        # HASH DEL REPO
                "author": commit_data.get("Author"),                                        # AUTOR DEL REPO
                "date": commit_data.get("CommitDate"),                                      # DIA QUE SE REALIZO EL COMMIT
                "message": commit_data.get("message", commit_data.get("Message")),          # MENSAJE DEL COMMIT
                "files": []                                                                 # AQUI INTRODUCIREMOS EL CONTENIDO
            }

            for file in files:
                filename = file["filename"]
                file_status = file["status"]

                # FILTRAMOS UNICAMENTE LO QUE NOS INTERESA, COMMITS CON ESTADOS A DE ADDED O M DE MODIFY, LOS DE TIPO D O DELETE NO LOS TENDREMOS EN CUENTA
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

                        commit_info["files"].append({"file": filename, "content": file_content}) # GUARDAMOS EL CONTENIDO
                    except subprocess.CalledProcessError as e:
                        commit_info["files"].append({"file": filename, "content": f"Error obteniendo contenido: {e}"})
                else:
                    print(f"Ignorado '{filename}' por extensión no permitida: {os.path.splitext(filename)[1].lower()}")

            if commit_info["files"]:
                commits_data.append(commit_info)

    except Exception as e:
        print(f"L Error al obtener commits: {e}")

    if not commits_data:
        print("No se encontraron archivos válidos para analizar en ningún commit. Finalizando ejecución.")
        return

    # GUARDADO DE DATOS EN EL JSON
    with open("commits_with_contents.json", "w", encoding="utf-8") as f:
        json.dump(commits_data, f, indent=4, ensure_ascii=False)

    #TRANFORMACION DE LA HORA
    def parse_date(date_str):
        try:
            # CONVETIMOS EL FORMATO "Mon Jan 30 12:02:23 2023 +0100" A FORMATO ISO PARA LA REPRESENTACION EN LA TIMELINE
            return datetime.strptime(date_str, "%a %b %d %H:%M:%S %Y %z").isoformat()
        except ValueError:
            return None

    # GENERAMOS UN NUEVO JSON CON LOS DATOS NECESARIOS PARA PREPARARLO PARA PASARSELO A PYCEFR

    pyzafer_data = []
    for commit in commits_data:
        commit_hash = commit.get("hash")
        commit_date = commit.get("date")
        commit_date_iso = parse_date(commit_date)
        for file_info in commit.get("files", []):
            pyzafer_data.append({
                "hash": commit_hash,
                "date": commit_date_iso,
                "file": file_info.get("file"),
                "content": file_info.get("content")
            })

    with open("JSON_TO_PYZAFER.json", "w", encoding="utf-8") as out_f:
        json.dump(pyzafer_data, out_f, indent=4, ensure_ascii=False)

    print("Archivo 'JSON_TO_PYZAFER.json' generado.")

    # LLAMAMOS A LA FUNCION QUE SE ENCARGARA DE LANZAR PYCEFR
    prepare_files_for_pycerfl()


def prepare_files_for_pycerfl(json_input="JSON_TO_PYZAFER.json", output_dir="analyzed_files"):

    # SI EXISTE LA CARPETA CON ARCHIVOS DE OTRO ANALISIS, NECESITAMOS BORRARLO PARA QUE NO ENTRE EN CONFLICTO CON EL SIGUENTE
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    # CREAMOS LA CARPETA VACIA
    os.makedirs(output_dir, exist_ok=True)

    with open(json_input, "r", encoding="utf-8") as f:
        data = json.load(f)

    # GENEREMAOS UNA CARPETA CON EL HASH COMO NOMBRE Y CREAMOS LOS DIFERENTES ARCHIVOS CON EL CONTENIDO EXTRAIDO DEL JSON
    for entry in data:
        commit_hash = entry["hash"]
        filename = os.path.basename(entry["file"].lower())
        content = entry["content"]

        commit_dir = os.path.join(output_dir, commit_hash)
        os.makedirs(commit_dir, exist_ok=True)

        full_path = os.path.join(commit_dir, filename)
        try:
            with open(full_path, "w", encoding="utf-8") as out_file:
                out_file.write(content)
        except Exception as e:
            print(f"Error escribiendo {full_path}: {e}")

    print(f"rchivos preparados en '{output_dir}' para pycerfl.py")

    # UNA VEZ LISTO Y PREPARADO, LANZAMOS EL PYCEFR MEDIANTE EL USO DE SUBPROCESS SOBRE CADA UNA DE LAS CARPETAS
    pycefr_dir = os.path.abspath("pycefr2.0")
    try:
        data_json_path = os.path.join("pycefr2.0", "data.json")

        with open(data_json_path, "w", encoding="utf-8") as f:
            json.dump({}, f)

        # ANTES DE ELLO, LANZAMOS EL ARCHIVO CON LA CONFIGURACIÓN APLICADA PARA QUE SE CARGUE
        print("Ejecutando dict.py una vez...")
        subprocess.run(
            ["python3", "dict.py"],
            cwd=pycefr_dir,
            check=True
        )

        if not os.path.exists(data_json_path):
            with open(data_json_path, "w", encoding="utf-8") as f:
                json.dump({}, f)
    except Exception as e:
        print(f"Error ejecutando dict.py: {e}")
        return

    # CREAMOS UN BUCLE, DONDE PARA CADA CARPETA, SE EJECUTARÁ PYCEFR SOBRE CADA UNO DE LOS ARCHIVOS .PY QUE ENCUENTRE
    for subfolder in os.listdir(output_dir):
        subfolder_path = os.path.abspath(os.path.join(output_dir, subfolder))
        if os.path.isdir(subfolder_path):
            print(f"Analizando carpeta {subfolder}...")
            try:
                pycerfl_dir = os.path.abspath("pycefr2.0")
                result = subprocess.run(
                    ["python3", "pycerfl.py", "directory", subfolder_path],
                    cwd=pycerfl_dir,  # asegúrate de que el cwd sea correcto
                )
                print("Subprocess terminado con código:", result.returncode)
                if result.returncode != 0:
                    print(f"pycerfl.py falló en {subfolder_path}")
                    print("STDERR:", result.stderr)
                    print("STDOUT:", result.stdout)
                else:
                    print(f"pycerfl.py ejecutado correctamente en {subfolder_path}")

                print(f"Análisis completado para {subfolder}")
            except Exception as e:
                print(f"Error analizando {subfolder}: {e}")



