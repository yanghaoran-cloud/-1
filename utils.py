# 仅保留必要依赖：openai（调用Deepseek）、requests（百度百科）、urllib（URL编码）
import openai
import requests
from urllib.parse import quote

# 百度百科搜索实现（替换原WikipediaAPIWrapper）
def baidu_baike_search(query):
    """
    调用百度百科开放接口获取主题信息，国内可直接访问
    :param query: 搜索关键词
    :return: 格式化的百科文本（和原维基百科返回格式兼容）
    """
    try:
        # 百度百科简易开放接口（非商用友好）
        api_url = f"https://baike.baidu.com/api/openapi/BaikeLemmaCardApi?bk_key={quote(query)}&bk_length=800"
        # 强制关闭代理，避免网络干扰，设置超时
        response = requests.get(
            api_url,
            timeout=15,
            proxies={"http": None, "https": None}
        )
        response.raise_for_status()  # 抛出HTTP错误
        data = response.json()

        # 格式化返回结果（贴近原维基百科的文本格式）
        if data.get("errno") == 0 and data.get("data"):
            lemma = data["data"][0] if len(data["data"]) > 0 else {}
            result_lines = []
            if lemma.get("title"):
                result_lines.append(f"【标题】：{lemma['title']}")
            if lemma.get("summary"):
                result_lines.append(f"【摘要】：{lemma['summary']}")
            if lemma.get("desc"):
                result_lines.append(f"【简介】：{lemma['desc']}")
            return "\n".join(result_lines) if result_lines else f"未查询到「{query}」的百度百科信息"
        else:
            return f"未查询到「{query}」的百度百科信息"
    except Exception as e:
        # 异常时返回友好提示，不中断脚本生成
        return f"百度百科查询异常：{str(e)}（将基于通用知识生成脚本）"

# 核心函数：生成视频脚本（完全移除LangChain，纯OpenAI库实现）
def generate_script(subject, video_length, creativity, api_key):
    """
    生成视频脚本（和原函数参数/返回值完全一致，兼容前端调用）
    :param subject: 视频主题
    :param video_length: 视频时长（分钟）
    :param creativity: 创造力（0-1）
    :param api_key: Deepseek API密钥（sk-开头）
    :return: search_result（百科信息）, title（视频标题）, script（视频脚本）
    """
    # 1. 配置Deepseek API（兼容OpenAI接口）
    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",  # Deepseek官方base_url
        timeout=30  # 超时设置
    )

    # 2. 生成视频标题（替换原LangChain的title_chain）
    title_prompt = f"请为'{subject}'这个主题的视频想一个吸引人的标题"
    try:
        title_response = client.chat.completions.create(
            model="deepseek-chat",  # Deepseek官方模型名
            messages=[{"role": "user", "content": title_prompt}],
            temperature=creativity,
            max_tokens=100  # 标题长度限制
        )
        title = title_response.choices[0].message.content.strip()
    except Exception as e:
        error_msg = str(e).lower()
        if "401" in error_msg or "authentication" in error_msg:
            raise Exception("API密钥认证失败：请检查密钥是否有效、是否以sk-开头")
        else:
            raise Exception(f"标题生成失败：{str(e)}")

    # 3. 百度百科搜索（替换原WikipediaAPIWrapper）
    search_result = baidu_baike_search(subject)

    # 4. 生成视频脚本（替换原LangChain的script_chain）
    script_prompt = f"""你是一位短视频频道的博主。根据以下标题和相关信息，为短视频频道写一个视频脚本。
    视频标题：{title}，视频时长：{video_length}分钟，生成的脚本的长度尽量遵循视频时长的要求。
    要求开头抓住眼球，中间提供干货内容，结尾有惊喜，脚本格式也请按照【开头、中间，结尾】分隔。
    整体内容的表达方式要尽量轻松有趣，吸引年轻人。
    脚本内容可以结合以下参考信息，但仅作为参考，只结合相关的即可，对不相关的进行忽略：
    ```{search_result}```"""

    try:
        script_response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": script_prompt}],
            temperature=creativity,
            max_tokens=2000  # 脚本长度限制
        )
        script = script_response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"脚本生成失败：{str(e)}")

    # 保持原返回值格式：search_result, title, script
    return search_result, title, script
