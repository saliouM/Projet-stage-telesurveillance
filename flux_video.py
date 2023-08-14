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




class StreamingVideo:
    def __init__(self,root):
        self.root=root
        self.root.title("Streaming Vidéo")
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
        btn_streaming_video=Button(self.root,text="Streaming vidéo", font=("times new roman",16),cursor="hand2",bg="blue",width=16).place(x=820,y=7)
        btn_deconnexion=Button(self.root,text="Déconnexion", font=("times new roman",16),cursor="hand2",bg="yellow",command=self.deconnextion).place(x=1200,y=7)

        
        #Heure
        self.lbl_heure=Label(self.root,font=("times new roman",12),bg="black",fg="white")
        self.lbl_heure.place(x=0,y=57,relwidth=1, height=20)
        self.update_time()

        #Input ID_Adresse
        self.lbl_ip_adress=Label(self.root,text="Adresse IP : ", font=("algerian"))
        self.lbl_ip_adress.place(x=150,y=90)
        
        self.entry_placeholder_ip = "192.168.11.149"
        self.entry_ip_adress=StringVar()
        self.input_ip=Entry(self.root,textvariable=self.entry_ip_adress, bd=2,width=20)
        self.input_ip.insert(0, self.entry_placeholder_ip)
        self.input_ip.place(x=260, y=90)
        
        #Input Port:
        self.lbl_ip_adress=Label(self.root,text="Port : ", font=("algerian"))
        self.lbl_ip_adress.place(x=400,y=90)

        self.entry_placeholder_port = "8080"
        self.entry_port=StringVar()
        self.input_port=Entry(self.root,textvariable=self.entry_port, bd=2,width=10)
        self.input_port.insert(0, self.entry_placeholder_port)
        self.input_port.place(x=460, y=90)
        
        self.ip_button = Button(self.root, text="Valider", bg="grey", width=12, command=self.ip_adresse_and_port_get,cursor="hand2")
        self.ip_button.place(x=530,y=88)

        # Frame pour afficher de la video en streaming
        self.video_frame = Frame(self.root, bg="grey")
        self.video_frame.place(x=300, y=150, width=800, height=480)

        # Label pour afficher l'image
        self.video_label = Label(self.video_frame, bg="white")
        self.video_label.pack(fill=BOTH, expand=YES)
        
        
        
        #Start Streaming
        self.start_streaming_button = Button(self.root, text="Démarer le Streaming", command=self.toggle_commande_streaming, bg="blue",font=("algerian",13),cursor="hand2")
        self.start_streaming_button.place(x=10,y=150)
        
        #buuton affichage de la video
        self.diffusion_button = Button(self.root, text="Afficher la Diffusion",bg="blue",font=("algerian",13),cursor="hand2", command=self.toggle_streaming_view)#command=self.toggle_recording
        self.diffusion_button.place(x=10,y=200)
        
        #Button recording (enregistrement)
        self.record_button = Button(self.root, text="Enregistrer",bg="blue",font=("algerian",13),cursor="hand2", command=self.toggle_recording)#command=self.toggle_recording
        self.record_button.place(x=10,y=250)

        # Cloud AWS télécharger
        self.upload_button = Button(self.root, text="Téléverser Dans AWS S3", command=self.on_upload_aws_button_click, bg="blue",font=("algerian",13),cursor="hand2")
        self.upload_button.place(x=10,y=300)
        
       
        
        # Notification
        self.notification = Frame(self.root, bg="grey")
        self.notification.place(x=10, y=350, width=260, height=300)
        
        #notify start_command_stream
        self.notify_start_stream = Label(self.notification,bg="grey",font=("times new roman",13))
        self.notify_start_stream.place(x=5, y=10)
        
        #notify start_recording
        self.notify_start_recording = Label(self.notification, bg="grey",font=("times new roman",13))
        self.notify_start_recording.place(x=5, y=30)
        
        #constante record
        self.streaming = False
        self.recording = False
        self.video_capture = None
        self.output_writer = None
        
        self.streaming_thread = None
        self.stop_streaming_signal = threading.Event()
        self.on_commande_streaming=False
        
        self.temps_ecoule = 0
        self.minuterie_active = False
        


    #Fonctions
    
    def send_command_arduino_start(self):
        self.on_commande_streaming=True
        # Informations de connexion SSH
        host = self.entry_ip_adress.get()  # Adresse IP de votre Arduino Yun
        port = 22 # Port SSH
        username = "root"  # Nom d'utilisateur (peut être différent)
        password = "passarduino"  # Mot de passe SSH
        
        # Commande à exécuter
        command = 'mjpg_streamer -i "input_uvc.so -d /dev/video0 -r 800x480 -f 25" -o "output_http.so -p 8080 -w /www/webcam"'
        
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
        
    def send_command_arduino_stop(self):
        self.on_commande_streaming=False
        # Informations de connexion SSH
        host = self.entry_ip_adress.get()  # Adresse IP de votre Arduino Yun
        port = 22 # Port SSH
        username = "root"  # Nom d'utilisateur (peut être différent)
        password = "passarduino"  # Mot de passe SSH
        
         #Commande pour arrêter le processus mjpg_streamer
        stop_command = 'killall mjpg_streamer'
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
   
    #dowload to AWS S3
    def upload_to_aws_s3(self, nameImg, file_path):
        # Configurer les informations d'authentification AWS
        self.ACCESS_KEY_ID='aws_key'
        self.ACCESS_SECRET_KEY='aws_secret_key'
        bucket_name = 'your_buket_name'

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
            return self.entry_ip_adress.get(),self.entry_port.get()
        
    ###### Video #######
    
    #Start streaming
    def start_streaming(self):
        self.streaming = True
        self.url_video=f"http://{self.entry_ip_adress.get()}:{self.entry_port.get()}/?action=stream"
        self.video_capture = cv2.VideoCapture(self.url_video)
        self.stream_thread = threading.Thread(target=self.update_stream)
        self.stream_thread.start()
            

    
    #update streaming
    def update_stream(self):
        try:
            while self.streaming:
                    ret, frame = self.video_capture.read()
                    if ret:
                        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        frame = cv2.resize(frame, (800,480))
                        self.photo = self.get_photo_image(frame)
                        self.video_label.config(image=self.photo)
                        self.video_label.image = self.photo

                        if self.recording and self.output_writer is not None:
                            self.output_writer.write(frame)
        except Exception as e:
                print("Erreur de flux vidéo :", str(e))
                messagebox.showerror("Erreur",f"Erreur de connexion: {str(e)} !",parent=self.root)
                self.stop_streaming()
                time.sleep(5)  # Attendre 5 secondes avant de redémarrer
                if self.streaming:
                    self.start_streaming()
        
    #Transforme en photo Tkinter
    def get_photo_image(self, frame):
        return PhotoImage(data=cv2.imencode('.ppm', frame)[1].tobytes())

    #Button "enregistrement" ou "arreter"
    def toggle_recording(self):
        if not self.recording :
            self.minuterie_active = True
            self.start_recording()
            self.record_button.config(text="Arrêter l'enregistrement",bg="red")
            self.actualiser_minuterie_recording()
            
        else:
            self.stop_recording()
            self.record_button.config(text="Enregistrer",bg="blue")
            self.arreter_minuterie()
            self.notify_start_recording.config(text="")
            
    def toggle_streaming_view(self):
        if not self.streaming :
            self.start_streaming()
            self.diffusion_button.config(text="Arreter l'Affichage",bg="red")
        else:
            self.stop_streaming()
            self.diffusion_button.config(text="Afficher la diffusion",bg="blue")
            
            
    def toggle_commande_streaming(self):
        if not self.on_commande_streaming:
            self.minuterie_active = True
            self.send_command_arduino_start()
            self.start_streaming_button.config(text="Arrêter le Streaming",bg="red")
            self.actualiser_minuterie_streaming()
        else:
            self.send_command_arduino_stop()
            self.start_streaming_button.config(text=" Démarer le Streaming",bg="blue")
            self.arreter_minuterie()
            self.notify_start_stream.config(text="") 
            
    def actualiser_minuterie_streaming(self):
        if self.minuterie_active:
            heures = self.temps_ecoule // 3600
            minutes = (self.temps_ecoule % 3600) // 60
            secondes = self.temps_ecoule % 60
            temps_formatte = f"{heures:02d}:{minutes:02d}:{secondes:02d}"
            self.notify_start_stream.config(text=f"Streaming en cours: {temps_formatte}",fg="green")
            self.temps_ecoule += 1
            self.root.after(1000, self.actualiser_minuterie_streaming)  # Actualiser chaque seconde
            
    def actualiser_minuterie_recording(self):
        if self.minuterie_active:
            heures = self.temps_ecoule // 3600
            minutes = (self.temps_ecoule % 3600) // 60
            secondes = self.temps_ecoule % 60
            temps_formatte = f"{heures:02d}:{minutes:02d}:{secondes:02d}"
            self.notify_start_recording.config(text=f"Enregistrement en cours: {temps_formatte}",fg="green")
            self.temps_ecoule += 1
            self.root.after(1000, self.actualiser_minuterie_recording)  # Actualiser chaque seconde
            
        
    def arreter_minuterie(self):
            self.minuterie_active = False
            self.temps_ecoule = 0
            
            
    # Start enregistrement    
    def start_recording(self):
        self.recording = True
        
        self.output_writer = cv2.VideoWriter(f'Video_{int(time.time())}.avi', cv2.VideoWriter_fourcc(*'XVID'), 25, (800, 480))

    #Stop enregistrement
    def stop_recording(self):
        self.recording = False
        if self.output_writer is not None:
            self.output_writer.release()
            messagebox.showinfo("Enregistrement terminé", "La vidéo a été enregistrée localement.")

    def clear_video_frame(self):
        self.video_label.config(image=None)

    #Stop streaming
    def stop_streaming(self):
        self.streaming = False
        if self.video_capture is not None:
            self.video_capture.release()
            self.clear_video_frame()

        
        
    def on_window_resize(self, event):
        self.lbl_heure.config(width=event.width)
       




if __name__=="__main__":
    root=Tk()
    objet=StreamingVideo(root)
    root.mainloop()
