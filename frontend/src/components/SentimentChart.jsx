import React, { useEffect, useState } from 'react'
import { getSegments } from '../api/api'
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts'

export default function SentimentChart({ meetingId }) {
  const [data, setData] = useState([])

  useEffect(() => {
    if (meetingId) getSegments(meetingId).then(rows => {
      setData(rows.map(r => ({ t: r.start, s: r.sentiment })))
    })
  }, [meetingId])

  return (
    <div className="bg-white rounded-2xl shadow p-4">
      <h3 className="text-lg font-semibold mb-2">Sentiment Over Time</h3>
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="t" tickFormatter={(v)=>v.toFixed(0)+'s'} />
          <YAxis domain={[-1,1]} />
          <Tooltip />
          <Line type="monotone" dataKey="s" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
