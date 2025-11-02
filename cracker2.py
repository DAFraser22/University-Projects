import zipfile
import argparse
from tqdm import tqdm
import string
import collections

print(r"""

  _______             ______ _ _        _____                                    _    _____                _             
 |___  (_)           |  ____(_) |      |  __ \                                  | |  / ____|              | |            
    / / _ _ __ ______| |__   _| | ___  | |__) |_ _ ___ _____      _____  _ __ __| | | |     _ __ __ _  ___| | _____ _ __ 
   / / | | '_ \______|  __| | | |/ _ \ |  ___/ _` / __/ __\ \ /\ / / _ \| '__/ _` | | |    | '__/ _` |/ __| |/ / _ \ '__|
  / /__| | |_) |     | |    | | |  __/ | |  | (_| \__ \__ \\ V  V / (_) | | | (_| | | |____| | | (_| | (__|   <  __/ |   
 /_____|_| .__/      |_|    |_|_|\___| |_|   \__,_|___/___/ \_/\_/ \___/|_|  \__,_|  \_____|_|  \__,_|\___|_|\_\___|_|   
         | |                                                                                                             
         |_|                                                                                                             
                                                                                                                                                                                                                                                                                                                                                                                                                                   
""")

#Extracts the contents of zip file if provided password is correct
def extract_zip(zip_file, password):
    try:
        zip_file.extractall(pwd=password.encode())
        return True
    except Exception:
        return False

#Reads in the wordlist file and attempts to crack target zip file
def crack_zip(zip_file_path, wordlist_path):
    passwords = []
    with open(wordlist_path, 'r', encoding="latin-1") as wordlist_file:
        #Reads passwords into the array until no lines are left in the file
        while True:
            line = wordlist_file.readline()
            passwords.append(line)
            if not line:
                break
            
    with zipfile.ZipFile(zip_file_path) as zip_file:
        total_passwords = len(passwords)
        password_found = False
        with tqdm(total=total_passwords, unit='passwords', desc='Cracking Passwords') as pbar:
            for password in passwords:
                #Removes leading and trailing whitespaces if applicable
                password = password.strip()  
                if extract_zip(zip_file, password):
                    password_found = True
                    #If the password is found, sets progress bar to 100% and breaks the loop
                    pbar.update(total_passwords - pbar.n)
                    return password
                else:
                    #Updates progress bar by 1 password attempt
                    pbar.update(1)
 
#Evaluates the strength of found password based on length and character variety 
def check_strength(password):
    lower_count = upper_count = number_count = special_count = length = 0

    for char in list(password):
        if char in string.ascii_lowercase:
            lower_count += 1
        elif char in string.ascii_uppercase:
            upper_count += 1
        elif char in string.digits:
            number_count += 1
        else:
            special_count += 1
    #Keeps track of which characters are repeated in the password
    countletter = collections.Counter(password)
    repeated = [i for i in countletter if countletter[i] > 1]           
        
    strength = 0

    #Password strength requirements are evaluated and give a score out of 6
    if lower_count >= 1:
        strength += 1
    if upper_count >= 1:
        strength += 1
    if number_count >= 1:
        strength += 1
    if special_count >= 1:
        strength += 1
    if len(password) >= 12:
        strength += 1 
    if len(repeated) == 0:
        strength += 1
            
    print(f"""Your password has:- 
        {lower_count} lowercase letter(s) 
        {upper_count} UPPERCASE LETTER(S)
        {number_count} Digit(s)
        {special_count} Special Character(s)
        {len(password)} Character(s) in Total
        Repeated letter(s) : {repeated}
        Password score: {strength}/6""")        
 
#Defines arguments necessary to run the script (Program, wordlist and zip file name) 
def main():
    parser = argparse.ArgumentParser(description='Zip file password cracker')
    parser.add_argument('wordlist', help='Path to the wordlist file')
    parser.add_argument('zipfile', help='Path to the zip file')
    args = parser.parse_args()
    
    found = crack_zip(args.zipfile, args.wordlist)
    print("Password Found: ", found, "\n")
    if not found:
        print("Your password was not found in the wordlist. Good Job!")
    else:
        check_strength(found)

#Ensures the main function can only be executed if run from the command terminal
if __name__ == "__main__":
    main()