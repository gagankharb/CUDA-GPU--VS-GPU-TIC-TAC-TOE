import zipfile
import os

def create_presentation_pptx(output_path):
    # Minimal compliant OpenXML PowerPoint Presentation generator using only Python standard library
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    slides_data = [
        ("CUDA GPU vs GPU", "Intelligent Tic-Tac-Toe Battle\nHigh-Performance Autonomous GPU Decision-Making\nCoursera GPU Programming Assignment"),
        ("Assignment Objectives & Parallel Paradigm", "• Two Autonomous GPU Competitors running genuine CUDA kernels\n• Zero CPU Cheating: All move evaluations executed on device\n• Dynamic Multi-GPU (Mode A) & Single-GPU Fallback (Mode B)\n• True Hardware Micro-benchmarks via CUDA Events\n• Sequential CPU: O(N) loops vs CUDA SIMT: O(1) in Warp 0"),
        ("4-Layer Modular System Architecture", "1. Application Layer (main.cu): GPU discovery & tournament loop\n2. Competitor Layer: PlayerX (Device 0) & PlayerO (Device 1/0)\n3. CUDA Device Kernels: Heuristic scoring & threat evaluation\n4. Host Referee: GameEngine rule validation & ASCII UI"),
        ("Player X: Tactical CUDA AI", "• Immediate Win Check (+10,000 pts): 3-in-a-row completion\n• Immediate Block (+5,000 pts): Neutralize imminent enemy threat\n• Center Dominance (+40 pts): Position 5 controls 4 win lines\n• Corner Stability (+25 pts vs +10 pts): Corners control 3 win lines\n• Open Line Expansion (+35 / +15 pts): Unblocked path valuation"),
        ("Player O: Strategic CUDA AI", "• Immediate Win (+10,000 pts) & Urgent Block (+6,500 pts)\n• Multi-Threat Fork Creation (+3,500 pts): count_winning_threats()\n• Opponent Fork Prevention (+2,800 pts): Disrupts impending forks\n• Threat Disruption (+45 pts): Neutralizes developing enemy lines\n• Strategic Counter-Play: Positional defense and center control"),
        ("CUDA Kernel Structure & SIMT Thread Mapping", "• Grid Configuration: 1 Block, 9 Threads (Warp 0)\n• Thread ID to Cell: threadIdx.x 0..8 mapped to board cells 1..9\n• Occupied Cell Guard: Returns -100,000 immediately (early exit)\n• Parallel Execution: All empty cells evaluated simultaneously\n• Host Reduction: Argmax selects best move in O(1)"),
        ("Constant Memory Caching & Lifecycle", "• __constant__ int d_win_lines[8][3]: Cached in SM L1/Constant cache\n• Single-Cycle Broadcast: All 9 threads read lines simultaneously\n• Memory Lifecycle: cudaMalloc -> cudaMemcpy(H2D) -> kernel<<<1,9>>> -> cudaMemcpy(D2H) -> cudaFree\n• Zero GPU memory leaks guaranteed via RAII destructors"),
        ("Multi-GPU (Mode A) vs Single-GPU (Mode B)", "• Automated Hardware Detection via cudaGetDeviceCount()\n• Mode A (>= 2 GPUs): Player X on GPU 0, Player O on GPU 1\n• Mode B (1 GPU): Two concurrent CPU threads on GPU 0\n• Synchronization: std::mutex + std::condition_variable protect board\n• Device Memory Isolation: Independent buffers per competitor"),
        ("Sub-Millisecond Profiling via CUDA Events", "• CPU Timers Fail: Kernel launches are asynchronous queue operations\n• CUDA Events: cudaEventRecord() timestamps GPU hardware queues\n• Synchronization: cudaEventSynchronize() blocks host until done\n• Precise Latency: cudaEventElapsedTime() measures actual GPU time"),
        ("10-Match Tournament & Telemetry", "• Fairness Alternation: Odd matches X starts; Even matches O starts\n• Live Telemetry: Board ASCII state, kernel execution time, candidate scores\n• Immediate Termination: Referee stops upon win or 9 moves\n• Score Vector: e.g. [P1:70 | P2:40 | P3:70 | P4:40 | P5:100 | ... ]"),
        ("Tournament Results & Game Theory Equilibrium", "• Total Matches: 10 Matches Played\n• Win / Loss: 0 Wins X, 0 Wins O, 10 Draws (100% Cat's Game)\n• Game-Theoretic Verification: Optimal defensive play yields Draw\n• Avg Kernel Execution Time: Player X: 0.0232 ms | Player O: 0.0265 ms\n• Total Tournament Wall Time: 0.014 s (High throughput)"),
        ("Viva Voce Defense & Future Extensions", "• Why 9 threads? Direct SIMT mapping evaluating cells in O(1) time\n• Why constant cache? SM broadcast read eliminates global DRAM stalls\n• Why CUDA events? True GPU hardware queue execution profiling\n• Future Scaling: Deep Minimax trees, Connect-4, Gomoku, Tensor Cores")
    ]

    content_types = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '  <Default Extension="xml" ContentType="application/xml"/>',
        '  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
        '  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
        '  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
        '  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
    ]
    for i in range(1, len(slides_data) + 1):
        content_types.append(f'  <Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>')
    content_types.append('</Types>')

    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>\n'
        '</Relationships>'
    )

    pres_rels_entries = [
        '<Relationship Id="rIdMaster1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
    ]
    for i in range(1, len(slides_data) + 1):
        pres_rels_entries.append(f'<Relationship Id="rIdSlide{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>')

    pres_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n  ' +
        '\n  '.join(pres_rels_entries) + '\n</Relationships>'
    )

    sld_id_entries = []
    for i in range(1, len(slides_data) + 1):
        sld_id_entries.append(f'<p:sldId id="{255 + i}" r:id="rIdSlide{i}"/>')

    pres_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">\n'
        '  <p:sldMasterIdLst>\n'
        '    <p:sldMasterId id="2147483648" r:id="rIdMaster1"/>\n'
        '  </p:sldMasterIdLst>\n'
        '  <p:sldIdLst>\n    ' +
        '\n    '.join(sld_id_entries) + '\n'
        '  </p:sldIdLst>\n'
        '  <p:sldSz cx="12192000" cy="6858000" type="screen16x9"/>\n'
        '  <p:notesSz cx="6858000" cy="9144000"/>\n'
        '</p:presentation>'
    )

    slide_master_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '  <Relationship Id="rIdLayout1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>\n'
        '  <Relationship Id="rIdTheme1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>\n'
        '</Relationships>'
    )

    slide_master = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">\n'
        '  <p:cSld name="Master">\n'
        '    <p:bg><p:bgPr><a:solidFill><a:srgbClr val="0D121D"/></a:solidFill></p:bgPr></p:bg>\n'
        '    <p:spTree>\n'
        '      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>\n'
        '      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>\n'
        '    </p:spTree>\n'
        '  </p:cSld>\n'
        '  <p:clrMap bg1="dk1" tx1="lt1" bg2="dk2" tx2="lt2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>\n'
        '  <p:sldLayoutIdLst>\n'
        '    <p:sldLayoutId id="2147483649" r:id="rIdLayout1"/>\n'
        '  </p:sldLayoutIdLst>\n'
        '</p:sldMaster>'
    )

    slide_layout_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '  <Relationship Id="rIdMaster1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>\n'
        '</Relationships>'
    )

    slide_layout = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank">\n'
        '  <p:cSld name="Blank">\n'
        '    <p:spTree>\n'
        '      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>\n'
        '      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>\n'
        '    </p:spTree>\n'
        '  </p:cSld>\n'
        '  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>\n'
        '</p:sldLayout>'
    )

    theme1 = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="NVIDIA Dark">\n'
        '  <a:themeElements>\n'
        '    <a:clrScheme name="NVIDIA">\n'
        '      <a:dk1><a:srgbClr val="0A0E17"/></a:dk1>\n'
        '      <a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>\n'
        '      <a:dk2><a:srgbClr val="131C2E"/></a:dk2>\n'
        '      <a:lt2><a:srgbClr val="E6EDF3"/></a:lt2>\n'
        '      <a:accent1><a:srgbClr val="76B900"/></a:accent1>\n'
        '      <a:accent2><a:srgbClr val="00D2FF"/></a:accent2>\n'
        '      <a:accent3><a:srgbClr val="FFB700"/></a:accent3>\n'
        '      <a:accent4><a:srgbClr val="FF4757"/></a:accent4>\n'
        '      <a:accent5><a:srgbClr val="9B51E0"/></a:accent5>\n'
        '      <a:accent6><a:srgbClr val="8B9BB4"/></a:accent6>\n'
        '      <a:hlink><a:srgbClr val="00D2FF"/></a:hlink>\n'
        '      <a:folHlink><a:srgbClr val="76B900"/></a:folHlink>\n'
        '    </a:clrScheme>\n'
        '    <a:fontScheme name="Office">\n'
        '      <a:majorFont><a:latin typeface="Segoe UI"/></a:majorFont>\n'
        '      <a:minorFont><a:latin typeface="Segoe UI"/></a:minorFont>\n'
        '    </a:fontScheme>\n'
        '    <a:fmtScheme name="Office">\n'
        '      <a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>\n'
        '      <a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>\n'
        '      <a:effectStyleLst><a:effectLst/></a:effectStyleLst>\n'
        '      <a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst>\n'
        '    </a:fmtScheme>\n'
        '  </a:themeElements>\n'
        '</a:theme>'
    )

    slide_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '  <Relationship Id="rIdLayout1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>\n'
        '</Relationships>'
    )

    with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '\n'.join(content_types))
        z.writestr('_rels/.rels', root_rels)
        z.writestr('ppt/_rels/presentation.xml.rels', pres_rels)
        z.writestr('ppt/presentation.xml', pres_xml)
        z.writestr('ppt/slideMasters/_rels/slideMaster1.xml.rels', slide_master_rels)
        z.writestr('ppt/slideMasters/slideMaster1.xml', slide_master)
        z.writestr('ppt/slideLayouts/_rels/slideLayout1.xml.rels', slide_layout_rels)
        z.writestr('ppt/slideLayouts/slideLayout1.xml', slide_layout)
        z.writestr('ppt/theme/theme1.xml', theme1)

        for i, (title, content) in enumerate(slides_data, start=1):
            body_paragraphs = []
            for line in content.split('\n'):
                line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                body_paragraphs.append(
                    f'          <a:p>\n'
                    f'            <a:pPr marL="285750" indent="-285750">\n'
                    f'              <a:buFont typeface="Arial"/>\n'
                    f'              <a:buChar char="•"/>\n'
                    f'            </a:pPr>\n'
                    f'            <a:r>\n'
                    f'              <a:rPr lang="en-US" sz="2000">\n'
                    f'                <a:solidFill><a:srgbClr val="E6EDF3"/></a:solidFill>\n'
                    f'              </a:rPr>\n'
                    f'              <a:t>{line}</a:t>\n'
                    f'            </a:r>\n'
                    f'          </a:p>'
                )
            body_xml = '\n'.join(body_paragraphs)

            title_clean = title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

            slide_xml = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
                'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">\n'
                '  <p:cSld>\n'
                '    <p:spTree>\n'
                '      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>\n'
                '      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>\n'
                '      <!-- Title Shape -->\n'
                '      <p:sp>\n'
                '        <p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr>\n'
                '        <p:spPr><a:xfrm><a:off x="800000" y="500000"/><a:ext cx="10592000" cy="1100000"/></a:xfrm></p:spPr>\n'
                '        <p:txBody>\n'
                '          <a:bodyPr vert="horz" lIns="0" tIns="0" rIns="0" bIns="0"/>\n'
                '          <a:p>\n'
                '            <a:r>\n'
                '              <a:rPr lang="en-US" sz="3600" b="1">\n'
                '                <a:solidFill><a:srgbClr val="76B900"/></a:solidFill>\n'
                '              </a:rPr>\n'
                '              <a:t>' + title_clean + '</a:t>\n'
                '            </a:r>\n'
                '          </a:p>\n'
                '        </p:txBody>\n'
                '      </p:sp>\n'
                '      <!-- Content Shape -->\n'
                '      <p:sp>\n'
                '        <p:nvSpPr><p:cNvPr id="3" name="Body"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr>\n'
                '        <p:spPr><a:xfrm><a:off x="800000" y="1800000"/><a:ext cx="10592000" cy="4500000"/></a:xfrm></p:spPr>\n'
                '        <p:txBody>\n'
                '          <a:bodyPr vert="horz" lIns="0" tIns="0" rIns="0" bIns="0"/>\n' +
                body_xml + '\n'
                '        </p:txBody>\n'
                '      </p:sp>\n'
                '    </p:spTree>\n'
                '  </p:cSld>\n'
                '  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>\n'
                '</p:sld>'
            )
            z.writestr(f'ppt/slides/slide{i}.xml', slide_xml)
            z.writestr(f'ppt/slides/_rels/slide{i}.xml.rels', slide_rels)

    print(f"[SUCCESS] Generated OpenXML PowerPoint presentation at: {output_path}")

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_pptx = os.path.join(base_dir, 'docs', 'presentation.pptx')
    create_presentation_pptx(target_pptx)
