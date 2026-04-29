import tarfile
import os

# 解压Data Dragon资源包
tar_path = r'C:\Users\Lenovo\Downloads\dragontail-12.6.1.tgz'
extract_path = r'f:\code-tengxun\LeagueAkari_CN\datadragon'

print(f"正在解压: {tar_path}")
print(f"目标路径: {extract_path}")

try:
    with tarfile.open(tar_path, 'r:gz') as tf:
        tf.extractall(extract_path)
    print("✅ 解压成功！")
    
    # 列出解压后的文件
    print("\n解压后的文件结构:")
    for root, dirs, files in os.walk(extract_path):
        level = root.replace(extract_path, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        sub_indent = ' ' * 2 * (level + 1)
        for file in files[:5]:  # 只显示前5个文件
            print(f'{sub_indent}{file}')
        if len(files) > 5:
            print(f'{sub_indent}... 还有 {len(files)-5} 个文件')
        if level >= 2:  # 只显示2层
            break
except Exception as e:
    print(f"❌ 解压失败: {e}")
