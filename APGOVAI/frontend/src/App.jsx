import { useState } from 'react'

import ChatWindow from './components/ChatWindow'
import ChatInput from './components/ChatInput'

import { streamChat } from './api'


export default function App() {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)


  const handleSend = async (question) => {
    setLoading(true)

    const userMessage = {
      role: 'user',
      text: question,
    }

    const assistantMessage = {
      role: 'assistant',
      text: '',
    }

    setMessages((prev) => [
      ...prev,
      userMessage,
      assistantMessage,
    ])

    let streamedText = ''

    await streamChat(question, (chunk) => {
      streamedText += chunk

      setMessages((prev) => {
        const updated = [...prev]

        updated[updated.length - 1] = {
          role: 'assistant',
          text: streamedText,
        }

        return updated
      })
    })

    setLoading(false)
  }


  return (
    <div className="app-container">
      <div className="chat-card">
        <h1>Welcome to APGOVAI</h1>

        <ChatWindow messages={messages} />

        <ChatInput
          onSend={handleSend}
          loading={loading}
        />
      </div>
    </div>
  )
}