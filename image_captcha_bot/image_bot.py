from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException



import signal
import time
import io
from PIL import Image
from image_model_run import predict

"""
uses selenium to automate captcha solving on https://services.just.edu.jo/courseschedule/
"""

total_attempts = 0
successful_accesses = 0

def handler(signum, frame):
  #handle INT signals and logs the run's results 
  f = open('UNI_LOG.txt','w')
  f.write(f'total: {total_attempts}\nsuccessful accesses: {successful_accesses}\naccuracy:{round(successful_accesses/total_attempts,2) * 100}%\nrun time: {round(time.time() - run_time,2)} seconds')
  f.close()
  exit(1)



def download_image(cap,index):
    """
    search a page for a specific element and download it on disk
    """
    img = cap.screenshot_as_png
    img_file = io.BytesIO(img)
    im = Image.open(img_file)
    im = im.convert('RGB')
    im.save(f'captcha{index}.jpg')


    

def solve_Captcha(): 
    """
    calls download_image to download the captcha image, calls predict to get the model's solution to the captcha and writes it on the page's input field 
    """
    try:  
      show_box = browser.find_element(By.ID, 'showbut')
    except NoSuchElementException:
      browser.get('http://127.0.0.1:30000/')
      show_box = browser.find_element(By.ID, 'showbut')



    show_box.click()
    answer = []

    #problem here
    text = open('../image_captcha_server/instruction.txt','r')
    animal = text.read().split(': ')[1]
    send_button = browser.find_element(By.ID,'submitbutton')

    for index in range(1,10):
        cap = browser.find_element(By.ID, f'captcha{index}')
        download_image(cap,index)
        if animal == predict(f'captcha{index}.jpg'):
            answer.append(index)
    
    for index in answer:
        image = browser.find_element(By.ID,f'captcha{index}')
        image.click()
        #slowing down only for human observation..
        time.sleep(0.5)


    send_button.click()



run_time = time.time()
browser = webdriver.Chrome('chromedriver.exe')
browser.get('http://127.0.0.1:30000/')

while True:
  solve_Captcha()
  time.sleep(1)
  total_attempts += 1
