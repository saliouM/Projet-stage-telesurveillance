from tkinter import *
from PIL import Image, ImageTk
import os
from io import BytesIO
from tkinter import messagebox, ttk
import time
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import cv2
from pydrive.auth import GoogleAuth 
from pydrive.drive import GoogleDrive
import boto3
from botocore.exceptions import NoCredentialsError
import paramiko
import subprocess
import threading






class FluxImage:
    def __init__(self,root):
        self.root=root
        self.root.title("Flux Images")
        self.root.geometry("1600x700+0+0")
        self.root.config(bg="grey")

        self.icon=Image.open("C:/Users/wilfr/Desktop/projet-Stage-Télésurveillance/Model/surveillance.png")
        self.icon_size=(60, 50)
        self.icon=self.icon.resize(self.icon_size)
        self.icon_image=ImageTk.PhotoImage(self.icon)
        self.icon_title=Label(self.root, text="TELESURVEILLANCE",image=self.icon_image,font=("times new roman",16,"bold"),width=1600, bg="cyan",anchor="w",padx=20,compound=LEFT).place(x=0,y=0)
        #self.root.add_commande(label="Télésurveillance",image=self.icon_image,compound=LEFT)
        
         #button_menu_barre
        btn_flux_image=Button(self.root,text="Flux images", font=("times new roman",16),cursor="hand2",bg="blue",width=16,command=self.windows_flux_images).place(x=600,y=7)
        btn_flux_image=Button(self.root,text="Acceuil", font=("times new roman",16),cursor="hand2",width=13,bg="blue",command=self.windows_acceuil).place(x=400,y=7)
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
        self.image_listbox.place(x=50,y=130)
        
        #Button mise a jour images
        self.browse_button = Button(self.root, text="Mettre à jour la liste des images", command=self.list_server_images, bg="blue",font=("algerian",13),cursor="hand2")
        self.browse_button.place(x=55,y=580)
        
        #Butoon suppression des images de la liste
        self.delete_button = Button(self.root, text="Supprimer la liste", command=self.delete_all_jpg_files,bg="blue",font=("algerian",13),cursor="hand2")
        self.delete_button.place(x=55,y=620)

        #Start Server
        self.start_server_button = Button(self.root, text="Démarer le Serveur", command=self.toggle_commande_server, bg="blue",font=("algerian",13),cursor="hand2")
        self.start_server_button.place(x=700,y=90)
        
        # Notification
        self.notification = Frame(self.root, bg="grey")
        self.notification.place(x=900, y=90, width=300, height=40)
        
        #notify start_command_stream
        self.notify_start_server = Label(self.notification,bg="grey",font=("times new roman",13))
        self.notify_start_server.place(x=10,y=2)

        self.streaming = False
        self.streaming_thread = None
        self.stop_streaming_signal = threading.Event()
        self.on_commande_server=False

        #section affichage d'image
        self.image_listbox.bind("<<ListboxSelect>>", self.on_listbox_click)
        self.root.bind("<Configure>", self.on_window_resize)

        # Frame pour afficher l'image sélectionnée
        self.image_frame = Frame(self.root, bg="grey")
        self.image_frame.place(x=500, y=150, width=600, height=400)

        # Label pour afficher l'image
        self.image_label = Label(self.image_frame, bg="white")
        self.image_label.pack(fill=BOTH, expand=YES)

        self.upload_button = Button(self.root, text="Téléverser Dans AWS S3", command=self.on_upload_aws_button_click, bg="blue",font=("algerian",13),cursor="hand2")
        self.upload_button.place(x=690,y=580)
        
        self.temps_ecoule = 0
        self.minuterie_active = False
    
    
    
    #Fonctions
    
    #Send command to arduino
    def send_command_arduino_start(self):
        self.on_commande_server=True
        # Informations de connexion SSH
        host = self.entry_ip_adress.get()  # Adresse IP de votre Arduino Yun
        port = 22 # Port SSH
        username = "root"  # Nom d'utilisateur (peut être différent)
        password = "arduinoyun"  # Mot de passe SSH
        
        # Commande à exécuter
        command = 'cd /mnt/sda1/server-images-stock uhttpd -h /mnt/sda1/server-images-stock -p 1024 -f'
        
        def ssh_thread():
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port, username, password)
            # Exécuter la commande
            stdin, stdout, stderr = ssh.exec_command(command)
            # Fermer la connexion SSH
            ssh.close()
        # Démarrer le thread SSH
        ssh_thread = threading.Thread(target=ssh_thread)
        ssh_thread.start()
        
    #Stop serveur
    def send_command_arduino_stop(self):
        self.on_commande_streaming=False
        # Informations de connexion SSH
        host = self.entry_ip_adress.get()  # Adresse IP de votre Arduino Yun
        port = 22 # Port SSH
        username = "root"  # Nom d'utilisateur (peut être différent)
        password = "arduinoyun"  # Mot de passe SSH
        
         #Commande pour arrêter le processus mjpg_streamer
        stop_command = "kill $(pgrep uhttpd)"
        try:
            # Se connecter au système Arduino Yun via SSH
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port, username, password)
            
            # Exécuter la commande
            stdin, stdout, stderr = ssh.exec_command(stop_command)
        
            ssh.close()
            messagebox.showinfo("Arrêt du streaming", "Le streaming a été arrêté.", parent=self.root)
        except paramiko.AuthenticationException:
            messagebox.showwarning("Echec",f"Erreur d'authentification",parent=self.root)
        except paramiko.SSHException as e:
            messagebox.showwarning("Echec",f"Erreur SSH: {str(e)}",parent=self.root)
        except Exception as e:
            messagebox.showwarning("Echec",f"Erreur: {str(e)}",parent=self.root)
        
        self.stop_streaming_signal.set()  # Définir le signal d'arrêt
        if self.streaming_thread:
            self.streaming_thread.join()  # Attendre que le thread se termine
            self.streaming_thread = None  # Réinitialiser le thread
            self.stop_streaming_signal.clear()  
        
    def toggle_commande_server(self):
        if not self.on_commande_server:
            self.minuterie_active = True
            self.send_command_arduino_start()
            self.start_server_button.config(text="Arrêter le serveur",bg="red")
            self.actualiser_minuterie_streaming()
        else:
            self.send_command_arduino_stop()
            self.start_server_button.config(text="Activer le serveur",bg="blue")
            self.arreter_minuterie()
            self.notify_start_server.config(text="")
            
    def actualiser_minuterie_streaming(self):
        if self.minuterie_active:
            heures = self.temps_ecoule // 3600
            minutes = (self.temps_ecoule % 3600) // 60
            secondes = self.temps_ecoule % 60
            temps_formatte = f"{heures:02d}:{minutes:02d}:{secondes:02d}"
            self.notify_start_server.config(text=f"Streaming en cours: {temps_formatte}",fg="green")
            self.temps_ecoule += 1
            self.root.after(1000, self.actualiser_minuterie_streaming)  # Actualiser chaque seconde
            
    def arreter_minuterie(self):
            self.minuterie_active = False
            self.temps_ecoule = 0
            #self.notify_start_stream.config(text="")
            
            
    #Button flux images
    def windows_acceuil(self):
        self.root.destroy()
        file_path = "C:/Users/wilfr/Desktop/Logiciel/acceuil.py"
        subprocess.run(["python", file_path])
    
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
    
    #Date time
    def update_time(self):
        current_time = time.strftime("%H:%M:%S")
        current_date = time.strftime("%d-%m-%Y")
        self.lbl_heure.config(text=f"Heure :{current_time}\t\t Date: {current_date}")
        self.lbl_heure.after(1000, self.update_time)

    def download_image(self,server_url, nameImg):
        # Récupérer l'image à partir du serveur de l'Arduino Yun Rev 2
        response = requests.get(server_url, stream=True)
        if response.status_code != 200:
            print("Échec du téléchargement de l'image depuis le serveur.")
            return
        # Sauvegarder l'image localement
        local_image_file = nameImg
        with open(local_image_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print("Image téléchargée depuis le serveur.")
        return local_image_file
    
    #Upload google drive    
    #upload a google drive (en modification)
    def upload_to_google_drive(self,nameImg):
        # Téléverser l'image dans Google Drive
        gauth = GoogleAuth()
        #gauth.LoadCredentialsFile("C:/Users/wilfr/Desktop/ArduinoYunRev2/Logiciel/credentials.json")  # Spécifiez le chemin complet vers client_secrets.json
        drive = GoogleDrive(gauth)

        # Créer un objet GoogleDriveFile avec les métadonnées
        file_metadata = {'title': nameImg, 'parents': [{'id': '1JhOLZPtPEcqVqxkb34IAr6ro1xHB7EWu'}]}
        file = drive.CreateFile(file_metadata)

        # Définir le contenu du fichier
        file.SetContentFile(nameImg)

        # Envoyer le fichier à Google Drive
        file.Upload()
        print("Image téléversée avec succès sur Google Drive.")

    #dowload to AWS S3
    def upload_to_aws_s3(self, nameImg, file_path):
        # Configurer les informations d'authentification AWS
        self.ACCESS_KEY_ID='AKIASUBTV6DHQRCAHROM'
        self.ACCESS_SECRET_KEY='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'
        bucket_name = 'bucketsaliou'

        s3 = boto3.client('s3', aws_access_key_id=self.ACCESS_KEY_ID, aws_secret_access_key=self.ACCESS_SECRET_KEY)

        try:
            s3.upload_file(file_path, bucket_name, nameImg)
            print("Image téléversée avec succès sur AWS S3.")
            messagebox.showinfo("Succès","Fichier téléversé dans AWS S3 avec succès",parent=self.root)
        except FileNotFoundError:
            print("Le fichier n'a pas été trouvé.")
            messagebox.showerror("Erreur","Fichier introuvable",parent=self.root)
        except NoCredentialsError:
            print("Les informations d'authentification AWS sont manquantes ou incorrectes.")
            messagebox.showerror("Erreur","Problème d'authentification",parent=self.root)
            
    #Upload au clique
    def on_upload_aws_button_click(self):
        selected_index = self.image_listbox.curselection()
        if selected_index:
            self.image_name = self.image_listbox.get(selected_index[0])
            self.upload_to_aws_s3(self.image_name, self.image_path)


    #ip_addre et port
    def ip_adresse_and_port_get(self):
        if self.entry_ip_adress.get()=="" and self.entry_port.get()=="":
            messagebox.showerror("Erreur","Veuillez saisir une adresse IP  et un numéro de Port !",parent=self.root)
        else:
            messagebox.showinfo("Succes","Adresse IP et numéro de port enregistrés")
            return self.entry_ip_adress.get()

    #Mise a jour images
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
                    
    #Au clique de la listbox affiche les images
    def on_listbox_click(self,event):
            selected_index = self.image_listbox.curselection()
            if selected_index:
                self.image_name = self.image_listbox.get(selected_index[0])
                self.image_path = self.download_image(f"http://{self.entry_ip_adress.get()}:{self.entry_port.get()}/{self.image_name}", self.image_name)
                #self.on_image_click(self.image_path)
                self.display_selected_image(self.image_path)

    #Afficheur d'images
    def display_selected_image(self, image_path):
            # Ouvrir l'image avec PIL
            img = Image.open(image_path)
            img = img.resize((600, 400))
            self.image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.image)
            
    #Delette images      
    #def delete_image(self,nameImg):
            # Supprimer le fichier local après le téléversement
            #self.result = messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cette image?",parent=self.root)
            #if self.result:
                #os.remove(nameImg)
                #print("Image supprimée du serveur local.")
                #messagebox.showinfo("Succes","Image supprimée du server local.",parent=self.root)  
              
    #def on_delete_button_click(self):
            #selected_index = self.image_listbox .curselection()
            #if selected_index:
                        #self.image_name = self.image_listbox.get(selected_index[0])
                        #self.delete_image(self.image_name)
                        #self.list_server_images()
                        
    
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
                                    #messagebox.showwarning("Danger",f"supprimer aussi  '{filename}' du server local ! ",parent=self.root)
                        messagebox.showinfo("Succes","Images supprimées du server local avec succès.",parent=self.root)
                        self.image_listbox.delete(0, END)
                    except OSError as e:
                            print(f"Erreur lors de la suppression des fichiers : {e}")
                            messagebox.showerror("Erreur","Erreur de suppression des images du server local.",parent=self.root)

    
    ##Télécharger AU clique de l'images
    def on_upload_button_click(self):
        selected_index = self.image_listbox.curselection()
        if selected_index:
            self.image_name = self.image_listbox.get(selected_index[0])
            self.upload_to_google_drive(self.image_name)


    #fénètre responsive en cours d'adaptation
    def on_window_resize(self, event):
        # Ajuster les widgets en réponse au changement de taille de fenêtre
        #self.icon_title.config(width=event.width)
        self.lbl_heure.config(width=event.width)
        #self.lbl_ip_adress.config(width=event.width)
        #self.input_ip.config(width=event.width  // 15)
        #self.lbl_ip_adress.config(width=event.width)
        #self.input_port.config(width=event.width)
        #self.image_listbox.config(height=event.height // 30)
        #self.image_frame.config(height=event.height // 30)
        
        #self.image_label.config(height=event.height // 30)
        
        #self.btn_flux_image.pack(fill=BOTH, padx=10, pady=10, expand=True)
        #self.btn_streaming_video.pack(fill=BOTH, padx=10, pady=10, expand=True)
        #self.ip_button.pack(fill=BOTH, padx=10, pady=10, expand=True)
        #self.browse_button.pack(fill=BOTH, padx=10, pady=10, expand=True)
        #self.delete_button.pack(fill=BOTH, padx=10, pady=10, expand=True)
        #self.upload_buttonpack(fill=BOTH, padx=10, pady=10, expand=True)



if __name__=="__main__":
    root=Tk()
    objet=FluxImage(root)
    root.mainloop()