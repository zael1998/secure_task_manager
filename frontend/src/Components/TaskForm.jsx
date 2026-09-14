import { useState } from "react"

export default function TaskForm() {
  const [titulo, setTitulo] = useState("")
  const [descripcion, setDescripcion] = useState("")
  const [estado, setEstado] = useState("")

  async function crearTarea(event) {
    event.preventDefault()

    const token = localStorage.getItem("token")

    const response = await fetch(
      "https://redesigned-journey-69gq6pqxx4q6frjwp-8000.app.github.dev/tasks",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          titulo,
          descripcion,
          estado
        })
      }
    )

    const data = await response.json()

    if (response.ok) {
      setTitulo("")
      setDescripcion("")
      setEstado("")
    }

    console.log(data)
  }

  return (
    <form onSubmit={crearTarea}>
      <fieldset>
        <legend>Nueva tarea</legend>

        <label>Título</label>
        <input
          type="text"
          value={titulo}
          onChange={(event) => setTitulo(event.target.value)}
        />

        <label>Descripción</label>
        <input
          type="text"
          value={descripcion}
          onChange={(event) => setDescripcion(event.target.value)}
        />

        <label>Estado</label>
        <input
          type="text"
          value={estado}
          onChange={(event) => setEstado(event.target.value)}
        />

        <button type="submit">
          Crear tarea
        </button>
      </fieldset>
    </form>
  )
}