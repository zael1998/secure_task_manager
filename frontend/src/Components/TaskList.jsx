import { useState, useEffect } from "react"

export default function TaskList() {
  const [tasks, setTasks] = useState([])

  useEffect(() => {
    async function cargarTareas() {
      const token = localStorage.getItem("token")

      const response = await fetch(
        "https://redesigned-journey-69gq6pqxx4q6frjwp-8000.app.github.dev/tasks",
        {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${token}`
          }
        }
      )

      const data = await response.json()

      if (response.ok) {
        setTasks(data)
      }

      console.log(data)
    }

    cargarTareas()
  }, [])

  return (
    <div>
      <h2>Mis tareas</h2>

      {tasks.map((task) => (
        <div key={task.id}>
          <h3>{task.titulo}</h3>
          <p>{task.descripcion}</p>
          <p>{task.estado}</p>
        </div>
      ))}
    </div>
  )
}