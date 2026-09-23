""" Manual Hash py """

import werkzeug.security

def manual_hash():
    """A manual hash function for admin accounts"""
    password = input("Enter the password to hash: ")
    hashed_pw = werkzeug.security.generate_password_hash(password)
    print("")
    print(hashed_pw)

if __name__ == "__main__":
    manual_hash()
