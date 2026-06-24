Attribute VB_Name = "HttpHelper"
' ==========================================================================
'  HttpHelper.bas — HTTP 通信 + Base64 编解码 + 轻量 JSON 解析
'  公文智能校审助手 Word VBA 插件 · 基础工具模块
' ==========================================================================
Option Explicit

' --- 常量 ---
Private Const API_BASE As String = "http://127.0.0.1:8765/api/office"
Private Const HTTP_TIMEOUT As Long = 60  ' 秒

' ==========================================================================
'  HTTP 请求
' ==========================================================================

' 发送 POST JSON 请求，返回响应文本
Public Function HttpPostJson(ByVal url As String, ByVal jsonBody As String) As String
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP.6.0")

    http.Open "POST", url, False
    http.setRequestHeader "Content-Type", "application/json; charset=utf-8"
    http.setRequestHeader "Accept", "application/json"
    http.send jsonBody

    ' 等待完成（同步模式下 Open 第三个参数 False 已阻塞，此处兜底）
    Dim waitCount As Long
    Do While http.readyState <> 4 And waitCount < HTTP_TIMEOUT * 10
        DoEvents
        waitCount = waitCount + 1
        Sleep 100
    Loop

    If http.readyState = 4 And http.Status = 200 Then
        HttpPostJson = http.responseText
    Else
        Err.Raise vbObjectError + 1001, "HttpPostJson", _
            "HTTP " & http.Status & " " & http.statusText & " [" & url & "]"
    End If

    Set http = Nothing
End Function

' 发送 GET 请求，返回响应文本
Public Function HttpGet(ByVal url As String) As String
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP.6.0")

    http.Open "GET", url, False
    http.setRequestHeader "Accept", "application/json"
    http.send

    If http.readyState = 4 And http.Status = 200 Then
        HttpGet = http.responseText
    Else
        Err.Raise vbObjectError + 1002, "HttpGet", _
            "HTTP " & http.Status & " " & http.statusText & " [" & url & "]"
    End If

    Set http = Nothing
End Function

' 下载文件到本地路径
Public Function HttpDownload(ByVal url As String, ByVal localPath As String) As Boolean
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP.6.0")

    http.Open "GET", url, False
    http.send

    If http.readyState = 4 And http.Status = 200 Then
        Dim stream As Object
        Set stream = CreateObject("ADODB.Stream")
        stream.Type = 1  ' adTypeBinary
        stream.Open
        stream.write http.responseBody
        stream.SaveToFile localPath, 2  ' adSaveCreateOverWrite
        stream.Close
        Set stream = Nothing
        HttpDownload = True
    Else
        HttpDownload = False
    End If

    Set http = Nothing
End Function

' 检测后端服务是否在线
Public Function IsServerOnline() As Boolean
    On Error GoTo Offline
    Dim resp As String
    resp = HttpGet(API_BASE & "/health")
    IsServerOnline = (InStr(resp, """status"":""ok""") > 0) Or (InStr(resp, """status"": ""ok""") > 0)
    Exit Function
Offline:
    IsServerOnline = False
End Function

' 获取 API 基础地址
Public Function GetApiBase() As String
    GetApiBase = API_BASE
End Function

' ==========================================================================
'  Base64 编解码
' ==========================================================================

' 将文件编码为 Base64 字符串
Public Function FileToBase64(ByVal filePath As String) As String
    Dim stream As Object
    Set stream = CreateObject("ADODB.Stream")
    stream.Type = 1  ' adTypeBinary
    stream.Open
    stream.LoadFromFile filePath

    Dim bytes() As Byte
    bytes = stream.read
    stream.Close
    Set stream = Nothing

    ' 使用 MSXML2.DOMDocument 的 Base64 编码
    Dim dom As Object
    Set dom = CreateObject("MSXML2.DOMDocument.6.0")
    Dim node As Object
    Set node = dom.createElement("b64")
    node.DataType = "bin.base64"
    node.nodeTypedValue = bytes
    FileToBase64 = Replace(node.text, vbLf, "")

    Set node = Nothing
    Set dom = Nothing
End Function

' 将 Base64 字符串解码并保存到文件
Public Sub Base64ToFile(ByVal base64Str As String, ByVal outputPath As String)
    Dim dom As Object
    Set dom = CreateObject("MSXML2.DOMDocument.6.0")
    Dim node As Object
    Set node = dom.createElement("b64")
    node.DataType = "bin.base64"
    node.text = base64Str

    Dim bytes() As Byte
    bytes = node.nodeTypedValue

    Dim stream As Object
    Set stream = CreateObject("ADODB.Stream")
    stream.Type = 1  ' adTypeBinary
    stream.Open
    stream.write bytes
    stream.SaveToFile outputPath, 2  ' adSaveCreateOverWrite
    stream.Close

    Set stream = Nothing
    Set node = Nothing
    Set dom = Nothing
End Sub

' 将当前活动文档保存为临时 docx 并返回 Base64
Public Function ActiveDocToBase64() As String
    Dim tmpPath As String
    tmpPath = Environ$("TEMP") & "\gw_assist_upload_" & Format(Now, "yyyymmddhhnnss") & ".docx"

    ' 保存当前文档为 docx 格式（不修改原文档格式）
    ActiveDocument.SaveAs2 tmpPath, wdFormatXMLDocument

    ActiveDocToBase64 = FileToBase64(tmpPath)

    ' 清理临时文件
    On Error Resume Next
    Kill tmpPath
    On Error GoTo 0
End Function

' ==========================================================================
'  轻量 JSON 构造（无需外部库）
' ==========================================================================

' 构造 JSON 字符串（转义特殊字符）
Public Function JsonEscape(ByVal s As String) As String
    Dim result As String
    result = s
    result = Replace(result, "\", "\\")
    result = Replace(result, """", "\""")
    result = Replace(result, vbCr, "")
    result = Replace(result, vbLf, "\n")
    result = Replace(result, vbTab, "\t")
    JsonEscape = result
End Function

' 从 JSON 文本中提取字符串值: "key":"value"
Public Function JsonGetString(ByVal json As String, ByVal key As String) As String
    Dim pattern As String
    pattern = """" & key & """\s*:\s*""([^""]*)"""

    Dim regex As Object
    Set regex = CreateObject("VBScript.RegExp")
    regex.pattern = pattern
    regex.IgnoreCase = True

    If regex.Test(json) Then
        JsonGetString = regex.Execute(json)(0).SubMatches(0)
    Else
        JsonGetString = ""
    End If

    Set regex = Nothing
End Function

' 从 JSON 文本中提取数字值: "key":123
Public Function JsonGetLong(ByVal json As String, ByVal key As String) As Long
    Dim pattern As String
    pattern = """" & key & """\s*:\s*(-?\d+)"

    Dim regex As Object
    Set regex = CreateObject("VBScript.RegExp")
    regex.pattern = pattern
    regex.IgnoreCase = True

    If regex.Test(json) Then
        JsonGetLong = CLng(regex.Execute(json)(0).SubMatches(0))
    Else
        JsonGetLong = 0
    End If

    Set regex = Nothing
End Function

' 从 JSON 文本中提取布尔值: "key":true
Public Function JsonGetBool(ByVal json As String, ByVal key As String) As Boolean
    JsonGetBool = (InStr(json, """" & key & """:true") > 0) Or _
                  (InStr(json, """" & key & """: true") > 0)
End Function

' 提取 JSON 数组中每个对象的指定字段值（返回逗号分隔字符串）
Public Function JsonArrayExtract(ByVal json As String, ByVal field As String) As String
    Dim regex As Object
    Set regex = CreateObject("VBScript.RegExp")
    regex.pattern = """" & field & """\s*:\s*""([^""]*)"""
    regex.Global = True
    regex.IgnoreCase = True

    Dim matches As Object
    Set matches = regex.Execute(json)

    Dim result As String
    Dim i As Long
    For i = 0 To matches.Count - 1
        If i > 0 Then result = result & ","
        result = result & matches(i).SubMatches(0)
    Next i

    JsonArrayExtract = result
    Set regex = Nothing
End Function

' 安全的 Sleep 封装（VBA 本身无 Sleep，需 API 调用）
Private Sub Sleep(ByVal ms As Long)
    #If VBA7 Then
        Declare PtrSafe Sub kernel32_sleep Lib "kernel32" Alias "Sleep" (ByVal dwMilliseconds As Long)
        kernel32_sleep ms
    #Else
        Declare Sub kernel32_sleep Lib "kernel32" Alias "Sleep" (ByVal dwMilliseconds As Long)
        kernel32_sleep ms
    #End If
End Sub
