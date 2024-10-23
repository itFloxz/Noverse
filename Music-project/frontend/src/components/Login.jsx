import axios from "axios";
import React, { useState, useEffect } from "react";
import { toast } from "react-toastify";
import { useNavigate, Link } from "react-router-dom";
import Stars from "./star"; // Assuming you have a component for Stars
import { MdOpacity } from "react-icons/md";

const Login = () => {
  const navigate = useNavigate();
  const [logindata, setLoginData] = useState({
    email: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access");
    if (token) {
      navigate("/dashboard");
      toast.success("You are already logged in");
    }
  }, [navigate]);

  const handleOnChange = (e) => {
    setLoginData({ ...logindata, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const { email, password } = logindata;

    if (!email || !password) {
      setError("Email and password are required");
      return;
    } else {
      setIsLoading(true);
      try {
        const res = await axios.post(
          "http://localhost:8000/api/v1/auth/login/",
          logindata
        );
        const response = res.data;

        const user = {
          email: response.email,
          names: response.full_name,
        };

        localStorage.setItem("user", JSON.stringify(user));
        localStorage.setItem("access", JSON.stringify(response.access_token));
        localStorage.setItem("refresh", JSON.stringify(response.refresh_token));
        navigate("/dashboard");
        toast.success("Login successful");
      } catch (error) {
        toast.error("Login failed. Please try again.");
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div style={styles.wrapper}>
      <Stars /> {/* Stars component is positioned in the background */}
      <div style={styles.formContainer}>
        <form onSubmit={handleSubmit} style={styles.form}>
          <h2 style={styles.title}>Login</h2>
          {isLoading && <p style={styles.loadingText}>Loading...</p>}
          <div style={styles.formGroup}>
            <label htmlFor="email" style={styles.label}>
              Email Address:
            </label>
            <input
              type="text"
              className="email-form"
              name="email"
              value={logindata.email}
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
              value={logindata.password}
              onChange={handleOnChange}
              style={styles.input}
            />
          </div>
          <input type="submit" value="Login" style={styles.submitButton} />
          <p>
            Don't have an account?{" "}
            <Link to="/signup" style={styles.link}>
              Register
            </Link>
          </p>
          <p className="pass-link">
            <Link to="/forget_password" style={styles.link}>
              Forgot password?
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
};

const styles = {
  wrapper: {
    position: "relative", // Contains the positioned child elements
    height: "100vh",
    overflow: "hidden",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  formContainer: {
    zIndex: 1, // Ensure the form is above the Stars background
    width: "700px",
    padding: "30px",
    borderRadius: "8px",
    backgroundColor: "rgba(255, 255, 255, 0.5)", // Slight transparency
    backdropFilter: "blur(10px)", // Optional: adds a blur effect behind the form
    position: "relative",
  },
  form: {
    display: "flex",
    flexDirection: "column",
  },
  title: {
    textAlign: "center",
    marginBottom: "20px",
    fontSize: "24px",
    color: "#333",
  },
  formGroup: {
    marginBottom: "15px",
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
    marginBottom: "10px",
    borderRadius: "4px",
    border: "1px solid #ddd",
    fontSize: "16px",
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
  link: {
    color: "#1E2A47",
    textDecoration: "none",
    marginTop: "10px",
  },
  loadingText: {
    textAlign: "center",
    marginBottom: "10px",
    color: "#666",
  },
};

export default Login;
