from datetime import datetime
import os

import cv2
from paddleocr import PaddleOCR


class OCRProcessor:
    def __init__(self, lang="ch", output_dir="OCR_output"):
        """
        初始化 OCR 處理類別
        """
        self.ocr = PaddleOCR(use_angle_cls=True, lang=lang)
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def flatten_coord(self, coord):
        """展平巢狀結構的座標，並轉換為浮點數"""
        while isinstance(coord, (list, tuple)):
            if not coord:
                return float("nan")
            coord = coord[0]
        try:
            return float(coord)
        except (TypeError, ValueError):
            print(f"警告: 無法將座標轉換為浮點數: {coord}, 原始輸入類型: {type(coord)}")
            return float("nan")

    def list_folders(self, directory):
        """回傳資料夾內所有的子資料夾名稱"""
        try:
            return [
                f
                for f in os.listdir(directory)
                if os.path.isdir(os.path.join(directory, f))
            ]
        except Exception as e:
            print(f"發生錯誤: {e}")
            return []

    def process_images(self, img_dir, save_file=True):
        """
        OCR 處理圖片資料夾中的所有圖片，並根據參數決定是否儲存結果。

        :param img_dir: 需要進行 OCR 的圖片資料夾
        :param save_file: 是否將 OCR 結果儲存為 .txt 檔案（預設 True）
        :return: OCR 轉換後的文字內容（string）
        """
        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        image_files = [
            f
            for f in os.listdir(img_dir)
            if os.path.splitext(f)[1].lower() in valid_extensions
        ]

        print(f"🔍 找到圖片: {image_files}")
        all_output = ""

        for img_filename in image_files:
            img_path = os.path.join(img_dir, img_filename)
            print(f"📷 處理圖片: {img_filename}")

            image = cv2.imread(img_path)
            if image is None:
                print(f"⚠️ 警告: 讀取 {img_path} 失敗，跳過此檔案。")
                continue

            height, width, _ = image.shape
            half_width = width / 2

            result = self.ocr.ocr(img_path, cls=True)
            messages = self._extract_messages(result, half_width)

            # 組合對話內容
            all_output += self._format_output(messages)

        if save_file:
            # 產生時間資訊並建立檔案名稱
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"OCR_output_{timestamp}.txt"
            txt_filename = os.path.join(self.output_dir, output_name)

            with open(txt_filename, "w", encoding="utf-8") as f:
                f.write(all_output.strip())

            print(f"✅ OCR 結果已儲存至 `{txt_filename}`")

        return all_output

    def _extract_messages(self, result, half_width):
        """從 OCR 結果提取對話訊息"""
        messages = []
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
            lines = result[0]
            for idx, line in enumerate(lines):
                bbox = line[0]
                line_info = line[1]
                if isinstance(line_info, tuple) and len(line_info) == 2:
                    text, confidence = line_info
                else:
                    text = "文字解析錯誤: line[1] 格式異常"
                    confidence = 0

                y_values = [self.flatten_coord(point[1]) for point in bbox]
                top = min(y_values)
                bottom = max(y_values)
                bbox_height = bottom - top
                x_values = [self.flatten_coord(point[0]) for point in bbox]
                center_x = sum(x_values) / len(x_values)

                speaker = "A" if center_x < half_width else "我"

                if (
                    text != "已讀"
                    and "下午" not in text
                    and "上午" not in text
                    and ":" not in text
                    and bbox_height > 10
                ):
                    messages.append((top, speaker, text.strip()))
                elif idx == 0 and text.startswith("<"):
                    if bbox_height > 5:
                        messages.append((top, speaker, text.strip()))
        else:
            print("警告: OCR 結果結構異常，不是預期的列表")
        return messages

    def _format_output(self, messages):
        """格式化對話內容"""
        messages.sort(key=lambda x: x[0])
        paragraphs = []
        current_paragraph = []
        last_top = -999

        for i, message in enumerate(messages):
            top, speaker, text = message
            if i == 0 and text.startswith("<"):
                text = text[1:]
                messages[i] = (top, speaker, text)

            if not current_paragraph or (top - last_top) < 20:
                current_paragraph.append((top, speaker, text))
            else:
                paragraphs.append(current_paragraph)
                current_paragraph = [(top, speaker, text)]
            last_top = top
        if current_paragraph:
            paragraphs.append(current_paragraph)

        output_text = ""
        for paragraph in paragraphs:
            for message in paragraph:
                speaker = message[1]
                text = message[2]
                output_text += f"{speaker}: {text} "
            output_text += "\n"

        return output_text


# 測試使用
if __name__ == "__main__":
    ocr_processor = OCRProcessor(lang="ch", output_dir="OCR_output")
    img_dir = "input_dir"
    #ocr_processor.process_images(img_dir, "output.txt")
    conversation = ocr_processor.process_images(img_dir)
    print(conversation)
