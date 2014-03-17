import socket, select, string, sys, threading, time 
TIME_OUT = 3600

def prompt() :
    sys.stdout.write('>')
    sys.stdout.flush()
 
def logout(sock): 
    sock.send("logout")
    sock.send("\n")
    sys.exit()


#main function
def main(): 
     
    host = sys.argv[1]
    port = int(sys.argv[2])
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
     
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        sys.exit()
     
    #prompt()
    
    logged_in = False 
    while 1:
        socket_list = [sys.stdin, s]
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
        try: 
            for sock in read_sockets:
                if sock == s:
                    data = sock.recv(4096)
                    if not data :
                        curr_time.cancel()
                        sys.exit()
                    else :
                        #sys.stdout.write(data)
                        prompt()
                        print data
                        if "You are logged in" in data:
                            logged_in = True
                            curr_time = threading.Timer(TIME_OUT, logout, [sock]) 
                            curr_time.start()

                else :
                    if logged_in == True:
                        curr_time.cancel()
                        curr_time = threading.Timer(TIME_OUT, logout, [sock]) 
                        #curr_time.start()
                    msg = sys.stdin.readline()
                    s.send(msg)
                    #prompt()
        except:
            #curr_time.cancel()
            sock.send("logout")
            sys.exit()
main()
