import { useState } from "react";
import { ToastContainer} from 'react-toastify';
import "react-toastify/dist/ReactToastify.css";
import reactLogo from "./assets/react.svg";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import viteLogo from "/vite.svg";
import {Signup, Login, Profile, VerifyEmail, ForgetPassword,FileUploadCrop,MusicHistory,NationaltoThai,MusicHistory2} from "./components";
import "./App.css";
import { ResetPassword } from "./components/ResetPassword";
import Home from "./components/Home";
function App() {

  return (
    <>
      <Router>
      <ToastContainer/>
        <Routes>
          <Route path='/' element={<Home />} />
          <Route path='/signup' element={<Signup />} />
          <Route path='/login' element={<Login />} />
          <Route path='/dashboard' element={<Profile />} />
          <Route path='/otp/verify' element={<VerifyEmail />} />
          <Route path='/forget_password' element={<ForgetPassword />} />
          <Route path="/password-reset" element={<ResetPassword />} />
          <Route path='/password-reset-confirm/:uid/:token' element={<ResetPassword />}/>
          <Route path='/FileUploadCrop' element={<FileUploadCrop />}/>
          <Route path="/music-history" element={<MusicHistory />} />
          <Route path='/international-to-thai' element={<NationaltoThai />} />
          <Route path="/music-history2" element={<MusicHistory2 />} />
        </Routes>
      </Router>
    </>
  );
}

export default App;
