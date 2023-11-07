#!/usr/bin/env python3
#
# Automated Teller Machine (ATM) client application.

import socket

HOST = "127.0.0.1"      # The bank server's IP address
PORT = 65432            # The port used by the bank server
                                                     
# ATM Client Network Operations      
def send_to_server(sock, msg):
    """ Given an open socket connection (sock) and a string msg, send the string to the server. """
    return sock.sendall(msg.encode('utf-8'))

def get_from_server(sock):
    """ Attempt to receive a message from the active connection. Block until message is received. """
    msg = sock.recv(1024)
    return msg.decode('utf-8')

def login_to_server(sock, acct_num, pin):
    """ Attempt to login to the bank server. Pass acct_num and pin, get response, parse and check whether login was successful. """
    send_to_server(sock, "Validate##" + str(acct_num) + "##" + str(pin))
    return get_from_server(sock)

def get_login_info():
    """ Get info from customer."""
    acct_num = ""
    pin = ""
    
    acct_num = input("Please enter your account number: ")
    check = isinstance(acct_num, str) and len(acct_num) == 8 and acct_num[2] == '-' and acct_num[:2].isalpha() and acct_num[3:8].isdigit()
    
    while(not check):
        acct_num = input("That was not valid. Please Try again: ")
        check = isinstance(acct_num, str) and len(acct_num) == 8 and acct_num[2] == '-' and acct_num[:2].isalpha() and acct_num[3:8].isdigit()
        
    pin = input("Please enter your four digit PIN: ")
    check = isinstance(pin, str) and len(pin) == 4 and pin.isdigit()
    
    while(not check):
        pin = input("That was not valid. Please try again: ")
        check = isinstance(pin, str) and len(pin) == 4 and pin.isdigit()
        
    return acct_num, pin

def process_deposit(sock):
    """ Processes a deposit """
    bal = get_acct_balance(sock, acct_num)
    
    check = False
    amt = input(f"How much would you like to deposit? (You have ${bal} available)\n")
    
    while(not check):
        try:
            amt = float(amt)
            check = True
        except:
            amt = input(f"That was not valid. Please try again. (You have ${bal} available)\n")
    
    send_to_server(sock, "Deposit##"+ str(amt))
    success = get_from_server(sock)
    # communicate with the server to request the deposit, check response for success or failure.
    
    bal = get_acct_balance(sock)
    if success == "0":
        print(f"Deposit transaction completed. (You have ${bal} available)")
    else:
        print(f"Desposit transaction was unable to be completed. (You have ${bal} available)")
        process_deposit(sock)
    return

def get_acct_balance(sock):
    """ Ask the server for current account balance. """
    send_to_server(sock, "Balance" )
    return get_from_server(sock)

def process_withdrawal(sock):
    """ Processes a withdrawl """
    bal = get_acct_balance(sock)
    check = False
    
    amt = input(f"How much would you like to withdraw? (You have ${bal} available)\n")
    
    while(not check):
        try:
            amt = float(amt)
            check = True
        except:
            amt = input(f"That was not valid. Please try again (You have ${bal} available)\n")
        
    
    send_to_server(sock, "Withdraw##" + str(amt))
    success = get_from_server(sock)
    
    # communicate with the server to request the withdrawal, check response for success or failure.
    
    bal = get_acct_balance(sock)
    if success == "0":
         print(f"Withdrawal transaction completed. (You have ${bal} available)")
    else:
        print(f"Withdrawal transaction was unable to be completed. You entered an invalid amount. (You have ${bal} available)")
        process_withdrawal(sock)
    return

def process_customer_transactions(sock): #
    """ Ask customer for a transaction, communicate with server. TODO: Revise as needed. """
    while True: #what do they want to do 
        print("Select a transaction. Enter 'd' to deposit, 'w' to withdraw, or 'x' to exit.")
        req = input("Your choice? ").lower()
        if req not in ('d', 'w', 'x'):
            print("Unrecognized choice, please try again.")
            continue
        if req == 'x':
            # if customer wants to exit, break out of the loop
            break
        elif req == 'd':
            process_deposit(sock)
        else:
            process_withdrawal(sock)

def run_atm_core_loop(sock):
    """ Given an active network connection to the bank server, run the core business loop. """
    acct_num, pin = get_login_info() #asks customer to log in
    validated = login_to_server(sock, acct_num, pin) #try to log in
    if validated == "0": 
        print("Thank you, your credentials have been validated.")
    elif validated == "2":
        print("You are already logged in on another device.")
        send_to_server(sock, "END")
        return False 
    elif validated == "3":
        print("Data was sent in the wrong format")
        send_to_server(sock, "END")
        return False 
    else: #exit out if incorrect sign in
        print("Account number and PIN do not match. Terminating ATM session.")
        send_to_server(sock, "END")
        return False 
    process_customer_transactions(sock)
    print("ATM session terminating.")
    send_to_server(sock, "END" )
    return True

def run_network_client():
    """ This function connects the client to the server and runs the main loop. """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            run_atm_core_loop(s)

    except Exception as e:
        print(f"Unable to connect to the banking server - exiting...")
        

if __name__ == "__main__":
    print("Welcome to the ACME ATM Client, where customer satisfaction is our goal!")
    run_network_client()
    print("Thanks for banking with us! Come again soon!!")