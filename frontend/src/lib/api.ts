const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface QueryRequest {
  query: string;
  top_k?: number;
}

export interface QueryResponse {
  answer: string;
  sources: Array<{
    content: string;
    document: string;
    similarity_score: number;
    document_id: string;
  }>;
  confidence: number;
  chunks_found: number;
  mode: string;
  query_processed: string;
}

export interface Document {
  document_id: string;
  filename: string;
  upload_time: string;
  chunk_count: number;
}

export const uploadDocument = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Upload failed');
  }

  return response.json();
};

export const queryDocuments = async (request: QueryRequest): Promise<QueryResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error('Query failed');
  }

  return response.json();
};

export const listDocuments = async () => {
  const response = await fetch(`${API_BASE_URL}/api/documents`);

  if (!response.ok) {
    throw new Error('Failed to fetch documents');
  }

  return response.json();
};
