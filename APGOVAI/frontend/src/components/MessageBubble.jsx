import ReactMarkdown from 'react-markdown'

import remarkGfm from 'remark-gfm'


export default function MessageBubble({

  role,

  text,

}) {

  return (

    <div className={`message ${role}`}>

      <div className='message-content markdown-body'>

        <ReactMarkdown
          remarkPlugins={[
            remarkGfm
          ]}
        >

          {text || ''}

        </ReactMarkdown>

      </div>

    </div>

  )

}