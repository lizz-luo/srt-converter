import streamlit as st
import re

st.set_page_config(page_title="SRT 字幕處理工具", layout="wide")
st.title("SRT 字幕處理工具")

# 建立兩個分頁
tab1, tab2 = st.tabs(["提取文本", "導入字幕"])

# 分頁 1：提取文本
with tab1:
    st.header("從 SRT 提取序號與文字")
    st.markdown("將完整的 SRT 內容貼在下方，系統會自動去除時間軸，並輸出以 Tab 鍵分隔的序號與文字。")
    
    srt_input = st.text_area("請在此貼上原始 SRT 內容：", height=250, key="extract_in")
    
    if st.button("提取", key="btn_extract"):
        if srt_input:
            # 支援以連續換行符號切割 SRT 區塊
            blocks = re.split(r'\n\s*\n', srt_input.strip())
            result_lines = []
            
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    idx = lines[0].strip()
                    # 跳過第二行的時間軸，提取後面的文字並用空格合併（以防原字幕有多行）
                    text = " ".join([line.strip() for line in lines[2:]])
                    result_lines.append(f"{idx}\t{text}")
            
            result_text = "\n".join(result_lines)
            st.text_area("提取結果（可直接複製並貼上至 Word/Excel）：", value=result_text, height=250)
            st.success("提取完成！")

# 分頁 2：導入字幕
with tab2:
    st.header("將修改後的文字導入 SRT")
    st.markdown("請提供原始的 SRT 以便保留時間軸，並貼上修改後的文字（支援從 Excel/Word 直接複製的 Tab 分隔格式）。")
    
    col1, col2 = st.columns(2)
    with col1:
        srt_original = st.text_area("A. 原始 SRT 文本：", height=250, key="import_srt")
    with col2:
        modified_text = st.text_area("B. 修改後的文字（包含序號與文字）：", height=250, key="import_mod")
        
    if st.button("合併並生成新 SRT", key="btn_import"):
        if srt_original and modified_text:
            mod_dict = {}
            
            # 解析修改後的文字
            # 優先判斷是否包含 Tab（適用於從 Excel/Word 複製的情境）
            if '\t' in modified_text:
                for line in modified_text.strip().split('\n'):
                    if '\t' in line:
                        parts = line.split('\t', 1)
                        mod_dict[parts[0].strip()] = parts[1].strip()
            else:
                # 兼容序號與文字分行顯示的情境
                lines = modified_text.strip().split('\n')
                idx = None
                for line in lines:
                    line = line.strip()
                    if line.isdigit():
                        idx = line
                    elif idx and line:
                        mod_dict[idx] = line
                        idx = None

            # 解析原始 SRT 並進行文字替換
            blocks = re.split(r'\n\s*\n', srt_original.strip())
            new_srt_blocks = []
            
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    idx = lines[0].strip()
                    timestamp = lines[1].strip()
                    
                    # 如果在修改名單中有找到該序號，則替換成新文字；否則保留原樣
                    new_text = mod_dict.get(idx, "\n".join(lines[2:]))
                    new_srt_blocks.append(f"{idx}\n{timestamp}\n{new_text}")
            
            final_srt = "\n\n".join(new_srt_blocks)
            
            st.success("字幕替換成功！你可以複製下方內容或直接下載檔案。")
            st.text_area("最終生成的 SRT 內容：", value=final_srt, height=250)
            
            # 提供下載按鈕
            st.download_button(
                label="📥 下載為 .srt 檔案",
                data=final_srt,
                file_name="modified_subtitles.srt",
                mime="text/plain"
            )
