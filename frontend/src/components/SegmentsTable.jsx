import React, { useEffect, useState } from 'react'
import { getSegments } from '../api/api'

export default function SegmentsTable({ meetingId }) {
  const [rows, setRows] = useState([])

  useEffect(() => {
    if (meetingId) getSegments(meetingId).then(setRows).catch(console.error)
  }, [meetingId])

  return (
    <div className="bg-white rounded-2xl shadow p-4 overflow-auto">
      <h3 className="text-lg font-semibold mb-2">Transcript</h3>
      <table className="min-w-full text-sm">
        <thead>
          <tr className="text-left border-b">
            <th className="py-2 pr-4">Time</th>
            <th className="py-2 pr-4">Speaker</th>
            <th className="py-2 pr-4">Text</th>
            <th className="py-2 pr-4">Sentiment</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(r => (
            <tr key={r.id} className="border-b">
              <td className="py-2 pr-4 text-xs">{r.start.toFixed(1)}–{r.end.toFixed(1)}s</td>
              <td className="py-2 pr-4">{r.speaker}</td>
              <td className="py-2 pr-4">{r.text}</td>
              <td className="py-2 pr-4">{r.sentiment?.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
