import React, { useEffect, useState } from 'react';
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import axiosInstance from "../utlils/axiosInstance"; // Adjust path if necessary
import HeaderStyled from './Header'; // Import Header component


const MusicHistory = () => {
  const [hoveredRow, setHoveredRow] = React.useState(null);
  const [musicHistory, setMusicHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchMusicHistory = async () => {
      try {
        const response = await axiosInstance.get('/music-history/');
        setMusicHistory(response.data);
      } catch (error) {
        console.error('Error fetching music history:', error);
        toast.error("Please login again!");
        navigate("/login"); // Redirect to login if there's an error
      } finally {
        setLoading(false);
      }
    };

    fetchMusicHistory();
  }, []);

  const downloadFile = async (filePath, fileName) => {
    try {
      const response = await axiosInstance.get(filePath, {
        responseType: 'blob', // Important to get the file as binary data (Blob)
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
    <HeaderStyled/>
    <div style={styles.container}>
      <h1 style={styles.title}>Your Music History</h1>
      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.th}>File Name</th>
            <th style={styles.th}>PDF</th>
            <th style={styles.th}>PNG</th>
            <th style={styles.th}>Uploaded At</th>
          </tr>
        </thead>
        <tbody>
          {musicHistory.map((file, index) => (
            <tr
              key={file.id}
              style={
                hoveredRow === index
                  ? { ...styles.tr, ...styles.trHover }
                  : styles.tr
              }
              onMouseEnter={() => setHoveredRow(index)}
              onMouseLeave={() => setHoveredRow(null)}
            >
              <td style={styles.td}>{file.original_file_name}</td>
              <td style={styles.td}>
                <button
                  style={styles.button}
                  onMouseOver={(e) =>
                    (e.target.style.backgroundColor = styles.buttonHover.backgroundColor)
                  }
                  onMouseOut={(e) =>
                    (e.target.style.backgroundColor = styles.button.backgroundColor)
                  }
                  onClick={() =>
                    downloadFile(file.pdf_file_path, `${file.original_file_name}_score.pdf`)
                  }
                >
                  Download PDF
                </button>
              </td>
              <td style={styles.td}>
                <button
                  style={styles.button}
                  onMouseOver={(e) =>
                    (e.target.style.backgroundColor = styles.buttonHover.backgroundColor)
                  }
                  onMouseOut={(e) =>
                    (e.target.style.backgroundColor = styles.button.backgroundColor)
                  }
                  onClick={() =>
                    downloadFile(file.png_file_path, `${file.original_file_name}_score.zip`)
                  }
                >
                  Download PNG
                </button>
              </td>
              <td style={styles.td}>
                {new Date(file.created_at).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    </div>
  );
};

export default MusicHistory;



const styles = {
  container: {
    padding: '20px',
    backgroundColor: '#f4f6f8',
    minHeight: '100vh',
    fontFamily: 'Arial, sans-serif',
  },
  title: {
    textAlign: 'center',
    marginTop: '20px',
    fontSize: '32px',
    color: '#333',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    marginTop: '20px',
    boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
  },
  th: {
    backgroundColor: '#1E2A47',
    color: '#fff',
    padding: '15px',
    textAlign: 'center',
  },
  tr: {
    backgroundColor: '#fff',
    transition: 'background-color 0.3s',
  },
  trHover: {
    backgroundColor: '#f1f1f1',
  },
  td: {
    padding: '15px',
    borderBottom: '1px solid #ddd',
    textAlign: 'center'
  },
  button: {
    padding: '10px 15px',
    backgroundColor: '#4caf50',
    border: 'none',
    borderRadius: '5px',
    color: '#fff',
    cursor: 'pointer',
    transition: 'background-color 0.3s',
  },
  buttonHover: {
    backgroundColor: '#45a049',
  },
};