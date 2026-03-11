import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="SRT 字幕處理工具", page_icon="🎬", layout="wide")
st.title("🎬 SRT 字幕處理工具")

# 建立兩個分頁
tab1, tab2 = st.tabs(["✂️ 提取文本", "🔄 導入字幕"])

# ==========================================
# 分頁 1：提取文本
# ==========================================
with tab1:
    st.header("✂️ 從 SRT 提取序號與文字")
    st.markdown("📝 將完整的 SRT 內容貼在下方，系統會自動去除時間軸，並生成表格供下載。")
    
    # 支援容納 5000+ 行，設定高度為 400
    srt_input = st.text_area("📥 請在此貼上原始 SRT 內容：", height=400, key="extract_in")
    
    if st.button("🚀 提取數據", key="btn_extract"):
        if srt_input:
            blocks = re.split(r'\n\s*\n', srt_input.strip())
            data_list = []
            
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    idx = lines[0].strip()
                    # 跳過第二行的時間軸，提取後面的文字並合併
                    text = " ".join([line.strip() for line in lines[2:]])
                    data_list.append({"序號": idx, "文本": text})
            
            if data_list:
                df = pd.DataFrame(data_list)
                st.success(f"✅ 成功提取 {len(df)} 筆數據！")
                
                # 顯示表格
                st.markdown("### 📊 提取結果預覽")
                st.dataframe(df, use_container_width=True)
                
                # 下載按鈕 (編碼設為 utf-8-sig 以完美相容 Windows Excel)
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 下載為 Excel 相容格式 (CSV)",
                    data=csv,
                    file_name="extracted_subtitles.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ 無法解析輸入的內容，請確認是否為標準 SRT 格式。")

# ==========================================
# 分頁 2：導入字幕
# ==========================================
with tab2:
    st.header("🔄 將修改後的文字導入 SRT")
    st.markdown("📋 請貼上修改後的文字與原始 SRT，系統會將新文字套入原有的時間軸中。")
    
    col1, col2 = st.columns(2)
    # A 和 B 對調：左邊為修改後的文字，右邊為原始 SRT
    with col1:
        modified_text = st.text_area("A. 📝 修改後的文字（請貼上序號與文字）：", height=400, key="import_mod")
    with col2:
        srt_original = st.text_area("B. ⏱️ 原始 SRT 文本（用於保留時間軸）：", height=400, key="import_srt")
        
    if st.button("✨ 合併並生成新 SRT", key="btn_import"):
        if srt_original and modified_text:
            mod_dict = {}
            
            # 支援包含 Tab 的複製格式或直接分行顯示的格式
            if '\t' in modified_text:
                for line in modified_text.strip().split('\n'):
                    if '\t' in line:
                        parts = line.split('\t', 1)
                        mod_dict[parts[0].strip()] = parts[1].strip()
            else:
                lines = modified_text.strip().split('\n')
                idx = None
                for line in lines:
                    line = line.strip()
                    if line.isdigit():
                        idx = line
                    elif idx and line:
                        mod_dict[idx] = line
                        idx = None

            blocks = re.split(r'\n\s*\n', srt_original.strip())
            new_srt_blocks = []
            
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    idx = lines[0].strip()
                    timestamp = lines[1].strip()
                    
                    new_text = mod_dict.get(idx, "\n".join(lines[2:]))
                    new_srt_blocks.append(f"{idx}\n{timestamp}\n{new_text}")
            
            final_srt = "\n\n".join(new_srt_blocks)
            
            st.success("🎉 字幕替換成功！")
            st.text_area("📄 最終生成的 SRT 內容預覽：", value=final_srt, height=300)
            
            st.download_button(
                label="📥 下載為 .srt 檔案",
                data=final_srt,
                file_name="modified_subtitles.srt",
                mime="text/plain"
            )
