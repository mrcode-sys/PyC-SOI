import shutil
import os
import numpy as np
from pathlib import Path
import json
import ctypes

similarity_lib = ctypes.CDLL("lib/category_grouper_lib.so")
similarity_lib.calculate_similarity.restype = ctypes.c_float

similarity_lib.calculate_similarity.argtypes = [
  ctypes.POINTER(ctypes.c_float),
  ctypes.POINTER(ctypes.c_float),
  ctypes.c_int
]


similarity = 0.8 # Aumentar para diminurir variação de imagens iniciais para categoria
#images_similarity = 0.78 Not used
leader_similarity = 0.44 # Aumentar para diminuir variação com imagem original da categoria
categories_similarity = 0.75 #A Aumentar para evitar junção de categorias diferentes

VECTOR_DATA_DIR = "data/images_vectors.json"

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

def open_vectors():

  if not Path(VECTOR_DATA_DIR).is_file():
    return {}

  with open(VECTOR_DATA_DIR, 'r', encoding='utf-8') as file:
    data = json.load(file)

    while isinstance(data, str):
      data = json.loads(data)

    for key in data:
        data[key] = np.array(data[key], dtype=np.float32)
    return data

def calculate_similarity_old1(vector1, vector2):
    dot_product = np.dot(vector1, vector2)
    norm_v1 = np.linalg.norm(vector1)
    norm_v2 = np.linalg.norm(vector2)

    return dot_product / (norm_v1 * norm_v2)

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

logs = {}

def search_similarity_old1(vector):

  for category in categories:
    print(f"DEBUG: {category.images}")
    print(c_calculate_similarity(category.mean_vector, vector))
    if c_calculate_similarity(category.mean_vector, vector) >= similarity:
      return category  
  return False

def search_similarity(vector):

  for category in categories:
    #print(f"DEBUG: {category.images}")
    #print(c_calculate_similarity(category.mean_vector, vector))
    if c_calculate_similarity(category.leader_vector, vector) >= leader_similarity:
      if c_calculate_similarity(category.mean_vector, vector) >= similarity:
        return category  
  return False

def search_similarity_old(vector): #old function

  for category in categories:
    #print(f"DEBUG: {category.images}")
    #print(c_calculate_similarity(category.leader_vector, vector))
    if c_calculate_similarity(category.leader_vector, vector) >= leader_similarity:
      for category_vector in category.vectors:
        #print(c_calculate_similarity(category_vector, vector))
        if c_calculate_similarity(category_vector, vector) >= images_similarity:
          return category  
  return False

def separate_categories():
  vectors = open_vectors()

  for i, v in vectors.items():
    obj = search_similarity(v)
    if obj:
      obj.add_image(i, v)
      print(f"{i} added on {obj.category}")
    else:
      category_name = f"Category_{len(categories)}"
      add_category(i, v, category_name)
      print(f"{category_name} added for {i}")

  i = 0
  while i < len(categories):
    category1 = categories[i]
    category1_mean = category1.mean_vector

    j = i + 1

    best_similarity = categories_similarity
    category_to_merge = None

    while j < len(categories):
      category2 = categories[j]
      category2_mean = category2.mean_vector

      categories_mean_similarity = c_calculate_similarity(category1_mean, category2_mean)

      #print(f"DEBUG\n{category1.category}\n{category2.category}\n{categories_mean_similarity}")

      if categories_mean_similarity >= best_similarity:
        best_similarity = categories_mean_similarity
        category_to_merge = category2
      
      j += 1

    if category_to_merge is not None:
      print(f"merge: {category_to_merge.category} > {category1.category} (Highest similarity: {best_similarity:.2f})")

      for img, vec in zip(category_to_merge.images, category_to_merge.vectors):
        category1.add_image(img, vec)


      category1_mean = category1.mean_vector
      categories.remove(category_to_merge)
    else:
      i += 1


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
  separate_categories()