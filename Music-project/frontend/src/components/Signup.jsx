import React, { useState } from "react";
import axios from "axios";
import { useNavigate ,Link} from "react-router-dom";
import { toast } from "react-toastify";
import Stars from "./star";

const Signup = () => {
  const navigate = useNavigate();
  const [formdata, setFormData] = useState({
    email: "",
    first_name: "",
    last_name: "",
    password: "",
    password2: "",
  });

  const [passwordConditions, setPasswordConditions] = useState({
    length: false,
    uppercase: false,
    lowercase: false,
    number: false,
    specialChar: false,
  });

  const [showTooltip, setShowTooltip] = useState(false); // Tooltip visibility
  const [error, setError] = useState("");

  const handleOnChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formdata, [name]: value });

    if (name === "password") validatePassword(value); // Validate password as user types
  };

  const validatePassword = (password) => {
    const conditions = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /[0-9]/.test(password),
      specialChar: /[!@#$%^&*(),.?":{}|<>]/.test(password),
    };
    setPasswordConditions(conditions);
  };

  const { email, first_name, last_name, password, password2 } = formdata;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !first_name || !last_name || !password || !password2) {
      setError("All fields are required");
    } else {
      try {
        const res = await axios.post(
          "http://localhost:8000/api/v1/auth/register/",
          formdata
        );
        const response = res.data;

        if (res.status === 201) {
          navigate("/otp/verify");
          toast.success(response.message);
        }
      } catch (error) {
        setError("Server error. Please try again.");
      }
    }
  };

  return (
    <div style={styles.container}>
      <Stars />
      <div style={styles.formWrapper}>
        <h2 style={styles.title}>Create Account</h2>
        <form onSubmit={handleSubmit} style={styles.form}>
          {error && <p style={styles.errorText}>{error}</p>}
          <div style={styles.formGroup}>
            <label htmlFor="email" style={styles.label}>
              Email Address:
            </label>
            <input
              type="text"
              className="email-form"
              name="email"
              value={email}
              onChange={handleOnChange}
              style={styles.input}
            />
          </div>
          <div style={styles.formGroup}>
            <label htmlFor="first_name" style={styles.label}>
              First Name:
            </label>
            <input
              type="text"
              className="email-form"
              name="first_name"
              value={first_name}
              onChange={handleOnChange}
              style={styles.input}
            />
          </div>
          <div style={styles.formGroup}>
            <label htmlFor="last_name" style={styles.label}>
              Last Name:
            </label>
            <input
              type="text"
              className="email-form"
              name="last_name"
              value={last_name}
              onChange={handleOnChange}
              style={styles.input}
            />
          </div>
          <div style={styles.formGroup}>
            <label htmlFor="password" style={styles.label}>
              Password:
            </label>
            <input
              type="password"
              className="email-form"
              name="password"
              value={password}
              onChange={handleOnChange}
              style={styles.input}
              onFocus={() => setShowTooltip(true)} // Show tooltip on focus
              onBlur={() => setShowTooltip(false)} // Hide tooltip on blur
            />
            {showTooltip && (
              <div style={styles.tooltip}>
                <p>Password must:</p>
                <ul>
                  <li style={passwordConditions.length ? styles.valid : styles.invalid}>
                    Be at least 8 characters long
                  </li>
                  <li style={passwordConditions.uppercase ? styles.valid : styles.invalid}>
                    Contain at least one uppercase letter
                  </li>
                  <li style={passwordConditions.lowercase ? styles.valid : styles.invalid}>
                    Contain at least one lowercase letter
                  </li>
                  <li style={passwordConditions.number ? styles.valid : styles.invalid}>
                    Contain at least one number
                  </li>
                  <li style={passwordConditions.specialChar ? styles.valid : styles.invalid}>
                    Contain at least one special character (e.g., @, #, $)
                  </li>
                </ul>
              </div>
            )}
          </div>
          <div style={styles.formGroup}>
            <label htmlFor="password2" style={styles.label}>
              Confirm Password:
            </label>
            <input
              type="password"
              className="email-form"
              name="password2"
              value={password2}
              onChange={handleOnChange}
              style={styles.input}
            />
          </div>
          <Link to="/login" style={styles.link}>
              Already Have Account ?
            </Link>
          <input
            type="submit"
            value="Submit"
            className="submitButton"
            style={styles.submitButton}
          />
        </form>
      </div>
    </div>
  );
};

const styles = {
  container: {
    height: "90vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(255, 255, 255, 0.5)",
    borderRadius: '8px',
  },
  formWrapper: {
    width: "700px",
    padding: "30px",
    borderRadius: "8px",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
    backgroundColor: "#fff",
    position: "relative",
  },
  title: {
    textAlign: "center",
    marginBottom: "20px",
    fontSize: "24px",
    color: "#333",
  },
  form: {
    display: "flex",
    flexDirection: "column",
  },
  formGroup: {
    marginBottom: "15px",
    position: "relative",
  },
  label: {
    marginBottom: "8px",
    fontSize: "16px",
    color: "#555",
    display: "block",
  },
  input: {
    width: "100%",
    padding: "10px",
    borderRadius: "4px",
    border: "1px solid #ddd",
    fontSize: "16px",
  },
  tooltip: {
    position: "absolute",
    right: "-300px",
    top: "0",
    width: "240px",
    backgroundColor: "#fff",
    border: "1px solid #ddd",
    borderRadius: "8px",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
    padding: "10px",
    zIndex: 1,
    fontSize: "14px",
  },
  valid: {
    color: "green",
  },
  invalid: {
    color: "red",
  },
  submitButton: {
    padding: "10px 20px",
    backgroundColor: "#1E2A47",
    color: "#fff",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "16px",
    transition: "background-color 0.3s",
  },
  errorText: {
    color: "red",
    marginBottom: "10px",
    textAlign: "center",
  },
};

export default Signup;
