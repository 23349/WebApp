from werkzeug.security import generate_password_hash

def manual_hash():
    password = input("Enter the password to hash: ")
    hashed_pw = generate_password_hash(password)
    print("")
    print(hashed_pw)

if __name__ == "__main__":
    manual_hash()