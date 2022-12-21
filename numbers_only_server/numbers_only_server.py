import http.server
import socketserver
from generator import get_captcha_image
import time
import signal

"""
this server generates and displays captcha images using the captcha library
the server runs on 127.0.0.1, port 10000
"""




def handler(signum, frame):
    """
    SIGINT signal handler writing log info before shutting down the server. LOG.txt will contain analytical data for the server's last run
    """
    f = open('LOG.txt','w')
    total_time = round(time.time() - RUN_TIME)
    f.write(f"""total run time:    {total_time} seconds
total requests:    {total_attempts}
requests per second:    {round(total_attempts/total_time,4)}
requests per second without the hard coded latency:    {round(total_attempts/(total_time - total_attempts * (0.6)),4)}
successfull accesses:    {successfull_accesses}
successfull accesses per second:    {round(successfull_accesses/total_time,4)}
successfull accesses per second without the hard coded latency:    {round( successfull_accesses / (total_time - total_attempts * (0.6)),4)}""")
    f.close()
    print("server closed, written log on LOG.txt")
    exit(1)


#constants and globals
PORT = 10000
RUN_TIME = time.time()
successfull_accesses = 0
total_attempts = 0
solution = ''

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """
        custom GET request handler.
        """
        global solution
        global total_attempts
        global successfull_accesses
        if total_attempts == 0:
        #get captcha on first run
            sol = get_captcha_image()
            total_attempts+=1
            solution = sol
        else:
            #if the image was not modified, retrive its solution
            sol = solution
        if self.path.find("input")!=-1:
            #checking the value of the user's input
            start = 8
            if self.path.find("index.html")!=-1:
                start += 10
            field=''
            for i in self.path[start:]:
                field+=i
            if field == sol:
                #comparing it with the captcha's solution. on success, takes the user to the service page
                successfull_accesses+=1
                self.path = 'access.html'
            else:
                #on fail, create a new captcha
                solution = get_captcha_image()
                total_attempts+=1
        elif self.path.find("click=true") !=-1 or self.path == "/out.png":
            #if the user presses the captcha reset button
            solution = get_captcha_image()
            total_attempts+=1
            #wait 0.6 seconds to wait for the new captcha image to be created and written on disk, otherwise the server might display the old image
            time.sleep(0.6)
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


#handle SIGINT signal
signal.signal(signal.SIGINT, handler)
Handler = MyHttpRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    #create server. serve until SIGINT signal is caught
    print("Http Server Serving at port", PORT)
    httpd.serve_forever()