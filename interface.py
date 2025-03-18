import socket
from tkinter import *
import tkinter as tk
from tkinter import scrolledtext
import threading
from tkinter import messagebox
from customtkinter import * 
import customtkinter as ctk
from tkinter import scrolledtext
from tkinter import font
from PIL import Image, ImageTk
import json
import time

client_iip = socket.gethostbyname(socket.gethostname())
clientppport = 12345
client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((client_iip, clientppport))
global n,Questions,user_name,email
n=0
Questions=" "
user_name=""
email=""


def sendRequest():
    global n,user_name,email
    i=0
    question=entrer.get()
    entrer.delete(0,'end')
    question=question.split(sep='\n')[0]
    n=1
    if(i==0):
        affichage.insert(tk.END,"\n", "sender")
        i=2
    affichage.insert(tk.END,f"{user_name}:\n", "sender_user")
    affichage.insert(tk.END,f"{question}", "message_right")
    question=f"{email}/"+question
    client.send(question.encode('UTF-8'))

def receveResponse():
    global n,Questions
    while True:
        reponse=client.recv(1024).decode('UTF-8')
        if('databasebase' in reponse):
            reponse=reponse[:-len('databasebase')]
            Questions=json.loads(reponse)
        elif(reponse.split(sep="/")[0]=="auth"):
            Seconnecter(reponse)
        else:
            if(n==1):
                affichage.insert(tk.END, f"\nChatBot :\n", "sender_chat")
                n=2
            for c in reponse:
                affichage.insert(tk.END,c, "message_left")
            affichage.yview("scroll",1, "units")
            
def fermer():
    global email
    if messagebox.askokcancel("Quitter", "Voulez-vous vraiment fermer la fenêtre ?"):
        client.send(f'{email}/quit'.encode('UTF-8'))
        client.detach()
        root.destroy()
    

threading.Thread(target=receveResponse,args=[]).start()

def affichage_history(button):
    global n,user_name,email
    frameHistory.pack_forget()
    affichage.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    entry_frame.pack(padx=10, pady=10, fill="x")
    n=1
    affichage.insert(tk.END,f"{user_name}:\n", "sender_user")
    affichage.insert(tk.END,f"{button}", "message_right")
    button=f"{email}/"+str(button)
    client.send(button.encode("UTF-8"))
    
def Historique():
    global Questions,user_name,email
    affichage.delete('1.0','end')
    entry_frame.pack_forget()
    affichage.pack_forget()
    q=email+"/"+"basedonne"
    client.send(q.encode("UTF-8"))
    frameHistory.pack(padx=10, pady=10, fill="both", expand=True)
    time.sleep(0.5)
    for q in Questions:
        button=ctk.CTkButton(
            scrollable_frame,
            text=q[0],
            command=lambda q_text=q[0]:affichage_history(q_text),
            fg_color='#212121',
            width=1000,
            height=30,
            hover_color="#555555",
        )
        button.pack(pady=5, padx=5,fill="x", expand=True)

def newChat():
    affichage.delete('1.0',tk.END)
    affichage.insert('end',f'Bonjour {user_name}\n','center')
    affichage.insert('end','Comment puis-je vous aidez ?\n','center2')
    
def enregistrer_utilisateur():
    global user_name,email
    user_name = entry_nom.get()
    email = entry_email.get()
    mot_de_passe = entry_mot_de_passe.get()
    confirmation = entry_confirmation.get()

    if not (user_name and email and mot_de_passe and confirmation):
        messagebox.showerror("Erreur", "Tous les champs sont obligatoires !")
        return

    if mot_de_passe != confirmation:
        messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas !")
        return
    user=f"createUser/{user_name}/{email}/{mot_de_passe}"
    client.send(user.encode("utf-8"))
    messagebox.showinfo("Succès", f"enregistré avec succès !")
    registre_frame.pack_forget()
    root.title("Login")
    root.geometry("400x350+200+10")
    login_frame.pack(padx=20, pady=10, fill="both", expand=True)
    

def basculer_affichage_mot_de_passe():
    if checkbox_var.get():
        entry_mot_de_passe.configure(show="")
        entry_confirmation.configure(show="")
    else:
        entry_mot_de_passe.configure(show="*")
        entry_confirmation.configure(show="*")
        
def Seconnecter(response):
    global user_name,email
    if str(response).split(sep="/")[1]=="success":
        user_name=str(response).split(sep="/")[2]
        email=str(response).split(sep="/")[3]
        login_frame.pack_forget()
        root.title("ChatBot")
        root.geometry("1000x600+200+10")
        root.configure(menu=menu_bar)
        affichage.insert('end',f'Bonjour {user_name}\n','center')
        affichage.insert('end','Comment puis-je vous aidez ?\n','center2')
        affichage.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        entry_frame.pack(padx=10, pady=10, fill="x")
    else:
        messagebox.showerror("Error","mot de passe ou email incorrect")
        return
    
def login():
    global email
    email = email_entry.get()
    password=password_entry.get()
    authentication=f"auth/{email}/{password}"
    client.send(authentication.encode('utf-8'))
    
def authentification():
    registre_frame.pack_forget()
    root.title("Login")
    root.geometry("400x350+200+10")
    login_frame.pack(padx=20, pady=10, fill="both", expand=True)
    
root = ctk.CTk()
root.title("Regiter")
root.geometry("400x500+200+20")
root.configure(bg="#f5f5f5")

registre_frame = ctk.CTkFrame(root)
registre_frame.pack(padx=10, pady=10, fill="x")

label_titre = ctk.CTkLabel(registre_frame, text="Inscription", font=("Helvetica",20, "bold"))
label_titre.pack(pady=20,padx=5)
label_nom = ctk.CTkLabel(registre_frame, text="Nom :", font=("Helvetica", 12))
label_nom.pack()
entry_nom = ctk.CTkEntry(registre_frame, placeholder_text="Entrez votre nom")
entry_nom.pack(pady=5, fill="x", padx=20)
label_email = ctk.CTkLabel(registre_frame, text="Email :", font=("Helvetica", 12))
label_email.pack(pady=5)
entry_email = ctk.CTkEntry(registre_frame, placeholder_text="Entrez votre email")
entry_email.pack(pady=5, fill="x", padx=20)
label_mot_de_passe = ctk.CTkLabel(registre_frame, text="Mot de passe :", font=("Helvetica", 12))
label_mot_de_passe.pack(pady=5)
entry_mot_de_passe = ctk.CTkEntry(registre_frame, placeholder_text="Entrez votre mot de passe", show="*")
entry_mot_de_passe.pack(pady=5, fill="x", padx=20)
label_confirmation = ctk.CTkLabel(registre_frame, text="Confirmez le mot de passe :", font=("Helvetica", 12))
label_confirmation.pack(pady=5)
entry_confirmation = ctk.CTkEntry(registre_frame, placeholder_text="Confirmez votre mot de passe", show="*")
entry_confirmation.pack(pady=5, fill="x", padx=20)
checkbox_var = ctk.BooleanVar()
checkbox_afficher = ctk.CTkCheckBox(
    registre_frame, text="Afficher le mot de passe", variable=checkbox_var, command=basculer_affichage_mot_de_passe
)
checkbox_afficher.pack(pady=5)
button_enregistrer = ctk.CTkButton(registre_frame, text="S'inscrire", command=enregistrer_utilisateur)
button_enregistrer.pack(pady=20,side=tk.LEFT,padx=20)
siginButton = ctk.CTkButton(registre_frame, text="Se Connecter", command=authentification)
siginButton.pack(pady=20,side=tk.RIGHT,padx=20)

login_frame = ctk.CTkFrame(root)
title_label = ctk.CTkLabel(login_frame, text="Connexion", font=("Arial", 20, "bold"))
title_label.pack(pady=20)
email_label = ctk.CTkLabel(login_frame, text="Email")
email_label.pack(pady=(0, 5))
email_entry = ctk.CTkEntry(login_frame, placeholder_text="Entrez votre email")
email_entry.pack(pady=(0, 10), fill="x")
password_label = ctk.CTkLabel(login_frame, text="Mot de passe")
password_label.pack(pady=(10, 5))
password_entry = ctk.CTkEntry(login_frame, placeholder_text="Entrez votre mot de passe", show="*")
password_entry.pack(pady=(0, 20), fill="x")
login_button = ctk.CTkButton(login_frame, text="Se connecter", command=login)
login_button.pack(pady=10)

menu_bar = tk.Menu(root,background="green",activebackground="red")
menu = tk.Menu(menu_bar, tearoff=0,font=("",16))
menu.add_command(label="Nouveau Chat",command=newChat)
menu.add_separator()
menu.add_command(label="Historique",command=Historique)
menu.add_separator()
menu.add_command(label="Quitter",command=fermer)
menu_bar.add_cascade(label="Options", menu=menu,font=("",16))


affichage = scrolledtext.ScrolledText(root, wrap=tk.WORD,  bg="#212121")
affichage.yview(tk.END)
affichage.tag_config("center", foreground="red", font=("", 23, "bold"),justify='center')
affichage.tag_config("center2", foreground="white", font=("", 23, "bold"),justify='center')
affichage.tag_config("sender_user", foreground="white", font=("", 19, "bold"),justify='right')
affichage.tag_config("sender_chat", foreground="white", font=("", 19,"bold"),justify='left')
affichage.tag_config("message_right", background="#555555",justify='right' ,foreground="white",spacing1=5, spacing3=5,spacing2=5,font=("Verdana", 16, "normal"))
affichage.tag_config("message_left",justify='left' ,foreground="white", spacing1=5, spacing3=5,spacing2=5,font=("", 16, "normal")) 

entry_frame = ctk.CTkFrame(root)
entrer = ctk.CTkEntry(entry_frame, font=("Verdana", 12),width=300,height=50,text_color="white",placeholder_text="Ask me a question ? ")
entrer.pack(side="left", fill="x", expand=True, padx=(0, 10))

send_button = ctk.CTkButton(
    entry_frame,
    text="Envoyer",  
    command=lambda: threading.Thread(target=sendRequest).start(),   
    hover_color="#45a049",  
    text_color="white", 
    font=("Arial", 14),  
    corner_radius=10,  
    width=100,  
    height=35
)
send_button.pack(side="right", padx=10, pady=5)

frameHistory = ctk.CTkFrame(root,width=1000,height=600,fg_color='#212121') #bg_color="#f5f5f5",fg_color="#f5f5f5"
canvas = tk.Canvas(frameHistory, bg="#212121", highlightthickness=0)
tite=ctk.CTkLabel(frameHistory,text="Chat history",text_color="white",font=("", 23, "bold"))
tite.pack()
canvas.pack(side="left", fill="both", expand=True)
scrollbar = tk.Scrollbar(frameHistory, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")
scrollable_frame = ctk.CTkFrame(canvas, fg_color="#212121",height=600)
scrollable_frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

scrollable_frame.bind("<Configure>", on_configure)

root.protocol("WM_DELETE_WINDOW", fermer)
root.mainloop()
