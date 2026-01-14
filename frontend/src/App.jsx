import React, {useState, useEffect, useRef} from 'react'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function App(){
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState(localStorage.getItem('session_id') || null)
  const boxRef = useRef(null)

  useEffect(()=>{
    localStorage.setItem('session_id', sessionId)
  },[sessionId])

  useEffect(()=>{
    if(boxRef.current) boxRef.current.scrollTop = boxRef.current.scrollHeight
  },[messages])

  const sendMessage = async () =>{
    if(!input.trim()) return
    const userMsg = {from:'user', text: input}
    setMessages(m=>[...m, userMsg])
    const payload = {message: input, session_id: sessionId}
    setInput('')
    try{
      const res = await axios.post(`${API_BASE}/chat`, payload)
      const {reply, session_id} = res.data
      setSessionId(session_id)
      setMessages(m=>[...m, {from:'ai', text: reply}])
    }catch(e){
      setMessages(m=>[...m, {from:'ai', text: 'Error contacting server.'}])
      console.error(e)
    }
  }

  const onKey = (e) =>{
    if(e.key === 'Enter' && !e.shiftKey){
      e.preventDefault(); sendMessage()
    }
  }

  return (
    <div className="chat-root">
      <div className="chat-box" ref={boxRef}>
        {messages.map((m, i)=> (
          <div key={i} className={"msg " + (m.from==='user'?'user':'ai')}>
            <div className="bubble">{m.text}</div>
          </div>
        ))}
      </div>
      <div className="composer">
        <textarea value={input} onChange={e=>setInput(e.target.value)} onKeyDown={onKey} placeholder="Type patient query or details..." />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  )
}
