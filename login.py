from tkinter import *
from PIL import Image, ImageTk
import os
from tkinter import messagebox, ttk
import time
import subprocess
#import pymysql


class Login:
    def __init__(self,root):
        self.root3=root
        self.root3.title("Acceuil")
        self.root3.geometry("1600x655+0+0")
        self.root3.config(bg="white")
        self.root3.focus_force()

        self.icon=Image.open("C:/Users/wilfr/Desktop/projet-Stage-Télésurveillance/Model/surveillance.png")
        self.icon_size=(60, 50)
        self.icon=self.icon.resize(self.icon_size)
        self.icon_image=ImageTk.PhotoImage(self.icon)
        icon_title=Label(self.root3, text="TELESURVEILLANCE",image=self.icon_image,font=("times new roman",16,"bold"),width=1600, bg="cyan",anchor="w",padx=20,compound=LEFT).place(x=0,y=0)
        #self.root3.add_commande(label="Télésurveillance",image=self.icon_image,compound=LEFT)



        #Frame register
        register=Frame(self.root3,bd=2, relief=RIDGE,bg="grey")
        register.place(x=430,y=200,width=500,height=250)

        label1=Label(register,text="Administrateur",font=("times new roman",16,"bold"),width=10,padx=5,bg="green")
        label1.pack(side=TOP,fill=X)

        #input_nom
        label2=Label(register,text="Nom   :   ",font=("times new roman",12),padx=2)
        label2.place(x=100,y=70)
        self.input1=Entry(register,bd=2)
        self.input1.place(x=220,y=70)

        #input_mot_de_passe
        label3=Label(register,text="Mot de passe :" ,font=("times new roman",12),padx=2)
        label3.place(x=100,y=100)
        self.input2=Entry(register,bd=2, show="*")
        self.input2.place(x=220,y=100)

        #button
        btn_submit=Button(register,text='Connexion',font=("times new roman",12),bg="green",cursor="hand2",command=self.ID_btn_submit)
        btn_submit.place(x=200,y=200)


    def ID_btn_submit(self):
            if self.input1.get()=="" or self.input2.get()=="":
                messagebox.showerror("Erreur :"," Veuillez remplir tout les champs!",parent=self.root3)
            else:
                if self.input1.get()=="saliou" and self.input2.get()=="saliou":
                    self.windows_acceuil()
                else: 
                    messagebox.showerror("Vos identifiants de correspondent pas.",parent=self.root3)


    #Button flux images
    def windows_acceuil(self):
        self.root3.destroy()
        file_path = "C:/Users/wilfr/Desktop/Logiciel/acceuil.py"
        subprocess.run(["python", file_path])



if __name__=="__main__":
    root=Tk()
    objet=Login(root)
    root.mainloop()
