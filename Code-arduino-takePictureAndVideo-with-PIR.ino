// Sketch to upload pictures to Dropbox when motion is detected
#include <Bridge.h>
#include <Process.h>
#include <SD.h>


Process p;
String filename; // Filename
string filePathFile;
int pirPin = 2; // Pin
String path = "/mnt/sda1/arduino/up-to-googledrive"; // Path
boolean motionDetected = false;
void setup() {
 
  Bridge.begin();
  Serial.begin(9600);
  
  pinMode(pir_pin,INPUT);
  //pinMode(ledPin, OUTPUT); // Définir la broche de la LED en tant que sortie
}

void loop(void) {
      int pirState = digitalRead(pirPin);
      if (pirState == HIGH) {
            if (!motionDetected) {
                  // Mouvement détecté

                  //digitalWrite(ledPin, HIGH); // Allumer la LED si le capteur détecte un mouvement

                  // Generate filename with timestamp
                  filename = "image"; 
                  p.runShellCommand("date +%s");
                  while(p.running());

                  while (p.available()>0) {
                    char c = p.read();
                    filename += c;
                  } 
                  filename.trim();
                  filename += ".png";
              
                  filePathFile = path + "/" + filename; // "/mnt/sda1/arduino/up-to-googledrive/image111111.png"
                  // Take picture
                  takePicture(filePathFile);
                  //upload-to-drive 
                  upload_to_drive(path);
                  
                  //digitalWrite(ledPin, HIGH); // Allumer la LED si le capteur détecte un mouvement
                  //digitalWrite(ledPin, LOW); // Éteindre la LED si aucun mouvement n'est détecté
                  motionDetected = true;
             }else {
                  // Pas de mouvement détecté
                  motionDetected = false;
            }
            delay(100);
          }
          //digitalWrite(ledPin, LOW); // Éteindre la LED si aucun mouvement n'est détecté
}

void takePicture(const char* filePath){
    // Ouvrir le fichier en mode lecture
    File file = SD.open(filePath, FILE_READ);
    // Vérifier si le fichier est ouvert
    if (file) {
          // Lire le contenu du fichier et faire quelque chose avec les données lues
            while (file.available()) {
                  char data = file.read();
                  // Faites quelque chose avec les données lues...
                    // Démarrez le processus pour capturer une image à partir de la webcam
                    Process p;
                    p.begin("fswebcam"); // Vous devez installer fswebcam sur votre Yun. Pour l'installer, exécutez "opkg update" et "opkg install fswebcam" via SSH.
                    // Ajoutez les paramètres de la commande pour configurer la résolution et le chemin du fichier de sortie
                    p.addParameter("--resolution");
                    p.addParameter("640x480"); // Changer la résolution selon vos besoins
                    p.addParameter("--no-banner");
                    p.addParameter(filePath); // Changer le chemin de sortie selon vos besoins
                    // Exécutez le processus de capture d'image
                    p.run();
              
                    // Attendez que le processus se termine
                    while (p.running());
              }

            File imageFile = SD.open(filePath);
            if (imageFile) {
                Serial.println("Capture d'image réussie !");
                imageFile.close();
            } else {
                Serial.println("Erreur lors de la capture d'image ou sauvegarde sur la carte SD.");
            }
      // Fermer le fichier après utilisation
        file.close();
      } else {
      // Gérer le cas où le fichier ne peut pas être ouvert
      Serial.println("Erreur lors de l'ouverture du fichier");
    }
}

void upload_to_drive(const char* filePath){
    // Démarrez le processus Python pour exécuter le script
      Process p;
      p.begin("python");
      
      // Ajoutez le chemin du script Python comme paramètre
      p.addParameter(filePath+"googledrive.py");
      
      // Exécutez le processus
      p.run();
      
      // Attendez que le processus Python se termine
      while (p.running());

      // Affichez la sortie du script Python s'il y en a
      while (p.available()) {
        char c = p.read();
        Serial.write(c);
      }
}
