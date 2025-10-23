from nonebot import get_plugin_config, logger, on_regex
from nonebot.plugin import PluginMetadata
from nonebot.params import RegexStr
import httpx
import re

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="[ 缩写翻译 ] 能不能好好说话 - nbnhhsh",
    description="能不能好好说话 - 使用神奇海螺api查询 @qingzhixing",
    usage="[缩写英文]是什么|是啥",
    config=Config,
    type="application",
    homepage="https://github.com/qingzhixing/nonebot-plugin-nbnhhsh-q",
    supported_adapters=None,
)

# 输出插件加载日志
logger.info("插件 nbnhhsh 已加载")

regular_expression = r"[a-z0-9]{2,}(?:是什么|是啥)"

config = get_plugin_config(Config)

nbnhhsh_macher = on_regex(
    regular_expression, priority=5, block=True, flags=re.IGNORECASE
)


@nbnhhsh_macher.handle()
async def handle_nbnhhsh(keyword: str = RegexStr()):
    logger.debug(f"原始 keywordGroup: {keyword}")

    keyword_string = keyword.replace("是什么", "").replace("是啥", "")
    logger.debug(f"nbnhhsh keyword: {keyword_string}")
    # 调用神奇海螺api查询
    result_dict = await query_nbnhhsh(keyword_string)

    # 发送查询结果
    if result_dict and "name" in result_dict:

        reply_string = f"{keyword_string} 可能是:\n"
        if "trans" in result_dict and result_dict["trans"]:

            results = result_dict["trans"]
            if len(results) == 1:
                reply_string += results[0]
            else:
                reply_string += "\n".join(results[:-1]) + "，" + results[-1]

        else:
            reply_string = f"没能找到 {keyword_string} 的含义"

    else:
        reply_string = f"没能找到 {keyword_string} 的含义"
    await nbnhhsh_macher.send(reply_string)


NBNHHSH_API_URL = "https://lab.magiconch.com/api/nbnhhsh/"

query_buffer = {}


async def query_nbnhhsh(keyword: str) -> dict:
    global query_buffer

    if len(query_buffer) > 1024:
        query_buffer = {}

    if not keyword:
        return {}

    if query_buffer.get(keyword):
        logger.debug(f"使用缓存结果: {query_buffer[keyword]}")
        return query_buffer[keyword]

    try:
        # 发送POST请求
        async with httpx.AsyncClient() as client:
            response = await client.post(
                NBNHHSH_API_URL + "guess",
                json={"text": keyword},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            # 解析响应
            data = response.json()
            if data and len(data) > 0:
                query_buffer[keyword] = data[0]
                return data[0]
            else:
                return {}

    except httpx._exceptions.RequestError as e:
        logger.error(f"请求出错: {e}")
        return {}
