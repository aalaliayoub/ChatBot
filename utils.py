import bcrypt


def hachPassword(password):
    salt=bcrypt.gensalt()
    hashedpassword=bcrypt.hashpw(password.encode('utf-8'),salt)
    return hashedpassword.decode("utf-8")

def verify_password(password,hashed_password):
    print("password utils before hash",password)
    return bcrypt.checkpw(password.encode('utf-8'),hashed_password.encode('utf-8'))