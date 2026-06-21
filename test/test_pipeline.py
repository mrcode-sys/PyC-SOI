import sys
import os

directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if directory not in sys.path:
  sys.path.append(directory)

import pytest
import numpy as np
from pathlib import Path
from core.category_separator import Category, c_search_similarity, categories, open_json, save_json, load_organized_categories, separate_categories

@pytest.fixture(autouse=True)
def run_around_tests():
  global categories
  categories.clear()
  yield

def test_category_creation_and_mean():
  cat = Category("Category_1")
  v1 = np.array([1.0, 0.0, 0.0], dtype=np.float32)
  v2 = np.array([0.0, 1.0, 0.0], dtype=np.float32)
  
  cat.add_image("img1.jpg", v1)
  cat.add_image("img2.jpg", v2)
  
  assert cat.images_found == 2
  assert cat.leader_vector is v1
  expected_mean = np.array([0.5, 0.5, 0.0], dtype=np.float32)
  assert np.allclose(cat.mean_vector, expected_mean)

def test_c_search_similarity_matching():
  global categories
  
  cat = Category("Category_0")
  know_vector = np.ones(1280, dtype=np.float32)
  cat.add_image("base.jpg", know_vector)
  categories.append(cat)
  
  query_vector = np.ones(1280, dtype=np.float32)
  match_index = c_search_similarity(query_vector)
  
  assert match_index == 0

def test_c_search_similarity_no_match():
  global categories
  
  cat = Category("Category_0")
  cat.add_image("base.jpg", np.ones(1280, dtype=np.float32))
  categories.append(cat)
  
  opposite_vector = np.ones(1280, dtype=np.float32) * -1.0
  match_index = c_search_similarity(opposite_vector)
  
  assert match_index == -1

def test_save_open_json():
  json_value = {"image": "vector"}
  save_json(json_value, "test.json")
  value_test = open_json("test.json")
  assert json_value == value_test
  if os.path.exists("test.json"):
      os.remove("test.json")

def test_categories_merge_logic():
    global categories
    
    cat1 = Category("Category_A")
    cat1.add_image("img_a.jpg", np.array([1.0, 0.0], dtype=np.float32))
    categories.append(cat1)
    
    cat2 = Category("Category_B")
    cat2.add_image("img_b.jpg", np.array([1.0, 0.0], dtype=np.float32))
    categories.append(cat2)

    cat2.images_found = 2
    cat1.images_found = 2
    
    i = 0
    while i < len(categories):
        category1 = categories[i]
        j = i + 1
        category_to_merge = None
        while j < len(categories):
            from core.category_separator import c_calculate_similarity, categories_similarity
            if c_calculate_similarity(category1.mean_vector, categories[j].mean_vector) >= categories_similarity:
                category_to_merge = categories[j]
            j += 1
        if category_to_merge:
            for img, vec in zip(category_to_merge.images, category_to_merge.vectors):
                category1.add_image(img, vec)
            categories.remove(category_to_merge)
        else:
            i += 1

    assert len(categories) == 1
    assert categories[0].category == "Category_A"
    assert "img_b.jpg" in categories[0].images


def test_unidentified_cleanup_logic():
    global categories

    cat_stable = Category("Category_Stable")
    cat_stable.add_image("stable1.jpg", np.array([1.0, 0.0], dtype=np.float32))
    cat_stable.add_image("stable2.jpg", np.array([1.0, 0.0], dtype=np.float32))
    categories.append(cat_stable)

    cat_orphan = Category("Category_Orphan")
    cat_orphan.add_image("isolated.jpg", np.array([0.0, 1.0], dtype=np.float32))
    categories.append(cat_orphan)

    unidentified_category = Category("unidentified")
    for category_obj in list(categories):
        if category_obj.images_found <= 1:
            unidentified_category.add_image(category_obj.images[0], category_obj.vectors[0])
            categories.remove(category_obj)
            
    if unidentified_category.images_found > 0:
        categories.append(unidentified_category)

    assert len(categories) == 2
    categories_names = [c.category for c in categories]
    assert "Category_Stable" in categories_names
    assert "unidentified" in categories_names

    unidentified_obj = [c for c in categories if c.category == "unidentified"][0]
    assert "isolated.jpg" in unidentified_obj.images


def test_load_organized_categories_from_disk(tmp_path):
    cat_dir = tmp_path / "Category_X"
    cat_dir.mkdir()
    img_file = cat_dir / "foto_teste.jpg"
    img_file.write_text("fake image content")
    
    unidentified_dir = tmp_path / "unidentified"
    unidentified_dir.mkdir()
    unidentified_file = unidentified_dir / "isolated.jpg"
    unidentified_file.write_text("fake isolated content")

    mock_vectors = {
        "foto_teste.jpg": [0.1, 0.2, 0.3],
        "isolated.jpg": [0.4, 0.5, 0.6]
    }
    
    import core.category_separator
    original_start_model = core.category_separator.start_model
    core.category_separator.start_model = lambda: None 
    loaded = load_organized_categories(tmp_path, mock_vectors)
    
    core.category_separator.start_model = original_start_model

    assert len(loaded) == 2
    names = [c.category for c in loaded]
    assert "Category_X" in names
    assert "unidentified" in names