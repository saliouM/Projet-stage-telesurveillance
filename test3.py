import cv2

# URL du flux vidéo depuis OBS (adresse IP de l'ordinateur exécutant OBS)
obs_stream_url = "http://192.168.11.149:8080/?action=stream"

cap = cv2.VideoCapture(obs_stream_url)

# Variable pour indiquer si l'enregistrement est en cours
enregistrement = False

# Créer un objet VideoWriter pour l'enregistrement
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow('OBS Stream', frame)

    # Si la touche 'q' est enfoncée, sortir de la boucle
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Si le bouton d'enregistrement est activé, commencer/enregistrer l'enregistrement
    if enregistrement:
        if out is None:
            out = cv2.VideoWriter('enregistrement.avi', fourcc, 25, (frame.shape[1], frame.shape[0]))
        out.write(frame)
    else:
        if out is not None:
            out.release()
            out = None

    # Détecter si la touche 'r' est enfoncée pour activer/désactiver l'enregistrement
    key = cv2.waitKey(1) & 0xFF
    if key == ord('r'):
        enregistrement = not enregistrement
        if enregistrement and out is None:
            out = cv2.VideoWriter('enregistrement.avi', fourcc, 25, (frame.shape[1], frame.shape[0]))
        elif not enregistrement and out is not None:
            out.release()
            out = None

cap.release()
cv2.destroyAllWindows()
