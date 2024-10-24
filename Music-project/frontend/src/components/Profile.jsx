import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axiosInstance from "../utlils/axiosInstance";
import { toast } from "react-toastify";
import Header from "./Header";

const Profile = () => {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user"));
  const jwt_access = localStorage.getItem("access");

  const [firstName, setFirstName] = useState(user?.first_name || "");
  const [lastName, setLastName] = useState(user?.last_name || "");
  const [password, setPassword] = useState("");
  const [oldPassword, setOldPassword] = useState("");

  // Refresh page only once after login
  useEffect(() => {
    if (!sessionStorage.getItem("profile_refreshed")) {
      sessionStorage.setItem("profile_refreshed", "true");
      window.location.reload(); // Reload the page only once
    }
  }, []);

  useEffect(() => {
    if (!jwt_access || !user) {
      navigate("/login");
    } else {
      getSomeData();
    }
  }, [jwt_access, user]);

  const getSomeData = async () => {
    try {
      const resp = await axiosInstance.get("/auth/profile/");
      if (resp.status === 200) {
        console.log(resp.data);
      }
    } catch (error) {
      console.error("Error fetching profile data:", error);
    }
  };

  const handleUpdateName = async () => {
    try {
      const response = await axiosInstance.post("/auth/profile/", {
        first_name: firstName,
        last_name: lastName,
      });
      if (response.status === 200) {
        toast.success("Name updated successfully!");
        localStorage.setItem("user", JSON.stringify({ 
          ...user, 
          first_name: firstName, 
          last_name: lastName 
        }));
      }
    } catch (error) {
      toast.error("Failed to update name!");
      console.error(error);
    }
  };

  const handleChangePassword = async () => {
    try {
      const response = await axiosInstance.post("/auth/change-password/", {
        old_password: oldPassword,
        new_password: password,
      });
      if (response.status === 200) {
        toast.success("Password changed successfully!");
        setPassword("");
        setOldPassword("");
      }
    } catch (error) {
      toast.error("Failed to change password!");
      console.error(error);
    }
  };

  const refresh = JSON.parse(localStorage.getItem("refresh"));

  const handleLogout = async () => {
    try {
      const res = await axiosInstance.post("/auth/logout/", {
        refresh_token: refresh,
      });
      if (res.status === 200) {
        localStorage.removeItem("user");
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        navigate("/login");
        toast.success("Logout successful!");
      }
    } catch (error) {
      toast.error("Logout failed!");
      console.error(error);
    }
  };

  return (
    <div>
      <Header />
      <div style={styles.container}>
        <h2>Hi, {user?.first_name} {user?.last_name}</h2>
        <p style={{ textAlign: "center" }}>Welcome to your profile</p>

        {/* Form for updating name */}
        <div style={styles.formGroup}>
          <label htmlFor="first_name">Change First Name:</label>
          <input
            type="text"
            id="first_name"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            style={styles.input}
          />
          <label htmlFor="last_name">Change Last Name:</label>
          <input
            type="text"
            id="last_name"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            style={styles.input}
          />
          <button onClick={handleUpdateName} style={styles.button}>
            Update Name
          </button>
        </div>

        {/* Form for changing password */}
        <div style={styles.formGroup}>
          <label htmlFor="old_password">Current Password:</label>
          <input
            type="password"
            id="old_password"
            value={oldPassword}
            onChange={(e) => setOldPassword(e.target.value)}
            style={styles.input}
          />
          <label htmlFor="password">New Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={styles.input}
          />
          <button onClick={handleChangePassword} style={styles.button}>
            Change Password
          </button>
        </div>

        <button onClick={handleLogout} style={styles.logoutButton}>
          Logout
        </button>
      </div>
    </div>
  );
};

const styles = {
  container: {
    maxWidth: "600px",
    margin: "0 auto",
    padding: "20px",
    textAlign: "center",
  },
  formGroup: {
    marginBottom: "20px",
  },
  input: {
    width: "100%",
    padding: "10px",
    marginBottom: "10px",
    borderRadius: "4px",
    border: "1px solid #ccc",
  },
  button: {
    padding: "10px 20px",
    backgroundColor: "#1E2A47",
    color: "#fff",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
  },
  logoutButton: {
    marginTop: "20px",
    padding: "10px 20px",
    backgroundColor: "#d9534f",
    color: "#fff",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
  },
};

export default Profile;
