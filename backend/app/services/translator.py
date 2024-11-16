from openai import AsyncOpenAI
from typing import List, Tuple, Dict
import asyncio
from ..config import settings
import os

os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class TranslatorService:
    TRANSLATION_PROMPT = """
        你是一名资深的翻译工作者，你的目标是帮助用户将指定文本内容翻译为中文。
        你必须满足以下要求：
        - 如果需要翻译的文本内容为空，则无需输出任何内容。请不要输出抱歉等任何说明和描述。
        - 下面为一些翻译时参考的角度，你需要考虑这些角度来确保翻译的准确性。
            - "准确性"：翻译内容需要尽可能准确地表达原文的意思。
            - "数字、公式、特殊符号与网址"：如果翻译内容涉及到数字、公式、特殊符号与网址，你无需对数字、公式、特殊符号与网址进行翻译，仅确保数字、公式、特殊符号与网址不变即可。
            - "术语"：在专业领域中，很多词汇有特定的含义，需要确保这些术语被准确地翻译。
            - "语境"：理解原文的语境对于准确翻译非常重要。你需要需要确认具体语境。
            - "语言风格"：如果原文是在特定的语言风格（如正式、口语、学术等）下写的，翻译时也应尽可能保持这种风格。
            - "文化差异"：有些表达方式可能在一种语言中很常见，但在另一种语言中却很少见。在翻译时，需要考虑这些文化差异。
            - "句子结构"：不同语种的句子结构有很大的不同，尤其是中文和英文。翻译时需要对这些差异有所了解。
            - "专业知识"：如果原文涉及到特定的专业知识，翻译时可能需要结合专业知识相关的内容以确保准确性。
            - "格式"：翻译内容需要保持原文的格式，包括段落、标题、列表等。
    下面为指定需要翻译的文本内容，你无需返回原文，无需给出任何说明和描述，仅提供最终翻译结果。
    {text}
    """

    @staticmethod
    async def translate_text(text: str, target_language: str) -> str:
        """翻译单个文本块"""
        try:
            prompt = TranslatorService.TRANSLATION_PROMPT.format(text=text)
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API 调用失败: {str(e)}")

    @staticmethod
    async def translate_blocks(
        text_blocks: List[Tuple[int, Dict]],
        target_language: str,
        progress_callback = None
    ) -> List[Tuple[int, Dict]]:
        """翻译所有文本块"""
        translated_blocks = []
        total_blocks = len(text_blocks)
        
        for i, (page_num, block_info) in enumerate(text_blocks):
            try:
                translated_text = await TranslatorService.translate_text(
                    block_info["text"], 
                    target_language
                )
                
                # 创建新的block_info，保持原有格式信息
                new_block_info = block_info.copy()
                new_block_info["text"] = translated_text
                translated_blocks.append((page_num, new_block_info))
                
                if progress_callback:
                    progress = (i + 1) / total_blocks * 100
                    await progress_callback(progress)
                    
            except Exception as e:
                raise Exception(f"翻译第 {page_num} 页时失败: {str(e)}")
        print(translated_blocks)  
        return translated_blocks