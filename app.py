from flask import Flask, request, render_template
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import os
import sqlite3


app = Flask(__name__)
model = load_model('model/tanaman_obat_final.h5')

class_names = [
    'Daun_binahong', 'Daun_brotowali', 'Daun_jintan_hitam',
    'Daun_jahe', 'Daun_kencur', 'Daun_kunyit',
    'Daun_sambiroto', 'Daun_sirih', 'Daun_temulawak'
]

@app.route('/', methods=['GET', 'POST'])
def index():
    prediction = None
    confidence = None
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filepath = os.path.join('static', file.filename)
            file.save(filepath)

            img = image.load_img(filepath, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0) / 255.

            pred = model.predict(img_array)
            prediction = class_names[np.argmax(pred)]
            confidence = round(np.max(pred) * 100, 2)

                        # Simpan hasil ke database
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO predictions (filename, result, confidence)
            VALUES (?, ?, ?)
        ''', (file.filename, prediction, float(confidence)))
            conn.commit()
            conn.close()


            return render_template('index.html', prediction=prediction, confidence=confidence, img_path=filepath)

    return render_template('index.html')

@app.route("/history")
def history():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM predictions ORDER BY timestamp DESC")
    data = cursor.fetchall()
    conn.close()

    # Konversi confidence (baris ke-4) dari bytes → string
    clean_data = []
    for row in data:
        confidence = row[3]
        if isinstance(confidence, bytes):
            confidence = confidence.decode("utf-8", errors="ignore")
        clean_row = (row[0], row[1], row[2], confidence, row[4])
        clean_data.append(clean_row)

    return render_template("history.html", data=clean_data)


@app.route('/delete-history', methods=['POST'])
def delete_history():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predictions")
    conn.commit()
    conn.close()
    return render_template('history.html', data=[])

@app.route('/delete/<int:id>', methods=['POST'])
def delete_item(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predictions WHERE id = ?", (id,))
    conn.commit()
    cursor.execute("SELECT * FROM predictions ORDER BY timestamp DESC")
    data = cursor.fetchall()
    conn.close()
    return render_template('history.html', data=data)


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000)) 
    app.run(debug=False, host="0.0.0.0", port=port)
