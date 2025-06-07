import time
import random
import sqlite3

# Connexion à la base de données
conn = sqlite3.connect("database/ids_data.db", check_same_thread=False)
cursor = conn.cursor()

# Créer la table pour stocker les données de trafic si elle n'existe pas
cursor.execute("""
CREATE TABLE IF NOT EXISTS traffic_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    duration REAL,
    src_bytes REAL,
    dst_bytes REAL,
    wrong_fragment REAL,
    num_failed_logins REAL,
    logged_in REAL,
    count REAL,
    srv_count REAL,
    dst_host_srv_serror_rate REAL,
    neptune REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Fonction pour générer des données de trafic normalisées (valeurs entre 0 et 1)
def generate_traffic():
    while True:
        traffic_data = {
            "duration": random.uniform(0, 1),  # Déjà entre 0 et 1
            "src_bytes": random.uniform(0, 1),  # Normalisé
            "dst_bytes": random.uniform(0, 1),  # Normalisé
            "wrong_fragment": random.uniform(0, 1),  # Déjà entre 0 et 1
            "num_failed_logins": random.uniform(0, 1),  # Normalisé
            "logged_in": random.choice([0, 1]),  # Binaire (0 ou 1)
            "count": random.uniform(0, 1),  # Normalisé
            "srv_count": random.uniform(0, 1),  # Normalisé
            "dst_host_srv_serror_rate": random.uniform(0, 1),  # Normalisé
            "neptune": random.uniform(0, 1)  # Déjà entre 0 et 1
        }
        cursor.execute("""
        INSERT INTO traffic_data (duration, src_bytes, dst_bytes, wrong_fragment, num_failed_logins,
                                  logged_in, count, srv_count, dst_host_srv_serror_rate, neptune)
        VALUES (:duration, :src_bytes, :dst_bytes, :wrong_fragment, :num_failed_logins,
                :logged_in, :count, :srv_count, :dst_host_srv_serror_rate, :neptune)
        """, traffic_data)
        conn.commit()

        print(f"Generated Traffic: {traffic_data}")
        time.sleep(1)  # Simuler le trafic toutes les secondes

if __name__ == "__main__":
    try:
        generate_traffic()
    except KeyboardInterrupt:
        print("Traffic simulation stopped.")
