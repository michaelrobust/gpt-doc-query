'use client';
import { useState, useEffect } from 'react';
import { listDocuments } from '@/lib/api';
import { Document } from '@/lib/types';

export default function DocumentList() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setIsLoading(true);
      const response = await listDocuments();
      setDocuments(response.documents);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading document list...</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      <div className="bg-gradient-to-r from-green-500 to-emerald-600 text-white p-4">
        <h2 className="text-xl font-bold">📚 Document Management</h2>
        <p className="text-green-100 text-sm">Manage your uploaded PDF documents</p>
      </div>

      <div className="p-6">
        {documents.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-4">📄</div>
            <h3 className="text-lg font-medium text-gray-700 mb-2">No documents uploaded</h3>
            <p className="text-gray-500">Upload your first PDF document to get started</p>
          </div>
        ) : (
          <div className="space-y-4">
            {documents.map((doc) => (
              <div
                key={doc.document_id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-800 mb-1">
                      📄 {doc.filename}
                    </h3>
                    <div className="text-sm text-gray-500 space-x-4">
                      <span>📅 {new Date(doc.upload_time).toLocaleString()}</span>
                      <span>📊 {doc.chunk_count} chunks</span>
                    </div>
                  </div>
                  
                  <div className="text-green-500 font-medium">
                    ✅ Ready
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
