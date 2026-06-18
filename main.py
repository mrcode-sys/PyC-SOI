from core.vector_extractor import create_vector
from core.category_separator import separate_categories
from core.folder_manager import copy_files, move_files
from pathlib import Path

OUTPUT_FILES = Path("../organized").resolve()

def main():
    while True:
        user_input_dir = input("Input directory (c to close): ").strip()

        if user_input_dir.lower() == "c":
            print("closing")
            return
        
        FILES_DIR = Path(user_input_dir).resolve()

        if not FILES_DIR.is_dir():
            print("Invalid directory")
            continue
        break

    while True:
        action = input("Copy or move (c to close): ")

        if action == "c":
            print("closing")
            return

        match action:
            case "move":
                should_move = True
            case "copy":
                should_move = False
            case _:
                print("Invalid argument")
                continue
        break


    print(f"\nProcessing images from: {FILES_DIR}")
    print(f"Target directory: {OUTPUT_FILES}\n")

    create_vector(FILES_DIR)
    obj_list = separate_categories(OUTPUT_FILES)

    for obj in obj_list:
        if should_move:
            move_files(FILES_DIR, OUTPUT_FILES, obj.images, obj.category)
        else:
            copy_files(FILES_DIR, OUTPUT_FILES, obj.images, obj.category)

main()