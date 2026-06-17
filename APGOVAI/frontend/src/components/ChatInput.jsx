import {
  useState,
} from 'react'

import {
  FiSend,
} from 'react-icons/fi'


export default function ChatInput({

  onSend,

  loading,

  placeholder,

  sendLabel,

}) {

  const [
    input,

    setInput,

  ] = useState(
    ''
  )


  const submit =
    (
      e
    ) => {

      e.preventDefault()

      if (
        !input.trim()
        ||
        loading
      ) {

        return

      }

      onSend(
        input
      )

      setInput(
        ''
      )

    }


  return (

    <form

      className='chat-input-form'

      onSubmit={
        submit
      }

    >

      <input

        value={
          input
        }

        onChange={
          e =>

            setInput(

              e.target.value

            )
        }

        placeholder={
          placeholder
        }

      />


      <button

        disabled={
          loading
        }

        title={
          sendLabel
        }

      >

        <FiSend aria-hidden="true" />

        <span>
          {sendLabel}
        </span>

      </button>

    </form>

  )

}
