import os
import http.server
import socketserver
import time
import signal
from PIL import Image
from random import choices,randint

"""
this server is a simple captcha system that asks the user to classify some animals into elephants, bears, tigers, tapirs and boars
to access the server:
http://127.0.0.1:30000/
"""

PORT = 30000
RUN_TIME = time.time()
successfull_accesses = 0
total_attempts = 0
solution = ''

def get_captcha_images():
    """
    randomly chooses several pictures of an animal and other pictures of an unwanted animal and prepares them to be displayed on the server
    """
    #choose an animal
    animals = os.listdir('dataset')

    #similiar_animals to avoid because they are hard to tell apart even by humans
    similiar_animals = ['boar','bear','tapir','elephant']
    while True:
        #forcing the two animals to be different
        animal,wrong_animal = choices(animals,k=2)

        #if the animals are similar, iterate again
        if animal in similiar_animals and wrong_animal in similiar_animals:
            continue

        #if animals are different and not similiar, end the loop
        if animal != wrong_animal:
            break
    del animals
    del similiar_animals


    #number of correct and wrong images out of 9
    correct_images_number = randint(3,6)
    wrong_images_number = 9 - correct_images_number

    #choose images of the correct and wrong animals to display
    correct_population = os.listdir(f'dataset/{animal}')
    wrong_population = os.listdir(f'dataset/{wrong_animal}')
    correct_images = choices(correct_population,k = correct_images_number)
    wrong_images = choices(wrong_population,k = wrong_images_number)
    del correct_population
    del wrong_population


    numbers = []
    solution = ""
    wrong_numbers = []
    count = randint(1,9)

    for img in correct_images:
        #display the correct images in random positions
        while count in numbers:
            count = randint(1,9)
        numbers.append(count)
        image = Image.open(f'dataset/{animal}/{img}')
        image.save(f'captcha{count}.jpg')
        image.close()
    del correct_images


    for index in range(1,10):
        #saving the locations of correct and wrong images to save the captcha's solution
        if index in numbers:
            solution+=str(index)
        else:
            wrong_numbers.append(index)
    del numbers


    count = 0
    for index in wrong_numbers:
        #display the images of the wrong animal
        image = Image.open(f'dataset/{wrong_animal}/{wrong_images[count]}')
        image.save(f'captcha{index}.jpg')
        image.close()
        count+=1
    del wrong_numbers


    #instruction.txt is used by the html page to inform the user of which animal they ara supposed to choose    
    text=open('instruction.txt','w')
    text.write(f'choose all images that contain: {animal}')
    text.close()


    #increment total attempts for analytical purposes
    global total_attempts
    total_attempts+=1
    return solution.strip()
    

def handler(signum, frame):
    """
    SIGINT signal handler writing log info before shutting down the server. LOG.txt will contain analytical data for the server's last run
    """
    f = open('LOG.txt','w')
    total_time = round(time.time() - RUN_TIME)
    f.write(f"""   
    total run time:    {total_time} seconds
    total requests:    {total_attempts}
    requests per second:    {round(total_attempts/total_time,4)}
    successfull accesses:    {successfull_accesses}
    successfull accesses per second:    {round(successfull_accesses/total_time,4)}
    """)


    f.close()
    print("server closed, written log on LOG.txt")
    exit(1)

def rename():
    """
    splits animals in a large set into different folders
    """
    animals = os.listdir('dataset')
    animals.remove('images_temp')
    for animal in animals:
        count = 0
        images = os.listdir('dataset/images_temp')
        for image in images:
            if animal in image:
                dst = f'dataset/{animal}/{animal}{count}.jpg'
                src = f'dataset/images_temp/{image}'
                os.rename(src,dst)
                count+=1



        
class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """
        custom GET request handler.
        """
        global solution
        if self.path.find("resetbutton=true") != -1:
            #if the user pressed the reset button and requested a new captcha
            solution = get_captcha_images()
            self.path = ''

        elif self.path.find("true") != -1:
            #checking which images were selected by the user
            checked_captchas_field = self.path.split('&')
            checked_captchas = []

            if len(checked_captchas_field) != 0:
                checked_captchas_field[0] = (checked_captchas_field[0].split('?'))[1]
                for field in checked_captchas_field:
                    #retrieving the images' numbers
                    checked_captchas.append(field[7])
                del checked_captchas_field
                

                #checking the user's solution
                correct_count = len(solution)
                correct_solution = False


                for checked_captcha in checked_captchas:
                    if checked_captcha in solution:
                        checked_captchas.remove(checked_captcha)
                        correct_count-=1
                    # the server will tolerates choosing one wrong image or missing one correct image.
                    if correct_count <= 1:
                        correct_solution = True
                        break
                #if the user's solution is accepted, open the access page
                if correct_solution:
                    self.path = 'access.html'
                    global successfull_accesses
                    solution = get_captcha_images()


                else:
                    #if the user's solution was wrong, create a new captcha
                    solution = get_captcha_images()
                del checked_captchas
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


#handle SIGINT signal
signal.signal(signal.SIGINT, handler)
Handler = MyHttpRequestHandler

#create a captcha on startup
#solution = get_captcha_images()


with socketserver.TCPServer(("", PORT), Handler) as httpd:
    #create server. serve until SIGINT signal is caught
    print("Http Server Serving at port", PORT)
    httpd.serve_forever()
