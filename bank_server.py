#!/usr/bin/env python3
#
# Bank Server application
# Jimmy da Geek


#mention on the document:
#error messages - unsure if I did them right
#my server doesnt close unless manually
#what am I supposed to do about malicious attempts
#I used threads instead of selectors


import socket
import threading
import signal
import sys

HOST = "127.0.0.1"      # Standard loopback interface address (localhost)
PORT = 65432            # Port to listen on (non-privileged ports are > 1023)
ALL_ACCOUNTS = dict()   # initialize an empty dictionary
ACCT_FILE = "accounts.txt"
server_running = True

connected_accounts = []


##########################################################
#                                                        #
# Bank Server Core Functions                             #
#                                                        #
# No Changes Needed in This Section                      #
#                                                        #
##########################################################

def acctNumberIsValid(ac_num):
    """Return True if ac_num represents a valid account number. This does NOT test whether the account actually exists, only
    whether the value of ac_num is properly formatted to be used as an account number.  A valid account number must be a string,
    lenth = 8, and match the format AA-NNNNN where AA are two alphabetic characters and NNNNN are five numeric characters."""
    return isinstance(ac_num, str) and \
        len(ac_num) == 8 and \
        ac_num[2] == '-' and \
        ac_num[:2].isalpha() and \
        ac_num[3:8].isdigit()

def acctPinIsValid(pin):
    """Return True if pin represents a valid PIN number. A valid PIN number is a four-character string of only numeric characters."""
    return (isinstance(pin, str) and len(pin) == 4 and pin.isdigit())

def amountIsValid(amount):
    """Return True if amount represents a valid amount for banking transactins. For an amount to be valid it must be a positive float()
    value with at most two decimal places."""
    return isinstance(amount, float) and (round(amount, 2) == amount) and (amount >= 0)

class BankAccount:
    """BankAccount instances are used to encapsulate various details about individual bank accounts."""
    acct_number = ''        # a unique account number
    acct_pin = ''           # a four-digit PIN code represented as a string
    acct_balance = 0.0      # a float value of no more than two decimal places
    
    def __init__(self, ac_num = "zz-00000", ac_pin = "0000", bal = 0.0):
        """ Initialize the state variables of a new BankAccount instance. """
        if acctNumberIsValid(ac_num):
            self.acct_number = ac_num
        if acctPinIsValid(ac_pin):
            self.acct_pin = ac_pin
        if amountIsValid(bal):
            self.acct_balance = bal
            
    def checkPin(self, pin):
        if self.acct_pin == pin:
            return "T"
        return "F"

    def deposit(self, amount):
        """ Make a deposit. The value of amount must be valid for bank transactions. If amount is valid, update the acct_balance.
        This method returns three values: self, success_code, current balance.
        Success codes are: 0: valid result; 1: invalid amount given. """
        result_code = 0
        if not amountIsValid(amount):
            result_code = 1
        else:
            # valid amount, so add it to balance and set succes_code 1
            self.acct_balance += amount
            self.acct_balance = round(self.acct_balance,2)
        return self, result_code, self.acct_balance

    def withdraw(self, amount):
        """ Make a withdrawal. The value of amount must be valid for bank transactions. If amount is valid, update the acct_balance.
        This method returns three values: self, success_code, current balance.
        Success codes are: 0: valid result; 1: invalid amount given; 2: attempted overdraft. """
        result_code = 0
        if not amountIsValid(amount):
            # invalid amount, return error 
            result_code = 1
        elif amount > self.acct_balance:
            # attempted overdraft
            result_code = 2
        else:
            # all checks out, subtract amount from the balance
            self.acct_balance -= amount
            self.acct_balance = round(self.acct_balance,2)
        return self, result_code, self.acct_balance

def get_acct(acct_num):
    """ Lookup acct_num in the ALL_ACCOUNTS database and return the account object if it's found.
        Return False if the acct_num is invalid. """
    if acctNumberIsValid(acct_num) and (acct_num in ALL_ACCOUNTS):
        return ALL_ACCOUNTS[acct_num]
    else:
        return False

def load_account(num_str, pin_str, bal_str):
    """ Load a presumably new account into the in-memory database. All supplied arguments are expected to be strings. """
    try:
        # it is possible that bal_str does not represent a float, so be sure to catch that error.
        bal = float(bal_str)
        if acctNumberIsValid(num_str):
            if get_acct(num_str):
                print(f"Duplicate account detected: {num_str} - ignored")
                return False
            # We have a valid new account number not previously loaded
            new_acct = BankAccount(num_str, pin_str, bal)
            # Add the new account instance to the in-memory database
            ALL_ACCOUNTS[num_str] = new_acct
            #print(f"loaded account '{num_str}'")
            return True
    except ValueError:
        print(f"error loading acct '{num_str}': balance value not a float")
    return False
    
def load_all_accounts(acct_file = "accounts.txt"):
    """ Load all accounts into the in-memory database, reading from a file in the same directory as the server application. """
    #print(f"loading account data from file: {acct_file}")
    with open(acct_file, "r") as f:
        while True:
            line = f.readline()
            if not line:
                # we're done
                break
            if line[0] == "#":
                # comment line, no error, ignore
                continue
            # convert all alpha characters to lowercase and remove whitespace, then split on comma
            acct_data = line.lower().replace(" ", "").split(',')
            if len(acct_data) != 3:
                print(f"ERROR: invalid entry in account file: '{line}' - IGNORED")
                continue
            load_account(acct_data[0], acct_data[1], acct_data[2])
    print("Finished loading account data")
    return True

def validate(conn,data):
    account = data[1]
    pin = data[2]
    result = "F"
    
    if(account in ALL_ACCOUNTS.keys()):
        result = ALL_ACCOUNTS[account].checkPin(pin)
        if(account in connected_accounts):
            result = "D"
        else:
            connected_accounts.append(account)
    
    conn.sendall(bytes(result, "utf-8"))
    
def deposit(conn,data):
    result = ALL_ACCOUNTS[data[1]].deposit(float(data[2]))
    
    if result[1] == 0:
        conn.sendall(bytes("YD", "utf-8"))
    else:
        conn.sendall(bytes("ND", "utf-8"))

def withdraw(conn,data):
    result = ALL_ACCOUNTS[data[1]].withdraw(float(data[2]))
    
    if result[1] == 0:
        conn.sendall(bytes("YW", "utf-8"))
    else:
        conn.sendall(bytes("NW", "utf-8"))

##########################################################
#                                                        #
# Bank Server Network Operations                         #
#                                                        #
# TODO: THIS SECTION NEEDS TO BE WRITTEN!!               #
#                                                        #
##########################################################

def run_network_server(conn, data):
    data = data.decode("utf-8")
    data = data.split("##")
    
    
    if(data[0]=="END"):
        print(f"Disconnecting from {client_socket.getpeername()}")
        if data[1] in connected_accounts:
            connected_accounts.remove(data[1])
        return False 

    if(data[0]=="Validate"):
        validate(conn, data)
        
    elif(data[0] == "Balance"):
        conn.sendall(bytes(str(ALL_ACCOUNTS[data[1]].acct_balance), "utf-8"))
    
    elif (data[0] == "Deposit"):
        deposit(conn, data)
        
    elif (data[0] == "Withdraw"):
        withdraw(conn,data)
    
    return True

##########################################################
#                                                        #
# Bank Server Demonstration                              #
#                                                        #
# Demonstrate basic server functions.                    #
# No changes needed in this section.                     #
#                                                        #
##########################################################

def demo_bank_server():
    """ A function that exercises basic server functions and prints out the results. """
    # get the demo account from the database
    acct = get_acct("zz-99999")
    print(f"Test account '{acct.acct_number}' has PIN {acct.acct_pin}")
    print(f"Current account balance: {acct.acct_balance}")
    print(f"Attempting to deposit 123.45...")
    _, code, new_balance = acct.deposit(123.45)
    if not code:
        print(f"Successful deposit, new balance: {new_balance}")
    else:
        print(f"Deposit failed!")
    print(f"Attempting to withdraw 123.45 (same as last deposit)...")
    _, code, new_balance = acct.withdraw(123.45)
    if not code:
        print(f"Successful withdrawal, new balance: {new_balance}")
    else:
        print("Withdrawal failed!")
    print(f"Attempting to deposit 123.4567...")
    _, code, new_balance = acct.deposit(123.4567)
    if not code:
        print(f"Successful deposit (oops), new balance: {new_balance}")
    else:
        print(f"Deposit failed as expected, code {code}") 
    print(f"Attempting to withdraw 12345.45 (too much!)...")
    _, code, new_balance = acct.withdraw(12345.45)
    if not code:
        print(f"Successful withdrawal (oops), new balance: {new_balance}")
    else:
        print(f"Withdrawal failed as expected, code {code}")
    print("End of demo!")

##########################################################
#                                                        #
# Bank Server Startup Operations                         #
#                                                        #
# No changes needed in this section.                     #
#                                                        #
##########################################################
def handle_client(client_socket):
    print(f"Accepted connection from {client_socket.getpeername()}")
    
    result = True
    while(result):
        data = client_socket.recv(1024)
        result = run_network_server(client_socket, data)
    
#terminante server by pressing CTRL+C
def signal_handler(signal, frame):
    print("bank server exiting...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    # on startup, load all the accounts from the account file
    load_all_accounts(ACCT_FILE)
    # uncomment the next line in order to run a simple demo of the server in action
    #demo_bank_server()
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(6)  # Listen for incoming connections
    
    while server_running:
        try:
            client_socket, addr = server_socket.accept()  # Accept a new connection

            # Create a new thread to handle the client
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.daemon = True #daemon thread so they won't stop the server from exiting
            client_handler.start()
            
        except KeyboardInterrupt:
            break
    
    server_socket.close()
    

            

