from flask import Flask, render_template, request, session, redirect, url_for
import random, time, json, os

app = Flask(__name__)
app.secret_key = "clave-secreta"

RECORDS_FILE = "records.json"

CORREOS_BASE = [
    {"remitente":"Seguridad <alerta@banco-falso.com>","asunto":"⚠️ Cuenta suspendida","mensaje":"Verifique su cuenta ahora.","respuesta":"falso","explicacion":"Urgencia y dominio falso."},
    {"remitente":"Facturación <facturas@empresa.com>","asunto":"Factura","mensaje":"Adjuntamos su factura.","respuesta":"real","explicacion":"Correo informativo."},
    {"remitente":"Soporte <support@secure-login.net>","asunto":"Contraseña","mensaje":"Actualice su contraseña.","respuesta":"falso","explicacion":"Amenaza."},
    {"remitente":"Tienda <ventas@tienda.com>","asunto":"Pedido enviado","mensaje":"Su pedido fue enviado.","respuesta":"real","explicacion":"Mensaje legítimo."},
    {"remitente":"Banco <info@bc-validacion.com>","asunto":"Verificación","mensaje":"Ingrese sus datos bancarios.","respuesta":"falso","explicacion":"Solicitud de datos sensibles."},
    {"remitente":"PayPal <service@paypal-check.com>","asunto":"Actividad inusual","mensaje":"Confirme su información.","respuesta":"falso","explicacion":"Dominio falso."},
    {"remitente":"Universidad <notificaciones@utp.ac.pa>","asunto":"Notas","mensaje":"Notas publicadas.","respuesta":"real","explicacion":"Correo institucional."},
    {"remitente":"Netflix <info@netflix.com>","asunto":"Pago rechazado","mensaje":"No se procesó su pago.","respuesta":"real","explicacion":"Mensaje habitual."},
    {"remitente":"Microsoft <secure@microsoft-check.net>","asunto":"Cuenta comprometida","mensaje":"Inicie sesión.","respuesta":"falso","explicacion":"Dominio falso."},
    {"remitente":"Amazon <orders@amazon.com>","asunto":"Confirmación","mensaje":"Gracias por su compra.","respuesta":"real","explicacion":"Correo legítimo."}
]

def load_records():
    if not os.path.exists(RECORDS_FILE):
        return []
    with open(RECORDS_FILE, "r") as f:
        return json.load(f)

def save_record(nombre, score, time_spent):
    records = load_records()

    records.append({
        "nombre": nombre,
        "puntaje": score,
        "tiempo": time_spent
    })

    records = sorted(
        records,
        key=lambda x: (-x["puntaje"], x["tiempo"])
    )[:5]

    with open(RECORDS_FILE, "w") as f:
        json.dump(records, f, indent=2)


@app.route("/")
def start():
    session.clear()
    return render_template("start.html")


@app.route("/inicio", methods=["POST"])
def inicio():
    session.clear()

    # guarda el nombre del jugador
    session["nombre"] = request.form.get("nombre", "Jugador").strip() or "Jugador"

    session["indice"] = 0
    session["puntaje"] = 0
    session["fallos"] = 0
    session["inicio_tiempo"] = time.time()

    correos = CORREOS_BASE.copy()
    random.shuffle(correos)
    session["correos"] = correos

    return redirect(url_for("juego"))


@app.route("/juego", methods=["GET", "POST"])
def juego():
    correos = session["correos"]
    i = session["indice"]

    if i >= len(correos):
        return redirect(url_for("resultado"))

    if request.method == "POST":
        eleccion = request.form.get("respuesta")
        correcto = correos[i]["respuesta"]
        session["es_phishing"] = correos[i]["respuesta"] == "falso"

        if eleccion == "timeout":
            session["fallos"] += 1
            session["correcto"] = False
            session["explicacion"] = "⏱️ Tiempo agotado."
        else:
            session["correcto"] = eleccion == correcto
            session["explicacion"] = correos[i]["explicacion"]

            if session["correcto"]:
                session["puntaje"] += 5
            else:
                session["fallos"] += 1

        session["indice"] += 1

        if session["fallos"] >= 3:
            return redirect(url_for("resultado"))

        return redirect(url_for("feedback"))

    progreso = int((i / len(correos)) * 100)
    return render_template("index.html", correo=correos[i], progreso=progreso)

@app.route("/feedback")
def feedback():
    return render_template("feedback.html",
        correcto=session["correcto"],
        explicacion=session["explicacion"],
        es_phishing=session["es_phishing"]
    )


@app.route("/resultado")
def resultado():
    nombre = session.get("nombre", "Jugador")
    puntaje = session.get("puntaje", 0)
    fallos = session.get("fallos", 3)
    total_time = int(time.time() - session.get("inicio_tiempo", time.time()))

    records = load_records()
    nuevo = False

    # SOLO guarda récord si NO perdió por las 3 vidas
    if fallos < 3:
        save_record(nombre, puntaje, total_time)
        records = load_records()

        # Verificar si este jugador entró al Top 5
        for r in records:
            if (
                r.get("nombre") == nombre and
                r.get("puntaje") == puntaje and
                r.get("tiempo") == total_time
            ):
                nuevo = True
                break

    # Orden final (por seguridad)
    records.sort(key=lambda x: (-x["puntaje"], x["tiempo"]))

    return render_template(
        "resultado.html",
        nombre=nombre,
        puntaje=puntaje,
        tiempo=total_time,
        records=records,
        nuevo=nuevo
    )

if __name__ == "__main__":
    app.run(debug=True)

