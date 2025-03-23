import json
import re
from typing import Any, Dict, Type

from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import BaseOutputParser

# from langchain_core.utils.json import parse_and_check_json_markdown


def parse_and_check_json_markdown(text: str,expected_keys) -> dict:
    # 尝试解析JSON
    try:
        # 清理字符串，移除可能的markdown代码块标记
        json_str = text.strip()
        markdown_match = re.search(r"```(json)?(.*)", json_str, re.DOTALL)
        json_str = json_str if markdown_match is None else markdown_match.group(2)
        # 尝试标准解析
        try:
            json_obj = json.loads(json_str)
        except json.JSONDecodeError:
            # 尝试修复不完整的JSON
            json_obj = _parse_partial_json(json_str)
        return json_obj
    except json.JSONDecodeError as e:
        raise OutputParserException(f"获取到无效的JSON对象。错误: {e}")
    except Exception as e:
        raise OutputParserException(f"解析JSON时出错: {e}")


def _parse_partial_json(s: str) -> dict:
    """
    解析可能不完整的JSON字符串（缺少结束括号，多个项之前缺少逗号等）
    """
    # 清理输入字符串
    s = s.strip()

    # 预处理：尝试修复缺少逗号的情况
    # 使用正则表达式查找可能缺少逗号的位置（如 "key": value "key"）
    s = re.sub(r'(\d+|true|false|null|"[^"]*")\s*"', r'\1, "', s)
    # 修复 } { 之间缺少逗号的情况
    s = re.sub(r"}\s*{", r"}, {", s)
    # 修复 ] [ 之间缺少逗号的情况
    s = re.sub(r"]\s*\[", r"], [", s)
    # 修复 } [ 或 ] { 之间缺少逗号的情况
    s = re.sub(r"}\s*\[", r"}, [", s)
    s = re.sub(r"]\s*{", r"], {", s)

    # 处理可能的不完整JSON
    new_chars = []
    stack = []
    is_inside_string = False
    escaped = False

    # 处理每个字符
    for char in s:
        if is_inside_string:
            if char == '"' and not escaped:
                is_inside_string = False
            elif char == "\n" and not escaped:
                char = "\\n"  # 将换行符替换为转义序列
            elif char == "\\":
                escaped = not escaped
            else:
                escaped = False
        else:
            if char == '"':
                is_inside_string = True
                escaped = False
            elif char == "{":
                stack.append("}")
            elif char == "[":
                stack.append("]")
            elif char == "}" or char == "]":
                if stack and stack[-1] == char:
                    stack.pop()
                else:
                    # 括号不匹配，输入格式不正确
                    return None

        # 将处理后的字符添加到新字符串
        new_chars.append(char)

    # 如果字符串结束时仍在字符串内，需要关闭字符串
    if is_inside_string:
        new_chars.append('"')

    # 反转堆栈以获取闭合字符
    stack.reverse()

    # 尝试解析字符串的不同修改版本，直到成功或用完字符
    while new_chars:
        try:
            return json.loads("".join(new_chars + stack))
        except json.JSONDecodeError:
            # 如果仍然无法解析为JSON，尝试删除最后一个字符
            new_chars.pop()

    # 如果到这里，说明我们已经用完了要删除的字符，仍然无法解析字符串为JSON
    try:
        return json.loads(s)
    except:
        # 最后尝试失败，返回空字典
        return {}


class JsonParser(BaseOutputParser[Dict[str, str]]):
    """Parser for output of router chain in the multi-prompt chain."""

    default_destination: str = "DEFAULT"
    next_inputs_type: Type = str
    next_inputs_inner_key: str = "input"

    def parse(self, text: str) -> Dict[str, Any]:
        try:
            expected_keys = ["destination", "next_inputs"]
            parsed = parse_and_check_json_markdown(text, expected_keys)
            if not isinstance(parsed["next_inputs"], self.next_inputs_type):
                raise ValueError(f"Expected 'next_inputs' to be {self.next_inputs_type}.")
            parsed["next_inputs"] = {self.next_inputs_inner_key: parsed["next_inputs"]}
            parsed["destination"] = parsed.get("destination", None)
            if isinstance(parsed["destination"], str):
                parsed["destination"] = parsed["destination"].strip()
                if parsed["destination"].strip().lower() == self.default_destination.lower():
                    parsed["destination"] = None
            return parsed
        except Exception as e:
            raise OutputParserException(f"Parsing text\n{text}\n raised following error:\n{e}")


if __name__ == "__main__":
    text = """
    {
        "destination": "DEFAULT",
        "next_inputs": "Hello, world!"
    }
    """
    print(parse_and_check_json_markdown(text,1))
