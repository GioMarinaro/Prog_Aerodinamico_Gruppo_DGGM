import os

def rinomina_file_cartelle(base_dir):
    for root, dirs, files in os.walk(base_dir):
        for filename in files:
            if "_03000" in filename or "_01500" in filename:
                nuovo_nome = filename.replace("_03000", "").replace("_01500", "")
                vecchio_path = os.path.join(root, filename)
                nuovo_path = os.path.join(root, nuovo_nome)
                os.rename(vecchio_path, nuovo_path)
                print(f"Rinominato: {vecchio_path} -> {nuovo_path}")

if __name__ == "__main__":
    base_dir = os.getcwd()  # Usa la cartella corrente
    rinomina_file_cartelle(base_dir)