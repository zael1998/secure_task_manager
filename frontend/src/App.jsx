import { useState } from "react"
import LoginForm from "./components/LoginForm"
import RegisterForm from "./components/RegisterForm"
import TaskForm from "./components/TaskForm"
import TaskList from "./components/TaskList"

export default function App() {
  const [token, setToken] = useState(
    localStorage.getItem("token")
  )

  function cerrarSesion() {
    localStorage.removeItem("token")
    setToken(null)
  }

  return (
    <div>
      <h1>Secure Task Manager</h1>

      {token ? (
        <>
          <button onClick={cerrarSesion}>
            Cerrar sesión
          </button>

          <TaskForm />

          <TaskList />
        </>
      ) : (
        <>
          <LoginForm onLogin={setToken} />

          <RegisterForm />
        </>
      )}
    </div>
  )
}