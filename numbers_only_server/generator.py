from captcha.image import ImageCaptcha
from random import choice

def get_random_string(length=4,digit_only=True):
    """
    generates a random string. the length paramter control the number of characters while the digit_only control whether a-z characters are included
    """
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    #get chars from a-z
    if not digit_only:
        for i in range(26):
            numbers.append(chr(ord('a') +  i))
    str = ''
    for _ in range(length):
        str += choice(numbers)
    return str

def get_captcha_image(length=4,digit_only=True):
    """
    creates a captcha image using get_random_string. writes the image on disk and returns its solution
    """
    image = ImageCaptcha(120, 100, fonts=['OpenSans-Regular.ttf'])
    s = get_random_string(length,digit_only)
    image.write(s, "out.png")
    return s

