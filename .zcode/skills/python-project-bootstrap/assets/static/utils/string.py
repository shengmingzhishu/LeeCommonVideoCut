import re

class StringUtils:
    @staticmethod
    def toCamelCase(text):
        """
        将字符串转换为小驼峰命名法（camelCase）
        
        支持输入格式：
        - 蛇形命名法（snake_case）
        - 短横线命名法（kebab-case）
        - 空格分隔
        - 大驼峰命名法（PascalCase）
        """
        if not text:
            return text
        
        # 统一替换分隔符为空格
        # 处理 snake_case, kebab-case, 以及连续的大写字母（PascalCase）
        normalized = re.sub(r'[-_]', ' ', text)
        
        # 处理 PascalCase：在大写字母前加空格（首字母除外）
        normalized = re.sub(r'(?<!^)(?=[A-Z])', ' ', normalized)
        
        # 分割成单词列表
        words = normalized.split()
        
        if not words:
            return ''
        
        # 第一个单词全小写，后续单词首字母大写
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
