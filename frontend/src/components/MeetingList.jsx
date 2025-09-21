import React from 'react'

export default function MeetingList({ items, onSelect }) {
  return (
    <div className="bg-white rounded-2xl shadow p-4">
      <h2 className="text-lg font-semibold mb-3">Meetings</h2>
      <ul className="space-y-2">
        {items.map(m => (
          <li key={m.id} className="border rounded-xl p-3 hover:bg-gray-50 cursor-pointer" onClick={() => onSelect(m)}>
            <div className="flex justify-between">
              <div>
                <p className="font-medium">{m.title}</p>
                <p className="text-xs text-gray-500">{new Date(m.created_at).toLocaleString()}</p>
              </div>
              <div className="text-right">
                <div className="text-xs text-gray-600">{(m.duration_sec || 0).toFixed(0)}s</div>
                <div className="space-x-1 mt-1">
                  {m.tags.slice(0,4).map(t => <span key={t} className="text-[10px] px-2 py-0.5 bg-gray-100 rounded-full">{t}</span>)}
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
