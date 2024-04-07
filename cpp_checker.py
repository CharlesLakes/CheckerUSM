import os
import subprocess
import shutil
import resource
import time
from checker_response import CheckerResponse

class CppChecker:
  def limit_virtual_memory(self) -> None:
    # The tuple below is of the form (soft limit, hard limit). Limit only
    # the soft part so that the limit can be increased later (setting also
    # the hard limit would prevent that).
    # When the limit cannot be changed, setrlimit() raises ValueError.
    MAX_VIRTUAL_MEMORY = 1024 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (MAX_VIRTUAL_MEMORY, resource.RLIM_INFINITY))

  def __init__(self, identification: int, temporal_directory=".temporal") -> None:
    # Constructor de la clase CppChecker
    # Recibe el parámetro 'identification' y un directorio temporal opcional
    self.temporal_directory = os.path.abspath(temporal_directory)
    self.identification = identification
    # Crea el directorio temporal si no existe
    if not os.path.isdir(self.temporal_directory):
      os.mkdir(self.temporal_directory)
  def load_testcase(self, directory: str):
    # Método para cargar los casos de prueba desde un directorio
    self.directory_testcase = os.path.abspath(directory)

  def compile(self, code: str) -> CheckerResponse:
    # Método para compilar el código fuente C++
    try:
      cpp_status = subprocess.check_output(
        [
          "g++",
          "-x",
          "c++",
          "-",
          "-o",
          f"{self.temporal_directory}/{self.identification}_main"
        ],
        input=code,
        universal_newlines=True,
        stderr=subprocess.STDOUT
      )
      return CheckerResponse("SC", "All good!")
    except subprocess.CalledProcessError as exc:
      # Si ocurre un error durante la compilación, imprime el error y retorna False
      return CheckerResponse("CE", exc)
  def execute_testfile(self, executable: str, rute_test: str, filename: str, max_length=10**7, timeout=3) -> CheckerResponse:
    # Método para ejecutar un caso de prueba desde un archivo
    # Copia el archivo de prueba al directorio temporal
    shutil.copyfile(os.path.abspath(rute_test), self.temporal_directory + "/" + filename)
    try:
      # Ejecuta el ejecutable utilizando subprocess.Popen
      process = subprocess.Popen(
        [os.path.abspath(executable)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        preexec_fn=self.limit_virtual_memory
      )

      start_time = time.time()
      output = ""
      while True:
        # Lee la salida del proceso línea por línea
        line = process.stdout.readline()
        if not line:
          break
        output += line
        # Verifica si la longitud de la salida supera el límite máximo
        if len(output) > max_length:
          raise ValueError(f"La respuesta supera el límite de {max_length} caracteres.")

        if time.time() - start_time > timeout:
          process.terminate()
          return CheckerResponse("TLE")
      # Espera a que el proceso termine
      process.wait()
        
      # Verifica si el proceso finalizó con un código de retorno distinto de cero
      if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, executable)
      return CheckerResponse("NE", output)
    except subprocess.TimeoutExpired as tle:
      # Si el proceso excede el tiempo límite, imprime un mensaje y retorna False
      return CheckerResponse("TLE", tle)
    except subprocess.CalledProcessError as exc:
      # Si ocurre un error durante la ejecución, imprime el error y retorna None
      return CheckerResponse("RTE", exc)
    except resource.error as mle:
      # Memoria limite excedida  
      return CheckerResponse("MLE", mle)
    except ValueError as pe:
      # Error de presentación
      return CheckerResponse("PE", pe)

test = CppChecker(1)

cpp_code = """
#include <bits/stdc++.h>

using namespace std;

int main(){
    
    cout << "HOLA" << endl;

    return 0;
}
"""

test.compile(cpp_code)

print(test.execute_testfile(".temporal/1_main","xd.txt","hola.txt").get_status())
