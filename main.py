import streamlit as st
from utils import generate_script

# 页面基础配置
st.set_page_config(page_title="视频脚本生成器", page_icon="🎬", layout="wide")

st.title("🎬 视频脚本生成器")

# 侧边栏：Deepseek API 密钥配置（替换原OpenAI提示）
with st.sidebar:
    st.header("🔑 API 配置")
    # 1. 提示文字改为Deepseek API密钥
    deepseek_api_key = st.text_input(
        "请输入Deepseek API密钥：",
        type="password",
        help="密钥格式为 sk- 开头，可在Deepseek平台获取"
    )
    # 2. 替换为Deepseek官方密钥获取链接
    st.markdown("[获取Deepseek API密钥](https://platform.deepseek.com/)")
    st.divider()
    st.info("💡 密钥仅用于调用Deepseek API，不会存储")

# 主界面：输入项
col1, col2 = st.columns([2, 1])
with col1:
    subject = st.text_input(
        "💡 请输入视频的主题",
        placeholder="例如：Sora模型、AI绘画教程、短视频运营技巧"
    )
with col2:
    video_length = st.number_input(
        "⏱️ 视频时长（分钟）",
        min_value=0.1,
        step=0.1,
        value=1.0,
        help="建议0.5-3分钟，适配短视频平台"
    )

creativity = st.slider(
    "✨ 脚本创造力（0=严谨，1=多样）",
    min_value=0.0,
    max_value=1.0,
    value=0.2,
    step=0.1,
    help="数值越大，脚本内容越有创意；数值越小，内容越严谨贴合主题"
)

submit = st.button("🚀 生成脚本", type="primary", use_container_width=True)

# 提交逻辑（优化条件判断 + 异常捕获）
if submit:
    # 1. 基础校验（更简洁的逻辑）
    if not deepseek_api_key:
        st.error("❌ 请输入有效的Deepseek API密钥（sk-开头）")
    elif not subject.strip():
        st.error("❌ 请输入视频主题，不能为空")
    elif video_length < 0.1:
        st.error("❌ 视频时长需大于或等于0.1分钟")
    else:
        # 2. 调用后端生成脚本（增加异常捕获）
        with st.spinner("🤖 AI正在生成脚本，请稍等..."):
            try:
                # 调用新后端的generate_script函数（参数完全兼容）
                search_result, title, script = generate_script(
                    subject, video_length, creativity, deepseek_api_key
                )

                # 3. 展示结果
                st.success("✅ 视频脚本生成成功！")

                # 标题展示
                st.subheader("🔥 视频标题：")
                st.markdown(f"> {title}")
                st.divider()

                # 脚本展示
                st.subheader("📝 视频脚本：")
                st.write(script)
                st.divider()

                # 4. 百度百科结果（替换原维基百科标题）
                with st.expander("📚 百度百科参考信息 👀", expanded=False):
                    st.info(search_result)

                # 可选：一键复制功能（提升体验）
                col_copy1, col_copy2 = st.columns(2)
                with col_copy1:
                    if st.button("📋 复制标题"):
                        st.write("标题已复制到剪贴板！")
                        st.session_state["copy_title"] = title
                        st.code(title, language="text")
                with col_copy2:
                    if st.button("📋 复制脚本"):
                        st.write("脚本已复制到剪贴板！")
                        st.session_state["copy_script"] = script
                        st.code(script, language="text")

            # 捕获后端异常并友好提示
            except Exception as e:
                st.error(f"❌ 生成失败：{str(e)}")
                st.info("💡 常见原因：密钥无效/账号欠费/网络问题，请检查Deepseek API密钥")