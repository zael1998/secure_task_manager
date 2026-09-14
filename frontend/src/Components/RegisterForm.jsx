import { useState } from "react"

export default function RegisterForm() {
  const [username, setUsername] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  const handleSubmit = async (event) => {
    event.preventDefault()

    const response = await fetch(
      "https://redesigned-journey-69gq6pqxx4q6frjwp-8000.app.github.dev/users",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          username,
          email,
          password
        })
      }
    )

    const data = await response.json()

    if (response.ok) {
      setUsername("")
      setEmail("")
      setPassword("")
    }

    console.log(data)
  }

  return (
    <form onSubmit={handleSubmit}>
      <fieldset>
        <legend>Registro</legend>

        <label>Username</label>
        <input
          type="text"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
        />

        <label>Email</label>
        <input
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />

        <label>Contraseña</label>
        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />

        <button type="submit">
          Registrarse
        </button>
      </fieldset>
    </form>
  )
}