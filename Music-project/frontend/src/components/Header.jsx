import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { VscAccount, VscHistory, VscSignOut } from "react-icons/vsc"; // Import icons

const HeaderStyled = () => {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user'));
  const [dropdownOpen, setDropdownOpen] = useState(false); // State for Dropdown

  const handleLogout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    toast.success("Logged out successfully");
    navigate("/login"); // Redirect to login after logout
  };

  const toggleDropdown = () => {
    setDropdownOpen(!dropdownOpen); // Toggle dropdown visibility
  };

  return (
    <nav style={styles.nav}>
      <div style={styles.leftSection}>
        {/* Link the logo to the home page */}
        <Link to="/">
          <img src="/src/img/logo.png" alt="Logo" style={styles.logo} /> {/* Adjusted image path */}
        </Link>
        <h1 style={styles.brandName}>Noteverse</h1>
      </div>
      <div style={styles.centerSection}>
        <a href="/FileUploadCrop" style={styles.link}>
          แปลงโน้ตไทย เป็น โน้ตสากล
        </a>
        <span style={styles.separator}> | </span>
        <a href="/international-to-thai" style={styles.link}>
          แปลงโน้ตสากล เป็น โน้ตไทย
        </a>
      </div>
      <div style={styles.rightSection}>
        {user ? (
          <div style={styles.profileMenu} onClick={toggleDropdown}>
            <VscAccount size={24} style={{ marginRight: '8px' }} />
            <span>{user.names}</span>
            {dropdownOpen && (
              <div style={styles.dropdown}>
                <Link to="/dashboard" style={styles.dropdownItem}>
                  <VscAccount style={styles.icon} /> Profile
                </Link>
                <Link to="/music-history" style={styles.dropdownItem}>
                  <VscHistory style={styles.icon} /> History
                </Link>
                <button onClick={handleLogout} style={styles.dropdownItem}>
                  <VscSignOut style={styles.icon} /> Logout
                </button>
              </div>
            )}
          </div>
        ) : (
          <Link to="/signup" style={styles.link}>
            Sign Up
          </Link>
        )}
      </div>
    </nav>
  );
};

const styles = {
  nav: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '10px 40px',
    backgroundColor: '#1E2A47',
    color: '#FFFFFF',
    height: '70px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
  },
  leftSection: {
    display: 'flex',
    alignItems: 'center',
  },
  logo: {
    height: '125px',  // Ensure the image fits within the header height
    maxWidth: 'auto',
    marginRight: '15px',
    objectFit: 'contain', // Maintain aspect ratio
  },
  brandName: {
    fontSize: '24px',
    fontWeight: 'bold',
    letterSpacing: '1px',
  },
  centerSection: {
    flex: 1,
    textAlign: 'center',
  },
  link: {
    fontSize: '16px',
    color: '#d1d5db',
    textDecoration: 'none',
    margin: '0 10px',
    transition: 'color 0.3s',
  },
  separator: {
    fontSize: '16px',
    color: '#FFFFFF',
  },
  rightSection: {
    display: 'flex',
    alignItems: 'center',
  },
  profileMenu: {
    position: 'relative',
    cursor: 'pointer',
    color: '#d1d5db',
    display: 'flex',
    alignItems: 'center',
  },
  dropdown: {
    position: 'absolute',
    top: '100%',
    right: 0,
    backgroundColor: '#1E2A47',
    border: '1px solid #d1d5db',
    borderRadius: '8px',
    marginTop: '10px',
    minWidth: '180px',
    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
    zIndex: 1,
  },
  dropdownItem: {
    display: 'flex',
    alignItems: 'center',
    padding: '10px',
    color: '#d1d5db',
    textDecoration: 'none',
    cursor: 'pointer',
    backgroundColor: 'transparent',
    border: 'none',
    width: '100%',
    transition: 'background-color 0.3s, color 0.3s',
  },
  icon: {
    marginRight: '10px',
    fontSize: '18px',
  },
};

export default HeaderStyled;
