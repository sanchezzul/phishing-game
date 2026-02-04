from flask import Flask, render_template, request, session, redirect, url_for
import random
import time

app = Flask(__name__)
app.secret_key = "clave-secreta"

# =========================
# BASE DE CORREOS (10)
# =========================
CORREOS_BASE = [
    {
        "remitente": "Seguridad Bancaria <alerta@banco-falso.com>",
        "asunto": "⚠️ Acción requerida: cuenta suspendida",
        "mensaje": "Detectamos actividad sospechosa. Verifique su cuenta inmediatamente.",
        "respuesta": "falso",
        "explicacion": "Urgencia, dominio falso y solicitud indirecta de acción."
    },
    {
        "remitente": "Facturación <facturas@empresa.com>",
        "asunto": "Factura del mes de enero",
        "mensaje": "Adjuntamos su factura correspondiente al mes actual.",
        "respuesta": "real",
        "explicacion": "Correo informativo sin enlaces ni presión."
    },
    {
        "remitente": "Soporte Técnico <support@secure-login.net>",
        "asunto": "Restablezca su contraseña",
        "mensaje": "Debe actualizar su contraseña para evitar el cierre de su cuenta.",
        "respuesta": "falso",
        "explicacion": "Amenaza y dominio sospechoso."
    },
    {
        "remitente": "Tienda Online <ventas@tiendaoficial.com>",
        "asunto": "📦 Pedido enviado",
        "mensaje": "Su pedido fue enviado correctamente.",
        "respuesta": "real",
        "explicacion": "Mensaje esperado sin solicitud de datos."
    },
    {
        "remitente": "Banco Central <info@bc-validacion.com>",
        "asunto": "Verificación de identidad",
        "mensaje": "Ingrese sus datos bancarios para validar su identidad.",
        "respuesta": "falso",
        "explicacion": "Solicitud directa de información sensible."
    },
    {
        "remitente": "PayPal <service@paypal-verificacion.com>",
        "asunto": "Actividad inusual detectada",
        "mensaje": "Confirme su información para evitar la suspensión.",
        "respuesta": "falso",
        "explicacion": "Dominio falso y solicitud de datos."
    },
    {
        "remitente": "Universidad <notificaciones@utp.ac.pa>",
        "asunto": "Publicación de calificaciones",
        "mensaje": "Las notas del semestre ya están disponibles.",
        "respuesta": "real",
        "explicacion": "Correo institucional legítimo."
    },
    {
        "remitente": "Netflix <info@netflix.com>",
        "asunto": "Problema con tu método de pago",
        "mensaje": "No pudimos procesar tu último pago.",
        "respuesta": "real",
        "explicacion": "Dominio legítimo y mensaje habitual."
    },
    {
        "remitente": "Soporte Microsoft <secure@microsoft-check.net>",
        "asunto": "Cuenta comprometida",
        "mensaje": "Inicie sesión para asegurar su cuenta.",
        "respuesta": "falso",
        "explicacion": "Dominio falso y mensaje alarmista."
    },
    {
        "remitente": "Amazon <orders@amazon.com>",
        "asunto": "Confirmación de pedido",
        "mensaje": "Gracias por su compra. Consulte los detalles en su cuenta.",
        "respuesta": "real",
        "explicacion": "Correo esperado sin solicitud de datos."
    }
]

# =========================
# RUTAS
# =========================

@app.route("/")
def inicio():
    session.clear()
    correos = CORREOS_BASE.copy()
    random.shuffle(correos)

    session["correos"] = correos
    session["indice"] = 0
    session["puntaje"] = 0

    return redirect(url_for("juego"))


@app.route("/juego", methods=["GET", "POST"])
def juego():
    indice = session.get("indice", 0)
    correos = session.get("correos", [])

    if indice >= len(correos):
        return redirect(url_for("resultado"))

    if request.method == "POST":
        eleccion = request.form.get("respuesta")
        correcto = correos[indice]["respuesta"]

        # ⏱️ Si se acaba el tiempo
        if eleccion == "timeout":
            session["correcto"] = False
            session["explicacion"] = "⏱️ Tiempo agotado. No se suman puntos."
        else:
            session["correcto"] = eleccion == correcto
            session["explicacion"] = correos[indice]["explicacion"]

            if session["correcto"]:
                session["puntaje"] += 1

        session["indice"] += 1
        return redirect(url_for("feedback"))

    return render_template(
        "index.html",
        correo=correos[indice],
        numero=indice + 1,
        total=len(correos),
        progreso=int(((indice + 1) / len(correos)) * 100)
    )


@app.route("/feedback")
def feedback():
    return render_template(
        "feedback.html",
        correcto=session.get("correcto"),
        explicacion=session.get("explicacion")
    )


@app.route("/resultado")
def resultado():
    puntaje = session.get("puntaje", 0)
    total = len(session.get("correos", []))

    if puntaje == total:
        mensaje = "🥇 ¡Experto en detección de phishing!"
    elif puntaje >= total // 2:
        mensaje = "🥈 Buen trabajo, pero puedes mejorar"
    else:
        mensaje = "🧠 Necesitas reforzar conceptos básicos"

    return render_template(
        "resultado.html",
        puntaje=puntaje,
        total=total,
        mensaje=mensaje
    )


@app.route("/reiniciar")
def reiniciar():
    return redirect(url_for("inicio"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
