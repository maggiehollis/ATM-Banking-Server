### Acknowledgements
Starter code was provided to me by my professor Brant Cheikes


# Overview
The server is always ready for incoming connections. 

Upon connection, the client sends a message in correct format with all necessary information for the requested action (grammar detailed below). The first message must be to login otherwise the server will not allow any other actions to take place. For all messages (assuming the client is logging in or has previously logged in) the server processes the message and responds with a success code or any requested information. The server is always listening for incoming messages until the client requests to end the connection.

Due to the nature of this client-server application, someone may attempt to access the same account from two different clients. In order to prevent this, the server keeps track of all the accounts that are currently connected in an array. Whenever a new client attempts to log into an account, the server checks to make sure the account is not in the array of connected accounts. If it is, the server responses with an error code (deatiled below). If the account is not already logged in, the account is added to the array of connected accounts and the server responds with a success code.

# ABNF Documentation

; Bank Server Message Grammar

; This grammar defines the syntax for sending messages to the Bank Server and the result codes that will be returned

## Send to Server

message = action_request *action_detail

### ; Action_request part of message

action_request = "END" / "Validate" / "Balance" / "Desposit" / "Withdraw"

### ; Action_detail part of message

; Do not include action_detail if "END" or "Balance"

; Use this option if "Depsoit" or "Withdraw"

action_detail = "##" 1\*DIGIT \*["."] \*DIGIT

; Use this option if "Validate"

action_detail =/ "##" 2ALPHA "-" 5DIGIT "##" 4DIGIT

## Recieve from Server

return_message = r_mes

### ; R_mes part of message

; For "Validate", "Deposit", "Withdraw"

return_message = 1DIGIT

; For "Balance"

return_message =/ 1\*DIGIT "." 1\*DIGIT

; No message for "END", disconnected


; If response from "Validate"

    0 = Pin and account match, success

    1 = Pin and account do not match, no success

    2 = Already logged in elsewhere, no success

    3 = Wrong format, no success

; If response from "Deposit"

    0 = Valid amount to deposit, success

    1 = Not valid amount to deposit, no success

    3 = Wrong format, no success

; If response from "Withdraw"

    0 = Valid amount to withdraw, success

    1 = Not valid amount to withdraw, no success

    2 = Attempted overdraw, no success

    3 = Wrong format, no success

# Message Components

Each message sent to the server consists of the type of request being made (Balance, Withdraw, etc.) followed by any necessary information.

If the request is to validate/login the message includes "Validate", the account number, and pin

If the request is to get the balance, the message is simply "Balance"

If the request is to deposit, the message is "Deposit" and the amount to be deposited

If the request is to withdraw, the message is "Withdraw" and the amount to be withdrawn

If the request is to end the connection, the message is simply "END"

For messages with multiple components, each part is divided using an "##"

# Example Messages and Communication

An example of a validation/login request is:

    send: "Validate"##"zz-99999"##9999

    response: 0

An example of a deposit request is:

    send: "Deposit"##12.5

    response: 0

An example of a withdrawal request is:

    send: "Withdraw"##20

    response: 0

An example of an incorrect withdrawal request is:

    send: "Withdraw"##"zz-99999"##20

    response: 3

An example of a balance request is:

    send: "Balance"

    response: [the balance]

An example of an END request is:

    send: "END"

    response: [disconnected]

# What I've done since Part 1

1. I adjusted my code to not send the account number in every request
2. I created standarized error codes
3. I wrote out all the documentation (including ABNF grammar)
4. I cleaned up my code and provided more comments