/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */
/**
 * Check API - 检查相关接口
 *
 * 路径与后端 backend/api/routes/check.py 一致：
 *   POST /api/check/{doc_id}           — 执行格式检查
 *   GET  /api/check/{doc_id}/results   — 获取检查结果
 *   PUT  /api/check/{doc_id}/issues/{issue_id} — 应用/忽略修复
 */
import apiClient from './client';

export interface CheckResult {
  id: number;
  document_id: number;
  check_type: string;
  severity: 'P0' | 'P1' | 'P2';
  rule_id?: string;
  location?: string;
  original_text?: string;
  suggested_fix?: string;
  reason?: string;
  status: 'pending' | 'accepted' | 'dismissed';
}

/**
 * 执行格式检查
 */
export const runCheck = async (docId: number, documentType?: string): Promise<unknown> => {
  return apiClient.post(`/api/check/${docId}`, { document_type: documentType });
};

/**
 * 获取检查结果
 */
export const getCheckResults = async (docId: number): Promise<CheckResult[]> => {
  return apiClient.get(`/api/check/${docId}/results`);
};

/**
 * 应用修复建议
 */
export const applyFix = async (docId: number, issueId: number): Promise<void> => {
  return apiClient.put(`/api/check/${docId}/issues/${issueId}`, { action: 'accept' });
};

/**
 * 忽略问题
 */
export const dismissIssue = async (docId: number, issueId: number): Promise<void> => {
  return apiClient.put(`/api/check/${docId}/issues/${issueId}`, { action: 'dismiss' });
};
