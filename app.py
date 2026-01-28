# app.py
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "clave-secreta"

correos = [
    {
        "mensaje": "Su cuenta será bloqueada. Verifique ahora haciendo clic en este enlace.",
        "respuesta": "falso",
        "explicacion": "Mensaje urgente con enlace sospechoso."
    },
    {
        "mensaje": "Adjuntamos la factura correspondiente al mes actual.",
        "respuesta": "real",
        "explicacion": "Correo informativo sin presión ni enlaces sospechosos."
    },
    {
        "mensaje": "Actualice su contraseña inmediatamente para evitar el cierre de su cuenta.",
        "respuesta": "falso",
        "explicacion": "Uso de amenazas y sensación de urgencia."
    },
    {
        "mensaje": "Su pedido ha sido enviado correctamente. Puede revisar el estado en su cuenta oficial.",
        "respuesta": "real",
        "explicacion": "Mensaje informativo sin solicitar datos personales."
    },
    {
        "mensaje": "Hemos detectado actividad inusual. Ingrese sus datos bancarios para validar su identidad.",
        "respuesta": "falso",
        "explicacion": "Solicitud directa de información sensible, típica de phishing."
    }
]

# 🔹 Ruta de inicio limpio
@app.route("/inicio")
def inicio():
    session.clear()
    session["indice"] = 0
    session["puntaje"] = 0
    return redirect(url_for("index"))

# 🔹 Juego principal
@app.route("/", methods=["GET", "POST"])
def index():
    if "indice" not in session or session.get("finalizado"):
        session.clear()
        session["indice"] = 0
        session["puntaje"] = 0
        session["finalizado"] = False

    if session["indice"] >= len(correos):
        session["finalizado"] = True
        return redirect(url_for("resultado"))

    indice = session["indice"]

    if request.method == "POST":
        eleccion = request.form["respuesta"]
        correcto = correos[indice]["respuesta"]

        session["es_correcto"] = eleccion == correcto
        session["explicacion"] = correos[indice]["explicacion"]

        if session["es_correcto"]:
            session["puntaje"] += 1

        return redirect(url_for("feedback"))

    return render_template(
        "index.html",
        correo=correos[indice],
        numero=indice + 1,
        total=len(correos)
    )

# 🔹 Pantalla de feedback
@app.route("/feedback")
def feedback():
    return render_template(
        "feedback.html",
        correcto=session.get("es_correcto"),
        explicacion=session.get("explicacion")
    )

# 🔹 Avanzar pregunta
@app.route("/siguiente")
def siguiente():
    session["indice"] += 1

    if session["indice"] >= len(correos):
        puntaje = session["puntaje"]
        total = len(correos)

        if puntaje == total:
            mensaje = "🥇 ¡Experto en detección de phishing!"
        elif puntaje >= 3:
            mensaje = "🥈 Buen trabajo, pero ojo con los detalles"
        else:
            mensaje = "🧠 Necesitas reforzar conceptos básicos"

        return render_template(
            "resultado.html",
            puntaje=puntaje,
            total=total,
            mensaje=mensaje
        )

    return redirect(url_for("index"))

# 🔹 Reiniciar juego
@app.route("/reiniciar")
def reiniciar():
    return redirect(url_for("inicio"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

