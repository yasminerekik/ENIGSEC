from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import pandas as pd
import sqlite3
import time

# Charger le modèle Random Forest
with open('selected_randomforest.pkl', 'rb') as file:
    model = pickle.load(file)

# Connexion à la base de données SQLite
conn = sqlite3.connect("database/ids_data.db", check_same_thread=False)
cursor = conn.cursor()

# Créer une instance de l'application FastAPI
app = FastAPI()

# Définir les caractéristiques (features) du modèle
selected_features = ['duration', 'src_bytes', 'dst_bytes', 'wrong_fragment', 'num_failed_logins',
                     'logged_in', 'count', 'srv_count', 'dst_host_srv_serror_rate', 'neptune']

# Créer une route GET pour vérifier les nouvelles données dans la base de données et faire une prédiction
@app.get("/predict")
def predict_real_time():
    # Lire les nouvelles données de la base de données
    cursor.execute("""
    SELECT duration, src_bytes, dst_bytes, wrong_fragment, num_failed_logins,
           logged_in, count, srv_count, dst_host_srv_serror_rate, neptune
    FROM traffic_data ORDER BY timestamp DESC LIMIT 1
    """)
    
    data = cursor.fetchone()

    if data:
        # Convertir les données en DataFrame
        input_data = pd.DataFrame([data], columns=selected_features)
        
        # Faire la prédiction avec le modèle
        prediction = model.predict(input_data)

        # Retourner le résultat de la prédiction
        if prediction[0] == 0:
            return {"prediction": "Normal traffic (class 0)", "data": data}
        else:
            return {"prediction": "Anomaly detected (class 1)", "data": data}
    else:
        return {"message": "No data available"}

# Fonction pour surveiller les nouvelles données de trafic
def watch_for_new_traffic():
    while True:
        cursor.execute("""
        SELECT COUNT(*) FROM traffic_data
        """)
        row_count = cursor.fetchone()[0]
        
        if row_count > 0:
            predict_real_time()
        time.sleep(5)  # Attendre 5 secondes avant de vérifier les nouvelles données
