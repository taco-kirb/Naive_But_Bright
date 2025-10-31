Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> def start_game():
...     if start == "yes" or start == "Yes":
...         print("Initialization Complete")
...     elif start == "no" or start == "No":
...         print("Initialization Failed")
... 
...         
>>> start = input("Would you like to launch the game?: ")
Would you like to launch the game?: yes
>>> start_game()
Initialization Complete
