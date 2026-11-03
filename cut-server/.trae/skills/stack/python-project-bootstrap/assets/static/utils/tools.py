import re
from re import Pattern
import json

class ToolUtils:
    _PY_PATTERN: Pattern = re.compile(r'```(python|json)?(.*?)```', re.DOTALL|re.IGNORECASE)
    
    @staticmethod
    def remove_prefix_suffix(content: str) -> str:
        if not content:
            return ''
        m = ToolUtils._PY_PATTERN.search(content)
        if m:
            ss: str = m.group(2).strip()
            return ss
        return content
    
    @staticmethod
    def extract_code_blocks(content: str) -> str:
        content = ToolUtils.remove_prefix_suffix(content)
        start = content.find("{")
        next_start = content.find("[")
        is_dkh = True
        min_start = start
        if start == -1 and next_start == -1:
            return ''
        if start == -1 and next_start != -1:
            min_start = next_start
            is_dkh = False
        elif start != -1 and next_start != -1:
            min_start = min(start, next_start)
            is_dkh = start == min_start
        if is_dkh:
            end = content.rfind("}")
        else:
            end = content.rfind("]")
        if end == -1:
            return ''
        elif end < min_start:
            return ''
        return content[min_start:end+1]

    @staticmethod
    def extract_json_str(content: str) -> str:
        return ToolUtils.extract_code_blocks(content)

    @staticmethod
    def parse_json_object(content: str) -> dict:
        json_str = ToolUtils.extract_json_str(content)
        if not json_str:
            raise ValueError("未提取到有效 JSON")
        result = json.loads(json_str)
        if not isinstance(result, dict):
            raise ValueError("JSON 结果不是对象")
        return result