from PIL import Image
import pygame as pg
import os

def make_white_bg_transparent(img_file):
    pic = Image.open(img_file)

    pic = pic.convert('RGBA')  # 转为RGBA模式
    width, height = pic.size
    array = pic.load()  # 获取图片像素操作入口
    for i in range(width):
        for j in range(height):
            pos = array[i, j]  # 获得某个像素点，格式为(R,G,B,A)元组
            # 如果R G B三者都大于240(很接近白色了，数值可调整)
            isEdit = (sum([1 for x in pos[0:3] if x > 230]) == 3)
            if isEdit:
                # 更改为透明
                array[i, j] = (255, 255, 255, 0)

    # 保存图片
    pic.save('result.png')

def get_image(sheet, x, y, width, height, colorkey=(0,0,0), scale=1):
    image = pg.Surface([width, height])
    rect = image.get_rect()

    image.blit(sheet, (0, 0), (x, y, width, height))
    image.set_colorkey(colorkey)
    image = pg.transform.scale(image,
                               (int(rect.width * scale),
                                int(rect.height * scale)))
    return image

def load_image(file_path, scale=1):
    img = pg.image.load(file_path).convert_alpha()
    rect = img.get_rect()
    img = pg.transform.scale(img,
                               (int(rect.width * scale),
                                int(rect.height * scale)))

    return img


def load_all_images(image_container, directory, accept=('.png', '.jpg', '.bmp', '.gif')):
    """loads all imgs in dir into image_contrainer"""
    for pic in os.listdir(directory):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pg.image.load(os.path.join(directory, pic))
            img = img.convert_alpha()
            image_container[name] = img

def load_all_sounds(sounds_container, directory, accept=('.ogg')):
    """loads all imgs in dir into image_contrainer"""
    for sound in os.listdir(directory):
        name, ext = os.path.splitext(sound)
        if ext.lower() in accept:
            sounds_container[name] = pg.mixer.Sound(os.path.join(directory, sound))



def save_pygame_img(img, file_name):
    pg.image.save(img, file_name)

if __name__ == '__main__':
    make_white_bg_transparent('left.png')