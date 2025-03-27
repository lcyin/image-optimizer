import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [quality, setQuality] = useState(100);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);

    // Create preview if file is an image
    if (file && file.type.match('image.*')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleQualityChange = (event) => {
    setQuality(parseInt(event.target.value));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!selectedFile) {
      setMessage('Please select an image to upload');
      return;
    }

    setIsLoading(true);
    setMessage('');

    try {
      const formData = new FormData();
      formData.append('image', selectedFile);
      formData.append('quality', quality);

      const response = await fetch('YOUR_API_ENDPOINT_HERE', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setMessage('Image uploaded successfully!');
        // Handle successful response here
      } else {
        setMessage('Error uploading image. Please try again.');
      }
    } catch (error) {
      console.error('Error:', error);
      setMessage('An error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Image Optimizer</h1>
        <p>Optimize your images with our simple tool</p>
      </header>

      <form onSubmit={handleSubmit}>
        <div className="grid-layout">
          <div className="grid-section upload-area">
            <h2 data-number="1">Select Image</h2>
            <div className="upload-section">
              <label htmlFor="image-upload" className="upload-label">
                {preview ?
                  <img src={preview} alt="Preview" className="image-preview" /> :
                  <div className="upload-placeholder">Click to select an image</div>
                }
              </label>
              <input
                id="image-upload"
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="file-input"
              />
            </div>

            {selectedFile && (
              <div className="file-info">
                <div>
                  <p><strong>File:</strong> {selectedFile.name}</p>
                </div>
                <div>
                  <p><strong>Size:</strong> {Math.round(selectedFile.size / 1024)} KB</p>
                </div>
              </div>
            )}
          </div>

          <div className="grid-section quality-area">
            <h2 data-number="2">Adjust Quality</h2>
            <div className="quality-control">
              <label htmlFor="quality-slider" className="quality-label">
                Quality
                <span>{quality}%</span>
              </label>
              <input
                id="quality-slider"
                type="range"
                min="0"
                max="100"
                value={quality}
                onChange={handleQualityChange}
                className="quality-slider"
              />
              <div className="quality-labels">
                <span>Lower file size</span>
                <span>Higher quality</span>
              </div>
            </div>
          </div>

          <div className="grid-section submit-area">
            <h2 data-number="3">Optimize</h2>
            <button
              type="submit"
              className="submit-button"
              disabled={isLoading || !selectedFile}
            >
              {isLoading ? 'Processing...' : 'Upload and Optimize'}
            </button>
          </div>

          {message && (
            <div className="grid-section message-area">
              <div className={`message ${message.includes('success') ? 'success' : 'error'}`}>
                {message}
              </div>
            </div>
          )}
        </div>
      </form>
    </div>
  );
}

export default App
