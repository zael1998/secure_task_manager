import { useState } from "react"

export default function LoginForm({ onLogin }) {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  async function handleSubmit(event) {
    event.preventDefault()

    const response = await fetch(
      "https://redesigned-journey-69gq6pqxx4q6frjwp-8000.app.github.dev/login",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          email,
          password
        })
      }
    )

    const data = await response.json()

    if (response.ok) {
      localStorage.setItem("token", data.access_token)
      onLogin(data.access_token)

      setEmail("")
      setPassword("")
    }

    console.log(data)
  }

  return (
    <form onSubmit={handleSubmit}>
      <fieldset>
        <legend>Login</legend>

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
          Login
        </button>
      </fieldset>
    </form>
  )
}