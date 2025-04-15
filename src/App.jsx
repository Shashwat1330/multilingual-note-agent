import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState('');
  const [transcript, setTranscript] = useState('');
  const [meetingId, setMeetingId] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  const handleUpload = async () => {
    if (!file) return alert("Please upload a file");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://127.0.0.1:8000/process_meeting", formData);
      setSummary(res.data.summary);
      setTranscript(res.data.transcript);
      setMeetingId(res.data.meeting_id);
    } catch (err) {
      alert("Error processing meeting");
    }
  };

  const handleSearch = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:8000/search", {
        query: searchQuery
      });
      setSearchResults(res.data.results);
    } catch (err) {
      alert("No results found");
    }
  };

  const downloadPDF = async () => {
    if (!meetingId) return alert("Upload first");

    try {
      const response = await axios.get(`http://127.0.0.1:8000/export/${meetingId}`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `meeting_${meetingId}_summary.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Error downloading PDF:", error);
      alert("Failed to download PDF.");
    }
  };

  return (
    <div style={{ padding: 20, fontFamily: 'sans-serif' }}>
      <h1>Multilingual Meeting Notes</h1>

      <input type="file" accept="audio/*" onChange={e => setFile(e.target.files[0])} />
      <button onClick={handleUpload}>Upload & Summarize</button>

      {summary && (
        <>
          <h2>Summary</h2>
          <p>{summary}</p>
          <h3>Transcript</h3>
          <p>{transcript}</p>
          <button onClick={downloadPDF}>Download PDF</button>
        </>
      )}

      <hr />

      <h2>Search Meetings</h2>
      <input
        type="text"
        value={searchQuery}
        onChange={e => setSearchQuery(e.target.value)}
        placeholder="Enter keyword"
      />
      <button onClick={handleSearch}>Search</button>

      {searchResults.length > 0 && (
        <ul>
          {searchResults.map((r, idx) => (
            <li key={idx}>
              <strong>ID {r.id}</strong>: {r.summary.slice(0, 100)}...
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;
