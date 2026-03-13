import random
import csv
import re
from typing import List
import unicodedata  # giữ nguyên như code bạn (dù hiện chưa dùng)

class VietnameseOCRNoiseGenerator:
    def __init__(self):
        # Bảng lỗi dấu thanh điệu
        self.tone_errors = {
            'á': ['a', 'à', 'ả', 'ã', 'ạ', 'ă', 'ắ', 'ằ', 'ẳ', 'ẵ', 'ặ', 'â', 'ấ', 'ầ', 'ẩ', 'ẫ', 'ậ'],
            'à': ['a', 'á', 'ả', 'ã', 'ạ', 'ă', 'ắ', 'ằ', 'ẳ', 'ẵ', 'ặ', 'â', 'ấ', 'ầ', 'ẩ', 'ẫ', 'ậ'],
            'ả': ['a', 'à', 'á', 'ã', 'ạ', 'ă', 'ắ', 'ằ', 'ẳ', 'ẵ', 'ặ', 'â', 'ấ', 'ầ', 'ẩ', 'ẫ', 'ậ'],
            'ã': ['a', 'à', 'á', 'ả', 'ạ', 'ă', 'ắ', 'ằ', 'ẳ', 'ẵ', 'ặ', 'â', 'ấ', 'ầ', 'ẩ', 'ẫ', 'ậ'],
            'ạ': ['a', 'à', 'á', 'ả', 'ã', 'ă', 'ắ', 'ằ', 'ẳ', 'ẵ', 'ặ', 'â', 'ấ', 'ầ', 'ẩ', 'ẫ', 'ậ'],
            'ă': ['a', 'à', 'á', 'ả', 'ã', 'ạ', 'ắ', 'ằ', 'ẳ', 'ẵ', 'ặ', 'â', 'ấ', 'ầ', 'ẩ', 'ẫ', 'ậ'],
            'ắ': ['a', 'à', 'á', 'ả', 'ã', 'ạ', 'ă', 'ằ', 'ẳ', 'ẵ', 'ặ', 'â', 'ấ', 'ầ', 'ẩ', 'ẫ', 'ậ'],
            'ằ': ['a', 'à', 'á', 'ả', 'ã', 'ạ', 'ă', 'ắ', 'ẳ', 'ẵ', 'ặ', 'â', 'ấ', 'ầ', 'ẩ', 'ẫ', 'ậ'],
            'ẳ': ['a', 'à', 'á', 'ả', 'ã', 'ạ', 'ă', 'ắ', 'ằ', 'ẵ', 'ặ', 'â', 'ấ', 'ầ', 'ẩ', 'ẫ', 'ậ'],
            'ẵ': ['a', 'à', 'á', 'ả', 'ã', 'ạ', 'ă', 'ắ', 'ằ', 'ẳ', 'ặ', 'â', 'ấ', 'ầ', 'ẩ', 'ẫ', 'ậ'],
            'ặ': ['a', 'à', 'á', 'ả', 'ã', 'ạ', 'ă', 'ắ', 'ằ', 'ẳ', 'ẵ', 'â', 'ấ', 'ầ', 'ẩ', 'ẫ', 'ậ'],
            'â': ['a', 'à', 'á', 'ả', 'ã', 'ạ', 'ă', 'ắ', 'ằ', 'ẳ', 'ẵ', 'ặ', 'ấ', 'ầ', 'ẩ', 'ẫ', 'ậ'],
            'ấ': ['a', 'à', 'á', 'ả', 'ã', 'ạ', 'ă', 'ắ', 'ằ', 'ẳ', 'ẵ', 'ặ', 'â', 'ầ', 'ẩ', 'ẫ', 'ậ'],
            'ầ': ['a', 'à', 'á', 'ả', 'ã', 'ạ', 'ă', 'ắ', 'ằ', 'ẳ', 'ẵ', 'ặ', 'â', 'ấ', 'ẩ', 'ẫ', 'ậ'],
            'ẩ': ['a', 'à', 'á', 'ả', 'ã', 'ạ', 'ă', 'ắ', 'ằ', 'ẳ', 'ẵ', 'ặ', 'â', 'ấ', 'ầ', 'ẫ', 'ậ'],
            'ẫ': ['a', 'à', 'á', 'ả', 'ã', 'ạ', 'ă', 'ắ', 'ằ', 'ẳ', 'ẵ', 'ặ', 'â', 'ấ', 'ầ', 'ẩ', 'ậ'],
            'ậ': ['a', 'à', 'á', 'ả', 'ã', 'ạ', 'ă', 'ắ', 'ằ', 'ẳ', 'ẵ', 'ặ', 'â', 'ấ', 'ầ', 'ẩ', 'ẫ'],
            'é': ['e', 'è', 'ẹ', 'ẻ', 'ẽ', 'ê', 'ề', 'ế', 'ể', 'ễ', 'ệ'],
            'è': ['e', 'é', 'ẹ', 'ẻ', 'ẽ', 'ê', 'ề', 'ế', 'ể', 'ễ', 'ệ'],
            'ẻ': ['e', 'è', 'é', 'ẹ', 'ẽ', 'ê', 'ề', 'ế', 'ể', 'ễ', 'ệ'],
            'ẽ': ['e', 'è', 'é', 'ẹ', 'ẻ', 'ê', 'ề', 'ế', 'ể', 'ễ', 'ệ'],
            'ẹ': ['e', 'è', 'é', 'ẻ', 'ẽ', 'ê', 'ề', 'ế', 'ể', 'ễ', 'ệ'],
            'ê': ['e', 'è', 'é', 'ẹ', 'ẻ', 'ẽ', 'ề', 'ế', 'ể', 'ễ', 'ệ'],
            'ế': ['e', 'è', 'é', 'ẹ', 'ẻ', 'ẽ', 'ê', 'ề', 'ể', 'ễ', 'ệ'],
            'ề': ['e', 'è', 'é', 'ẹ', 'ẻ', 'ẽ', 'ê', 'ế', 'ể', 'ễ', 'ệ'],
            'ể': ['e', 'è', 'é', 'ẹ', 'ẻ', 'ẽ', 'ê', 'ề', 'ế', 'ễ', 'ệ'],
            'ễ': ['e', 'è', 'é', 'ẹ', 'ẻ', 'ẽ', 'ê', 'ề', 'ế', 'ể', 'ệ'],
            'ệ': ['e', 'è', 'é', 'ẹ', 'ẻ', 'ẽ', 'ê', 'ề', 'ế', 'ể', 'ễ'],
            'í': ['i', 'ì', 'ỉ', 'ĩ', 'ị'],
            'ì': ['i', 'í', 'ỉ', 'ĩ', 'ị'],
            'ỉ': ['i', 'í', 'ì', 'ĩ', 'ị'],
            'ĩ': ['i', 'í', 'ì', 'ỉ', 'ị'],
            'ị': ['i', 'í', 'ì', 'ỉ', 'ĩ'],
            'ó': ['o', 'ò', 'ỏ', 'õ', 'ọ', 'ơ', 'ớ', 'ờ', 'ở', 'ỡ', 'ợ', 'ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ'],
            'ò': ['o', 'ó', 'ỏ', 'õ', 'ọ', 'ơ', 'ớ', 'ờ', 'ở', 'ỡ', 'ợ', 'ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ'],
            'ỏ': ['o', 'ò', 'ó', 'õ', 'ọ', 'ơ', 'ớ', 'ờ', 'ở', 'ỡ', 'ợ', 'ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ'],
            'õ': ['o', 'ò', 'ó', 'ỏ', 'ọ', 'ơ', 'ớ', 'ờ', 'ở', 'ỡ', 'ợ', 'ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ'],
            'ọ': ['o', 'ò', 'ó', 'ỏ', 'õ', 'ơ', 'ớ', 'ờ', 'ở', 'ỡ', 'ợ', 'ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ'],
            'ô': ['o', 'ò', 'ó', 'ỏ', 'õ', 'ọ', 'ơ', 'ớ', 'ờ', 'ở', 'ỡ', 'ợ', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ'],
            'ố': ['o', 'ò', 'ó', 'ỏ', 'õ', 'ọ', 'ơ', 'ớ', 'ờ', 'ở', 'ỡ', 'ợ', 'ô', 'ồ', 'ổ', 'ỗ', 'ộ'],
            'ồ': ['o', 'ò', 'ó', 'ỏ', 'õ', 'ọ', 'ơ', 'ớ', 'ờ', 'ở', 'ỡ', 'ợ', 'ô', 'ố', 'ổ', 'ỗ', 'ộ'],
            'ổ': ['o', 'ò', 'ó', 'ỏ', 'õ', 'ọ', 'ơ', 'ớ', 'ờ', 'ở', 'ỡ', 'ợ', 'ô', 'ồ', 'ố', 'ỗ', 'ộ'],
            'ỗ': ['o', 'ò', 'ó', 'ỏ', 'õ', 'ọ', 'ơ', 'ớ', 'ờ', 'ở', 'ỡ', 'ợ', 'ô', 'ồ', 'ố', 'ổ', 'ộ'],
            'ộ': ['o', 'ò', 'ó', 'ỏ', 'õ', 'ọ', 'ơ', 'ớ', 'ờ', 'ở', 'ỡ', 'ợ', 'ô', 'ồ', 'ố', 'ổ', 'ỗ'],
            'ơ': ['o', 'ò', 'ó', 'ỏ', 'õ', 'ọ', 'ớ', 'ờ', 'ở', 'ỡ', 'ợ', 'ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ'],
            'ớ': ['o', 'ò', 'ó', 'ỏ', 'õ', 'ọ', 'ơ', 'ờ', 'ở', 'ỡ', 'ợ', 'ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ'],
            'ờ': ['o', 'ò', 'ó', 'ỏ', 'õ', 'ọ', 'ơ', 'ớ', 'ở', 'ỡ', 'ợ', 'ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ'],
            'ở': ['o', 'ò', 'ó', 'ỏ', 'õ', 'ọ', 'ơ', 'ớ', 'ờ', 'ỡ', 'ợ', 'ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ'],
            'ỡ': ['o', 'ò', 'ó', 'ỏ', 'õ', 'ọ', 'ơ', 'ớ', 'ờ', 'ở', 'ợ', 'ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ'],
            'ợ': ['o', 'ò', 'ó', 'ỏ', 'õ', 'ọ', 'ơ', 'ớ', 'ờ', 'ở', 'ỡ', 'ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ'],
            'ú': ['u', 'ù', 'ụ', 'ũ', 'ủ', 'ư', 'ứ', 'ừ', 'ự', 'ử', 'ữ'],
            'ù': ['u', 'ú', 'ụ', 'ũ', 'ủ', 'ư', 'ứ', 'ừ', 'ự', 'ử', 'ữ'],
            'ủ': ['u', 'ù', 'ú', 'ụ', 'ũ', 'ư', 'ứ', 'ừ', 'ự', 'ử', 'ữ'],
            'ũ': ['u', 'ù', 'ú', 'ụ', 'ủ', 'ư', 'ứ', 'ừ', 'ự', 'ử', 'ữ'],
            'ụ': ['u', 'ù', 'ú', 'ũ', 'ủ', 'ư', 'ứ', 'ừ', 'ự', 'ử', 'ữ'],
            'ư': ['u', 'ù', 'ú', 'ụ', 'ũ', 'ủ', 'ứ', 'ừ', 'ự', 'ử', 'ữ'],
            'ứ': ['u', 'ù', 'ú', 'ụ', 'ũ', 'ủ', 'ư', 'ừ', 'ự', 'ử', 'ữ'],
            'ừ': ['u', 'ù', 'ú', 'ụ', 'ũ', 'ủ', 'ư', 'ứ', 'ự', 'ử', 'ữ'],
            'ử': ['u', 'ù', 'ú', 'ụ', 'ũ', 'ủ', 'ư', 'ứ', 'ừ', 'ự', 'ữ'],
            'ữ': ['u', 'ù', 'ú', 'ụ', 'ũ', 'ủ', 'ư', 'ứ', 'ừ', 'ự', 'ử'],
            'ự': ['u', 'ù', 'ú', 'ụ', 'ũ', 'ủ', 'ư', 'ứ', 'ừ', 'ử', 'ữ'],
            'ý': ['y', 'ỳ', 'ỷ', 'ỹ', 'ỵ'],
            'ỳ': ['y', 'ý', 'ỷ', 'ỹ', 'ỵ'],
            'ỷ': ['y', 'ý', 'ỳ', 'ỹ', 'ỵ'],
            'ỹ': ['y', 'ý', 'ỳ', 'ỷ', 'ỵ'],
            'ỵ': ['y', 'ý', 'ỳ', 'ỷ', 'ỹ'],
        }

        # Bảng lỗi nhầm lẫn ký tự giống nhau về mặt hình ảnh
        self.visual_errors = {
            'd': ['đ'],
            'đ': ['d'],
            'o': ['0', 'ô', 'ơ', 'ọ', 'O'],
            'O': ['0', 'Ô', 'Ơ', 'o'],
            'I': ['1', 'l', 'i', '|', 'L'],
            'l': ['1', '|', 'i', 'I'],
            'i': ['1', 'l', 'I', '|'],
            'S': ['5', '$', 's'],
            's': ['5', '$', 'S'],
            'B': ['8', 'b'],
            'b': ['8', 'B', '6'],
            'Z': ['2', 'z'],
            'z': ['2', 'Z'],
            'g': ['9', 'q'],
            'q': ['9', 'g'],
            'G': ['6', 'C'],
            'a': ['@', 'á', 'à'],
            'A': ['@', 'Á', 'À'],
            'e': ['3', 'é', 'è'],
            'E': ['3', 'É', 'È'],
            't': ['+', 'T'],
            'T': ['+', 't'],
            'c': ['(', 'C', '<'],
            'C': ['(', 'c', '<'],
            'n': ['ñ', 'N', 'η'],
            'N': ['ñ', 'n', 'Ñ'],
            'u': ['ủ', 'ú', 'ù'],
            'U': ['Ủ', 'Ú', 'Ù'],
            'h': ['#', 'H'],
            'H': ['#', 'h'],
        }

        # Ký tự đặc biệt để thay thế
        self.special_chars = ['@', '$', '#', '! ', '%', '^', '&', '*', '=', '~', '+', '|', '<', '>', '?', '{', '}', '[', ']']

        # Tỷ lệ áp dụng các loại lỗi
        self.noise_types = [
            'remove_char',      # Xóa ký tự
            'tone_error',       # Lỗi dấu thanh
            'visual_error',     # Lỗi nhầm lẫn hình ảnh
            'special_char',     # Thay thế ký tự đặc biệt
            'remove_all_tones', # Loại bỏ tất cả dấu
        ]

    # =========================
    # -------------- CÁC HÀM TẠO NOISE --------------
    # =========================
    def remove_vietnamese_accents(self, text: str) -> str:
        """Loại bỏ tất cả dấu tiếng Việt"""
        text = re.sub(r'[àáảãạăắằẳẵặâấầẩẫậ]', 'a', text)
        text = re.sub(r'[ÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬ]', 'A', text)
        text = re.sub(r'[èéẻẽẹêềếểễệ]', 'e', text)
        text = re.sub(r'[ÈÉẺẼẸÊỀẾỂỄỆ]', 'E', text)
        text = re.sub(r'[ìíỉĩị]', 'i', text)
        text = re.sub(r'[ÌÍỈĨỊ]', 'I', text)
        text = re.sub(r'[òóỏõọôồốổỗộơờớởỡợ]', 'o', text)
        text = re.sub(r'[ÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢ]', 'O', text)
        text = re.sub(r'[ùúủũụưừứửữự]', 'u', text)
        text = re.sub(r'[ÙÚỦŨỤƯỪỨỬỮỰ]', 'U', text)
        text = re.sub(r'[ỳýỷỹỵ]', 'y', text)
        text = re.sub(r'[ỲÝỶỸỴ]', 'Y', text)
        text = re.sub(r'[đ]', 'd', text)
        text = re.sub(r'[Đ]', 'D', text)
        return text

    def add_char_deletion_error(self, word: str) -> str:
        """Xóa 1 ký tự trong từ (ưu tiên ký tự ở giữa)"""
        if len(word) <= 2:
            return word
        # Tạo danh sách vị trí với trọng số
        positions = []
        mid_start = len(word) // 3
        mid_end = 2 * len(word) // 3
        for i in range(1, len(word) - 1):  # Không xóa ký tự đầu/cuối
            if mid_start <= i <= mid_end:
                positions.extend([i] * 3)  # Ưu tiên giữa, trọng số x3
            else:
                positions.append(i)
        if positions:
            pos = random.choice(positions)
            return word[:pos] + word[pos+1:]
        return word

    def add_tone_error(self, word: str) -> str:
        """Thêm lỗi dấu thanh điệu"""
        chars = list(word)
        # Tìm các vị trí có dấu
        tone_positions = [i for i, c in enumerate(chars) if c in self.tone_errors]
        if tone_positions:
            # Ưu tiên ký tự ở giữa
            mid_start = len(word) // 3
            mid_end = 2 * len(word) // 3
            middle_positions = [p for p in tone_positions if mid_start <= p <= mid_end]
            if middle_positions:
                pos = random.choice(middle_positions)
            else:
                pos = random.choice(tone_positions)
            original_char = chars[pos]
            replacement_chars = self.tone_errors[original_char]
            chars[pos] = random.choice(replacement_chars)
        return ''.join(chars)

    def add_visual_error(self, word: str) -> str:
        """Thêm lỗi nhầm lẫn ký tự giống nhau về hình ảnh"""
        chars = list(word)
        visual_positions = [i for i, c in enumerate(chars) if c in self.visual_errors]
        if visual_positions:
            # Ưu tiên ký tự ở giữa
            mid_start = len(word) // 3
            mid_end = 2 * len(word) // 3
            middle_positions = [p for p in visual_positions if mid_start <= p <= mid_end]
            if middle_positions:
                pos = random.choice(middle_positions)
            else:
                pos = random.choice(visual_positions)
            original_char = chars[pos]
            replacement_chars = self.visual_errors[original_char]
            chars[pos] = random.choice(replacement_chars)
        return ''.join(chars)

    def add_special_char_error(self, word: str) -> str:
        """Thay thế 1 ký tự bằng ký tự đặc biệt"""
        if len(word) <= 1:
            return word
        chars = list(word)
        # Ưu tiên ký tự ở giữa
        mid_start = max(1, len(word) // 3)
        mid_end = min(len(word) - 1, 2 * len(word) // 3)
        positions = []
        for i in range(1, len(word) - 1):
            if mid_start <= i <= mid_end:
                positions.extend([i] * 3)  # Trọng số cao cho giữa
            else:
                positions.append(i)
        if positions:
            pos = random.choice(positions)
            chars[pos] = random.choice(self.special_chars)
        return ''.join(chars)

    def apply_noise_to_word(self, word: str, noise_type: str) -> str:
        """Áp dụng một loại nhiễu cho từ"""
        if noise_type == 'remove_char':
            return self.add_char_deletion_error(word)
        elif noise_type == 'tone_error':
            return self.add_tone_error(word)
        elif noise_type == 'visual_error':
            return self.add_visual_error(word)
        elif noise_type == 'special_char':
            return self.add_special_char_error(word)
        return word

    def add_noise_to_sentence(self, sentence: str) -> str:
        """Thêm nhiễu cho câu"""
        # 20% khả năng loại bỏ tất cả dấu cho cả câu
        if random.random() < 0.2:
            return self.remove_vietnamese_accents(sentence)
        # Tách từ và dấu câu
        words = []
        current_word = ""
        for char in sentence:
            if char.isalnum() or char in 'àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđĐÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠƯẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪỬỮỰỲỴÝỶỸ':
                current_word += char
            else:
                if current_word:
                    words.append(('word', current_word))
                    current_word = ""
                words.append(('punct', char))
        if current_word:
            words.append(('word', current_word))
        # Áp dụng nhiễu cho mỗi từ
        noisy_sentence = []
        for word_type, word in words:
            if word_type == 'word' and len(word) > 1:
                # 60% khả năng thêm nhiễu vào từ
                if random.random() < 0.6:
                    # Chọn loại nhiễu ngẫu nhiên (trừ remove_all_tones)
                    noise_type = random.choice(self.noise_types[:-1])
                    noisy_word = self.apply_noise_to_word(word, noise_type)
                    noisy_sentence.append(noisy_word)
                else:
                    noisy_sentence.append(word)
            else:
                noisy_sentence.append(word)

        return ''.join(noisy_sentence)

    def split_into_chunks(self, text: str, max_tokens: int = 256) -> List[str]:
        """Chia văn bản thành các đoạn phù hợp với tokenizer"""
        # Ước lượng:  1 token ≈ 1 từ tiếng Việt
        # Để an toàn, chia theo câu với giới hạn khoảng 200 từ
        sentences = re.split(r'([.!?;])\s+', text)
        chunks = []
        current_chunk = ""
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            separator = sentences[i+1] if i+1 < len(sentences) else ""
            test_chunk = current_chunk + sentence + separator
            word_count = len(test_chunk.split())
            if word_count <= max_tokens - 50:  # Giữ buffer 50 tokens
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + separator
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

    # =========================
    # -------------- AUGMENTATION --------------
    # =========================

    def choose_chunk_target_len(self) -> int:
        r = random.random()
        if r < 0.15:
            return random.randint(10, 25)
        elif r < 0.99:
            return random.randint(25, 35)
        else:
            return random.randint(45, 55)

    def _is_good_cut_token(self, tok: str) -> bool:
        return tok.endswith((",", ";", ":", ")", "]")) or tok == "-"

    def split_sentence_like_sample(self, sentence: str) -> List[str]:
        sentence = re.sub(r"\s+", " ", sentence).strip()
        if not sentence:
            return []
        tokens = sentence.split(" ")
        n = len(tokens)
        # Giữ nguyên các dòng rất ngắn (vd: "Khung pháp lý 2", "TS.", ...)
        if n < 12:
            return [sentence]
        chunks: List[str] = []
        i = 0
        while i < n:
            target_len = self.choose_chunk_target_len()
            j = min(i + target_len, n)
            # Nếu chưa đến cuối, tìm điểm cắt "đẹp" gần j
            if j < n:
                # cửa sổ +-8 token quanh j, tránh tạo chunk quá ngắn
                window_left = max(i + 5, j - 8)
                window_right = min(n - 1, j + 8)
                best = None
                # ưu tiên cắt lùi (không vượt target quá nhiều)
                for k in range(j - 1, window_left - 1, -1):
                    if self._is_good_cut_token(tokens[k]):
                        best = k + 1
                        break
                # nếu không có, thử cắt tiến lên một chút
                if best is None:
                    for k in range(j, window_right + 1):
                        if self._is_good_cut_token(tokens[k]):
                            best = k + 1
                            break
                if best is not None and best > i:
                    j = best
            chunk = " ".join(tokens[i:j]).strip()
            if chunk:
                chunks.append(chunk)
            i = j
        return chunks

    # =========================
    # -------------- PROCESS FILE --------------
    # =========================

    def process_file(self, input_file: str, output_file: str, max_tokens: int = 256):
        print(f"Đọc file: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"Đã đọc {len(lines)} dòng")
        print("Bắt đầu tạo nhiễu...")
        data = []
        for idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            coarse_chunks = self.split_into_chunks(line, max_tokens=max_tokens)
            for coarse in coarse_chunks:
                # (B) Cắt nhỏ theo style dataset_sample.csv
                chunks = self.split_sentence_like_sample(coarse)
                for chunk in chunks:
                    noisy_chunk = self.add_noise_to_sentence(chunk)
                    data.append({
                        'input': noisy_chunk,
                        'corrected_text': chunk
                    })
            if (idx + 1) % 100 == 0:
                print(f"Đã xử lý {idx + 1}/{len(lines)} dòng")
        print(f"\nGhi {len(data)} mẫu vào file: {output_file}")
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['input', 'corrected_text'])
            writer.writeheader()
            writer.writerows(data)
        print("Hoàn thành!")
        print(f"Tổng số mẫu: {len(data)}")

if __name__ == "__main__":
    generator = VietnameseOCRNoiseGenerator()
    input_file = "/content/drive/MyDrive/Colab Notebooks/DA2-v3/test_2.txt"     # File chứa các câu sạch
    output_file = "/content/drive/MyDrive/Colab Notebooks/DA2-v3/noisy_dataset_aug_3.csv"  # File output
    generator.process_file(input_file, output_file, max_tokens=256)