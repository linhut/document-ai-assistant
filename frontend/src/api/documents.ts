/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */
/**
 * Documents API - 文档相关接口
 */
import apiClient from './client';

export interface Document {
  id: number;
  filename: string;
  file_path: string;
  document_type?: string;
  status: string;
  created_at: string;
  page_count?: number;
  paragraph_count?: number;
}

export interface UploadResponse {
  id: number;
  filename: string;
  file_path: string;
  document_type: string;
  status: string;
  page_count: number;
  paragraph_count: number;
  created_at: string;
}

/**
 * 上传文档
 */
export const uploadDocument = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  return apiClient.post('/api/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

/**
 * 获取文档列表
 */
export const getDocuments = async (): Promise<Document[]> => {
  return apiClient.get('/api/documents');
};

/**
 * 获取文档详情
 */
export const getDocument = async (id: number): Promise<Document> => {
  return apiClient.get(`/api/documents/${id}`);
};
