import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const uploadFile = async (file) => {
  const form = new FormData()
  form.append('file', file)
  const res = await axios.post(`${API_URL}/upload`, form, { headers: { 'Content-Type': 'multipart/form-data' } })
  return res.data
}

export const processMeeting = async (meetingId) => {
  const res = await axios.post(`${API_URL}/meetings/${meetingId}/process`, { force: true })
  return res.data
}

export const listMeetings = async () => {
  const res = await axios.get(`${API_URL}/meetings`)
  return res.data
}

export const getSegments = async (id) => {
  const res = await axios.get(`${API_URL}/meetings/${id}/segments`)
  return res.data
}

export const getSummary = async (id) => {
  const res = await axios.get(`${API_URL}/meetings/${id}/summary`)
  return res.data
}

export const searchSegments = async (q) => {
  const res = await axios.get(`${API_URL}/search`, { params: { q } })
  return res.data
}

export const getGraph = async (id) => {
  const res = await axios.get(`${API_URL}/meetings/${id}/graph`)
  return res.data
}
