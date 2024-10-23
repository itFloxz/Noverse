import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axiosInstance from "../utlils/axiosInstance";
import { toast } from "react-toastify";
import Header from "./Header";
import Stars from "./star";


const Profile = () => {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user"));
  const jwt_access = localStorage.getItem("access");

  const [name, setName] = useState(user?.names || ""); // State สำหรับชื่อ
  const [password, setPassword] = useState(""); // State สำหรับรหัสผ่านใหม่

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
      const response = await axiosInstance.put("/auth/profile/", { names: name });
      if (response.status === 200) {
        toast.success("Name updated successfully!");
        localStorage.setItem("user", JSON.stringify({ ...user, names: name }));
      }
    } catch (error) {
      toast.error("Failed to update name!");
      console.error(error);
    }
  };

  const handleChangePassword = async () => {
    try {
      const response = await axiosInstance.post("/auth/change-password/", {
        password,
      });
      if (response.status === 200) {
        toast.success("Password changed successfully!");
        setPassword(""); // ล้างฟิลด์รหัสผ่านหลังจากเปลี่ยนเสร็จ
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
        <h2>Hi, {user?.names}</h2>
        <p style={{ textAlign: "center" }}>Welcome to your profile</p>

        {/* Form for updating name */}
        <div style={styles.formGroup}>
          <label htmlFor="name">Change Name:</label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            style={styles.input}
          />
          <button onClick={handleUpdateName} style={styles.button}>
            Update Name
          </button>
        </div>

        {/* Form for changing password */}
        <div style={styles.formGroup}>
          <label htmlFor="password">Change Password:</label>
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
