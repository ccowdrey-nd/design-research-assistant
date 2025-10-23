/**
 * Image analysis component for brand compliance checks.
 */
import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import ReactMarkdown from 'react-markdown';
import apiClient from '../api';
import './ImageAnalyzer.css';

function ImageAnalyzer() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const onDrop = (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setSelectedFile(file);
      setAnalysis(null);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
    },
    multiple: false,
  });

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setIsAnalyzing(true);
    try {
      const result = await apiClient.analyzeImage(selectedFile);
      setAnalysis(result);
    } catch (error) {
      console.error('Error analyzing image:', error);
      setAnalysis({
        analysis: 'Error analyzing image. Please try again.',
        sources: [],
        recommendations: [],
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreview(null);
    setAnalysis(null);
  };

  return (
    <div className="image-analyzer">
      <div className="analyzer-content">
        <div className="upload-section">
          <h2>Brand Compliance Analysis</h2>
          <p>Upload creative materials (emails, ads, social posts) to check brand alignment</p>

          {!selectedFile ? (
            <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
              <input {...getInputProps()} />
              {isDragActive ? (
                <p>Drop the image here...</p>
              ) : (
                <div>
                  <p>Drag and drop an image here, or click to select</p>
                  <p className="supported-formats">Supports: PNG, JPG, GIF, WebP</p>
                </div>
              )}
            </div>
          ) : (
            <div className="preview-section">
              <img src={preview} alt="Preview" className="image-preview" />
              <div className="preview-actions">
                <button onClick={handleAnalyze} disabled={isAnalyzing}>
                  {isAnalyzing ? 'Analyzing...' : 'Analyze Brand Compliance'}
                </button>
                <button onClick={handleReset} className="secondary">
                  Upload Different Image
                </button>
              </div>
            </div>
          )}
        </div>

        {analysis && (
          <div className="analysis-section">
            <h3>Analysis Results</h3>

            <div className="analysis-content">
              <ReactMarkdown>{analysis.analysis}</ReactMarkdown>
            </div>

            {analysis.recommendations && analysis.recommendations.length > 0 && (
              <div className="recommendations">
                <h4>Key Recommendations</h4>
                <ul>
                  {analysis.recommendations.map((rec, idx) => (
                    <li key={idx}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}

            {analysis.sources && analysis.sources.length > 0 && (
              <div className="sources">
                <h4>Referenced Guidelines</h4>
                <ul>
                  {analysis.sources.map((source, idx) => (
                    <li key={idx}>
                      <a href={source.url} target="_blank" rel="noopener noreferrer">
                        {source.name} ({source.type})
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default ImageAnalyzer;

