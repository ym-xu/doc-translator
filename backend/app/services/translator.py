from openai import AsyncOpenAI
from typing import List, Tuple, Dict
import asyncio
from ..config import settings
import os

# os.environ["http_proxy"] = "http://127.0.0.1:7890"
# os.environ["https_proxy"] = "http://127.0.0.1:7890"

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class TranslatorService:
    TRANSLATION_PROMPT = """
        You are a senior translator, and your goal is to help users translate specified text content into Chinese.
        You must meet the following requirements:
        - If the text content to be translated is empty, no output is required. Please do not output any apologies or descriptions.
        - Below are some aspects to consider when translating to ensure accuracy.
            - "Accuracy": The translation needs to accurately express the meaning of the original text.
            - "Numbers, Formulas, Special Symbols and URLs": If the translation involves numbers, formulas, special symbols and URLs, you don't need to translate them, just keep them unchanged.
            - "Terminology": In professional fields, many terms have specific meanings, and these terms need to be accurately translated.
            - "Context": Understanding the context of the original text is very important for accurate translation. You need to confirm the specific context.
            - "Language Style": If the original text is written in a specific language style (such as formal, colloquial, academic, etc.), try to maintain this style in the translation.
            - "Cultural Differences": Some expressions may be common in one language but rare in another. These cultural differences need to be considered in translation.
            - "Sentence Structure": Different languages have very different sentence structures, especially Chinese and English. These differences need to be understood when translating.
            - "Professional Knowledge": If the original text involves specific professional knowledge, you may need to combine relevant professional knowledge to ensure accuracy.
            - "Format": The translation needs to maintain the format of the original text, including paragraphs, titles, lists, etc.
        Below is the specified text content to be translated. You don't need to return the original text, no explanations or descriptions are needed, just provide the final translation result.
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