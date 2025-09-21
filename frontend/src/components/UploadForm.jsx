import React, { useState } from 'react'
import { uploadFile, processMeeting } from '../api/api'

export default function UploadForm({ onUploaded }) {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState('')

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    setStatus('Uploading...')
    try {
      const up = await uploadFile(file)
      setStatus('Processing...')
      await processMeeting(up.meeting_id)
      setStatus('Processing started — refresh in a few seconds.')
      onUploaded && onUploaded(up)
    } catch (e) {
      console.error(e)
      setStatus('Error: ' + e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-4 rounded-2xl bg-white shadow">
      <h2 className="text-lg font-semibold mb-2">Upload meeting audio/video</h2>
      <input type="file" onChange={(e)=>setFile(e.target.files?.[0])} className="mb-2" />
      <div className="flex gap-2">
        <button onClick={handleUpload} disabled={loading || !file} className="px-3 py-1 rounded-xl bg-blue-600 text-white">
          {loading ? 'Please wait...' : 'Upload & Process'}
        </button>
        <span className="text-sm text-gray-600">{status}</span>
      </div>
    </div>
  )
}
