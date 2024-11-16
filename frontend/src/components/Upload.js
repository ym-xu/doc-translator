import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload as UploadIcon } from 'lucide-react';

function Upload({ onFileSelect }) {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxFiles: 1
  });

  return (
    <div className="upload-section">
      <div 
        {...getRootProps()} 
        className={`dropzone ${isDragActive ? 'active' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="upload-content">
          <UploadIcon className="w-12 h-12 text-gray-400" strokeWidth={1.5} />
          <p className="text-[16px] font-medium text-gray-700 mt-4">
            Drag and drop your PDF, or click to select
          </p>
          <button className="select-button mt-4">
            Select PDF
          </button>
          <p className="text-sm text-gray-500 mt-2">PDF files only, up to 10MB</p>
        </div>
      </div>
    </div>
  );
}

export default Upload;