# 图片水印工具 (Photo Watermark Tool)

一个基于Python的命令行程序，能够自动读取图片EXIF信息中的拍摄时间，并将其作为水印添加到图片上。

## 功能特性

- ✅ **自动EXIF读取**: 从图片EXIF信息中提取拍摄日期
- ✅ **灵活水印配置**: 支持自定义字体大小、颜色、位置和透明度
- ✅ **批量处理**: 支持处理单个文件或整个目录
- ✅ **多种图片格式**: 支持JPG、PNG、TIFF等常见格式
- ✅ **交互模式**: 提供友好的交互式界面
- ✅ **配置保存**: 支持保存和加载用户配置
- ✅ **错误处理**: 完善的错误处理和日志记录

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
# 处理单个图片文件
python watermark_tool.py photo.jpg

# 批量处理目录
python watermark_tool.py /path/to/photos

# 进入交互模式
python watermark_tool.py
```

### 高级用法

```bash
# 自定义水印样式
python watermark_tool.py photo.jpg --font-size 30 --color red --position top-left

# 设置透明度
python watermark_tool.py photo.jpg --opacity 0.6

# 指定输出目录
python watermark_tool.py photo.jpg --output /path/to/output

# 使用自定义字体
python watermark_tool.py photo.jpg --font-path /path/to/font.ttf
```

### 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--input` | `-i` | 输入图片文件或目录路径 | - |
| `--font-size` | `-s` | 字体大小 | 24 |
| `--color` | `-c` | 字体颜色 | white |
| `--position` | `-p` | 水印位置 | top-left |
| `--opacity` | `-o` | 透明度 (0-1) | 0.8 |
| `--output` | `-out` | 输出目录 | 自动生成 |
| `--font-path` | - | 字体文件路径 | 系统默认 |
| `--verbose` | `-v` | 详细输出 | False |
| `--save-config` | - | 保存当前配置 | False |
| `--load-config` | - | 加载保存的配置 | False |

### 水印位置选项

- `top-left`: 左上角
- `top-right`: 右上角
- `bottom-left`: 左下角
- `bottom-right`: 右下角
- `center`: 居中

### 颜色选项

支持预定义颜色名称：
- `red`, `green`, `blue`, `white`, `black`
- `yellow`, `cyan`, `magenta`, `orange`
- `purple`, `pink`, `gray`, `brown`

或RGB格式：`255,0,0` (红色)

## 输出说明

- 处理后的图片会保存在原目录下的 `原目录名_watermark` 子目录中
- 文件名格式：`原文件名_watermark.扩展名`
- 保持原图片格式和质量

## 配置文件

程序支持保存和加载配置文件 `watermark_config.json`：

```json
{
  "font_size": 24,
  "color": "white",
  "position": "top-left",
  "opacity": 0.8,
  "font_path": null
}
```

## 错误处理

- 如果图片没有EXIF信息，程序会使用文件修改时间
- 如果文件修改时间也无法获取，会使用当前时间
- 所有错误信息会记录在 `watermark.log` 文件中

## 系统要求

- Python 3.7+
- 支持的操作系统：Windows, macOS, Linux
- 内存要求：最低512MB RAM
- 存储空间：50MB (包含依赖)

## 依赖库

- `Pillow`: 图片处理
- `exifread`: EXIF信息读取

## 使用示例

### 示例1：基本使用
```bash
python watermark_tool.py vacation_photo.jpg
```
输出：在 `vacation_photo.jpg` 所在目录下创建 `目录名_watermark` 文件夹，保存带水印的图片。

### 示例2：自定义样式
```bash
python watermark_tool.py photo.jpg --font-size 36 --color "255,0,0" --position bottom-right --opacity 0.9
```
输出：红色水印，36号字体，右下角位置，90%透明度。

### 示例3：批量处理
```bash
python watermark_tool.py /Users/username/Pictures/2023 --font-size 20 --position top-left
```
输出：处理整个目录中的所有图片，统一添加左上角水印。

## 故障排除

### 常见问题

1. **"缺少必要的依赖库"错误**
   ```bash
   pip install -r requirements.txt
   ```

2. **"文件不存在"错误**
   - 检查文件路径是否正确
   - 确保文件存在且有读取权限

3. **"不支持的图片格式"警告**
   - 确保图片格式为：JPG, JPEG, PNG, TIFF, BMP
   - 检查文件扩展名是否正确

4. **水印位置不正确**
   - 检查位置参数是否正确
   - 尝试不同的位置选项

### 日志文件

程序运行时会生成 `watermark.log` 日志文件，包含详细的处理信息和错误记录。

## 开发信息

- **版本**: 1.0
- **作者**: 开发团队
- **日期**: 2025年
- **许可证**: 见 LICENSE 文件

## 贡献

欢迎提交Issue和Pull Request来改进这个工具！

## 更新日志

### v1.0 (2025年)
- 初始版本发布
- 支持EXIF信息读取
- 支持多种水印配置选项
- 支持批量处理
- 支持交互模式
- 支持配置文件保存/加载