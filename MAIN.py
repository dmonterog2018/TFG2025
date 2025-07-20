from analyzer import analyze_repository

# CARGAMOS EL PROGRAMA PRINCIPAL CON EL MENU DONDE NOS DARA UNA BREVE INTRODUCCIÓN AL PROGRAMA Y NOS PREGUNTARÁ POR EL URL.
def main():
    print("------> Welcome to the GitHub repository commit analyzer with Pycefr for Python files <-------")
    print("------> This program will help you understand the complexity level of the selected project based on its development <-------\n")

    repo_url = input("First, enter the URL of the GitHub repository (ej: https://github.com/user/repository): ").strip()
    allowed_extensions = '.py' # SE DEJA ESTA VARIABLE ABIERTA PARA POSIBLES FUTUROS ANALISIS DE OTRO TIPO DE ARCHIVOS

    print("\n Starting UP...")
    print(" Processing...\n")
    analyze_repository(repo_url, allowed_extensions)

if __name__ == "__main__":
    main()