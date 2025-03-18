import pathlib
import textwrap
import json
import socket
import threading
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown
import sqlite3
import time
from datetime import datetime
from utils import *
server_ip = socket.gethostbyname(socket.gethostname())
servire_port = 12345
formatt = "utf-8"
servire = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servire.bind((server_ip, servire_port))
servire.listen()
print("serveur en ecoute ...........")
clients=[]
clients_email=[]
global lastquestion
lastquestion=""
def to_markdown(text):
  
  text =text.replace("* **", "").replace("**", "").replace("* ", "")
  paragraphs = text.split("\n\n")
  cleaned_paragraphs = []
  
  for paragraph in paragraphs:
      lines = paragraph.split("\n")
      cleaned_paragraphs.append(" ".join(line.strip() for line in lines if line.strip()))
    
  final_text = "".join(cleaned_paragraphs)+" "
  return final_text
 
genai.configure(api_key='API_KEY')
model = genai.GenerativeModel('gemini-1.5-flash')

global client
def database(question):
  global client
  a,user_name,email,password=str(question).split(sep="/")
  if email not in clients_email:
    clients_email.append(email)
  conn = sqlite3.connect('ma_base_de_donnees.db')
  cursor = conn.cursor()
  cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT,user_name TEXT, email TEXT,password TEXT)")
  print("password : ",password)
  hashedpassword=hachPassword(password)
  print(hashedpassword)
  cursor.execute("INSERT INTO users(user_name,email,password) VALUES(?,?,?)",(user_name,email,hashedpassword))
  conn.commit()
  conn.close()
  
def getUserByemail(Email,Password):
  global client
  if Email not in clients_email:
    clients_email.append(Email)
  conn = sqlite3.connect('ma_base_de_donnees.db')
  cursor = conn.cursor()
  try:
    cursor.execute("SELECT user_name,email,password FROM users WHERE email=?",(Email,))
    user=cursor.fetchone()
    conn.commit()
    conn.close()
    User="auth"
    username,email,password=user
    print("user",password)
    if user is None:
        User=User+"/vide"
    else :
     if verify_password(Password,user[2]):
       User=User+"/success/"+username+"/"+email
     else:
       User=User+"/failed"
    client.send(User.encode(formatt))
  except Exception as e:
    print(e,"user not found")
  
    
def reciver():
  global client
  while True:
    try:
      client,ip= servire.accept()
      clients.append(client)
      threading.Thread(target=handeRequest).start()
    except:
      break

def handeRequest():
    global client,lastquestion
    while True:
      try:
        conn = sqlite3.connect('ma_base_de_donnees.db')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS chatbot (user_email TEXT,question TEXT, reponse TEXT,date TEXT)")
        question=client.recv(1024).decode(formatt)
        threading.Thread(target=handeRequest).start()
        email=question.split(sep="/")[0]
        if(question.split(sep='/')[1]=='quit'):
          if email in clients_email:
            clients_email.remove(email)
        elif(question.split(sep='/')[0]=="createUser"):
          
          database(question)
        elif(question.split(sep="/")[0]=="auth"):
          getUserByemail(question.split(sep='/')[1],question.split(sep='/')[2])
        elif(question.split(sep='/')[1]=="basedonne"):
          cursor.execute("SELECT question FROM chatbot WHERE user_email=?",(email,))
          questions=cursor.fetchall()
          questions=json.dumps(questions)+"databasebase"
          client.send(questions.encode(formatt))
        else:
          questionn=question.split(sep="/")[1]
          allText=" "
          response = model.generate_content(questionn,stream=True)
          for res in response:
            text=to_markdown(res.parts[0].text)
            allText+=text
            for clt in clients:
              index=clients.index(clt)
              if email==clients_email[index]:
                clt.send(text.encode(formatt))
        if(question.split(sep='/')[0] not in ["createUser","auth"] and question.split(sep='/')[1]not in ["basedonne","quit"] and len(question.split(sep='/'))==2):
          date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
          cursor.execute("INSERT INTO chatbot VALUES (?,?,?,?)",(email,question.split(sep="/")[1],allText,date))
          conn.commit()
          conn.close()
      except  Exception as e:
        break
threading.Thread(target=reciver).start()

  

