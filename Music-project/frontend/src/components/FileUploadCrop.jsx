import React, { useState, useRef, useCallback } from 'react';
import ReactCrop from 'react-image-crop';
import 'react-image-crop/dist/ReactCrop.css';
import * as pdfjsLib from 'pdfjs-dist/webpack'; // Correct import for pdfjs
import axios from 'axios';

const FileUploadCrop = () => {
  const [file, setFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [crop, setCrop] = useState({ unit: '%', width: 30, aspect: 16 / 9 });
  const [completedCrop, setCompletedCrop] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
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
        }
      }
    }
  };

  const convertPdfToImage = async (pdfFile) => {
    try {
      const pdf = await pdfjsLib.getDocument(URL.createObjectURL(pdfFile)).promise;
      const page = await pdf.getPage(1);  // Choose the first page
      const viewport = page.getViewport({ scale: 1.5 });
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
      createCropPreview(imgRef.current, crop, 'newFile.jpeg');
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
      }, 'image/jpeg');
    });
  };

  const handleSubmit = () => {
    if (previewUrl) {
      setIsLoading(true);
      axios
        .post('http://localhost:8000/upload', { image: previewUrl })
        .then((res) => {
          console.log(res.data);
        })
        .catch((err) => {
          console.error(err);
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  };

  return (
    <div>
      <h2>Upload and Crop Image or PDF</h2>

      <input type="file" accept="image/*,application/pdf" onChange={onFileChange} disabled={isLoading} />

      {isLoading && (
        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          <div className="spinner"></div>
          <p>กำลังประมวลผล...</p>
        </div>
      )}

      {!isLoading && (
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px' }}>
          {imagePreview && (
            <div style={{ width: '45%' }}>
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
                style={{ 
                  maxWidth: '100%', 
                  width: '100%', 
                  height: 'auto'
                }} 
              />
            </div>
          )}
        </div>
      )}

      <button onClick={handleSubmit} style={{ marginTop: '20px' }} disabled={isLoading || !previewUrl}>
        {isLoading ? 'กำลังอัปโหลด...' : 'อัปโหลด'}
      </button>

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
