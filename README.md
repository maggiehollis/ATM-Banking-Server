# Banking Client-Server

## Status Report

### Included Design Requirements
I have completed all the banking functionalities. It enables customers to log it, verify their username and pin, and then withdraw and desposit money. There is error checking in place to ensure the username and pin are in the correct format, are a valid login, and also to make sure no one over draws money.

Once I implemented the ability to connect multiple clients to the server at the same time, I made sure you could not log into the same account from multiple clients. 

### Missing Design Requirements
The main section of this project that I have yet to complete is the deliverables. I haven't started working on the documention yet partly because it seems like a very daunting task. 

Otherwise I believe I have satisfied all of the design requirements with a few caveats:

1. I am unsure if I properly handled errors and sending error messages to the client.
2. My server does not close unless you manually quit it using CTRL-C because it is always ready to connect with more clients.
3. The requirments mention preventing malicious attempts and I am confused as to what preventing them entails.
4. I used threads instead of selectors because after quite a long time trying to incorporate selectors into my program, I was unable to make it work. When I went to research solutions, threads was the most suggested way to support multiple clients.
5. My code is not fully commented.

### Knowledge Gaps

The aspects of the code that I mentioned above are, I believe, the only things in my way of completing this project. If you would prefer I use selectors rather than threads, I would say that is a large gap in understanding that I will need to overcome.

### Moving Forward

Now that we have more time, I would love to try to attend office hours or TA hours to discuss where I am at in the project and how I can complete it. 
