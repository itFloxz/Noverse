import React, { useState } from 'react';
import { toast } from 'react-toastify';
import axiosInstance from '../utlils/axiosInstance';
import Stars from './star';

const PasswordResetRequest = () => {
  const [email, setEmail] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (email) {
      try {
        const res = await axiosInstance.post('auth/password-reset/', { email });
        if (res.status === 200) {
          console.log(res.data);
          toast.success('A link to reset your password has been sent to your email.');
        }
      } catch (error) {
        toast.error('Something went wrong. Please try again.');
      }
      setEmail('');
    }
  };

  return (
    <div style={styles.container}>
      <Stars />
      <div style={styles.formWrapper}>
        <h2 style={styles.title}>Enter your registered email</h2>
        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.formGroup}>
            <label htmlFor="email" style={styles.label}>Email Address:</label>
            <input
              type="email"
              id="email"
              name="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={styles.input}
              required
            />
          </div>
          <button type="submit" style={styles.button}>Send</button>
        </form>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '55vh',
    width: '100vh',
    backgroundColor: "rgba(255, 255, 255, 0.5)",
    borderRadius: '8px',
  },
  formWrapper: {
    zIndex: 1,
    width: '700px',
    padding: '30px',
    borderRadius: '8px',
    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.5)',
    backgroundColor: '#ffffff',
    textAlign: 'center',
  },
  title: {
    marginBottom: '20px',
    fontSize: '24px',
    color: '#333',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
  },
  formGroup: {
    marginBottom: '15px',
    textAlign: 'left',
  },
  label: {
    marginBottom: '8px',
    fontSize: '16px',
    color: '#555',
    display: 'block',
  },
  input: {
    width: '100%',
    padding: '10px',
    borderRadius: '4px',
    border: '1px solid #ddd',
    fontSize: '16px',
    marginTop: '5px',
    boxSizing: 'border-box',
  },
  button: {
    marginTop: '15px',
    padding: '10px 20px',
    backgroundColor: '#1E2A47',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    cursor: 'pointer',
    transition: 'background-color 0.3s',
  },
};

export default PasswordResetRequest;
