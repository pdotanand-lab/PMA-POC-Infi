import React, { useEffect, useState } from 'react'
import UploadForm from '../components/UploadForm'
import MeetingList from '../components/MeetingList'
import SummaryCard from '../components/SummaryCard'
import SegmentsTable from '../components/SegmentsTable'
import SentimentChart from '../components/SentimentChart'
import SearchBox from '../components/SearchBox'
import KnowledgeGraph from '../components/KnowledgeGraph'
import { listMeetings, getSummary } from '../api/api'

export default function App() {
  const [meetings, setMeetings] = useState([])
  const [selected, setSelected] = useState(null)
  const [summary, setSummary] = useState(null)

  const refresh = async () => {
    const ms = await listMeetings()
    setMeetings(ms)
    if (!selected && ms.length) setSelected(ms[0])
  }

  const fetchSummary = async (meetingId) => {
    if (!meetingId) {
      setSummary(null)
      return
    }
    try {
      const summaryData = await getSummary(meetingId)
      setSummary(summaryData)
    } catch (error) {
      console.error('Error fetching summary:', error)
      setSummary(null)
    }
  }

  useEffect(() => { refresh() }, [])

  useEffect(() => {
    if (selected) {
      fetchSummary(selected.id)
    } else {
      setSummary(null)
    }
  }, [selected])

  return (
    <div className="max-w-7xl mx-auto p-4 space-y-4">
      <h1 className="text-2xl font-bold">Post-Meeting Analysis</h1>
      <UploadForm onUploaded={() => { refresh(); if (selected) fetchSummary(selected.id); }} />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-1 space-y-4">
          <MeetingList items={meetings} onSelect={setSelected} />
          <SearchBox />
        </div>
        <div className="md:col-span-2 space-y-4">
          <SummaryCard summary={summary} />
          {selected && <SentimentChart meetingId={selected.id} />}
          {selected && <KnowledgeGraph meetingId={selected.id} />}
          {selected && <SegmentsTable meetingId={selected.id} />}
        </div>
      </div>
    </div>
  )
}
