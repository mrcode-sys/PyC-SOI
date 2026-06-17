import os
import shutil
import numpy
import onnxruntime
from PIL import Image
import json
from pathlib import Path

lot_value = 500

MODEL_DIR = "./models/mobilenet_v2_embeddings.onnx"
VECTOR_DATA_DIR = "data/images_vectors.json"

def start_model():
    if not os.path.exists(MODEL_DIR):
        print(f"Erro: O arquivo do modelo não foi encontrado em '{MODEL_DIR}'")
        return None
    print("Carregando modelo ONNX na memória...")
    session = onnxruntime.InferenceSession(MODEL_DIR, providers=['CPUExecutionProvider'])
    return session
    
def configure_image(img_dir):
    try:
        img = Image.open(img_dir).convert('RGB')
        img = img.resize((224, 224), Image.Resampling.BILINEAR)
        img_data = numpy.array(img, dtype=numpy.float32)
        
        img_data /= 255.0
        
        img_data = numpy.expand_dims(img_data, axis=0)
        return img_data
    except Exception as e:
        print(f"Erro ao preparar imagem {img_dir}: {e}")
        return None

def obtain_vectors(session, image_dir):
    img_data = configure_image(image_dir)
    if img_data is None:
        return None
                
    input_name = session.get_inputs()[0].name
    
    outputs = session.run(None, {input_name: img_data})
    vectors = outputs[0][0]
    return vectors.tolist()

def open_json(data_file):
  if not Path(data_file).is_file():
    return {}
  with open(data_file, 'r', encoding='utf-8') as file:
    return json.load(file)

def save_json(data, data_file):
  with open(data_file, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)



def create_vector(files_dir):
  session = start_model()
  print(session)
  if not session:
    return
  
  extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
  files = [f for f in os.listdir(files_dir) if f.lower().endswith(extensions)]

  #if files == open_json("files.json"):
    #return
  if not files:
      print("Nenhuma imagem na pasta para o ONNX analisar.")
      return

  vectors_cached = open_json(VECTOR_DATA_DIR)
  vectors = {name: vec for name, vec in vectors_cached.items() if name in files}
  
  removed_files = len(vectors_cached) - len(vectors)
  if removed_files > 0:
      print(f"Limpeza de Cache: Removidos {removed_files} vetores antigos do JSON que não existem mais na pasta.")
  #vectors = {}
  loop_count = 0
  print(files_dir)
  for file in files:

    if not file in vectors:
      file_path = os.path.join(files_dir, file)
      file_vector = obtain_vectors(session, file_path)
      if file_vector is not None:
        vectors[file] = file_vector
        loop_count += 1

        if loop_count % lot_value == 0:
          save_json(vectors, VECTOR_DATA_DIR)

  if loop_count > 0 or removed_files > 0:
    print("Atualizando arquivo images_vectors.json...")
    save_json(vectors, VECTOR_DATA_DIR)

  #save_json(files, "files.json")



if __name__ == "__main__":
  create_vector(FILES_DIR)