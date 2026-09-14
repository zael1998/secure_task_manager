from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError
import sqlite3


# -------------------------
# APP
# -------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://redesigned-journey-69gq6pqxx4q6frjwp-5173.app.github.dev"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# CONFIGURACIÓN SEGURIDAD
# -------------------------

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

SECRET_KEY = "mi_clave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# -------------------------
# MODELOS
# -------------------------

class LoginData(BaseModel):
    email: str
    password: str


class User(BaseModel):
    username: str
    email: str
    password: str


class Task(BaseModel):
    titulo: str
    descripcion: str
    estado: str


class TaskOpcional(BaseModel):
    titulo: str | None = None
    descripcion: str | None = None
    estado: str | None = None


# -------------------------
# BASE DE DATOS
# -------------------------

def conectarDb():
    conexion = sqlite3.connect("user.db")
    conexion.row_factory = sqlite3.Row
    return conexion


def crearTablas():
    with conectarDb() as conexion:
        cursor = conexion.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            fechaCreacion TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            estado TEXT NOT NULL,
            fechaCreacion TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)


crearTablas()


# -------------------------
# AUTENTICACIÓN
# -------------------------

def crearToken(datos: dict):
    datosToken = datos.copy()

    expiracion = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    datosToken.update({
        "exp": expiracion
    })

    token = jwt.encode(
        datosToken,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def obtenerUsuarioActual(
    token: str = Depends(oauth2_scheme)
):
    try:
        datosToken = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = datosToken["sub"]

    except (JWTError, KeyError):
        raise HTTPException(
            status_code=401,
            detail="Token no válido"
        )

    with conectarDb() as conexion:
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        )

        usuario = cursor.fetchone()

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Usuario no válido"
        )

    return usuario


# -------------------------
# USUARIOS
# -------------------------

@app.post("/users")
def crearUsuario(nuevoUsuario: User):
    fechaActual = datetime.now().isoformat()

    passwordHasheada = pwd_context.hash(
        nuevoUsuario.password
    )

    with conectarDb() as conexion:
        cursor = conexion.cursor()

        cursor.execute("""
        INSERT INTO users(
            username,
            email,
            password,
            fechaCreacion
        )
        VALUES (?, ?, ?, ?)
        """, (
            nuevoUsuario.username,
            nuevoUsuario.email,
            passwordHasheada,
            fechaActual
        ))

    return {
        "message": "Usuario creado con éxito"
    }


@app.post("/login")
def login(logeo: LoginData):
    with conectarDb() as conexion:
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email = ?",
            (logeo.email,)
        )

        usuario = cursor.fetchone()

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas"
        )

    passwordCorrecta = pwd_context.verify(
        logeo.password,
        usuario["password"]
    )

    if not passwordCorrecta:
        raise HTTPException(
            status_code=401,
            detail="Contraseña incorrecta"
        )

    token = crearToken({
        "sub": usuario["email"]
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@app.get("/perfil")
def obtenerPerfil(
    usuarioActual=Depends(obtenerUsuarioActual)
):
    return {
        "id": usuarioActual["id"],
        "username": usuarioActual["username"],
        "email": usuarioActual["email"],
        "fechaCreacion": usuarioActual["fechaCreacion"]
    }


# -------------------------
# TAREAS
# -------------------------

@app.post("/tasks")
def crearTarea(
    nuevaTarea: Task,
    usuarioActual=Depends(obtenerUsuarioActual)
):
    fechaCreacion = datetime.now().isoformat()

    with conectarDb() as conexion:
        cursor = conexion.cursor()

        cursor.execute("""
        INSERT INTO tasks(
            titulo,
            descripcion,
            estado,
            fechaCreacion,
            user_id
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            nuevaTarea.titulo,
            nuevaTarea.descripcion,
            nuevaTarea.estado,
            fechaCreacion,
            usuarioActual["id"]
        ))

    return {
        "message": "Tarea creada correctamente"
    }


@app.get("/tasks")
def obtenerTareas(
    usuarioActual=Depends(obtenerUsuarioActual)
):
    with conectarDb() as conexion:
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT * FROM tasks WHERE user_id = ?",
            (usuarioActual["id"],)
        )

        tareas = cursor.fetchall()

    resultado = []

    for tarea in tareas:
        resultado.append(dict(tarea))

    return resultado


@app.get("/tasks/{id}")
def obtenerTareasPorId(
    id: int,
    usuarioActual=Depends(obtenerUsuarioActual)
):
    with conectarDb() as conexion:
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
            (id, usuarioActual["id"])
        )

        resultado = cursor.fetchone()

    if resultado is None:
        raise HTTPException(
            status_code=404,
            detail="Tarea no encontrada"
        )

    return dict(resultado)


@app.delete("/tasks/{id}")
def borrarTarea(
    id: int,
    usuarioActual=Depends(obtenerUsuarioActual)
):
    with conectarDb() as conexion:
        cursor = conexion.cursor()

        cursor.execute(
            "DELETE FROM tasks WHERE id = ? AND user_id = ?",
            (id, usuarioActual["id"])
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Tarea no encontrada"
            )

    return {
        "message": "Tarea borrada correctamente"
    }


@app.patch("/tasks/{id}")
def editarTarea(
    id: int,
    cambios: TaskOpcional,
    usuarioActual=Depends(obtenerUsuarioActual)
):
    with conectarDb() as conexion:
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
            (id, usuarioActual["id"])
        )

        tarea = cursor.fetchone()

        if tarea is None:
            raise HTTPException(
                status_code=404,
                detail="Tarea no encontrada"
            )

        if cambios.titulo is not None:
            cursor.execute(
                "UPDATE tasks SET titulo = ? WHERE id = ? AND user_id = ?",
                (cambios.titulo, id, usuarioActual["id"])
            )

        if cambios.descripcion is not None:
            cursor.execute(
                "UPDATE tasks SET descripcion = ? WHERE id = ? AND user_id = ?",
                (cambios.descripcion, id, usuarioActual["id"])
            )

        if cambios.estado is not None:
            cursor.execute(
                "UPDATE tasks SET estado = ? WHERE id = ? AND user_id = ?",
                (cambios.estado, id, usuarioActual["id"])
            )

    return {
        "message": "Tarea actualizada correctamente"
    }