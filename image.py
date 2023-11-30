import os
from PIL import Image, ImageFilter


def blur_image_new(order, src_filename):

    with Image.open(os.path.join(f'src_files/{order}', src_filename)) as img:
        img.load()
        new_img = img.filter(ImageFilter.GaussianBlur(5))
        os.remove(os.path.join(f'src_files/{order}', src_filename))
        new_img.save(os.path.join(f'src_files/{order}', src_filename))


# for file in os.listdir('temp_files/'):
#     print(file)
#     blur_image(file)
