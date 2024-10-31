import React, { useEffect, useState } from 'react';
import axiosInstance from '../utlils/axiosInstance';

function MusicHistory2() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await axiosInstance.get('/history/');
        setHistory(response.data);
      } catch (error) {
        console.error('Error fetching history:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  if (loading) return <p>Loading history...</p>;

  return (
    <div>
      <h1>History</h1>
      {history.length > 0 ? (
        <ul>
          {history.map((sheet) => (
            <li key={sheet.id}>
              <h2>{sheet.title_text}</h2>
              <p>Key: {sheet.key}</p>
              <p>Tempo: {sheet.tempo}</p>
              <p>Clef Type: {sheet.clef_type}</p>
              <p>Clef Music: {sheet.clef_music}</p>
              <p>Created At: {new Date(sheet.created_at).toLocaleString()}</p>
              <a href={sheet.pdf_path} target="_blank" rel="noopener noreferrer">View PDF</a>
              <br />
              <a href={sheet.image_path} target="_blank" rel="noopener noreferrer">View Image</a>
            </li>
          ))}
        </ul>
      ) : (
        <p>No history available.</p>
      )}
    </div>
  );
}

export default MusicHistory2;
