import { useState } from 'react'


export default function ChatInput({ onSend, loading }) {
  const [input, setInput] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()

    if (!input.trim() || loading) {
      return
    }

    onSend(input)
    setInput('')
  }

  return (
    <form className="chat-input-form" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Ask something about your PDFs..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />

      <button type="submit" disabled={loading}>
        {loading ? 'Thinking...' : 'Send'}
      </button>
    </form>
  )
}