Attribute VB_Name = "RibbonCallbacks"
' ==========================================================================
'  RibbonCallbacks.bas — 功能区 Ribbon UI 回调处理
'  处理 ribbon.xml 中定义的按钮点击事件
' ==========================================================================
Option Explicit

' Ribbon 对象引用（由 onRibbonLoad 回调设置）
Private mRibbon As IRibbonUI

' 文档类型下拉当前选中值
Private mSelectedDocType As String

' ==========================================================================
'  Ribbon 初始化回调
' ==========================================================================
Public Sub OnRibbonLoad(ByVal ribbon As IRibbonUI)
    Set mRibbon = ribbon
    mSelectedDocType = "notice"  ' 默认通知
End Sub

' ==========================================================================
'  按钮回调：格式检查
' ==========================================================================
Public Sub OnCheckClick(ByVal control As Object)
    On Error GoTo ErrHandler

    ' 检查是否有活动文档
    If ActiveDocument Is Nothing Then
        MsgBox "请先打开一个 Word 文档。", vbExclamation, "公文校审助手"
        Exit Sub
    End If

    ' 显示状态
    Application.StatusBar = "正在检查文档格式..."

    ' 调用检查 API
    Dim resp As String
    resp = CheckCurrentDocument(mSelectedDocType)

    ' 解析结果
    Dim totalIssues As Long
    totalIssues = JsonGetLong(resp, "total_issues")
    Dim p0Count As Long
    p0Count = JsonGetLong(resp, "p0_count")
    Dim p1Count As Long
    p1Count = JsonGetLong(resp, "p1_count")
    Dim p2Count As Long
    p2Count = JsonGetLong(resp, "p2_count")

    Application.StatusBar = False

    ' 显示结果
    If totalIssues = 0 Then
        MsgBox "恭喜！文档格式完全符合规范，未发现问题。", vbInformation, "公文校审助手 - 检查完成"
    Else
        Dim msg As String
        msg = "文档格式检查完成，共发现 " & totalIssues & " 个问题：" & vbCrLf & vbCrLf
        If p0Count > 0 Then msg = msg & "  P0 严重错误: " & p0Count & " 个" & vbCrLf
        If p1Count > 0 Then msg = msg & "  P1 格式瑕疵: " & p1Count & " 个" & vbCrLf
        If p2Count > 0 Then msg = msg & "  P2 优化建议: " & p2Count & " 个" & vbCrLf
        msg = msg & vbCrLf & "是否立即自动修复？"

        Dim answer As VbMsgBoxResult
        answer = MsgBox(msg, vbQuestion + vbYesNo, "公文校审助手 - 检查结果")

        If answer = vbYes Then
            OnOptimizeClick control
        End If
    End If
    Exit Sub

ErrHandler:
    Application.StatusBar = False
    MsgBox "检查失败：" & vbCrLf & Err.Description, vbCritical, "公文校审助手"
End Sub

' ==========================================================================
'  按钮回调：一键优化
' ==========================================================================
Public Sub OnOptimizeClick(ByVal control As Object)
    On Error GoTo ErrHandler

    If ActiveDocument Is Nothing Then
        MsgBox "请先打开一个 Word 文档。", vbExclamation, "公文校审助手"
        Exit Sub
    End If

    ' 确认操作
    Dim answer As VbMsgBoxResult
    answer = MsgBox("即将对当前文档进行自动格式优化。" & vbCrLf & _
                     "优化后文档将被修改，是否继续？", _
                     vbQuestion + vbYesNo, "公文校审助手 - 一键优化")
    If answer <> vbYes Then Exit Sub

    Application.StatusBar = "正在优化文档格式，请稍候..."

    ' 调用优化 API
    Dim fixesApplied As Long
    fixesApplied = OptimizeCurrentDocument(mSelectedDocType)

    Application.StatusBar = False

    MsgBox "优化完成！共应用了 " & fixesApplied & " 项格式修复。" & vbCrLf & _
           "请检查文档内容是否正确。", vbInformation, "公文校审助手 - 优化完成"

    Exit Sub

ErrHandler:
    Application.StatusBar = False
    MsgBox "优化失败：" & vbCrLf & Err.Description, vbCritical, "公文校审助手"
End Sub

' ==========================================================================
'  按钮回调：套用模板
' ==========================================================================
Public Sub OnApplyTemplateClick(ByVal control As Object)
    On Error GoTo ErrHandler

    If ActiveDocument Is Nothing Then
        MsgBox "请先打开一个 Word 文档。", vbExclamation, "公文校审助手"
        Exit Sub
    End If

    ' 获取模板列表
    Dim templateJson As String
    templateJson = GetTemplateList()

    ' 提取模板名称列表供用户选择
    Dim templateNames As String
    templateNames = JsonArrayExtract(templateJson, "name")

    ' 简化：使用 InputBox 让用户输入模板 ID
    ' TODO: 后续改为 UserForm 列表选择
    Dim templateId As String
    templateId = InputBox("可用模板：" & vbCrLf & templateNames & vbCrLf & vbCrLf & _
                          "请输入要套用的模板 ID（如 notice、report、letter）：", _
                          "公文校审助手 - 套用模板", mSelectedDocType)

    If Len(templateId) = 0 Then Exit Sub

    Application.StatusBar = "正在套用模板 [" & templateId & "]..."

    Dim result As Long
    result = ApplyTemplateToCurrentDocument(templateId, mSelectedDocType)

    Application.StatusBar = False

    MsgBox "模板套用完成！文档格式已更新。", vbInformation, "公文校审助手"
    Exit Sub

ErrHandler:
    Application.StatusBar = False
    MsgBox "套用模板失败：" & vbCrLf & Err.Description, vbCritical, "公文校审助手"
End Sub

' ==========================================================================
'  下拉框回调：文档类型选择
' ==========================================================================
Public Sub OnDocTypeChange(ByVal control As Object, ByVal selectedId As String, _
                            ByVal selectedIndex As Long)
    mSelectedDocType = selectedId
End Sub

Public Sub OnDocTypeGetItemCount(ByVal control As Object, ByRef count As Long)
    count = 14  ' 文档类型数量
End Sub

Public Sub OnDocTypeGetItemLabel(ByVal control As Object, ByVal index As Long, _
                                  ByRef label As String)
    Dim types As Variant
    types = GetDocumentTypes()
    If index >= 0 And index <= UBound(types) Then
        label = types(index)(1)
    End If
End Sub

Public Sub OnDocTypeGetItemId(ByVal control As Object, ByVal index As Long, _
                               ByRef id As String)
    Dim types As Variant
    types = GetDocumentTypes()
    If index >= 0 And index <= UBound(types) Then
        id = types(index)(0)
    End If
End Sub

Public Sub OnDocTypeGetSelectedItemIndex(ByVal control As Object, ByRef index As Long)
    Dim types As Variant
    types = GetDocumentTypes()
    Dim i As Long
    For i = 0 To UBound(types)
        If types(i)(0) = mSelectedDocType Then
            index = i
            Exit Sub
        End If
    Next i
    index = 0  ' 默认选中第一个
End Sub

' ==========================================================================
'  按钮回调：关于
' ==========================================================================
Public Sub OnAboutClick(ByVal control As Object)
    Dim msg As String
    msg = "公文智能校审助手 — Word 插件" & vbCrLf & vbCrLf
    msg = msg & "版本: v1.0.0" & vbCrLf
    msg = msg & "基于 GB/T 9704 公文格式标准" & vbCrLf
    msg = msg & "后端: http://127.0.0.1:8765" & vbCrLf & vbCrLf
    msg = msg & "功能：格式检查 · 一键优化 · 模板套用"
    MsgBox msg, vbInformation, "关于公文校审助手"
End Sub

' ==========================================================================
'  辅助：获取当前选中的文档类型
' ==========================================================================
Public Function GetCurrentDocType() As String
    GetCurrentDocType = mSelectedDocType
End Function
