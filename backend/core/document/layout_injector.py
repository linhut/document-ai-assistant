# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""
Layout Injector — 版头/版记/页码注入（GB/T 9704-2012）

从 api/routes/optimize.py 下沉的文档版式能力（原 Q1 反向依赖修复）：
- _inject_header_to_docx       版头注入：发文机关标志 + 发文字号/签发人 + 红色反线
- _inject_footer_to_docx       版记注入：抄送 + 印发机关/日期 + 分隔线
- _inject_page_number_to_docx  页码注入：{PAGE}/{NUMPAGES} 域代码 + 奇偶页

本模块只依赖 core/document（font_utils）与 utils.logger，
可被 services / CLI（wfp_cli.py）/ office-plugin 独立复用。
"""

from utils.logger import logger


def _insert_before(new_para, reference_p, body) -> None:
    """将段落插入到 reference_p 之前。"""
    if reference_p is not None:
        body.insert(list(body).index(reference_p), new_para._element)
    else:
        body.append(new_para._element)


def _inject_header_to_docx(output_path: str, header_config: dict) -> None:
    """注入版头：发文机关标志 + 空行 + 发文字号 + 红色分隔线。

    使用 python-docx API 而非裸 OOXML，确保样式正确写入。
    公文版头顺序（从上到下）：机关名 → 空行 → 发文字号/签发人 → 红色分隔线
    """
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
        from core.document.font_utils import set_run_font

        doc = Document(output_path)
        org_name = header_config.get("org_name", "")
        doc_number = header_config.get("doc_number", "")
        signer = header_config.get("signer", "")

        if not org_name:
            return

        body = doc.element.body
        first_p = body.find(qn("w:p"))

        # === 按正确顺序插入（从文档最前面开始） ===

        # 1. 发文机关标志：红色 30pt 方正小标宋简体 居中（最顶部）
        p_org = doc.add_paragraph()
        p_org.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_org = p_org.add_run(org_name)
        from core.document.font_utils import TITLE_FONT, BODY_FONT

        set_run_font(run_org, TITLE_FONT)
        run_org.font.size = Pt(30)
        run_org.font.color.rgb = RGBColor(0xE0, 0x00, 0x00)
        p_org.paragraph_format.line_spacing = Pt(28.95)
        p_org.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        _insert_before(p_org, first_p, body)

        # 2. 空二行（保持版头与发文字号之间的间距）
        for _ in range(2):
            p_empty = doc.add_paragraph()
            p_empty.paragraph_format.line_spacing = Pt(28.95)
            p_empty.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
            _insert_before(p_empty, first_p, body)

        # 3. 发文字号与签发人同行（发文号左对齐，签发人右对齐）
        # 计算右对齐制表位位置：基于页面实际宽度
        page_w_mm = 210.0  # A4 默认
        margin_l_mm = 28.0
        margin_r_mm = 26.0
        try:
            pw = doc.sections[0].page_width
            ml = doc.sections[0].left_margin
            mr = doc.sections[0].right_margin
            if pw and ml and mr:
                # 从 EMU 转换为 mm: 1mm = 36000 EMU, 1 twip = 1/1440 inch = 1/567 cm
                # from docx.shared import Emu  # unused
                usable_twips = int((pw - ml - mr) / 635)  # 1 twip ≈ 635 EMU (实际 1mm=36000EMU, 1twip=635EMU)
                tab_pos = usable_twips
            else:
                tab_pos = int((page_w_mm - margin_l_mm - margin_r_mm) / 25.4 * 1440)
        except Exception:
            tab_pos = int((page_w_mm - margin_l_mm - margin_r_mm) / 25.4 * 1440)

        if doc_number and signer:
            # 同一段落：发文号左 + 制表位右 + 签发人右
            p_num = doc.add_paragraph()
            p_num.alignment = WD_ALIGN_PARAGRAPH.LEFT
            pf = p_num.paragraph_format
            pf.line_spacing = Pt(28.95)
            pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY

            # 设置右对齐制表位到页面右边界
            tabs_el = OxmlElement("w:tabs")
            tab_el = OxmlElement("w:tab")
            tab_el.set(qn("w:val"), "right")
            tab_el.set(qn("w:pos"), str(tab_pos))
            tab_el.set(qn("w:leader"), "none")
            tabs_el.append(tab_el)
            pPr = p_num._element.get_or_add_pPr()
            pPr.append(tabs_el)

            # 发文号（左）
            run_num = p_num.add_run(doc_number)
            set_run_font(run_num, BODY_FONT)
            run_num.font.size = Pt(16)

            # Tab 字符
            p_num.add_run("\t")

            # 签发人（右）
            run_signer = p_num.add_run(f"签发人：{signer}")
            set_run_font(run_signer, BODY_FONT)
            run_signer.font.size = Pt(16)

            _insert_before(p_num, first_p, body)
        elif doc_number:
            # 仅有发文号：居中
            p_num = doc.add_paragraph()
            p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run_num = p_num.add_run(doc_number)
            set_run_font(run_num, BODY_FONT)
            run_num.font.size = Pt(16)
            p_num.paragraph_format.line_spacing = Pt(28.95)
            p_num.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
            _insert_before(p_num, first_p, body)
        elif signer:
            # 仅有签发人：右对齐
            p_signer = doc.add_paragraph()
            p_signer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            run_signer = p_signer.add_run(f"签发人：{signer}")
            set_run_font(run_signer, BODY_FONT)
            run_signer.font.size = Pt(16)
            p_signer.paragraph_format.line_spacing = Pt(28.95)
            p_signer.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
            _insert_before(p_signer, first_p, body)

        # 5. 红色分隔线（底部边框）— 紧贴在发文字号下方
        p_border = doc.add_paragraph()
        p_border.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pPr = p_border._element.get_or_add_pPr()
        pBdr = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "15")
        bottom.set(qn("w:color"), "E00000")
        bottom.set(qn("w:space"), "1")
        pBdr.append(bottom)
        pPr.append(pBdr)
        spacing = OxmlElement("w:spacing")
        spacing.set(qn("w:line"), "60")  # 3pt 高度
        spacing.set(qn("w:lineRule"), "exact")
        pPr.append(spacing)
        _insert_before(p_border, first_p, body)

        doc.save(output_path)
        logger.info(f"Injected header into {output_path}")
    except Exception as e:
        logger.error(f"Failed to inject header: {e}", exc_info=True)


def _inject_footer_to_docx(output_path: str, footer_config: dict) -> None:
    """注入版记：分隔线 + 抄送 + 印发 + 分隔线。

    使用 python-docx API 而非裸 OOXML，确保样式正确写入。
    GB/T 9704 §7.4：版记用四号仿宋（14pt），左空一字。
    """
    try:
        from docx import Document
        from docx.shared import Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
        from core.document.font_utils import set_run_font, BODY_FONT

        doc = Document(output_path)
        cc = footer_config.get("cc", "")
        printer = footer_config.get("printer", "")
        # 兼容前后端字段名差异：前端发 print_date，后端也支持 printDate
        print_date = footer_config.get("printDate", footer_config.get("print_date", ""))

        # === 版记换页逻辑 ===
        # 计算末页剩余空间，若不足 30mm 则强制分页
        try:
            section = doc.sections[0]
            ph = section.page_height  # EMU
            tm = section.top_margin  # EMU
            bm = section.bottom_margin  # EMU
            if ph and tm and bm:
                # 可用内容高度 = 页高 - 上边距 - 下边距 (EMU)
                content_height_emu = ph - tm - bm
                # 一行的高度 ≈ 28.95pt = 28.95 * 12700 EMU ≈ 367665 EMU
                line_height_emu = 367665
                lines_per_page = int(content_height_emu / line_height_emu)

                # 统计正文段落数（不包括版头注入的段落，它们 count 少不影响结果）
                para_count = len(doc.paragraphs)

                # 版记需要的最小行数（上分隔线 + 抄送 + 印发行 + 下分隔线 ≈ 3行）
                MIN_LINES_FOR_FOOTER = 3
                # MIN_FOOTER_HEIGHT_EMU = MIN_LINES_FOR_FOOTER * line_height_emu  # ≈ 30mm（未使用）

                # 计算最后一个内容段落在第几页
                last_page_paras = para_count % lines_per_page
                if last_page_paras == 0:
                    last_page_paras = lines_per_page

                # 剩余行数 = 该页总行数 - 已用行数
                remaining_lines = lines_per_page - last_page_paras

                if remaining_lines < MIN_LINES_FOR_FOOTER:
                    # 剩余空间不足，在文档末尾插入分页符
                    page_break_para = doc.add_paragraph()
                    run_pb = page_break_para.add_run("")
                    br = OxmlElement("w:br")
                    br.set(qn("w:type"), "page")
                    run_pb._element.append(br)
                    logger.info(
                        f"Footer: insufficient space ({remaining_lines} lines < {MIN_LINES_FOR_FOOTER}), forced page break"
                    )
        except Exception as e:
            logger.warning(f"Footer page break calculation failed: {e}")

        if not (cc or printer or print_date):
            return

        # 辅助：创建带顶部分隔线的段落（GB/T 9704：0.35mm 黑色实线，与版心等宽）
        def _add_border_para(doc, border_size="8", border_color="000000"):
            p = doc.add_paragraph()
            pPr = p._element.get_or_add_pPr()
            # 确保左右顶格（无任何缩进）
            ind = OxmlElement("w:ind")
            ind.set(qn("w:left"), "0")
            ind.set(qn("w:right"), "0")
            ind.set(qn("w:firstLine"), "0")
            pPr.append(ind)
            # 设置黑色边框
            pBdr = OxmlElement("w:pBdr")
            top = OxmlElement("w:top")
            top.set(qn("w:val"), "single")
            top.set(qn("w:sz"), border_size)  # 0.35mm ≈ 1pt = sz=8
            top.set(qn("w:color"), border_color)
            top.set(qn("w:space"), "0")
            pBdr.append(top)
            pPr.append(pBdr)
            # 最小行高、零间距
            spacing = OxmlElement("w:spacing")
            spacing.set(qn("w:before"), "0")
            spacing.set(qn("w:after"), "0")
            spacing.set(qn("w:line"), "200")
            spacing.set(qn("w:lineRule"), "atLeast")
            pPr.append(spacing)
            return p

        # 1. 上分隔线（0.35mm 黑色实线），加前方间距将版记推到底部
        # 使用约 200pt 前间距（约 70mm），确保版记出现在末页底部
        p_top_line = doc.add_paragraph()
        pPr_top = p_top_line._element.get_or_add_pPr()
        ind_top = OxmlElement("w:ind")
        ind_top.set(qn("w:left"), "0")
        ind_top.set(qn("w:right"), "0")
        pPr_top.append(ind_top)
        spacing_top = OxmlElement("w:spacing")
        spacing_top.set(qn("w:before"), str(200 * 20))  # 200pt before spacing
        spacing_top.set(qn("w:after"), "0")
        spacing_top.set(qn("w:line"), "200")
        spacing_top.set(qn("w:lineRule"), "atLeast")
        pPr_top.append(spacing_top)
        pBdr_top = OxmlElement("w:pBdr")
        top_line = OxmlElement("w:top")
        top_line.set(qn("w:val"), "single")
        top_line.set(qn("w:sz"), "8")  # 0.35mm
        top_line.set(qn("w:color"), "000000")
        top_line.set(qn("w:space"), "0")
        pBdr_top.append(top_line)
        pPr_top.append(pBdr_top)

        # 2. 抄送行（三号仿宋=16pt，左空一字，悬挂缩进）
        if cc:
            p_cc = doc.add_paragraph()
            p_cc.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run_cc = p_cc.add_run(f"抄送：{cc}。")
            set_run_font(run_cc, BODY_FONT)
            run_cc.font.size = Pt(16)  # 三号=16pt
            p_cc.paragraph_format.line_spacing = Pt(28.95)
            p_cc.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
            # 悬挂缩进：左空一字 + 悬挂（回行与冒号后首字对齐）
            # 左空一字 = 16pt = 320 twips，悬挂量 = 16pt = 320 twips
            pPr_cc = p_cc._element.get_or_add_pPr()
            ind_cc = OxmlElement("w:ind")
            ind_cc.set(qn("w:left"), "320")  # 左空一字 (16pt ≈ 320 twips)
            ind_cc.set(qn("w:hanging"), "320")  # 悬挂缩进，使首行回到左边界
            pPr_cc.append(ind_cc)

            # 细分隔线（抄送与印发之间）
            if printer or print_date:
                _add_border_para(doc, "8")

        # 3. 印发机关和印发日期（同一行，左空一字+右空一字，日期用制表位推到最右）
        if printer or print_date:
            p_info = doc.add_paragraph()
            p_info.alignment = WD_ALIGN_PARAGRAPH.LEFT
            pPr_info = p_info._element.get_or_add_pPr()

            # 左空一字 + 右空一字
            ind_info = OxmlElement("w:ind")
            ind_info.set(qn("w:left"), "320")  # 左空一字 (16pt ≈ 320 twips)
            ind_info.set(qn("w:right"), "320")  # 右空一字 (16pt ≈ 320 twips)
            pPr_info.append(ind_info)

            # 设置右对齐制表位，将印发日期推到最右端
            tabs_el = OxmlElement("w:tabs")
            tab_el = OxmlElement("w:tab")
            tab_el.set(qn("w:val"), "right")
            # 制表位位置 = 可用宽度 - 右缩进 (在 twips 中)
            # A4 可用宽度约 156mm ≈ 8844 twips
            tab_el.set(qn("w:pos"), "8500")
            tab_el.set(qn("w:leader"), "none")
            tabs_el.append(tab_el)
            pPr_info.append(tabs_el)

            # 行距
            spacing = OxmlElement("w:spacing")
            spacing.set(qn("w:line"), "579")  # 28.95pt
            spacing.set(qn("w:lineRule"), "exact")
            pPr_info.append(spacing)

            # 印发机关（左）
            if printer:
                run_printer = p_info.add_run(printer)
                set_run_font(run_printer, BODY_FONT)
                run_printer.font.size = Pt(16)

            # Tab → 将日期推到右边
            if printer and print_date:
                p_info.add_run("\t")

            # 印发日期（右）
            if print_date:
                run_date = p_info.add_run(f"{print_date}印发")
                set_run_font(run_date, BODY_FONT)
                run_date.font.size = Pt(16)

        # 4. 下分隔线（0.35mm 实线）
        _add_border_para(doc, "8")

        doc.save(output_path)
        logger.info(f"Injected footer into {output_path}")
    except Exception as e:
        logger.error(f"Failed to inject footer: {e}", exc_info=True)


def _inject_page_number_to_docx(output_path: str, page_number_config: dict) -> None:
    """
    将页码写入文档页脚，使用 Word 域代码（{PAGE} / {NUMPAGES}）实现动态页码。

    GB/T 9704 标准：页码用四号宋体(14pt)，居中排列，
    格式为 - 1 - 或 第 1 页 共 N 页

    page_number_config 格式:
    {
        "enabled": true,
        "font": "宋体",
        "size": 14,
        "alignment": "center",
        "format": "- {PAGE} -"
    }
    """
    try:
        from docx import Document
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.shared import Pt

        # 兼容前端字段名差异：前端发送 show/position，后端期望 enabled/alignment
        enabled = page_number_config.get("enabled")
        if enabled is None:
            enabled = page_number_config.get("show", True)
        if not enabled:
            return

        fmt = page_number_config.get("format", "— {PAGE} —")
        font_name = page_number_config.get("font", "宋体")
        size_pt = page_number_config.get("size", 14)
        align = page_number_config.get("alignment")
        if not align:
            align = page_number_config.get("position", "center")
        # 归一化：前端"单右双左"发送 'right-left'，转为内部 'right'（奇数页右、偶数页左）
        if align == "right-left":
            align = "right"

        doc = Document(output_path)

        # ==== 启用奇偶页不同（文档级设置，必须放在 settings.xml 中）====
        is_odd_even = align in ("left", "right", "right-left")
        if is_odd_even:
            doc.settings.odd_and_even_pages_header_footer = True

        for section in doc.sections:
            # ==== SECTION A: 默认/奇数页 footer ====
            try:
                footer = section.footer
            except Exception:
                footer = None
            if footer is None:
                continue
            for p in list(footer.paragraphs):
                p._element.getparent().remove(p._element)
            para = footer.add_paragraph()
            pPr = para._element.get_or_add_pPr()
            align_map = {"center": "center", "left": "left", "right": "right"}
            jc = OxmlElement("w:jc")
            jc.set(qn("w:val"), align_map.get(align, "center"))
            pPr.append(jc)
            if is_odd_even:
                ind = OxmlElement("w:ind")
                if align == "right":
                    ind.set(qn("w:right"), str(int(14 * 20)))
                else:
                    ind.set(qn("w:left"), str(int(14 * 20)))
                pPr.append(ind)
            # 页脚距离
            try:
                bm = section.bottom_margin
                if bm:
                    bm_mm = bm / 36000
                    fd_mm = max(2, bm_mm - 7)
                    section.footer_distance = int(fd_mm * 36000)
                else:
                    section.footer_distance = Pt(22)
            except Exception:
                section.footer_distance = Pt(22)
            elems = _build_page_number_xml(fmt, font_name, size_pt)
            _apply_page_number_elements(para._element, elems)

        # ==== 保存文档（完成奇数页页脚） ====
        doc.save(output_path)

        # ==== SECTION B: 若需要奇偶页不同，直接修改 ZIP 添加偶数页页脚 ====
        if is_odd_even:
            _inject_even_page_footer_direct(output_path, fmt, font_name, size_pt)

        logger.info(f"Injected page number field into {output_path}")
    except Exception as e:
        logger.error(f"Failed to inject page number: {e}", exc_info=True)


def _inject_even_page_footer_direct(output_path: str, fmt: str, font_name: str, size_pt: int) -> None:
    """
    直接操作 ZIP 文件，添加偶数页页脚和 evenAndOddHeaders。

    完全绕过 python-docx，直接修改 OOXML 包结构：
    1. 在 sectPr 中添加 w:evenAndOddHeaders
    2. 添加偶数页 w:footerReference
    3. 创建 word/footer2.xml（左对齐+左空一字）
    4. 添加关系映射
    """
    import zipfile
    import io
    from lxml import etree

    even_ftr_xml = (
        '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:p><w:pPr>"
        '<w:jc w:val="left"/>'
        '<w:ind w:left="280"/>'
        "</w:pPr></w:p></w:ftr>"
    )
    even_ftr = etree.fromstring(even_ftr_xml.encode())
    even_p = even_ftr.find(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p")
    elems = _build_page_number_xml(fmt, font_name, size_pt)
    _apply_page_number_elements(even_p, elems)

    buf = io.BytesIO()
    with zipfile.ZipFile(output_path, "r") as zin:
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "word/document.xml":
                    root = etree.fromstring(data)
                    ns_w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
                    ns_r = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                    for sp in root.findall(".//{%s}sectPr" % ns_w):
                        # 偶数页 footerReference（不再加 evenAndOddHeaders 到 sectPr）
                        even_fr = etree.SubElement(sp, "{%s}footerReference" % ns_w)
                        even_fr.set("{%s}type" % ns_w, "even")
                        even_fr.set("{%s}id" % ns_r, "rIdFtrEven")
                        for i, child in enumerate(sp):
                            tag = child.tag.split("}")[1] if "}" in child.tag else child.tag
                            if tag == "footerReference" and child.get("{%s}type" % ns_w) == "default":
                                sp.remove(even_fr)
                                sp.insert(i + 1, even_fr)
                                break
                    zout.writestr(
                        item.filename, etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
                    )
                elif item.filename == "word/settings.xml":
                    # 在 settings.xml 中添加 evenAndOddHeaders（文档级设置）
                    root = etree.fromstring(data)
                    ns_w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
                    existing = root.find("{%s}evenAndOddHeaders" % ns_w)
                    if existing is None:
                        eo = etree.SubElement(root, "{%s}evenAndOddHeaders" % ns_w)
                        root.insert(0, eo)
                    zout.writestr(
                        item.filename, etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
                    )
                elif item.filename == "word/_rels/document.xml.rels":
                    rels = data.decode("utf-8")
                    if "rIdFtrEven" not in rels:
                        rels = rels.replace(
                            "</Relationships>",
                            '<Relationship Id="rIdFtrEven" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer2.xml"/></Relationships>',
                        )
                    zout.writestr(item.filename, rels.encode())
                else:
                    zout.writestr(item.filename, data)
            zout.writestr(
                "word/footer2.xml", etree.tostring(even_ftr, xml_declaration=True, encoding="UTF-8", standalone=True)
            )

    with open(output_path, "wb") as f:
        f.write(buf.getvalue())
    logger.info("Injected even page footer (direct ZIP method)")


def _add_page_run(para_elem, text: str, font_name: str, size_pt: int) -> None:
    """添加一个普通文本 run 到段落元素。"""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    run_el = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:eastAsia"), font_name)
    rFonts.set(qn("w:ascii"), "Times New Roman")
    rPr.append(rFonts)
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), str(size_pt * 2))
    rPr.append(sz)
    run_el.append(rPr)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    run_el.append(t)
    para_elem.append(run_el)


def _build_page_number_xml(fmt: str, font_name: str, size_pt: int) -> list:
    """
    构建页码域代码的 XML 元素列表。

    返回 [(tag, attrs, text), ...] 列表，由调用方直接 append 到段落。
    """
    import re

    elements = []
    remaining = fmt
    while remaining:
        m = re.search(r"\{PAGE\}|\{NUMPAGES\}", remaining)
        if not m:
            if remaining.strip():
                elements.append(("text", remaining, font_name, size_pt))
            break

        prefix = remaining[: m.start()]
        if prefix:
            elements.append(("text", prefix, font_name, size_pt))

        field_name = m.group()[1:-1]
        elements.append(("field", field_name, font_name, size_pt))
        remaining = remaining[m.end() :]

    return elements


def _apply_page_number_elements(para_elem, elements: list) -> None:
    """将 _build_page_number_xml 返回的元素列表写入段落 XML。"""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    for elem in elements:
        etype = elem[0]
        if etype == "text":
            _add_page_run(para_elem, elem[1], elem[2], elem[3])
        elif etype == "field":
            field_name = elem[1]
            font_name = elem[2]
            size_pt = elem[3]

            # fldChar begin
            r1 = OxmlElement("w:r")
            fc1 = OxmlElement("w:fldChar")
            fc1.set(qn("w:fldCharType"), "begin")
            r1.append(fc1)
            para_elem.append(r1)

            # instrText
            r2 = OxmlElement("w:r")
            rPr2 = OxmlElement("w:rPr")
            rf2 = OxmlElement("w:rFonts")
            rf2.set(qn("w:eastAsia"), font_name)
            rf2.set(qn("w:ascii"), "Times New Roman")
            rPr2.append(rf2)
            r2.append(rPr2)
            instr = OxmlElement("w:instrText")
            instr.set(qn("xml:space"), "preserve")
            instr.text = f" {field_name} "
            r2.append(instr)
            para_elem.append(r2)

            # fldChar separate
            r3 = OxmlElement("w:r")
            fc3 = OxmlElement("w:fldChar")
            fc3.set(qn("w:fldCharType"), "separate")
            r3.append(fc3)
            para_elem.append(r3)

            # 默认显示值
            r4 = OxmlElement("w:r")
            rPr4 = OxmlElement("w:rPr")
            rf4 = OxmlElement("w:rFonts")
            rf4.set(qn("w:eastAsia"), font_name)
            rf4.set(qn("w:ascii"), "Times New Roman")
            rPr4.append(rf4)
            sz4 = OxmlElement("w:sz")
            sz4.set(qn("w:val"), str(size_pt * 2))
            rPr4.append(sz4)
            r4.append(rPr4)
            t4 = OxmlElement("w:t")
            t4.set(qn("xml:space"), "preserve")
            t4.text = "1"
            r4.append(t4)
            para_elem.append(r4)

            # fldChar end
            r5 = OxmlElement("w:r")
            fc5 = OxmlElement("w:fldChar")
            fc5.set(qn("w:fldCharType"), "end")
            r5.append(fc5)
            para_elem.append(r5)
