#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
包含图片水印工具的各种辅助函数

作者: 开发团队
版本: 1.0
日期: 2025年
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import logging


def validate_image_file(file_path: str) -> bool:
    """
    验证图片文件是否有效
    
    Args:
        file_path: 图片文件路径
        
    Returns:
        是否为有效的图片文件
    """
    if not os.path.exists(file_path):
        return False
    
    # 检查文件扩展名
    supported_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif'}
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext not in supported_extensions:
        return False
    
    # 检查文件大小（避免处理过大的文件）
    try:
        file_size = os.path.getsize(file_path)
        if file_size > 100 * 1024 * 1024:  # 100MB
            logging.warning(f"文件过大: {file_path} ({file_size / 1024 / 1024:.1f}MB)")
            return False
    except OSError:
        return False
    
    return True


def get_image_files(directory: str) -> List[str]:
    """
    获取目录中所有支持的图片文件
    
    Args:
        directory: 目录路径
        
    Returns:
        图片文件路径列表
    """
    image_files = []
    supported_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif'}
    
    try:
        for file_path in Path(directory).iterdir():
            if file_path.is_file():
                if file_path.suffix.lower() in supported_extensions:
                    if validate_image_file(str(file_path)):
                        image_files.append(str(file_path))
    except PermissionError:
        logging.error(f"没有权限访问目录: {directory}")
    except Exception as e:
        logging.error(f"扫描目录失败 {directory}: {e}")
    
    return sorted(image_files)


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小显示
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        格式化的大小字符串
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / 1024 / 1024:.1f} MB"
    else:
        return f"{size_bytes / 1024 / 1024 / 1024:.1f} GB"


def get_system_font_path() -> Optional[str]:
    """
    获取系统默认字体路径
    
    Returns:
        字体文件路径或None
    """
    import platform
    
    system = platform.system()
    
    if system == "Windows":
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "C:/Windows/Fonts/tahoma.ttf"
        ]
    elif system == "Darwin":  # macOS
        font_paths = [
            "/System/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf"
        ]
    else:  # Linux
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/arial.ttf"
        ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            return font_path
    
    return None


def create_output_directory(input_path: str, custom_output: Optional[str] = None) -> str:
    """
    创建输出目录
    
    Args:
        input_path: 输入文件或目录路径
        custom_output: 自定义输出目录
        
    Returns:
        输出目录路径
    """
    if custom_output:
        output_dir = Path(custom_output)
    else:
        input_path = Path(input_path)
        if input_path.is_file():
            parent_dir = input_path.parent
            output_dir = parent_dir / f"{parent_dir.name}_watermark"
        else:
            output_dir = input_path / f"{input_path.name}_watermark"
    
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        return str(output_dir)
    except Exception as e:
        logging.error(f"创建输出目录失败: {e}")
        raise


def calculate_text_size(text: str, font_size: int) -> Tuple[int, int]:
    """
    估算文字尺寸（不依赖PIL）
    
    Args:
        text: 文字内容
        font_size: 字体大小
        
    Returns:
        估算的文字尺寸 (width, height)
    """
    # 简单估算：每个字符大约占字体大小的0.6倍宽度
    char_width = int(font_size * 0.6)
    text_width = len(text) * char_width
    text_height = font_size
    
    return text_width, text_height


def parse_position_string(position: str) -> str:
    """
    解析和标准化位置字符串
    
    Args:
        position: 位置字符串
        
    Returns:
        标准化的位置字符串
    """
    position = position.lower().strip()
    
    position_map = {
        'tl': 'top-left',
        'tr': 'top-right',
        'bl': 'bottom-left',
        'br': 'bottom-right',
        'c': 'center',
        '左上': 'top-left',
        '右上': 'top-right',
        '左下': 'bottom-left',
        '右下': 'bottom-right',
        '居中': 'center',
        '中心': 'center'
    }
    
    return position_map.get(position, position)


def validate_color_string(color: str) -> bool:
    """
    验证颜色字符串是否有效
    
    Args:
        color: 颜色字符串
        
    Returns:
        是否为有效颜色
    """
    # 预定义颜色
    predefined_colors = {
        'red', 'green', 'blue', 'white', 'black', 'yellow', 'cyan', 'magenta',
        'orange', 'purple', 'pink', 'gray', 'grey', 'brown'
    }
    
    if color.lower() in predefined_colors:
        return True
    
    # RGB格式检查
    if ',' in color:
        try:
            parts = color.split(',')
            if len(parts) == 3:
                for part in parts:
                    val = int(part.strip())
                    if not (0 <= val <= 255):
                        return False
                return True
        except ValueError:
            pass
    
    return False


def get_progress_bar(current: int, total: int, width: int = 50) -> str:
    """
    生成进度条字符串
    
    Args:
        current: 当前进度
        total: 总数
        width: 进度条宽度
        
    Returns:
        进度条字符串
    """
    if total == 0:
        return "[" + "=" * width + "] 0/0 (0%)"
    
    progress = current / total
    filled = int(width * progress)
    bar = "=" * filled + "-" * (width - filled)
    percentage = int(progress * 100)
    
    return f"[{bar}] {current}/{total} ({percentage}%)"


def setup_console_output():
    """
    设置控制台输出编码（Windows兼容）
    """
    if sys.platform == "win32":
        try:
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
        except:
            pass


def check_dependencies() -> bool:
    """
    检查必要的依赖库是否已安装
    
    Returns:
        是否所有依赖都已安装
    """
    missing_deps = []
    
    try:
        import PIL
    except ImportError:
        missing_deps.append("Pillow")
    
    try:
        import exifread
    except ImportError:
        missing_deps.append("exifread")
    
    if missing_deps:
        print("错误: 缺少以下依赖库:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    
    return True


def get_version_info() -> str:
    """
    获取版本信息
    
    Returns:
        版本信息字符串
    """
    return "图片水印工具 v1.0 - 2025年"


def print_banner():
    """
    打印程序横幅
    """
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    图片水印工具 v1.0                          ║
║                Photo Watermark Tool                          ║
║                                                              ║
║  自动读取图片EXIF信息中的拍摄时间并添加为水印                  ║
║  支持批量处理、自定义样式、多种输出格式                        ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


if __name__ == "__main__":
    # 测试工具函数
    print("工具函数模块测试")
    print(f"版本信息: {get_version_info()}")
    print(f"系统字体路径: {get_system_font_path()}")
    print(f"依赖检查: {check_dependencies()}")
