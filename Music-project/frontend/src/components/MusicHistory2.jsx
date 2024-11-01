import React, { useEffect, useState } from 'react';
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import axiosInstance from "../utlils/axiosInstance"; // Adjust path if necessary
import HeaderStyled from './Header'; // Import Header component

const MusicHistory2 = () => {
  const [hoveredRow, setHoveredRow] = React.useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await axiosInstance.get('/history/');
        setHistory(response.data);
      } catch (error) {
        console.error('Error fetching history:', error);
        toast.error("Please login again!");
        navigate("/login"); // Redirect to login if there's an error
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  const downloadFile = async (filePath, fileName) => {
    try {
      const response = await axiosInstance.get(filePath, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (error) {
      console.error('Error downloading the file:', error);
    }
  };

  const navigateToNationToThai = () => {
    navigate('/music-history'); // Update with the correct route path
  };

  if (loading) return <p>Loading history...</p>;

  return (
    <div>
      <HeaderStyled />
      <div style={styles.container}>
        <h1 style={styles.title}>Your Music History of Converting Thai to National</h1>
        <div style={styles.buttonContainer}>
          <button
            style={styles.navigateButton}
            onClick={navigateToNationToThai}
          >
            Go to Nation to Thai History
          </button>
        </div>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Title</th>
              <th style={styles.th}>Key</th>
              <th style={styles.th}>Tempo</th>
              <th style={styles.th}>Clef Type</th>
              <th style={styles.th}>PDF</th>
              <th style={styles.th}>Image</th>
              <th style={styles.th}>Uploaded At</th>
            </tr>
          </thead>
          <tbody>
            {history.map((sheet, index) => (
              <tr
                key={sheet.id}
                style={
                  hoveredRow === index
                    ? { ...styles.tr, ...styles.trHover }
                    : styles.tr
                }
                onMouseEnter={() => setHoveredRow(index)}
                onMouseLeave={() => setHoveredRow(null)}
              >
                <td style={styles.td}>{sheet.title_text}</td>
                <td style={styles.td}>{sheet.key}</td>
                <td style={styles.td}>{sheet.tempo}</td>
                <td style={styles.td}>{sheet.clef_type}</td>
                <td style={styles.td}>
                  <button
                    style={styles.button}
                    onMouseOver={(e) => e.target.style.backgroundColor = styles.buttonHover.backgroundColor}
                    onMouseOut={(e) => e.target.style.backgroundColor = styles.button.backgroundColor}
                    onClick={() => downloadFile(sheet.pdf_path, `${sheet.title_text}_score.pdf`)}
                  >
                    Download PDF
                  </button>
                </td>
                <td style={styles.td}>
                  <button
                    style={styles.button}
                    onMouseOver={(e) => e.target.style.backgroundColor = styles.buttonHover.backgroundColor}
                    onMouseOut={(e) => e.target.style.backgroundColor = styles.button.backgroundColor}
                    onClick={() => downloadFile(sheet.image_path, `${sheet.title_text}_image.png`)}
                  >
                    Download Image
                  </button>
                </td>
                <td style={styles.td}>
                  {new Date(sheet.created_at).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default MusicHistory2;

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
  buttonContainer: {
    display: 'flex',
    justifyContent: 'flex-end',
    marginBottom: '20px',
  },
  navigateButton: {
    padding: '15px 15px',
    backgroundColor: '#1E2A47',
    color: '#fff',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
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
