import os
import sqlite3
from datetime import date, datetime, timezone

from flask import Flask, jsonify, request


app = Flask(__name__)

DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    "/data/presenze.db"
)


def connection():
    database = sqlite3.connect(DATABASE_PATH)
    database.row_factory = sqlite3.Row
    return database


def initialize_database():
    os.makedirs(
        os.path.dirname(DATABASE_PATH),
        exist_ok=True
    )

    with connection() as database:
        database.execute(
            """
            CREATE TABLE IF NOT EXISTS presenze (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                giorno TEXT NOT NULL,
                inserita_il TEXT NOT NULL
            )
            """
        )

        database.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            indice_nome_giorno
            ON presenze(nome COLLATE NOCASE, giorno)
            """
        )

        database.commit()


@app.get("/health")
def health():
    return "attendance-api-ok\n"


@app.get("/api/presenze")
def list_attendance():
    giorno = request.args.get(
        "giorno",
        date.today().isoformat()
    )

    with connection() as database:
        rows = database.execute(
            """
            SELECT id, nome, giorno, inserita_il
            FROM presenze
            WHERE giorno = ?
            ORDER BY nome COLLATE NOCASE
            """,
            (giorno,)
        ).fetchall()

    return jsonify({
        "giorno": giorno,
        "totale": len(rows),
        "presenze": [
            dict(row)
            for row in rows
        ]
    })


@app.post("/api/presenze")
def add_attendance():
    content = request.get_json(
        silent=True
    ) or {}

    nome = str(
        content.get("nome", "")
    ).strip()

    giorno = str(
        content.get(
            "giorno",
            date.today().isoformat()
        )
    ).strip()

    if not nome:
        return jsonify({
            "error": "Il nome è obbligatorio"
        }), 400

    if len(nome) > 80:
        return jsonify({
            "error": "Il nome è troppo lungo"
        }), 400

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    try:
        with connection() as database:
            cursor = database.execute(
                """
                INSERT INTO presenze (
                    nome,
                    giorno,
                    inserita_il
                )
                VALUES (?, ?, ?)
                """,
                (
                    nome,
                    giorno,
                    timestamp
                )
            )

            database.commit()

            attendance_id = cursor.lastrowid

    except sqlite3.IntegrityError:
        return jsonify({
            "error": (
                "Questo nome è già presente "
                "per la giornata selezionata"
            )
        }), 409

    return jsonify({
        "id": attendance_id,
        "nome": nome,
        "giorno": giorno,
        "inserita_il": timestamp
    }), 201


@app.delete("/api/presenze/<int:attendance_id>")
def delete_attendance(attendance_id):
    with connection() as database:
        cursor = database.execute(
            """
            DELETE FROM presenze
            WHERE id = ?
            """,
            (attendance_id,)
        )

        database.commit()

    if cursor.rowcount == 0:
        return jsonify({
            "error": "Presenza non trovata"
        }), 404

    return jsonify({
        "deleted": True,
        "id": attendance_id
    })


@app.delete("/api/presenze")
def clear_attendance():
    giorno = request.args.get(
        "giorno",
        date.today().isoformat()
    )

    with connection() as database:
        cursor = database.execute(
            """
            DELETE FROM presenze
            WHERE giorno = ?
            """,
            (giorno,)
        )

        database.commit()

    return jsonify({
        "deleted": cursor.rowcount,
        "giorno": giorno
    })


initialize_database()

app.run(
    host="0.0.0.0",
    port=5000
)
