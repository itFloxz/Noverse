import React from 'react';



const HeaderStyled = (
  {open}
) => {
  return (
    <nav style={styles.nav}>
      <div style={styles.leftSection}>
        <img src="#" alt="Logo" style={styles.logo} />
        <h1 style={styles.brandName}>Noteverse</h1>
      </div>
      <div style={styles.centerSection}>
        <a href="/" style={styles.link}>
          แปลงโน้ตไทย เป็น โน้ตสากล
        </a>
        <span style={styles.separator}> | </span>
        <a href="/international-to-thai" style={styles.link}>
          แปลงโน้ตสากล เป็น โน้ตไทย
        </a>
      </div>
      <div style={styles.rightSection}>
        {/* <div style={styles.profileCircle}></div> */}
        {/* <span style={styles.username}>Login</span> */}
        {open==true&&(<a href="/login" style={styles.link}>Login</a>)}
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
    width: '50px',
    height: '50px',
    marginRight: '15px',
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
    textDecoration: 'none', // ไม่ให้มีเส้นใต้ลิงก์
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
  profileCircle: {
    width: '45px',
    height: '45px',
    borderRadius: '50%',
    backgroundColor: '#C4C4C4',
    marginRight: '10px',
    border: '2px solid #FFFFFF',
  },
  username: {
    fontSize: '16px',
    fontWeight: '500',
  },
};

export default HeaderStyled;
