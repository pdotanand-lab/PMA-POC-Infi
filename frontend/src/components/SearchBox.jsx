import React, { useState } from 'react'
import { searchSegments } from '../api/api'

export default function SearchBox() {
  const [q, setQ] = useState('')
  const [hits, setHits] = useState([])

  const onSearch = async () => {
    if (!q) return
    try {
      const res = await searchSegments(q)
      setHits(res || [])
    } catch (error) {
      console.error('Search error:', error)
      setHits([])
    }
  }

  return (
    <div className="bg-white rounded-2xl shadow p-4">
      <h3 className="text-lg font-semibold mb-2">Semantic Search</h3>
      <div className="flex gap-2">
        <input
          value={q}
          onChange={e=>setQ(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && onSearch()}
          placeholder="Search meetings..."
          className="flex-1 border rounded-xl px-3 py-1"
        />
        <button onClick={onSearch} className="px-3 py-1 rounded-xl bg-green-600 text-white">Search</button>
      </div>
      <ul className="mt-3 space-y-2">
        {hits.map((h,i)=>(
          <li key={i} className="text-sm border rounded-xl p-2">
            <div className="text-gray-600">{h.meeting_title} — {h.start}s</div>
            <div>{h.text}</div>
            <div className="text-xs text-gray-500">score: {h.score?.toFixed(3) || 'N/A'}</div>
          </li>
        ))}
      </ul>
    </div>
  )
}
