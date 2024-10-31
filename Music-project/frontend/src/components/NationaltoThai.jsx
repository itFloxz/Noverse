import React, { useState } from 'react';
import axios from 'axios';
import Header from "./Header";
import axiosInstance from '../utlils/axiosInstance';

function NationaltoThai() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [titleText, setTitleText] = useState(null);
  const [key, setKey] = useState(null);
  const [tempo, setTempo] = useState(null);
  const [clefType, setClefType] = useState("classic");
  const [clefMusic, setClefMusic] = useState("G");
  const [pdfBlob, setPdfBlob] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert('Please select a file to upload.');
      return;
  }

  const formData = new FormData();
  formData.append('image', selectedFile);
  formData.append('title_text', titleText || "เพลง บรรเลงใจ");
  formData.append('key', key || "C Major");
  formData.append('tempo', tempo || "120 BPM");
  formData.append('clef_type', clefType || "classic");
  formData.append('clef_music', clefMusic || "G");

  console.log([...formData]); // Log the form data for verification

  setLoading(true);

  try {
      const response = await axiosInstance.post('/process_custom_music_sheet/', formData);

      // ตรวจสอบให้แน่ใจว่า response.data.pdf_base64 มีค่าก่อนใช้งาน
      const pdfBase64 = response.data.pdf_base64;
      if (!pdfBase64) {
          throw new Error("PDF data is missing in the response");
      }

      // แปลง base64 เป็น Blob และสร้าง URL สำหรับไฟล์ PDF
      const byteArray = new Uint8Array(atob(pdfBase64).split("").map(char => char.charCodeAt(0)));
      const blob = new Blob([byteArray], { type: 'application/pdf' });
      setPdfBlob(URL.createObjectURL(blob));
  } catch (error) {
      console.error('Error uploading file:', error);
      alert('เกิดข้อผิดพลาดในการอัปโหลดไฟล์');
  } finally {
      setLoading(false);
  }
  };
  
  

  return (
    <div>
  <Header />
  <h1 style={{ textAlign: "center", fontSize: "2em", margin: "20px 0", color: "#4A4A4A" }}>Convert National to Thai</h1>

  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: '20px', padding: '20px', borderRadius: '10px', boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.1)', maxWidth: '500px', margin: 'auto', backgroundColor: '#f9f9f9' }}>
    <input type="file" accept="image/*" onChange={handleFileChange} style={{ marginBottom: '15px', padding: '10px' }} />

    <input 
      type="text" 
      placeholder="Title Text" 
      value={titleText} 
      onChange={(e) => setTitleText(e.target.value)} 
      style={{ marginBottom: '10px', padding: '10px', width: '100%', borderRadius: '5px', border: '1px solid #ccc' }}
    />

    <input 
      type="text" 
      placeholder="Key" 
      value={key} 
      onChange={(e) => setKey(e.target.value)} 
      style={{ marginBottom: '10px', padding: '10px', width: '100%', borderRadius: '5px', border: '1px solid #ccc' }}
    />

    <input 
      type="text" 
      placeholder="Tempo" 
      value={tempo} 
      onChange={(e) => setTempo(e.target.value)} 
      style={{ marginBottom: '10px', padding: '10px', width: '100%', borderRadius: '5px', border: '1px solid #ccc' }}
    />

    <select 
      value={clefType} 
      onChange={(e) => setClefType(e.target.value)}
      style={{ marginBottom: '10px', padding: '10px', width: '100%', borderRadius: '5px', border: '1px solid #ccc' }}
    >
            <option value="classic">Classic</option>
            <option value="sharp_1">Sharp 1</option>
            <option value="sharp_2">Sharp 2</option>
            <option value="sharp_3">Sharp 3</option>
            <option value="sharp_4">Sharp 4</option>
            <option value="sharp_5">Sharp 5</option>
            <option value="sharp_6">Sharp 6</option>
            <option value="sharp_7">Sharp 7</option>
            <option value="flat_1">Flat 1</option>
            <option value="flat_2">Flat 2</option>
            <option value="flat_3">Flat 3</option>
            <option value="flat_4">Flat 4</option>
            <option value="flat_5">Flat 5</option>
            <option value="flat_6">Flat 6</option>
            <option value="flat_7">Flat 7</option>
    </select>

    <select 
      value={clefMusic} 
      onChange={(e) => setClefMusic(e.target.value)}
      style={{ marginBottom: '10px', padding: '10px', width: '100%', borderRadius: '5px', border: '1px solid #ccc' }}
    >
      <option value="G">G</option>
      <option value="F">F</option>
    </select>

    <button 
      onClick={handleUpload} 
      disabled={loading}
      style={{ padding: '10px 20px', borderRadius: '5px', backgroundColor: loading ? '#ccc' : '#1E2A47', color: '#fff', fontWeight: 'bold', border: 'none', cursor: loading ? 'default' : 'pointer' }}
    >
      {loading ? 'กำลังประมวลผล...' : 'อัปโหลดและสร้าง PDF'}
    </button>
  </div>

  {pdfBlob && (
        <div style={{ marginTop: '30px', textAlign: 'center' }}>
          <h2 style={{ color: "#4A4A4A" }}>Preview :</h2>
          <a href={pdfBlob} download="song_structure_custom.pdf" style={{ textDecoration: 'none' }}>
            <button style={{
              backgroundColor: '#1E2A47',
              color: '#FFF',
              padding: '10px 20px',
              fontSize: '16px',
              fontWeight: 'bold',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer'
            }}>
              ดาวน์โหลด PDF
            </button>
          </a>
          <div style={{ marginTop: '10px' }}>
            <embed
              src={pdfBlob}
              type="application/pdf"
              width="80%"
              height="600px"
              style={{ border: '1px solid #ddd', borderRadius: '5px' }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default NationaltoThai;
