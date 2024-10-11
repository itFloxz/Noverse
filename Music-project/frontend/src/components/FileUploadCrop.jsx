import React, { useState, useRef, useCallback } from 'react';
import ReactCrop from 'react-image-crop';
import 'react-image-crop/dist/ReactCrop.css';
import * as pdfjsLib from 'pdfjs-dist/webpack';
import axios from 'axios';

const FileUploadCrop = () => {
  const [file, setFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [crop, setCrop] = useState({ unit: '%', width: 30, aspect: 16 / 9 });
  const [completedCrop, setCompletedCrop] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [pdfUrl, setPdfUrl] = useState(null);  // To store PDF URL from backend
  const [pngUrl, setPngUrl] = useState(null);  // To store PNG URL from backend
  const imgRef = useRef(null);

  const onFileChange = async (e) => {
    e.preventDefault();
    let files = e.target.files;
    if (files && files.length > 0) {
      const selectedFile = files[0];
      setFile(selectedFile);
      setIsLoading(true);

      if (selectedFile.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = () => {
          setImagePreview(reader.result);
          setIsLoading(false);
        };
        reader.readAsDataURL(selectedFile);
      } else if (selectedFile.type === 'application/pdf') {
        try {
          const pdfImage = await convertPdfToImage(selectedFile);
          setImagePreview(pdfImage);
        } catch (error) {
          console.error('Error converting PDF:', error);
        } finally {
          setIsLoading(false);
          setPdfUrl(null);
          setPngUrl(null);
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
      
      const formData = new FormData();
  
      // Append the cropped image blob
      fetch(previewUrl)
        .then(res => res.blob())
        .then((blob) => {
          formData.append('file', blob, 'cropped_image.png');  // Make sure 'file' matches the backend field name
  
          axios
            .post('http://localhost:8000/api/v1/process-music-ocr/', formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            })
            .then((res) => {
              console.log(res.data);
              setPdfUrl(res.data.pdf_url);  // Assuming backend sends PDF URL
              setPngUrl(res.data.png_url);  // Assuming backend sends PNG URL
            })
            .catch((err) => {
              console.error(err);
            })
            .finally(() => {
              setIsLoading(false);
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
    <div>
      <h2>Convert Thai to Nation</h2>

      <input type="file" accept="image/*,application/pdf" onChange={onFileChange} disabled={isLoading} />

      {isLoading && (
        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          <div className="spinner"></div>
          <p>Processing...</p>
        </div>
      )}

      {!isLoading && (
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
            <div style={{ width: '45%' }}>
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

      <button onClick={handleSubmit} style={{ marginTop: '20px' }} disabled={isLoading || !previewUrl}>
        {isLoading ? 'Downloading...' : 'Upload'}
      </button>

      {/* Display the generated PDF and PNG */}
      {pdfUrl && (
  <div style={{ marginTop: '20px' }}>
    <h3>Generated Music Score PDF:</h3>
    <button onClick={() => handleDownload(pdfUrl, 'music_score.pdf')}>
      Download PDF
    </button>
  </div>
)}

{pngUrl && (
  <div style={{ marginTop: '20px' }}>
    <h3>Generated Music Score PNG:</h3>
    <img 
      src={`${pngUrl}?t=${new Date().getTime()}`}  // Add a cache-busting query parameter
      alt="Generated Music Score" 
      style={{ maxWidth: '100%' }} 
    />
    <br />
    <button onClick={() => handleDownload(pngUrl, 'music_score.png')}>
      Download PNG
    </button>
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
