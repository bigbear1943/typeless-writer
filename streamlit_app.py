"""
Typeless Writer - 無壓力碎片化創作工具
使用 Streamlit 開發的輕量版本
"""

import streamlit as st
import json
import os
from datetime import datetime
import google.generativeai as genai
from openai import OpenAI

# 設定頁面
st.set_page_config(
    page_title="Typeless Writer - 無壓力碎片化創作",
    page_icon="✍️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 資料儲存路徑
DATA_FILE = "typeless_data.json"

# ========== 資料管理 ==========
def load_data():
    """載入儲存的資料"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"projects": {}, "current_project": "", "settings": {"api_provider": "gemini", "api_key": ""}}

def save_data(data):
    """儲存資料"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_api_settings():
    """取得 API 設定，優先使用 Streamlit Secrets"""
    # 優先從 Streamlit Secrets 讀取
    if hasattr(st, 'secrets'):
        try:
            provider = st.secrets.get("API_PROVIDER", "gemini")
            key = st.secrets.get("API_KEY", "")
            if key:
                return provider, key, True  # True = 使用 Secrets
        except Exception:
            pass
    return None, None, False

# ========== AI 生成 ==========
SYSTEM_PROMPT = """你是一位專業的內容編輯與 SEO 專家。你的任務是將使用者提供的「碎片化靈感」整理成結構完整的文章和社群貼文。

請嚴格遵守以下規則：
1. **語氣保留**：輸出的文章必須保留使用者原始輸入的「口語感」與「個人風格」，僅做錯別字修正與過場連接，不可過度修飾成機器人語氣。
2. **SEO 文章結構**：
   - 必須包含一個 H1 主標題
   - 必須包含 2-4 個 H2 副標題
   - 段落要通順有邏輯
   - 控制在 800-1500 字左右
3. **社群貼文**：
   - 生成 4-6 篇短貼文
   - 適合 Facebook、Threads、Instagram
   - 每篇 100-200 字
   - 分段清晰，適合手機閱讀
   - 可以使用 emoji 增加吸引力

請以 JSON 格式回傳結果，格式如下：
{
  "article": {
    "title": "H1 主標題",
    "content": "完整的 Markdown 文章內容（包含 ## H2 標籤）"
  },
  "socialPosts": [
    {
      "platform": "Facebook",
      "content": "貼文內容"
    }
  ]
}"""

def generate_with_gemini(api_key: str, fragments: list, promotion: dict = None) -> dict:
    """使用 Gemini API 生成內容"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    user_message = build_user_message(fragments, promotion)
    full_prompt = f"{SYSTEM_PROMPT}\n\n{user_message}"
    
    response = model.generate_content(
        full_prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.7
        )
    )
    
    return json.loads(response.text)

def generate_with_openai(api_key: str, fragments: list, promotion: dict = None) -> dict:
    """使用 OpenAI API 生成內容"""
    client = OpenAI(api_key=api_key)
    
    user_message = build_user_message(fragments, promotion)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)

def build_user_message(fragments: list, promotion: dict = None) -> str:
    """建立使用者訊息"""
    message = "以下是我的靈感碎片，請幫我整理成文章和社群貼文：\n\n"
    
    for i, fragment in enumerate(fragments, 1):
        message += f"【碎片 {i}】\n{fragment['content']}\n\n"
    
    if promotion and promotion.get("link") and promotion.get("product_name"):
        message += f"\n---\n導購資訊：\n"
        message += f"產品/服務名稱：{promotion['product_name']}\n"
        message += f"推廣連結：{promotion['link']}\n"
        message += "請在社群貼文中自然地融入這個推廣連結。\n"
    
    return message

# ========== 自訂樣式 ==========
st.markdown("""
<style>
    /* 整體樣式 */
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    
    /* 標題樣式 */
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #10b981, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .subtitle {
        text-align: center;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    
    /* 碎片卡片 */
    .fragment-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }
    
    .fragment-time {
        color: #9ca3af;
        font-size: 0.75rem;
    }
    
    /* 生成結果 */
    .result-card {
        background: #f0fdf4;
        border: 1px solid #86efac;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    
    .social-post {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .platform-badge {
        background: #e5e7eb;
        color: #374151;
        padding: 0.25rem 0.5rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ========== 主程式 ==========
def main():
    # 載入資料
    if "data" not in st.session_state:
        st.session_state.data = load_data()
    
    data = st.session_state.data
    
    # 標題
    st.markdown('<h1 class="main-title">✍️ Typeless Writer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">無壓力的碎片化創作</p>', unsafe_allow_html=True)
    
    # 檢查是否有 Secrets 設定
    secrets_provider, secrets_key, using_secrets = get_api_settings()
    
    # 側邊欄設定
    with st.sidebar:
        st.header("⚙️ 設定")
        
        if using_secrets:
            # 使用 Secrets，顯示已連接狀態
            st.success("✅ 已連接雲端 API 設定")
            st.caption(f"使用 {secrets_provider.upper()} API")
            api_provider = secrets_provider
            api_key = secrets_key
        else:
            # 手動輸入模式
            api_provider = st.selectbox(
                "AI 服務提供商",
                ["gemini", "openai"],
                index=0 if data["settings"]["api_provider"] == "gemini" else 1,
                format_func=lambda x: "Google Gemini ✨" if x == "gemini" else "OpenAI 🤖"
            )
            
            api_key = st.text_input(
                "API Key",
                value=data["settings"]["api_key"],
                type="password",
                help="你的 API Key 只會儲存在本機"
            )
            
            if st.button("💾 儲存設定"):
                data["settings"]["api_provider"] = api_provider
                data["settings"]["api_key"] = api_key
                save_data(data)
                st.success("設定已儲存！")
    
    # 專案管理
    col1, col2 = st.columns([3, 1])
    
    with col1:
        project_list = list(data["projects"].keys())
        if project_list:
            current_project = st.selectbox(
                "選擇專案",
                project_list,
                index=project_list.index(data["current_project"]) if data["current_project"] in project_list else 0
            )
            data["current_project"] = current_project
        else:
            st.info("👆 請先建立一個新專案")
            current_project = None
    
    with col2:
        new_project = st.text_input("新專案名稱", placeholder="輸入名稱...")
        if st.button("➕ 建立", use_container_width=True):
            if new_project.strip():
                data["projects"][new_project.strip()] = {"fragments": []}
                data["current_project"] = new_project.strip()
                save_data(data)
                st.rerun()
    
    if not current_project:
        return
    
    st.divider()
    
    # 模式切換
    mode = st.radio(
        "模式",
        ["✏️ 捕捉靈感", "🚀 AI 轉換"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # ========== 捕捉靈感模式 ==========
    if mode == "✏️ 捕捉靈感":
        # 初始化輸入框狀態
        if "fragment_input" not in st.session_state:
            st.session_state.fragment_input = ""
        
        # 輸入區
        new_fragment = st.text_area(
            "記錄你的靈感碎片...",
            value=st.session_state.fragment_input,
            height=120,
            placeholder="在這裡輸入任何想法、句子、關鍵詞...",
            label_visibility="collapsed",
            key="fragment_text_area"
        )
        
        if st.button("📝 加入碎片", use_container_width=True, type="primary"):
            if new_fragment.strip():
                fragment = {
                    "content": new_fragment.strip(),
                    "created_at": datetime.now().isoformat()
                }
                data["projects"][current_project]["fragments"].insert(0, fragment)
                save_data(data)
                # 清空輸入框
                st.session_state.fragment_input = ""
                st.rerun()
        
        st.divider()
        
        # 碎片列表
        fragments = data["projects"][current_project]["fragments"]
        
        if fragments:
            st.caption(f"📚 已收集 {len(fragments)} 個靈感碎片")
            
            for i, fragment in enumerate(fragments):
                with st.container():
                    col1, col2 = st.columns([10, 1])
                    
                    with col1:
                        st.markdown(f"**{fragment['content']}**")
                        created = datetime.fromisoformat(fragment["created_at"])
                        st.caption(f"🕐 {created.strftime('%m/%d %H:%M')}")
                    
                    with col2:
                        if st.button("🗑️", key=f"del_{i}"):
                            data["projects"][current_project]["fragments"].pop(i)
                            save_data(data)
                            st.rerun()
                    
                    st.divider()
        else:
            st.info("💡 開始記錄你的靈感吧！每一個小碎片都可能成為精彩文章的一部分。")
    
    # ========== AI 轉換模式 ==========
    else:
        fragments = data["projects"][current_project]["fragments"]
        
        if not fragments:
            st.warning("⚠️ 請先在「捕捉靈感」模式中加入一些碎片")
            return
        
        # 導購整合
        with st.expander("🔗 導購整合（選填）"):
            promo_col1, promo_col2 = st.columns(2)
            with promo_col1:
                product_name = st.text_input("產品/服務名稱", placeholder="例如：Typeless Pro")
            with promo_col2:
                promo_link = st.text_input("推廣連結", placeholder="https://...")
        
        # 顯示碎片摘要
        st.info(f"📦 將 {len(fragments)} 個碎片轉換為精彩內容")
        
        with st.expander("預覽碎片內容"):
            for i, f in enumerate(fragments, 1):
                st.write(f"**{i}.** {f['content'][:100]}{'...' if len(f['content']) > 100 else ''}")
        
        # 生成按鈕
        if not using_secrets and not data["settings"]["api_key"]:
            st.error("⚠️ 請先在側邊欄設定中輸入 API Key")
            return
        
        if st.button("✨ 生成文章與貼文", use_container_width=True, type="primary"):
            promotion = None
            if product_name and promo_link:
                promotion = {"product_name": product_name, "link": promo_link}
            
            with st.spinner("🤖 AI 正在創作中..."):
                try:
                    if data["settings"]["api_provider"] == "gemini":
                        result = generate_with_gemini(
                            data["settings"]["api_key"],
                            fragments,
                            promotion
                        )
                    else:
                        result = generate_with_openai(
                            data["settings"]["api_key"],
                            fragments,
                            promotion
                        )
                    
                    st.session_state.result = result
                    
                except Exception as e:
                    st.error(f"❌ 生成失敗：{str(e)}")
        
        # 顯示結果
        if "result" in st.session_state:
            result = st.session_state.result
            
            st.divider()
            
            # SEO 文章
            st.subheader("📝 SEO 文章")
            
            article_content = f"# {result['article']['title']}\n\n{result['article']['content']}"
            st.markdown(article_content)
            
            st.code(article_content, language="markdown")
            
            st.divider()
            
            # 社群貼文
            st.subheader("📱 社群貼文")
            
            cols = st.columns(2)
            for i, post in enumerate(result.get("socialPosts", [])):
                with cols[i % 2]:
                    with st.container():
                        st.markdown(f"**{post['platform']}**")
                        st.write(post["content"])
                        st.code(post["content"], language=None)
                        st.divider()

if __name__ == "__main__":
    main()
