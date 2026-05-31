import {
  useState,
} from 'react'


export default function ChatInput({

  onSend,

  loading,

  placeholder,

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

      >

        Send

      </button>

    </form>

  )

}