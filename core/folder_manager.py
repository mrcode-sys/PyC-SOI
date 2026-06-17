import os
import shutil

def copy_files(files_dir, output_dir, files, dir):
  output_img_dir = os.path.abspath(output_dir)

  input_dir = os.path.abspath(files_dir)
  output_dir = os.path.abspath(os.path.join(output_dir, dir))

  if not os.path.exists(input_dir):
    print("No input folder")
    return False

  for file in files:
    input_file_dir = os.path.join(input_dir, file)
    output_file_dir = os.path.join(output_dir, file)

    if not os.path.exists(input_file_dir):
      continue

    if not os.path.exists(output_dir):
      os.makedirs(output_dir)

    shutil.copy(input_file_dir, output_file_dir)