from core.vector_extractor import create_vector
from core.category_separator import separate_categories
from core.folder_manager import copy_files
from pathlib import Path

FILES_DIR = Path("../all")
OUTPUT_FILES = Path("../organized")
create_vector(FILES_DIR)
obj_list = separate_categories()

for obj in obj_list:
    copy_files(FILES_DIR, OUTPUT_FILES, obj.images, obj.category)