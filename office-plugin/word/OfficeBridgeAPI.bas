Attribute VB_Name = "OfficeBridgeAPI"
' ==========================================================================
'  OfficeBridgeAPI.bas — 公文校审 API 业务封装
'  调用后端 /api/office/* 端点，提供一键校审/优化/套用模板功能
' ==========================================================================
Option Explicit

Private Const API_BASE As String = "http://127.0.0.1:8765/api/office"

' 文档类型映射
Public Function GetDocumentTypes() As Variant
    ' 返回 (id, label) 二维数组，供 UI 下拉使用
    GetDocumentTypes = Array( _
        Array("notice", "通知"), _
        Array("request", "请示"), _
        Array("report", "报告"), _
        Array("letter", "函"), _
        Array("reply", "批复"), _
        Array("decision", "决定"), _
        Array("opinion", "意见"), _
        Array("bulletin", "公报"), _
        Array("announcement", "公告"), _
        Array("communique", "通告"), _
        Array("instruction", "指示"), _
        Array("meeting", "会议纪要"), _
        Array("resolution", "决议"), _
        Array("command", "命令") _
    )
End Function

' ==========================================================================
'  核心功能：检查当前文档
' ==========================================================================
' 返回: CheckResponse 结构 (issues 数组, counts)
Public Function CheckCurrentDocument(Optional ByVal docType As String = "notice") As String
    ' 1. 检测服务状态
    If Not IsServerOnline() Then
        Err.Raise vbObjectError + 2001, "CheckCurrentDocument", _
            "后端服务未启动。请先运行公文智能校审助手桌面应用。"
    End If

    ' 2. 编码当前文档
    Dim base64 As String
    base64 = ActiveDocToBase64()

    ' 3. 构造 JSON 请求体
    Dim filename As String
    filename = ActiveDocument.Name
    If Right(filename, 5) <> ".docx" Then filename = filename & ".docx"

    Dim jsonBody As String
    jsonBody = "{""document_base64"":""" & base64 & """," & _
               """document_type"":""" & JsonEscape(docType) & """," & _
               """filename"":""" & JsonEscape(filename) & """}"

    ' 4. 发送请求
    Dim resp As String
    resp = HttpPostJson(API_BASE & "/check", jsonBody)

    ' 5. 返回原始 JSON（由调用方解析展示）
    CheckCurrentDocument = resp
End Function

' ==========================================================================
'  核心功能：一键优化当前文档
' ==========================================================================
' 操作：发送文档 → 后端修复 → 返回修复后的文档 → 替换当前文档内容
Public Function OptimizeCurrentDocument(Optional ByVal docType As String = "notice", _
                                         Optional ByVal selectedRuleIds As String = "") As Long
    ' 1. 检测服务
    If Not IsServerOnline() Then
        Err.Raise vbObjectError + 2002, "OptimizeCurrentDocument", _
            "后端服务未启动。请先运行公文智能校审助手桌面应用。"
    End If

    ' 2. 编码文档
    Dim base64 As String
    base64 = ActiveDocToBase64()

    Dim filename As String
    filename = ActiveDocument.Name
    If Right(filename, 5) <> ".docx" Then filename = filename & ".docx"

    ' 3. 构造请求（支持选择性修复）
    Dim jsonBody As String
    jsonBody = "{""document_base64"":""" & base64 & """," & _
               """document_type"":""" & JsonEscape(docType) & """," & _
               """filename"":""" & JsonEscape(filename) & """"

    If Len(selectedRuleIds) > 0 Then
        jsonBody = jsonBody & ",""selected_rule_ids"":[" & selectedRuleIds & "]"
    End If
    jsonBody = jsonBody & "}"

    ' 4. 发送修复请求
    Dim resp As String
    resp = HttpPostJson(API_BASE & "/fix", jsonBody)

    ' 5. 解析返回
    Dim fixesApplied As Long
    fixesApplied = JsonGetLong(resp, "fixes_applied")

    Dim fixedBase64 As String
    fixedBase64 = JsonGetString(resp, "document_base64")

    If Len(fixedBase64) = 0 Then
        Err.Raise vbObjectError + 2003, "OptimizeCurrentDocument", _
            "服务器未返回优化后的文档。"
    End If

    ' 6. 将修复后的文档写回当前文档
    ReplaceActiveDocContent fixedBase64

    OptimizeCurrentDocument = fixesApplied
End Function

' ==========================================================================
'  核心功能：套用模板
' ==========================================================================
Public Function ApplyTemplateToCurrentDocument(ByVal templateId As String, _
                                                Optional ByVal docType As String = "notice") As Long
    If Not IsServerOnline() Then
        Err.Raise vbObjectError + 2004, "ApplyTemplate", "后端服务未启动。"
    End If

    Dim base64 As String
    base64 = ActiveDocToBase64()

    Dim filename As String
    filename = ActiveDocument.Name
    If Right(filename, 5) <> ".docx" Then filename = filename & ".docx"

    Dim jsonBody As String
    jsonBody = "{""template_id"":""" & JsonEscape(templateId) & """," & _
               """document_base64"":""" & base64 & """," & _
               """filename"":""" & JsonEscape(filename) & """}"

    Dim resp As String
    resp = HttpPostJson(API_BASE & "/apply-template", jsonBody)

    Dim fixedBase64 As String
    fixedBase64 = JsonGetString(resp, "document_base64")

    If Len(fixedBase64) = 0 Then
        Err.Raise vbObjectError + 2005, "ApplyTemplate", "服务器未返回套用模板后的文档。"
    End If

    ReplaceActiveDocContent fixedBase64
    ApplyTemplateToCurrentDocument = 1
End Function

' ==========================================================================
'  辅助功能：获取模板列表
' ==========================================================================
Public Function GetTemplateList() As String
    If Not IsServerOnline() Then
        Err.Raise vbObjectError + 2006, "GetTemplateList", "后端服务未启动。"
    End If
    GetTemplateList = HttpGet(API_BASE & "/templates")
End Function

' ==========================================================================
'  辅助功能：下载模板到指定路径
' ==========================================================================
Public Function DownloadTemplate(ByVal templateId As String, ByVal savePath As String, _
                                  Optional ByVal fmt As String = "dotx") As Boolean
    If Not IsServerOnline() Then
        Err.Raise vbObjectError + 2007, "DownloadTemplate", "后端服务未启动。"
    End If
    DownloadTemplate = HttpDownload(API_BASE & "/generate-template?template_id=" & _
                                     templateId & "&format=" & fmt, savePath)
End Function

' ==========================================================================
'  内部辅助：将 Base64 文档内容替换到当前活动文档
' ==========================================================================
Private Sub ReplaceActiveDocContent(ByVal base64Content As String)
    ' 解码到临时文件
    Dim tmpPath As String
    tmpPath = Environ$("TEMP") & "\gw_assist_fixed_" & Format(Now, "yyyymmddhhnnss") & ".docx"
    Base64ToFile base64Content, tmpPath

    ' 保存当前文档的路径
    Dim currentPath As String
    currentPath = ActiveDocument.FullName
    Dim isSaved As Boolean
    isSaved = (Len(currentPath) > 0 And ActiveDocument.Saved)

    ' 用修复后的内容覆盖当前文档
    ' 策略：打开临时文档 → 全选复制 → 切回原文档 → 全选粘贴
    ' 这样保留原文档的窗口状态和未保存的路径信息
    Dim tmpDoc As Document
    Set tmpDoc = Documents.Open(tmpPath, ReadOnly:=True, Visible:=False)

    ' 复制临时文档全部内容
    tmpDoc.Content.Copy

    ' 切回原文档，全选粘贴
    ActiveDocument.Content.Paste

    ' 关闭临时文档
    tmpDoc.Close SaveChanges:=False

    ' 清理临时文件
    On Error Resume Next
    Kill tmpPath
    On Error GoTo 0

    ' 标记文档为已修改
    ActiveDocument.Saved = False
End Sub
