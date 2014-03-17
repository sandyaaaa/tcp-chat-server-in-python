import socket, select, sys, time 
BUF = 2048
BLOCK_TIME = 60 
LAST_HOUR = 1000 #3600
TIME_OUT = 1800
PORT = int(sys.argv[1])

#list of current users
current_users = []

#sockfd : user
current_user_names = {}

#user : sockfd
user_sock = {}

# user : password
user_password = {}

# username : time 
login_time = {}

# ip : time 
block_user = {}

# user : []
users_blocklist = {}

#user : offline message
offline_message = {}

# 
file = open('user_pass.txt', "r")
for pair in file:
    (user, pw) = pair.split()
    user_password[user] = pw
    users_blocklist[user] = []
    offline_message[user] = []


def register(sockfd): 
    sockfd.send("What user name do you want?")
    user_name_new = sockfd.recv(BUF)
    un_new = user_name_new.split()
    user_name_new = un_new[0]
    not_pass = True
    while not_pass: 
        sockfd.send("What password do you want? ")
        password_new = sockfd.recv(BUF)
        sockfd.send("Confirm password by retyping. ")
        password_new_2 = sockfd.recv(BUF)
        if not password_new == password_new_2:
            sockfd.send("Those passwords don't match. ")
            sockfd.send("Retry. ")
        else:
            sockfd.send("Okay you are now registered! ")
            password = password_new.split()
            password_new = password[0]
            user_password[user_name_new] = password_new
            users_blocklist[user_name_new] = []
            offline_message[user_name_new] = []  
            sockfd.send("Now log back in!")
            sockfd.close()
            break

def authorization(sockfd, addr):
    menu_items = """    
Choose an option:
whoelse             wholasthr
broadcast           message
block               unblock
logout\n"""
    sockfd.send("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
    sockfd.send("Welcome to the CSEE 4119 Chat Room\n")
    sockfd.send("Sign up or login? [1/2]\n")
    resp = sockfd.recv(BUF)
    resp_arr = resp.split()
    resp = resp_arr[0]
    if resp == "1":
        register(sockfd)
    else: 
        while 1:
            sockfd.send("Enter username: ")
            username = sockfd.recv(BUF)
            if not username == "\n":
                username = username.split()
                username = username[0]
                if still_blocked(sockfd, addr):
                    sockfd.send("You are currently blocked from logging in. ")
                    sockfd.close()
                    return False
                elif username in user_sock:
                    sockfd.send("This username is logged in already. ")
                    continue
                elif username in user_password:
                    for i in range(0,3):
                        sockfd.send("Enter password:")
                        password = sockfd.recv(BUF)
                        if not password == "\n":
                            password = password.split()
                            password = password[0]
                            if user_password[username] == password:
                                sockfd.send("Welcome to simple chat server!\n")
                                you_have_mail(username, sockfd)
                                sockfd.send("Here are your commands. Be precise!")
                                sockfd.send(menu_items)
                                current_user_names[sockfd] = username
                                user_sock[username] = sockfd
                                print "ahsfs"
                                login_time[sockfd] = time.time()
                                current_users.append(sockfd)
                                login_time[username] = time.time()
                                return True
                    sockfd.send("You failed three times to give the right passcode. \n")
                    sockfd.send("You will be blocked for 60 seconds. \n")
                    block_user[addr[0]] = time.time()
                    print addr[0]
                    sockfd.close()
                    return False

def you_have_mail(username, usr_sockfd):
    temp_messages = offline_message[username]
    if not len(temp_messages)==0:
        usr_sockfd.send("\nYou have some offline messages.\n")
        for item1 in temp_messages:
            usr_sockfd.send(item1)
            usr_sockfd.send("\n")
    offline_message[username] = []     

def logout(sockfd):
    print current_user_names[sockfd]
    temp = current_user_names[sockfd]
    del current_user_names[sockfd]
    del user_sock[temp]
    current_users.remove(sockfd)
    sockfd.close()

def still_blocked(sockfd, addr):
    if block_user.has_key(addr[0]):
        curr_time = time.time()
        print curr_time - block_user[addr[0]]
        if (curr_time - block_user[addr[0]]) <= 60:
            return True
        else:
            sockfd.send("Welcome back! Your IP address is no longer blocked. \n")
            del block_user[addr[0]]
    return False

#do chat con like thing for this 
def menu(sockfd):
    try:
        try:
            resp =  sockfd.recv(BUF)
            new = resp.split()
            option = new[0]
            if (option == "whoelse"):
                whoelse(sockfd)

            elif (option == "wholasthr"):
                wholasthr(sockfd)

            elif (option == "broadcast"):
                index = resp.find(" ")
                p = resp[0:index]
                message = resp[index+1:len(resp)]
                broadcast(sockfd, message) 

            elif (option == "logout"):
                logout(sockfd)

            elif (option == "message"):
                print "start"
                index = resp.find(" ")
                p1 = resp[0:index]
                p2 = resp[index+1: len(resp)]
                index2 = p2.find(" ")
                p3 = p2[0:index2]
                p4 = p2[index2+1: len(p2)]
                print "check"
                if not_blocked(sockfd, p3):
                    print "poop"
                    pm_message(p3, p4, sockfd)
                else:
                    sockfd.send("You can't send a message to a user whos blocked you ")
                    print "failed" 
            elif (option == "block"):
                index = resp.find(" ")
                p = resp[0:index]
                block_user = resp[index+1:len(resp)]
                block(sockfd, block_user)

            elif (option == "unblock"):
                index = resp.find(" ")
                p = resp[0:index]
                unblock_user = resp[index+1:len(resp)]
                unblock(sockfd, unblock_user) 
            else:
                sockfd.send("That's not a command.")
        finally:
            print "served", sockfd
    except:
        pass


def pm_message(user, message, original_sockfd):
    print is_online(user, original_sockfd)
    if is_online(user, original_sockfd):
        temp_usr = user_sock[user]
        temp_usr.send(current_user_names[original_sockfd] + " says: ")
        temp_usr.send(message)
    else:
        if user in user_password: 
            original_sockfd.send("That user is not online right now!")
            original_sockfd.send(" But he will get your message when he signs in.")
            usr = current_user_names[original_sockfd]
            new_mess = usr + " said "
            new_mess = new_mess + message
            offline_message[user].append(new_mess)
            print "Done"

        else:
            original_sockfd.send("We do not know that this user exists. ")


def not_blocked(sockfd, user_toblock):
    print "bob"
    us = current_user_names[sockfd]
    print us
    user_you_block = user_toblock.split()
    print user_you_block
    if user_you_block[0] not in users_blocklist:
        return True
    temp = users_blocklist[user_you_block[0]]
    print temp
    if us in temp:
        return False
    else:
        return True

def is_online(username, original_sockfd):
    if username in current_user_names.values():
        return True
    else:
        return False

def whoelse(sockfd): 
    if len(current_user_names) == 1:
        sockfd.send("No one else is here!\n")
    else:
        sockfd.send("Other online users are:\n")
        for keyval in current_user_names:
            if not current_user_names[keyval] == current_user_names[sockfd]:
                sockfd.send(current_user_names[keyval] + "\n")


def wholasthr(sockfd):
    curr_time = time.time()
    sockfd.send("These users have been active in the last hour: \n")
    for user in login_time.iterkeys():
        if (curr_time - login_time[user]) <= LAST_HOUR:
            sockfd.send(user + "\n")

#send a message to all 
def broadcast(sockfd, message):
    for socket in current_users:
        if socket != servsock and socket != sockfd:
            try :
                socket.send(current_user_names[sockfd] + " says: ")
                socket.send(message)
            except :
                socket.close()
                current_users.remove(socket)
        elif socket != servsock and socket == sockfd:
                socket.send("You said: ")
                socket.send(message)


def block(sockfd, user_toblock):
    print current_user_names[sockfd]
    temp_user = user_toblock.split()
    if current_user_names[sockfd] == temp_user[0]:
        sockfd.send("Error! You cannot block yourself!")
    else: 
        temp = users_blocklist[current_user_names[sockfd]]
        temp.append(temp_user[0])
        users_blocklist[current_user_names[sockfd]] = temp 
        temp_mess = "You have successfully blocked " + temp_user[0] 
        temp_mess = temp_mess + "from sending you messages."
        sockfd.send(temp_mess)


def unblock(sockfd, user_to_unblock):
    user_to_unblock = user_to_unblock.split()
    user_to_unblock = user_to_unblock[0]
    try:
        temp = users_blocklist[current_user_names[sockfd]]
        temp.remove(user_to_unblock)
        users_blocklist[current_user_names[sockfd]] = temp 
    except:
        pass

servsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servsock.bind(('', PORT))
servsock.listen(10)
current_users.append(servsock)

while 1:
    read_sockets,write_sockets,error_sockets = select.select(current_users,[],[])
    for sock in read_sockets:
        if sock == servsock:
            sockfd, addr = servsock.accept()
            authorization(sockfd, addr)
        else: 
            try:
                menu(sock)
            except: 
                sock.close()
servsock.close()
