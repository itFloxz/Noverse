import React, { useEffect, useState } from 'react';
import axiosInstance from "../utlils/axiosInstance"; // Adjust the path if necessary

const MusicHistory = () => {
  const [musicHistory, setMusicHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMusicHistory = async () => {
      try {
        const response = await axiosInstance.get('/music-history/');
        setMusicHistory(response.data);
      } catch (error) {
        console.error('Error fetching music history:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMusicHistory();
  }, []);

  const downloadFile = async (filePath, fileName) => {
    try {
      const response = await axiosInstance.get(filePath, {
        responseType: 'blob', // Important: to get the file as binary data (Blob)
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName); // Specify the file name
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link); // Clean up
    } catch (error) {
      console.error('Error downloading the file:', error);
    }
  };

  if (loading) {
    return <p>Loading...</p>;
  }

  return (
    <div>
      <h1>Your Music History</h1>
      <table border="1" cellPadding="10" cellSpacing="0" style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th>File Name</th>
            <th>PDF</th>
            <th>PNG</th>
            <th>Uploaded At</th>
          </tr>
        </thead>
        <tbody>
          {musicHistory.map((file) => (
            <tr key={file.id}>
              <td>{file.original_file_name}</td>
              <td>
                <button
                  onClick={() => downloadFile(file.pdf_file_path, `MusicScore.pdf`)}
                >
                  Download PDF
                </button>
              </td>
              <td>
                <button
                  onClick={() => downloadFile(file.png_file_path, `MusicScore.png`)}
                >
                  Download PNG
                </button>
              </td>
              <td>{new Date(file.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default MusicHistory;
