import React, { useState, useRef, useCallback,useEffect } from 'react';
import ReactCrop from 'react-image-crop';
import 'react-image-crop/dist/ReactCrop.css';
import * as pdfjsLib from 'pdfjs-dist/webpack';
import axios from 'axios';
import Header from "./Header"
import { useNavigate } from "react-router-dom";

const FileUploadCrop = () => {
  const [file, setFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [crop, setCrop] = useState({ unit: '%', width: 30, aspect: 16 / 9 });
  const [completedCrop, setCompletedCrop] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmit,setIsSubmit] = useState(false);
  const [pdfUrl, setPdfUrl] = useState(null);  // To store PDF URL from backend
  const [pngUrl, setPngUrl] = useState(null);  // To store PNG URL from backend
  const [zipUrl,setZipUrl] = useState(null);
  const [filename, setFilename] = useState('');  // State for filename input
  const imgRef = useRef(null);
  const navigate = useNavigate();


  useEffect(() => {
    return () => previewUrl && URL.revokeObjectURL(previewUrl); // Cleanup URL
  }, [previewUrl]);


  const onFileChange = async (e) => {
    e.preventDefault();
    let files = e.target.files;
    if (files && files.length > 0) {
      const selectedFile = files[0];
      setFile(selectedFile);
      setIsLoading(true);
      

      if (selectedFile.type.startsWith('image/')) {
        const reader = new FileReader();
        setPdfUrl(null)
        setPngUrl(null)
        setCrop(null)
        setPreviewUrl(null)
        reader.onload = () => {
          setImagePreview(reader.result);
          setIsLoading(false)
          setIsSubmit(false)
          setInput(false)
          setPdfUrl(null)
          setPngUrl(null)
          setZipUrl(null)
          setCrop(null)
          setPreviewUrl(null)
        };
        reader.readAsDataURL(selectedFile);
      } else if (selectedFile.type === 'application/pdf') {
        try {
          const pdfImage = await convertPdfToImage(selectedFile);
          setImagePreview(pdfImage)
          setIsSubmit(false)
          setPdfUrl(null)
          setPngUrl(null)
          setZipUrl(null)
          setCrop(null)
          setPreviewUrl(null)
        } catch (error) {
          console.error('Error converting PDF:', error);
        } finally {
          setIsLoading(false);
        }
      }
    }
  };

  const convertPdfToImage = async (pdfFile) => {
    try {
      const pdf = await pdfjsLib.getDocument(URL.createObjectURL(pdfFile)).promise;
      const page = await pdf.getPage(1);
      const viewport = page.getViewport({ scale: 3 });
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      canvas.height = viewport.height;
      canvas.width = viewport.width;
      await page.render({ canvasContext: context, viewport: viewport }).promise;
      return canvas.toDataURL('image/png');
    } catch (error) {
      console.error('PDF conversion failed:', error);
      throw error;
    }
  };

  const onCropComplete = useCallback((crop) => {
    setCompletedCrop(crop);
    makeClientCrop(crop);
  }, []);

  const makeClientCrop = async (crop) => {
    if (imgRef.current && crop.width && crop.height) {
      createCropPreview(imgRef.current, crop, 'newFile.png');
    }
  };

  const createCropPreview = async (image, crop, fileName) => {
    const canvas = document.createElement('canvas');
    const scaleX = image.naturalWidth / image.width;
    const scaleY = image.naturalHeight / image.height;
    canvas.width = crop.width;
    canvas.height = crop.height;
    const ctx = canvas.getContext('2d');

    ctx.drawImage(
      image,
      crop.x * scaleX,
      crop.y * scaleY,
      crop.width * scaleX,
      crop.height * scaleY,
      0,
      0,
      crop.width,
      crop.height
    );

    return new Promise((resolve) => {
      canvas.toBlob(blob => {
        if (!blob) {
          console.error('Canvas is empty');
          return;
        }
        blob.name = fileName;
        window.URL.revokeObjectURL(previewUrl);
        setPreviewUrl(window.URL.createObjectURL(blob));
      }, 'image/png');
    });
  };



  const handleSubmit = () => {
    if (previewUrl) {
      setIsLoading(true);
      
      const token = localStorage.getItem('access') ? JSON.parse(localStorage.getItem('access')) : null;
      const formData = new FormData();
      
      // Append the cropped image blob
      fetch(previewUrl)
        .then(res => res.blob())
        .then((blob) => {
          const finalFilename = `${filename}` || 'cropped_image';  // Use filename from input or default
          formData.append('file', blob, finalFilename);  // Make sure 'file' matches the backend field name
  
          axios.post('http://localhost:8000/api/v1/process-music-ocr/', formData, {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {},
            'Content-Type': 'multipart/form-data'
          })
          .then((res) => {
            console.log(res.data);
            setPdfUrl(res.data.pdf_url);  // Set the PDF URL from backend
            setPngUrl(res.data.png_url);  // Set the PNG URL from backend
            setZipUrl(res.data.zip_url);
          })
          .catch((err) => {
            console.error(err);
          })
          .finally(() => {
            setIsLoading(false);
            setIsSubmit(true);
          });
        });
    }
  };
  

  const handleDownload = (url, filename) => {
    fetch(url)
      .then(response => response.blob())
      .then(blob => {
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      })
      .catch(error => console.error('Download failed:', error));
  };
  

  return (
    <div > 
   <Header ></Header>
      <h2>Convert Thai to National</h2>
      <div style={{display: "center",}}> 
      {(<input type="file" accept="image/*,application/pdf" onChange={onFileChange} disabled={isLoading} />)}
      <div>
      <input
        type="text"
        placeholder="Enter Music Name"
        value={filename}
        onChange={(e) => setFilename(e.target.value)}
        required
        style={{ marginTop: '10px', width: '94%', }}
      />
<button onClick={handleSubmit} style={{ marginTop: '20px',height:'40px' }} disabled={isLoading || !previewUrl}>
        {isLoading ? 'Downloading...' : 'Upload'}
      </button>
      </div>

      {isLoading && (
        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          <div className="spinner"></div>
          <p>Processing...</p>
        </div>
      )}

      {!isLoading && !isSubmit && (
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px' }}>
          {imagePreview && (
            <div style={{ width: '45%' }}>
              <h3>Original</h3>
              <ReactCrop
                src={imagePreview}
                onImageLoaded={imgRef.current}
                crop={crop}
                onChange={(newCrop) => setCrop(newCrop)}
                onComplete={onCropComplete}
              >
                <img ref={imgRef} src={imagePreview} alt="Crop me" style={{ maxWidth: '100%' }} />
              </ReactCrop>
            </div>
          )}

          {previewUrl && (
            <div style={{ width: '50%' }}>
              <h3>Preview</h3>
              <img 
                src={previewUrl} 
                alt="Crop preview" 
                style={{ maxWidth: '100%', width: '100%', height: 'auto' }} 
              />
            </div>
          )}
        </div>
      )}


      {/* Display the generated PDF and PNG */}
      {pdfUrl && pngUrl && (
  <div style={{ marginTop: '20px',justifyContent:'space-evenly',gap:'10px'}}>
    <h3>Generated Music Score PDF:</h3>
    <button onClick={() => handleDownload(pdfUrl, 'music_score.pdf')} style={{ padding: '10px 20px',marginRight:'10px' }} >
      Download PDF
    </button>
    <button onClick={() => handleDownload(zipUrl, 'music_score.zip')} style={{ padding: '10px 20px',marginRight:'10px' ,}} >
      Download PNG
    </button>
  </div>
)}</div>

{pngUrl && (
  <div style={{ marginTop: '20px' }}>
    <h3>Generated Music Score PNG:</h3>
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
  <img 
    src={`${pngUrl}?t=${new Date().getTime()}`}  // Add a cache-busting query parameter
    alt="Generated Music Score" 
    style={{ maxWidth: '50%', overflowY: 'auto' }} 
  />
</div>
    <br />
  </div>
)}




      <style jsx>{`
        .spinner {
          border: 4px solid #f3f3f3;
          border-top: 4px solid #3498db;
          border-radius: 50%;
          width: 40px;
          height: 40px;
          animation: spin 1s linear infinite;
          margin: 20px auto;
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default FileUploadCrop;

// import React, { useState, useRef, useCallback, useEffect } from 'react';
// import ReactCrop from 'react-image-crop';
// import 'react-image-crop/dist/ReactCrop.css';
// import * as pdfjsLib from 'pdfjs-dist/webpack';
// import axios from 'axios';
// import Header from "./Header";
// import { useNavigate } from "react-router-dom";
// import { InboxOutlined } from '@ant-design/icons';
// import { message, Upload } from 'antd';

// const FileUploadCrop = () => {
//   const [file, setFile] = useState(null);
//   const [imagePreview, setImagePreview] = useState(null);
//   const [crop, setCrop] = useState({ unit: '%', width: 30, aspect: 16 / 9 });
//   const [completedCrop, setCompletedCrop] = useState(null);
//   const [previewUrl, setPreviewUrl] = useState(null);
//   const [isLoading, setIsLoading] = useState(false);
//   const [pdfUrl, setPdfUrl] = useState(null);
//   const [pngUrl, setPngUrl] = useState(null);
//   const [filename, setFilename] = useState('');
//   const imgRef = useRef(null);
//   const navigate = useNavigate();

//   const { Dragger } = Upload;

//   const onFileChange = async (e) => {
//     // e.preventDefault();
//     console.log(e.file)
//     let files = e.file;
//     if (files && files.length > 0) {
//       const selectedFile = files[0];
//       setFile(selectedFile);
//       setIsLoading(true);
      

//       if (selectedFile.type.startsWith('image/')) {
//         const reader = new FileReader();
//         setPdfUrl(null)
//         setPngUrl(null)
//         setCrop(null)
//         setPreviewUrl(null)
//         reader.onload = () => {
//           setImagePreview(reader.result);
//           setIsLoading(false);
//           setInput(false)
//           setPdfUrl(null)
//           setPngUrl(null)
//           setCrop(null)
//           setPreviewUrl(null)
//         };
//         reader.readAsDataURL(selectedFile);
//       } else if (selectedFile.type === 'application/pdf') {
//         try {
//           const pdfImage = await convertPdfToImage(selectedFile);
//           setImagePreview(pdfImage);
//           setPdfUrl(null)
//           setPngUrl(null)
//           setCrop(null)
//           setPreviewUrl(null)
//         } catch (error) {
//           console.error('Error converting PDF:', error);
//         } finally {
//           setIsLoading(false);
//         }
//       }
//     }
//   };

//   const resetStates = () => {
//     setPdfUrl(null);
//     setPngUrl(null);
//     setCrop(null);
//     setPreviewUrl(null);
//     setIsLoading(false);
//   };

//   const props = {
//     name: 'file',
//     multiple: false,
//     accept: "image/*,application/pdf",
//     showUploadList: false,
//   };

//   const convertPdfToImage = async (pdfFile) => {
//     try {
//       const pdf = await pdfjsLib.getDocument(URL.createObjectURL(pdfFile)).promise;
//       const page = await pdf.getPage(1);
//       const viewport = page.getViewport({ scale: 3 });
//       const canvas = document.createElement('canvas');
//       const context = canvas.getContext('2d');
//       canvas.height = viewport.height;
//       canvas.width = viewport.width;
//       await page.render({ canvasContext: context, viewport: viewport }).promise;
//       return canvas.toDataURL('image/png');
//     } catch (error) {
//       console.error('PDF conversion failed:', error);
//       throw error;
//     }
//   };

//   useEffect(() => {
//     return () => previewUrl && URL.revokeObjectURL(previewUrl);
//   }, [previewUrl]);

//   const onCropComplete = useCallback((crop) => {
//     setCompletedCrop(crop);
//     makeClientCrop(crop);
//   }, []);

//   const makeClientCrop = async (crop) => {
//     if (imgRef.current && crop.width && crop.height) {
//       createCropPreview(imgRef.current, crop, 'newFile.png');
//     }
//   };

//   const createCropPreview = async (image, crop, fileName) => {
//     const canvas = document.createElement('canvas');
//     const scaleX = image.naturalWidth / image.width;
//     const scaleY = image.naturalHeight / image.height;
//     canvas.width = crop.width;
//     canvas.height = crop.height;
//     const ctx = canvas.getContext('2d');

//     ctx.drawImage(
//       image,
//       crop.x * scaleX,
//       crop.y * scaleY,
//       crop.width * scaleX,
//       crop.height * scaleY,
//       0,
//       0,
//       crop.width,
//       crop.height
//     );

//     return new Promise((resolve) => {
//       canvas.toBlob(blob => {
//         if (!blob) {
//           console.error('Canvas is empty');
//           return;
//         }
//         blob.name = fileName;
//         window.URL.revokeObjectURL(previewUrl);
//         setPreviewUrl(window.URL.createObjectURL(blob));
//       }, 'image/png');
//     });
//   };

//   const handleSubmit = () => {
//     if (previewUrl) {
//       setIsLoading(true);
//       const token = localStorage.getItem('access') ? JSON.parse(localStorage.getItem('access')) : null;
//       const formData = new FormData();

//       fetch(previewUrl)
//         .then(res => res.blob())
//         .then((blob) => {
//           const finalFilename = filename || 'cropped_image.png';
//           formData.append('file', blob, finalFilename);

//           axios.post('http://localhost:8000/api/v1/process-music-ocr/', formData, {
//             headers: token ? { 'Authorization': `Bearer ${token}` } : {},
//             'Content-Type': 'multipart/form-data'
//           })
//           .then((res) => {
//             setPdfUrl(res.data.pdf_url);
//             setPngUrl(res.data.png_url);
//           })
//           .catch((err) => {
//             console.error(err);
//           })
//           .finally(() => {
//             setIsLoading(false);
//           });
//         });
//     }
//   };

//   const handleDownload = (url, filename) => {
//     fetch(url)
//       .then(response => response.blob())
//       .then(blob => {
//         const link = document.createElement('a');
//         link.href = window.URL.createObjectURL(blob);
//         link.download = filename;
//         document.body.appendChild(link);
//         link.click();
//         document.body.removeChild(link);
//       })
//       .catch(error => console.error('Download failed:', error));
//   };

//   return (
//     <div>
//       <Header />
//       <h2>Convert Thai to National</h2>
//       <Dragger {...props}onChange={onFileChange}>
//         <p className="ant-upload-drag-icon">
//           <InboxOutlined />
//         </p>
//         <p className="ant-upload-text">Click or drag file to this area to upload</p>
//         <p className="ant-upload-hint">Support for a single file upload. Strictly prohibited from uploading banned files.</p>
//       </Dragger>
//       <input
//         type="text"
//         placeholder="Enter Music Name"
//         value={filename}
//         onChange={(e) => setFilename(e.target.value)}
//         required
//         style={{ marginTop: '10px', width: '94%' }}
//       />
//       <button onClick={handleSubmit} style={{ marginTop: '20px', height: '40px' }} disabled={isLoading || !previewUrl}>
//         {isLoading ? 'Downloading...' : 'Upload'}
//       </button>

//       {isLoading && (
//         <div style={{ marginTop: '20px', textAlign: 'center' }}>
//           <div className="spinner"></div>
//           <p>Processing...</p>
//         </div>
//       )}

//       {!isLoading && imagePreview && (
//         <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px' }}>
//           <div style={{ width: '45%' }}>
//             <h3>Original</h3>
//             <ReactCrop
//               src={imagePreview}
//               onImageLoaded={(img) => (imgRef.current = img)}
//               crop={crop}
//               onChange={(newCrop) => setCrop(newCrop)}
//               onComplete={onCropComplete}
//             />
//           </div>

//           {previewUrl && (
//             <div style={{ width: '50%' }}>
//               <h3>Preview</h3>
//               <img src={previewUrl} alt="Crop preview" style={{ maxWidth: '100%', width: '100%', height: 'auto' }} />
//             </div>
//           )}
//         </div>
//       )}

//       {pdfUrl && pngUrl && (
//         <div style={{ marginTop: '20px', justifyContent: 'space-evenly', gap: '10px' }}>
//           <h3>Generated Music Score PDF:</h3>
//           <button onClick={() => handleDownload(pdfUrl, 'music_score.pdf')} style={{ padding: '10px 20px', marginRight: '10px' }}>
//             Download PDF
//           </button>
//           <button onClick={() => handleDownload(pngUrl, 'music_score.png')} style={{ padding: '10px 20px', marginRight: '10px' }}>
//             Download PNG
//           </button>
//         </div>
//       )}

//       {pngUrl && (
//         <div style={{ marginTop: '20px' }}>
//           <h3>Generated Music Score PNG:</h3>
//           <img
//             src={`${pngUrl}?t=${new Date().getTime()}`}
//             alt="Generated Music Score"
//             style={{ maxWidth: '100%', overflowY: 'auto' }}
//           />
//         </div>
//       )}

//       <style jsx>{`
//         .spinner {
//           border: 4px solid #f3f3f3;
//           border-top: 4px solid #3498db;
//           border-radius: 50%;
//           width: 40px;
//           height: 40px;
//           animation: spin 1s linear infinite;
//           margin: 20px auto;
//         }
//         @keyframes spin {
//           0% { transform: rotate(0deg); }
//           100% { transform: rotate(360deg); }
//         }
//       `}</style>
//     </div>
//   );
// };

// export default FileUploadCrop;
