export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  sources?: SourceInfo[];
  timestamp: Date;
}

export interface SourceInfo {
  content: string;
  document: string;
  page?: number;
}

export interface Document {
  document_id: string;
  filename: string;
  upload_time: string;
  chunk_count: number;
}
