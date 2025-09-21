import React from 'react'

export default function SummaryCard({ summary }) {
  if (!summary) return <div className="p-4 bg-white rounded-2xl shadow">No summary yet.</div>
  const Item = ({title, items}) => (
    <div className="mb-3">
      <h4 className="font-semibold mb-1">{title}</h4>
      <ul className="list-disc ml-5 text-sm">{items?.map((x,i)=><li key={i}>{x}</li>)}</ul>
    </div>
  )
  return (
    <div className="p-4 bg-white rounded-2xl shadow">
      <h3 className="text-lg font-semibold mb-2">Summary</h3>
      <p className="text-sm mb-3">{summary.overview}</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Item title="Key Topics" items={summary.key_topics} />
        <Item title="Decisions" items={summary.decisions} />
        <Item title="Action Items" items={summary.action_items} />
        {!!summary.risks?.length && <Item title="Risks" items={summary.risks} />}
      </div>
      <div className="mt-3 text-sm"><b>Vibe:</b> {summary.vibe}</div>
    </div>
  )
}
