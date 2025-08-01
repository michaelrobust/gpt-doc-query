'use client';
import { useState } from 'react';

export default function Home() {
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.pdf')) {
      alert('Please select a PDF file');
      return;
    }

    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setUploadedFiles(prev => [...prev, file.name]);
        alert(`✅ Upload successful: ${result.message || 'File uploaded!'}`);
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('❌ Upload failed, please try again');
    } finally {
      setIsUploading(false);
    }
  };

  const handleQuery = async () => {
    const input = document.getElementById('queryInput') as HTMLInputElement;
    const query = input?.value.trim();
    if (!query) return;

    try {
      const response = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (response.ok) {
        const result = await response.json();
        const resultDiv = document.getElementById('queryResult');
        if (resultDiv) {
          resultDiv.innerHTML = `
            <div style="background: #f0f9ff; padding: 16px; border-radius: 8px; margin-top: 16px; border-left: 4px solid #3b82f6;">
              <div style="margin-bottom: 8px;"><strong>🤔 Your Question:</strong> ${query}</div>
              <div><strong>🤖 Assistant Answer:</strong> ${result.answer}</div>
              ${result.sources ? `<div style="margin-top: 8px; font-size: 0.9em; color: #6b7280;"><strong>📚 Sources:</strong> ${result.sources.length} references found</div>` : ''}
            </div>
          `;
        }
        input.value = '';
      } else {
        throw new Error('Query failed');
      }
    } catch (error) {
      console.error('Query error:', error);
      alert('❌ Query failed, please try again');
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      handleQuery();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-2 text-gray-800">
          RAG Assistant
        </h1>
        <p className="text-center text-gray-600 mb-8">Smart Document Q&A System</p>
        
        <div className="bg-white p-6 rounded-xl shadow-lg mb-6">
          <h2 className="text-2xl font-bold mb-4 flex items-center">
            📄 Upload PDF Document
          </h2>
          <div className="border-2 border-dashed border-gray-300 hover:border-blue-400 p-8 text-center rounded-lg transition-colors">
            <input 
              type="file" 
              accept=".pdf" 
              onChange={handleFileChange}
              disabled={isUploading}
              className="mb-4 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" 
            />
            <p className="text-gray-600">
              {isUploading ? '⏳ Uploading and processing...' : 'Select a PDF file to upload and analyze'}
            </p>
            {uploadedFiles.length > 0 && (
              <div className="mt-4 text-green-600">
                ✅ {uploadedFiles.length} file(s) uploaded: {uploadedFiles.join(', ')}
              </div>
            )}
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-2xl font-bold mb-4 flex items-center">
            💬 Ask Questions
          </h2>
          <div className="flex gap-4 mb-4">
            <input 
              id="queryInput"
              type="text" 
              placeholder="Ask anything about your document..."
              onKeyPress={handleKeyPress}
              className="flex-1 border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 p-3 rounded-lg outline-none transition-all"
            />
            <button 
              onClick={handleQuery}
              className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Send 🚀
            </button>
          </div>
          <div id="queryResult"></div>
        </div>

        <div className="mt-8 text-center text-gray-500">
          <p>✅ Frontend: Next.js 14 + React 18 | Backend: FastAPI + Test Mode</p>
          <p>🔗 API Connection: {window.location.protocol}//localhost:8000</p>
        </div>
      </div>
    </div>
  );
}
