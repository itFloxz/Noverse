import React from 'react';
import { Link } from 'react-router-dom';
import Header from './Header'; // Assuming you have a Header component

const Home = () => {
  return (
    <div>
      <Header /> {/* Use the Header component if available */}
      <div style={styles.container}>
        <h1>Welcome to Noteverse</h1>
        <p style={styles.description}>A platform where you can convert Thai musical notes to international notation and vice versa!</p>
        
        <div style={styles.buttonContainer}>
          <Link to="/file-upload" style={styles.link}>
            <button style={styles.button}>Convert Thai to International</button>
          </Link>
          <Link to="/international-to-thai" style={styles.link}>
            <button style={styles.button}>Convert International to Thai</button>
          </Link>
          <Link to="/profile" style={styles.link}>
            <button style={styles.button}>Go to Profile</button>
          </Link>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    textAlign: 'center',
    padding: '50px',
  },
  description: {
    fontSize: '18px',
    margin: '20px 0',
  },
  buttonContainer: {
    display: 'flex',
    justifyContent: 'center',
    gap: '20px',
    marginTop: '30px',
  },
  link: {
    textDecoration: 'none',
  },
  button: {
    padding: '15px 30px',
    backgroundColor: '#1E2A47',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '16px',
  },
};

export default Home;
