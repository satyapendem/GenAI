import MessageBubble from './MessageBubble'


export default function ChatWindow({

  messages,

  loading,

  t,

}) {

  return (

    <div className='chat-window'>

      {

        messages.map(
          (msg, idx) => (

            <div key={idx}>

              {

                msg.text && (

                  <MessageBubble

                    role='user'

                    text={
                      msg.text
                    }

                  />

                )

              }


              {

                msg.answer && (

                  <MessageBubble

                    role='assistant'

                    text={
                      msg.answer
                    }

                  />

                )

              }

            </div>

          )

        )

      }


      {

        loading && (

        <div className='thinking'>

            {t.app.thinking}

          </div>

        )

      }

    </div>

  )

}
