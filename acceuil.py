from tkinter import *
from PIL import Image, ImageTk
import os
from tkinter import messagebox, ttk
import time
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import cv2
import subprocess



class Acceuil:
    def __init__(self,root):
        self.root=root
        self.root.title("Acceuil")
        self.root.geometry("1600x700+0+0")
        self.root.config(bg="grey")

        self.icon=Image.open("C:/Users/wilfr/Desktop/projet-Stage-Télésurveillance/Model/surveillance.png")
        self.icon_size=(60, 50)
        self.icon=self.icon.resize(self.icon_size)
        self.icon_image=ImageTk.PhotoImage(self.icon)
        icon_title=Label(self.root, text="TELESURVEILLANCE",image=self.icon_image,font=("times new roman",16,"bold"),width=1600, bg="cyan",anchor="w",padx=20,compound=LEFT).place(x=0,y=0)
        
        
        #button_menu_barre
        btn_flux_image=Button(self.root,text="Flux images", font=("times new roman",16),cursor="hand2",bg="blue",width=16,command=self.windows_flux_images).place(x=600,y=7)
        btn_streaming_video=Button(self.root,text="Streaming vidéo", font=("times new roman",16),cursor="hand2",bg="blue",width=16,command=self.windows_flux_video).place(x=820,y=7)
        btn_deconnexion=Button(self.root,text="Déconnexion", font=("times new roman",16),cursor="hand2",bg="yellow",command=self.deconnextion).place(x=1200,y=7)

        
        #Heure
        self.lbl_heure=Label(self.root,font=("times new roman",12),bg="black",fg="white")
        self.lbl_heure.place(x=0,y=57,relwidth=1, height=20)
        self.update_time()
        
        #Input ID_Adresse
        self.lbl_ip_adress=Label(self.root,text="Adresse IP : ", font=("algerian"))
        self.lbl_ip_adress.place(x=150,y=90)
        
        self.entry_placeholder_ip = "192.168.11.145"
        self.entry_ip_adress=StringVar()
        self.input_ip=Entry(self.root,textvariable=self.entry_ip_adress, bd=2,width=20)
        self.input_ip.insert(0, self.entry_placeholder_ip)
        self.input_ip.place(x=260, y=90)
        
        #Input Port:
        self.lbl_ip_adress=Label(self.root,text="Port : ", font=("algerian"))
        self.lbl_ip_adress.place(x=400,y=90)

        self.entry_placeholder_port = "1024"
        self.entry_port=StringVar()
        self.input_port=Entry(self.root,textvariable=self.entry_port, bd=2,width=10)
        self.input_port.insert(0, self.entry_placeholder_port)
        self.input_port.place(x=460, y=90)

        self.ip_button = Button(self.root, text="Valider", bg="grey", width=12, command=self.ip_adresse_and_port_get,cursor="hand2")
        self.ip_button.place(x=530,y=88)
        
        #Liste box Img:
        self.image_listbox =Listbox(self.root, width=40, height=20,font=("times new roman",14),bg='grey')
        self.image_listbox.place(x=200,y=130)
        
        #Button mise a jour images
        self.browse_button = Button(self.root, text="Mettre à jour la liste des images", command=self.list_server_images, bg="blue",font=("algerian",13),cursor="hand2")
        self.browse_button.place(x=200,y=580)
        
        #Butoon suppression des images de la liste
        self.delete_button = Button(self.root, text="Supprimer la liste", command=self.delete_all_jpg_files,bg="blue",font=("algerian",13),cursor="hand2")
        self.delete_button.place(x=200,y=620)
        

        #Liste box video:
        self.video_listbox =Listbox(self.root, width=40, height=20,font=("times new roman",14),bg='grey')
        self.video_listbox.place(x=800,y=130)

        browse_button = Button(self.root, text="Metre a jour lesvidéos enrégistées", bg="blue",font=("algerian",13))
        browse_button.place(x=800,y=580)

       
       
    #Functions
    
    #Date time
    def update_time(self):
        current_time = time.strftime("%H:%M:%S")
        current_date = time.strftime("%d-%m-%Y")
        self.lbl_heure.config(text=f"Heure : {current_time}\t\t Date: {current_date}")
        self.lbl_heure.after(1000, self.update_time)
        
    #ip_addre et port
    def ip_adresse_and_port_get(self):
        if self.entry_ip_adress.get()=="" and self.entry_port.get()=="":
            messagebox.showerror("Erreur","Veuillez saisir une adresse IP  et un numéro de Port !",parent=self.root)
        else:
            messagebox.showinfo("Succes","Adresse IP et numéro de port enregistrés")
            return self.entry_ip_adress.get()


    #image
    def ip_adresse_get(self):
        if self.entry_ip_adress.get()=="":
            messagebox.showerror("Erreur","Veuillez saisir une adresse IP !",parent=self.root)
        else:
            messagebox.showinfo("Succes","Adresse IP enregistrée")
            return self.entry_ip_adress

        
    #Mise a jour images(téléchargemnt)
    def browse_server_images(self):
            self.server_ip=self.entry_ip_adress.get()
            self.port=self.entry_port.get()
            self.server_url = f"http://{self.server_ip}:{self.port}"
            response = requests.get(self.server_url)
            if response.status_code != 200:
                print("Échec de la connexion au serveur.")
                return []
            soup = BeautifulSoup(response.text, 'html.parser')
            self.image_list = [a['href'] for a in soup.find_all('a') if a['href'] != '/../']
            return self.image_list

    #Afficher la liste lisbox
    def list_server_images(self):
            if self.entry_ip_adress.get()=="":
                return messagebox.showerror("Erreur","Veuillez saisir une adresse IP !",parent=self.root)
            else:
                self.image_listbox.delete(0, END)
                self.images = self.browse_server_images()
                for self.img in self.images:
                    img_name = self.img.lstrip('/')  # Supprimer le "/" initial
                    self.image_listbox.insert(END, img_name)
                    
    #Suppression des images enrégistrée localement
    def delete_all_jpg_files(self):
            self.folder_path = "C:/Users/wilfr/Desktop/Logiciel/"
            self.result = messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer ces images?",parent=self.root)
            if self.result:
                    try:
                        
                        for filename in os.listdir(self.folder_path):
                                if filename.endswith(".jpg"):
                                    file_path = os.path.join(self.folder_path, filename)
                                    os.remove(file_path)
                                    print(f"Fichier {file_path} supprimé avec succès.")
                        messagebox.showinfo("Succes","Images supprimées du server local avec succès.",parent=self.root)
                        self.image_listbox.delete(0, END)
                    except OSError as e:
                            print(f"Erreur lors de la suppression des fichiers : {e}")
                            messagebox.showerror("Erreur","Erreur de suppression des images du server local.",parent=self.root)

    #Button flux images
    def windows_flux_images(self):
        self.root.destroy()
        file_path = "C:/Users/wilfr/Desktop/Logiciel/flux-image.py"
        subprocess.run(["python", file_path])
        
    #Button flux video
    def windows_flux_video(self):
        self.root.destroy()
        file_path = "C:/Users/wilfr/Desktop/Logiciel/flux_video.py"
        subprocess.run(["python", file_path])
        
    #Button déconnextion
    def deconnextion(self):
        self.root.destroy()
        file_path = "C:/Users/wilfr/Desktop/Logiciel/login.py"
        subprocess.run(["python", file_path])

    #video
    def browse_server_video(self,server_ip):
        if self.entry_ip_adress.get()=="":
            messagebox.showerror("Erreur","Veuillez saisir une adresse IP !",parent=self.root)
        else:
            server_ip=self.entry_ip_adress.get()
            self.server_url = f"http://{server_ip}"
            response = requests.get(self.server_url)
            if response.status_code != 200:
                print("Échec de la connexion au serveur.")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            self.video_list = [a['href'] for a in soup.find_all('a') if a['href'] != '/../']
            return self.video_list



if __name__=="__main__":
    root=Tk()
    objet=Acceuil(root)
    root.mainloop()
