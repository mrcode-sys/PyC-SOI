import shutil
import os
import numpy as np
import platform
from pathlib import Path
import json
import ctypes
from core.vector_extractor import start_model, obtain_vectors

if platform.system() == "Windows":
    lib_path = Path("lib/category_grouper_lib.dll")
else:
    lib_path = Path("lib/category_grouper_lib.so")

similarity_lib = ctypes.CDLL(str(lib_path))

similarity_lib.calculate_similarity.restype = ctypes.c_float
similarity_lib.find_best_category.restype = ctypes.c_int
similarity_lib.find_categories_to_merge.restype = None

similarity_lib.calculate_similarity.argtypes = [
  ctypes.POINTER(ctypes.c_float),
  ctypes.POINTER(ctypes.c_float),
  ctypes.c_int
]

similarity_lib.find_best_category.argtypes = [
  ctypes.POINTER(ctypes.c_float),
  ctypes.POINTER(ctypes.c_float),
  ctypes.POINTER(ctypes.c_float),
  ctypes.c_float,
  ctypes.c_float,
  ctypes.c_int,
  ctypes.c_int
]

similarity_lib.find_categories_to_merge.argtypes = [
    ctypes.POINTER(ctypes.c_float),
    ctypes.c_float,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
    ctypes.c_int
]

similarity = 0.8 # Aumentar para diminurir variação de imagens iniciais para categoria
#images_similarity = 0.78 Not used
leader_similarity = 0.44 # Aumentar para diminuir variação com imagem original da categoria
categories_similarity = 0.75 #A Aumentar para evitar junção de categorias diferentes

VECTOR_DATA_DIR = Path("data/images_vectors.json")

categories = []

class Category:
  def __init__(self, category):
    self.category = category
    self.leader_vector = None
    self.mean_vector = None
    self.images = []
    self.images_found = 0
    self.vectors = []

  def add_image(self, image, vector):
    self.images.append(image)
    self.images_found += 1

    if not isinstance(vector, np.ndarray):
        vector = np.array(vector, dtype=np.float32)

    self.vectors.append(vector)
    if self.leader_vector is None:
      self.leader_vector = vector

    self.mean_vector = np.mean(self.vectors, axis=0)


def open_json(data_file):
  if not Path(data_file).is_file():
    return {}
  with open(data_file, 'r', encoding='utf-8') as file:
    return json.load(file)

def save_json(data, data_file):
  with open(data_file, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)

def c_calculate_similarity(vector1, vector2):
  c_vector1 = vector1.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
  c_vector2 = vector2.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

  n = len(vector1)

  similarity = similarity_lib.calculate_similarity(c_vector1, c_vector2, n)

  return similarity

def add_category(image, vector, category):
  category = Category(category)
  category.add_image(image, vector)
  categories.append(category)

def load_organized_categories(categories_dir, vectors):
  loaded_categories = []
  session = start_model()
  categories_dir = Path(categories_dir)

  if not categories_dir.is_dir():
    return loaded_categories
  
  for folder_path in categories_dir.iterdir():

    if folder_path.is_dir():
      folder_name = folder_path.name
      category_obj = Category(folder_name)

      for file_path in folder_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
          image_name = file_path.name
          image_vector = vectors.get(image_name)

          if image_vector is None:
            print(f"Image '{image_name}' not found in vectors cache. Extracting now...")
            if session:
              image_vector = obtain_vectors(session, file_path)
          if not image_vector is None:
            category_obj.add_image(image_name, image_vector)

      loaded_categories.append(category_obj)
  save_json(vectors, VECTOR_DATA_DIR)
  return loaded_categories

def search_similarity(vector):

  for category in categories:
    #print(f"DEBUG: {category.images}")
    #print(c_calculate_similarity(category.mean_vector, vector))
    if c_calculate_similarity(category.leader_vector, vector) >= leader_similarity:
      if c_calculate_similarity(category.mean_vector, vector) >= similarity:
        return category  
  return False

def c_search_similarity(vector):
  if not categories:
    return -1

  np_leaders = np.array([cat.leader_vector for cat in categories], dtype=np.float32)
  np_centroids = np.array([cat.mean_vector for cat in categories], dtype=np.float32)

  c_vector = vector.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
  c_leaders = np_leaders.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
  c_centroids = np_centroids.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

  index = similarity_lib.find_best_category(
    c_vector,
    c_centroids,
    c_leaders,
    float(leader_similarity),
    float(similarity),
    len(vector),
    len(categories)
  )
  return index

def c_merge_categories(old_categories_count):
  global categories
  if len(categories) < 1:
    return
  np_centroids = np.array([cat.mean_vector for cat in categories], dtype=np.float32)
  
  merge_map = np.zeros(len(categories), dtype=np.int32)

  c_centroids = np_centroids.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
  c_merge_map = merge_map.ctypes.data_as(ctypes.POINTER(ctypes.c_int))

  similarity_lib.find_categories_to_merge(
      c_centroids, 
      float(categories_similarity), 
      len(categories[0].mean_vector), 
      len(categories), 
      c_merge_map,
      old_categories_count
  )

  categories_to_remove = set()
  
  for idx_child, idx_parent in enumerate(merge_map):
      if idx_child != idx_parent:
          parent_cat = categories[idx_parent]
          child_cat = categories[idx_child]
          
          print(f"merge: {child_cat.category} > {parent_cat.category}")
          
          for img, vec in zip(child_cat.images, child_cat.vectors):
              parent_cat.add_image(img, vec)
              
          categories_to_remove.add(child_cat)

  categories = [cat for cat in categories if cat not in categories_to_remove]

def separate_categories(categories_path):
  vectors = open_json(VECTOR_DATA_DIR)

  global categories
  categories = load_organized_categories(categories_path, vectors)

  old_categories_count = len(categories)

  already_organized = set()
  
  for category in categories:
    already_organized.update(category.images)

  # Cria as categorias
  for i, v in vectors.items():
    if i in already_organized:
      continue
    idx = c_search_similarity(np.array(v, dtype=np.float32))

    if idx != -1:
      obj = categories[idx]
      obj.add_image(i, v)
      print(f"{i} added on {obj.category}")
    else:
      category_name = f"Category_{len(categories)}"
      add_category(i, v, category_name)
      print(f"{category_name} created for {i}")

  c_merge_categories(old_categories_count)


  print("Cleaning unidentified categories")
  unidentified_category = Category("unidentified")

  for category_obj in list(categories):
    if category_obj.images_found <= 1:
      image_unidentified = category_obj.images[0]
      image_unidentified_vector = category_obj.vectors[0]
      
      unidentified_category.add_image(image_unidentified, image_unidentified_vector)

      categories.remove(category_obj)

  if unidentified_category.images_found > 0:
    categories.append(unidentified_category)
    print(f"Cleaned up! {unidentified_category.images_found} isolated images moved to 'unidentified'")

  return categories

if __name__ == "__main__":
  test_path = Path("../organized")
  separate_categories(test_path)