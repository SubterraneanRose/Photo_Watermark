#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片水印工具 (Photo Watermark Tool)
根据PRD要求开发的命令行程序，能够自动读取图片EXIF信息中的拍摄时间，
并将其作为水印添加到图片上。

作者: 并非开发团队
版本: 1.0
日期: 2025年
"""

import argparse
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple, Union
import json

try:
    from PIL import Image, ImageDraw, ImageFont
    import exifread
except ImportError as e:
    print(f"错误: 缺少必要的依赖库 - {e}")
    print("请运行: pip install -r requirements.txt")
    sys.exit(1)


class WatermarkConfig:
    """水印配置类"""
    
    def __init__(self):
        self.font_size = 24
        self.color = "white"
        self.position = "bottom-right"  # 默认右下角
        self.opacity = 0.8
        self.output_dir = None
        self.font_path = None
        
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'font_size': self.font_size,
            'color': self.color,
            'position': self.position,
            'opacity': self.opacity,
            'font_path': self.font_path
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'WatermarkConfig':
        """从字典创建配置"""
        config = cls()
        config.font_size = data.get('font_size', 24)
        config.color = data.get('color', 'white')
        config.position = data.get('position', 'top-left')
        config.opacity = data.get('opacity', 0.8)
        config.font_path = data.get('font_path', None)
        return config


class ExifReader:
    """EXIF信息读取器"""
    
    @staticmethod
    def get_date_taken(image_path: str) -> Optional[str]:
        """
        从图片EXIF信息中获取拍摄日期
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            日期字符串 (YYYY-MM-DD格式) 或 None
        """
        try:
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
                
            # 尝试获取拍摄日期
            date_fields = [
                'EXIF DateTimeOriginal',
                'EXIF DateTimeDigitized', 
                'Image DateTime'
            ]
            
            for field in date_fields:
                if field in tags:
                    date_str = str(tags[field])
                    # 解析日期格式: "2023:12:25 14:30:15" -> "2023-12-25"
                    if ':' in date_str:
                        date_part = date_str.split(' ')[0]  # 取日期部分
                        date_part = date_part.replace(':', '-')  # 替换分隔符
                        return date_part
                        
        except Exception as e:
            logging.warning(f"读取EXIF信息失败 {image_path}: {e}")
            
        return None
    
    @staticmethod
    def get_fallback_date(image_path: str) -> str:
        """
        获取备用日期（文件修改时间或当前时间）
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            日期字符串 (YYYY-MM-DD格式)
        """
        try:
            # 尝试使用文件修改时间
            mtime = os.path.getmtime(image_path)
            return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
        except:
            # 使用当前时间
            return datetime.now().strftime('%Y-%m-%d')


class WatermarkProcessor:
    """水印处理器"""
    
    def __init__(self, config: WatermarkConfig):
        self.config = config
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp'}
        
    def get_position_coordinates(self, image_size: Tuple[int, int], 
                               text_size: Tuple[int, int]) -> Tuple[int, int]:
        """
        根据位置设置计算水印坐标
        
        Args:
            image_size: 图片尺寸 (width, height)
            text_size: 文字尺寸 (width, height)
            
        Returns:
            水印位置坐标 (x, y)
        """
        img_width, img_height = image_size
        text_width, text_height = text_size
        
        # 边距设置
        margin = 20
        
        position_map = {
            'top-left': (margin, margin),
            'top-right': (img_width - text_width - margin, margin),
            'bottom-left': (margin, img_height - text_height - margin),
            'bottom-right': (img_width - text_width - margin, img_height - text_height - margin),
            'center': ((img_width - text_width) // 2, (img_height - text_height) // 2)
        }
        
        return position_map.get(self.config.position, position_map['top-left'])
    
    def get_font(self) -> ImageFont.FreeTypeFont:
        """获取字体对象"""
        try:
            if self.config.font_path and os.path.exists(self.config.font_path):
                return ImageFont.truetype(self.config.font_path, self.config.font_size)
            else:
                # 尝试使用系统默认字体
                try:
                    return ImageFont.truetype("arial.ttf", self.config.font_size)
                except:
                    return ImageFont.load_default()
        except:
            return ImageFont.load_default()
    
    def add_watermark(self, image_path: str, output_path: str) -> bool:
        """
        为图片添加水印
        
        Args:
            image_path: 输入图片路径
            output_path: 输出图片路径
            
        Returns:
            是否成功
        """
        try:
            # 获取拍摄日期
            date_str = ExifReader.get_date_taken(image_path)
            if not date_str:
                date_str = ExifReader.get_fallback_date(image_path)
                logging.info(f"使用备用日期: {date_str}")
            
            # 打开图片
            with Image.open(image_path) as img:
                # 转换为RGBA模式以支持透明度
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # 创建透明图层用于绘制水印
                watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(watermark)
                
                # 获取字体
                font = self.get_font()
                
                # 获取文字尺寸
                bbox = draw.textbbox((0, 0), date_str, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # 计算位置
                x, y = self.get_position_coordinates(img.size, (text_width, text_height))
                
                # 解析颜色
                color = self.parse_color(self.config.color)
                
                # 设置透明度
                alpha = int(255 * self.config.opacity)
                color_with_alpha = (*color, alpha)
                
                # 绘制文字
                draw.text((x, y), date_str, font=font, fill=color_with_alpha)
                
                # 合并图层
                result = Image.alpha_composite(img, watermark)

                # 根据输出文件格式调整颜色模式，确保JPEG不包含Alpha通道
                try:
                    ext = Path(output_path).suffix.lower()
                except Exception:
                    ext = ""

                if ext in {'.jpg', '.jpeg'}:
                    if result.mode != 'RGB':
                        result = result.convert('RGB')
                else:
                    # 非JPEG可保持带Alpha的PNG/TIFF，若原图无Alpha也可以保持当前模式
                    pass

                # 保存图片
                save_kwargs = {}
                if ext in {'.jpg', '.jpeg'}:
                    save_kwargs['quality'] = 95
                elif ext in {'.png'}:
                    # 让Pillow为PNG自动处理压缩级别
                    save_kwargs['optimize'] = True
                else:
                    # 其他格式采用默认参数
                    pass

                result.save(output_path, **save_kwargs)
                
            logging.info(f"成功处理: {image_path} -> {output_path}")
            return True
            
        except Exception as e:
            logging.error(f"处理图片失败 {image_path}: {e}")
            return False
    
    def parse_color(self, color_str: str) -> Tuple[int, int, int]:
        """
        解析颜色字符串
        
        Args:
            color_str: 颜色字符串 (如 "red", "white", "255,0,0")
            
        Returns:
            RGB颜色元组
        """
        color_map = {
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'yellow': (255, 255, 0),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255)
        }
        
        if color_str.lower() in color_map:
            return color_map[color_str.lower()]
        
        # 尝试解析RGB格式 "255,0,0"
        if ',' in color_str:
            try:
                parts = color_str.split(',')
                if len(parts) == 3:
                    return (int(parts[0]), int(parts[1]), int(parts[2]))
            except ValueError:
                pass
        
        # 默认返回白色
        return (255, 255, 255)
    
    def process_file(self, input_path: str) -> bool:
        """
        处理单个文件
        
        Args:
            input_path: 输入文件路径
            
        Returns:
            是否成功
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            logging.error(f"文件不存在: {input_path}")
            return False
        
        if input_path.suffix.lower() not in self.supported_formats:
            logging.warning(f"不支持的图片格式: {input_path}")
            return False
        
        # 确定输出路径
        if self.config.output_dir:
            output_dir = Path(self.config.output_dir)
        else:
            # 在原目录下创建watermark子目录
            parent_dir = input_path.parent
            output_dir = parent_dir / f"{parent_dir.name}_watermark"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成输出文件名
        output_filename = f"{input_path.stem}_watermark{input_path.suffix}"
        output_path = output_dir / output_filename
        
        return self.add_watermark(str(input_path), str(output_path))
    
    def process_directory(self, input_dir: str) -> Tuple[int, int]:
        """
        批量处理目录
        
        Args:
            input_dir: 输入目录路径
            
        Returns:
            (成功数量, 总数量)
        """
        input_dir = Path(input_dir)
        
        if not input_dir.exists() or not input_dir.is_dir():
            logging.error(f"目录不存在: {input_dir}")
            return 0, 0
        
        # 查找所有支持的图片文件
        image_files = []
        for ext in self.supported_formats:
            image_files.extend(input_dir.glob(f"*{ext}"))
            image_files.extend(input_dir.glob(f"*{ext.upper()}"))
        
        if not image_files:
            logging.warning(f"目录中没有找到支持的图片文件: {input_dir}")
            return 0, 0
        
        # 处理每个文件
        success_count = 0
        total_count = len(image_files)
        
        print(f"开始批量处理 {total_count} 个文件...")
        
        for i, image_file in enumerate(image_files, 1):
            print(f"处理进度: {i}/{total_count} - {image_file.name}")
            
            if self.process_file(str(image_file)):
                success_count += 1
        
        print(f"批量处理完成: {success_count}/{total_count} 成功")
        return success_count, total_count


class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_file: str = "watermark_config.json"):
        self.config_file = Path(config_file)
    
    def save_config(self, config: WatermarkConfig) -> bool:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"保存配置失败: {e}")
            return False
    
    def load_config(self) -> Optional[WatermarkConfig]:
        """从文件加载配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return WatermarkConfig.from_dict(data)
        except Exception as e:
            logging.error(f"加载配置失败: {e}")
        return None


def setup_logging(verbose: bool = False):
    """设置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('watermark.log', encoding='utf-8')
        ]
    )


def interactive_mode():
    """交互模式"""
    print("=== 图片水印工具 - 交互模式 ===")
    print()
    
    # 获取输入路径
    while True:
        input_path = input("请输入图片文件或目录路径: ").strip()
        if input_path and Path(input_path).exists():
            break
        print("路径不存在，请重新输入。")
    
    # 创建配置
    config = WatermarkConfig()
    
    # 获取字体大小
    while True:
        try:
            font_size = input(f"字体大小 (默认: {config.font_size}): ").strip()
            if font_size:
                config.font_size = int(font_size)
            break
        except ValueError:
            print("请输入有效的数字。")
    
    # 获取颜色
    color = input(f"字体颜色 (默认: {config.color}): ").strip()
    if color:
        config.color = color
    
    # 获取位置
    print("可选位置: top-left, top-right, bottom-left, bottom-right, center")
    position = input(f"水印位置 (默认: {config.position}): ").strip()
    if position:
        config.position = position
    
    # 获取透明度
    while True:
        try:
            opacity = input(f"透明度 0-1 (默认: {config.opacity}): ").strip()
            if opacity:
                opacity_val = float(opacity)
                if 0 <= opacity_val <= 1:
                    config.opacity = opacity_val
                else:
                    print("透明度必须在0-1之间。")
                    continue
            break
        except ValueError:
            print("请输入有效的数字。")
    
    return input_path, config


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="图片水印工具 - 自动读取EXIF信息并添加时间水印",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python watermark_tool.py photo.jpg
  python watermark_tool.py photo.jpg --font-size 30 --color red --position top-left
  python watermark_tool.py /path/to/photos --font-size 20 --position bottom-right
  python watermark_tool.py  # 进入交互模式
        """
    )
    
    parser.add_argument('input', nargs='?', help='输入图片文件或目录路径')
    parser.add_argument('-i', '--input', dest='input_alt', help='输入图片文件或目录路径')
    parser.add_argument('-s', '--font-size', type=int, default=24, help='字体大小 (默认: 24)')
    parser.add_argument('-c', '--color', default='white', help='字体颜色 (默认: white)')
    parser.add_argument('-p', '--position', default='bottom-right', 
                       choices=['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'],
                       help='水印位置 (默认: bottom-right)')
    parser.add_argument('-o', '--opacity', type=float, default=0.8, help='透明度 0-1 (默认: 0.8)')
    parser.add_argument('--output', '-out', help='输出目录 (可选)')
    parser.add_argument('--font-path', help='字体文件路径 (可选)')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    parser.add_argument('--save-config', action='store_true', help='保存当前配置')
    parser.add_argument('--load-config', action='store_true', help='加载保存的配置')
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.verbose)
    
    # 确定输入路径
    input_path = args.input or args.input_alt
    
    # 如果没有输入路径，进入交互模式
    if not input_path:
        input_path, config = interactive_mode()
    else:
        # 创建配置
        config = WatermarkConfig()
        
        # 尝试加载保存的配置
        if args.load_config:
            config_manager = ConfigManager()
            saved_config = config_manager.load_config()
            if saved_config:
                config = saved_config
                print("已加载保存的配置")
        
        # 应用命令行参数
        config.font_size = args.font_size
        config.color = args.color
        config.position = args.position
        config.opacity = args.opacity
        config.output_dir = args.output
        config.font_path = args.font_path
    
    # 保存配置
    if args.save_config:
        config_manager = ConfigManager()
        if config_manager.save_config(config):
            print("配置已保存")
        else:
            print("配置保存失败")
    
    # 创建处理器
    processor = WatermarkProcessor(config)
    
    # 处理输入
    input_path = Path(input_path)
    
    if input_path.is_file():
        # 处理单个文件
        print(f"处理文件: {input_path}")
        success = processor.process_file(str(input_path))
        if success:
            print("处理完成!")
        else:
            print("处理失败!")
            sys.exit(1)
    elif input_path.is_dir():
        # 批量处理目录
        success_count, total_count = processor.process_directory(str(input_path))
        if success_count == 0:
            print("没有文件处理成功!")
            sys.exit(1)
        elif success_count < total_count:
            print(f"部分文件处理失败: {success_count}/{total_count}")
        else:
            print("所有文件处理完成!")
    else:
        print(f"路径不存在: {input_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
