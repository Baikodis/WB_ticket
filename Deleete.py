import os
import time

# здесь хранятся pdf файлы
folder_path = "temp/"
temp_dir = 'temp'

if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

while True:
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            if time.time() - os.path.getctime(file_path) > 60 * 60 * 24:  # с момента создания прошли сутки
                os.remove(file_path)
    time.sleep(82800)  # каждые 23 часа
