import bcrypt
from flasgger import Swagger
from flask import Flask, jsonify, redirect, request
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)

# Configuración explícita de Swagger
app.config['SWAGGER'] = {
    'title': 'API Gestor de Contraseñas',
    'uiversion': 3,
}
swagger = Swagger(app)


def conectar():
  return pymysql.connect(
      host='localhost',
      user='root',
      passwd='',
      db='gestor_contrasena',
      charset='utf8mb4',
  )


# Redirección manual para evitar el error 404
@app.route('/docs')
def redirect_docs():
  return redirect('/apidocs/')


@app.route('/', methods=['GET'])
def consulta_general():
  """Consulta general del baul de contrasenas.
  ---
  responses:
    200:
      description: Lista de registros
  """
  try:
    conn = conectar()
    cur = conn.cursor()
    cur.execute('SELECT id_baul, plataforma, usuario, clave FROM baul')
    datos = cur.fetchall()
    data = [
        {
            'id_baul': row[0],
            'Plataforma': row[1],
            'usuario': row[2],
            'clave': row[3],
        }
        for row in datos
    ]
    cur.close()
    conn.close()
    return jsonify({'baul': data, 'mensaje': 'Baul de contrasenas'})
  except Exception as ex:
    return jsonify({'mensaje': 'Error'}), 500


@app.route('/consulta_individual/<int:codigo>', methods=['GET'])
def consulta_individual(codigo):
  """Consulta individual por ID.
  ---
  parameters:
    - name: codigo
      in: path
      required: true
      type: integer
  responses:
    200:
      description: Registro encontrado
  """
  try:
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        'SELECT id_baul, plataforma, usuario, clave FROM baul WHERE id_baul = %s',
        (codigo,),
    )
    datos = cur.fetchone()
    cur.close()
    conn.close()
    if datos:
      dato = {
          'id_baul': datos[0],
          'Plataforma': datos[1],
          'usuario': datos[2],
          'clave': datos[3],
      }
      return jsonify({'baul': dato, 'mensaje': 'Registro encontrado'})
    return jsonify({'mensaje': 'Registro no encontrado'}), 404
  except Exception as ex:
    return jsonify({'mensaje': 'Error'}), 500


@app.route('/registro/', methods=['POST'])
def registro():
  """Registrar nueva contrasena.
  ---
  parameters:
    - name: body
      in: body
      required: true
      schema:
        type: object
        properties:
          plataforma:
            type: string
          usuario:
            type: string
          clave:
            type: string
  responses:
    200:
      description: Registro agregado
  """
  try:
    data = request.get_json()
    clave_enc = bcrypt.hashpw(
        data['clave'].encode('utf-8'), bcrypt.gensalt()
    ).decode('utf-8')
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO baul (plataforma, usuario, clave) VALUES (%s, %s, %s)',
        (data['plataforma'], data['usuario'], clave_enc),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'mensaje': 'Registro agregado'})
  except Exception as ex:
    return jsonify({'mensaje': 'Error'}), 500


@app.route('/eliminar/<int:codigo>', methods=['DELETE'])
def eliminar(codigo):
  """Eliminar registro por ID.
  ---
  parameters:
    - name: codigo
      in: path
      required: true
      type: integer
  responses:
    200:
      description: Registro eliminado
  """
  try:
    conn = conectar()
    cur = conn.cursor()
    cur.execute('DELETE FROM baul WHERE id_baul = %s', (codigo,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'mensaje': 'Eliminado'})
  except Exception as ex:
    return jsonify({'mensaje': 'Error'}), 500


@app.route('/actualizar/<int:codigo>', methods=['PUT'])
def actualizar(codigo):
  """Actualizar registro por ID.
  ---
  parameters:
    - name: codigo
      in: path
      required: true
      type: integer
    - name: body
      in: body
      required: true
      schema:
        type: object
        properties:
          plataforma:
            type: string
          usuario:
            type: string
          clave:
            type: string
  responses:
    200:
      description: Registro actualizado
  """
  try:
    data = request.get_json()
    clave_enc = bcrypt.hashpw(
        data['clave'].encode('utf-8'), bcrypt.gensalt()
    ).decode('utf-8')
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        'UPDATE baul SET plataforma=%s, usuario=%s, clave=%s WHERE id_baul=%s',
        (data['plataforma'], data['usuario'], clave_enc, codigo),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'mensaje': 'Registro actualizado'})
  except Exception as ex:
    return jsonify({'mensaje': 'Error'}), 500


if __name__ == '__main__':
  app.run(debug=True)