import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axiosInstance from "../utlils/axiosInstance";
import { toast } from "react-toastify";
import Header from "./Header"

const Profile = () => {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user"));
  const jwt_access = localStorage.getItem("access");

  useEffect(() => {
    if (jwt_access === null && !user) {
      navigate("/login");
    } else {
      getSomeData();
    }
  }, [jwt_access, user]);



  const getSomeData = async () => {
    const resp = await axiosInstance.get("/auth/profile/");
    if (resp.status === 200) {
      console.log(resp.data);
    }
  }

  const refresh = JSON.parse(localStorage.getItem("refresh"));

  const handlelogout = async () => {
    const res = await axiosInstance.post("/auth/logout/", {
      refresh_token: refresh,
    });
    if (res.status === 200) {
      localStorage.removeItem("user");
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
      navigate("/login");
      toast.success("logout successful")
    }
  }

  return (
    <div>
      <Header></Header>
      <h2>hi {user?.names}</h2>
      <p style={{ textAlign: "center" }}>welcome to your profile</p>
      <button onClick={handlelogout} className="logout-btn">
        Logout
      </button>
    </div>
  );
};

export default Profile;
