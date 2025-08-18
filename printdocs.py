import subprocess
import os

class PrintDocument:

    def print_document(path_to_file, number_of_copies=1) -> None:
            if not os.path.exists(path_to_file):
                print(f"Error: PDF file not found at {path_to_file}")
                return
            command = fr'SumatraPDF.exe -print-to-default -silent -exit-on-print -print-settings "{number_of_copies}x" "{path_to_file}"'
            try:
                subprocess.run(command, shell=True, check=True)
                print(f"{path_to_file} отправлен на печать")
            except subprocess.CalledProcessError as e:
                print(f"Error printing document: {e}")
            except FileNotFoundError:
                print("Error: SumatraPDF.exe not found. Please ensure it's in your PATH or provide the full path.")
           

