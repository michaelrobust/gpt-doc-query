'use client';
import { useState } from 'react';
import { uploadDocument } from '@/lib/api';

interface UploadFormProps {
  onUploadSuccess: (filename: string) => void;
}

export default function UploadForm({ onUploadSuccess }: UploadFormProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.pdf')) {
      alert('Please select a PDF file');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const result = await uploadDocument(file);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      setTimeout(() => {
        onUploadSuccess(file.name);
        setIsUploading(false);
        setUploadProgress(0);
        // Reset file input
        if (event.target) {
          event.target.value = '';
        }
      }, 500);

    } catch (error) {
      console.error('Upload failed:', error);
      setIsUploading(false);
      setUploadProgress(0);
      alert('Upload failed, please try again');
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Upload PDF Document</h2>
      
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
        {isUploading ? (
          <div className="space-y-4">
            <div className="text-2xl">⏳</div>
            <div>
              <div className="text-lg font-medium text-gray-700 mb-2">
                Processing... {uploadProgress}%
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-4xl text-gray-400">📁</div>
            <div>
              <p className="text-xl font-medium text-gray-700 mb-4">
                Select PDF file to upload
              </p>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
              <p className="text-gray-500 mt-2">
                PDF format • Max 10MB
              </p>
            </div>
          </div>
        )}
      </div>

      <div className="mt-6 text-sm text-gray-600">
        <div className="flex items-center space-x-4 justify-center">
          <span className="flex items-center">
            <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
            Auto text extraction
          </span>
          <span className="flex items-center">
            <span className="w-2 h-2 bg-blue-400 rounded-full mr-2"></span>
            Smart chunking
          </span>
          <span className="flex items-center">
            <span className="w-2 h-2 bg-purple-400 rounded-full mr-2"></span>
            Vector indexing
          </span>
        </div>
      </div>
    </div>
  );
}
