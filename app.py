from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from config import Config
import pandas as pd
import io

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(80), unique=True, nullable=False)
    contraseña = db.Column(db.String(80), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='empleado')

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    proyecto = db.Column(db.String(100), nullable=False)
    porcentaje = db.Column(db.Integer, nullable=False)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def validar_login():
    correo = request.form['correo']
    contraseña = request.form['contraseña']
    usuario = Usuario.query.filter_by(correo=correo, contraseña=contraseña).first()
    if usuario:
        return redirect(url_for('dashboard', user_id=usuario.id))
    else:
        flash('Credenciales inválidas')
        return redirect(url_for('login'))

@app.route('/dashboard/<int:user_id>')
def dashboard(user_id):
    registros = Registro.query.filter_by(usuario_id=user_id).all()
    return render_template('dashboard.html', user_id=user_id, registros=registros)

@app.route('/registrar', methods=['POST'])
def registrar_tiempo():
    user_id = int(request.form['user_id'])
    proyecto = request.form['proyecto']
    porcentaje = int(request.form['porcentaje'])
    registros = Registro.query.filter_by(usuario_id=user_id).all()
    suma_total = sum(r.porcentaje for r in registros) + porcentaje
    if suma_total > 100:
        flash('❌ Error: El total supera el 100%.')
    else:
        nuevo = Registro(usuario_id=user_id, proyecto=proyecto, porcentaje=porcentaje)
        db.session.add(nuevo)
        db.session.commit()
        flash('✅ Registro guardado correctamente.')
    return redirect(url_for('dashboard', user_id=user_id))

@app.route('/editar/<int:registro_id>/<int:user_id>', methods=['GET','POST'])
def editar_registro(registro_id, user_id):
    registro = Registro.query.get_or_404(registro_id)
    if request.method == 'POST':
        registro.proyecto = request.form['proyecto']
        registro.porcentaje = int(request.form['porcentaje'])
        db.session.commit()
        flash('Registro actualizado correctamente.')
        return redirect(url_for('dashboard', user_id=user_id))
    return render_template('editar.html', registro=registro, user_id=user_id)

@app.route('/reporte')
def reporte():
    registros = Registro.query.all()
    return render_template('reporte.html', registros=registros)

@app.route('/exportar')
def exportar():
    registros = Registro.query.all()
    data = [{'Usuario ID': r.usuario_id, 'Proyecto': r.proyecto, 'Porcentaje': r.porcentaje} for r in registros]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte')
    output.seek(0)
    return send_file(output, download_name='reporte.xlsx', as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Usuario.query.filter_by(correo='admin@empresa.com').first():
            admin = Usuario(correo='admin@empresa.com', contraseña='admin123', rol='admin')
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)
