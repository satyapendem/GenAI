import MessageBubble from './MessageBubble'


export default function ChatWindow({ messages }) {
  return (
    <div className="chat-window">
      {messages.map((message, index) => (
        <MessageBubble
          key={index}
          role={message.role}
          text={message.text}
        />
      ))}
    </div>
  )
}