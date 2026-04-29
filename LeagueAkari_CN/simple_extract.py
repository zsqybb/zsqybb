import tarfile
import os

# 解压文件
src = r'C:\Users\Lenovo\Downloads\dragontail-12.6.1.tgz'
dst = r'f:\code-tengxun\LeagueAkari_CN\datadragon'

print(f"解压: {src}")
print(f"到: {dst}")

os.makedirs(dst, exist_ok=True)

try:
    with tarfile.open(src, 'r:gz') as tar:
        tar.extractall(dst)
    print("✅ 解压成功！")
    
    # 显示目录结构
    print("\n文件结构:")
    for root, dirs, files in os.walk(dst):
        level = root.replace(dst, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        sub_indent = ' ' * 2 * (level + 1)
        for file in files[:3]:
            print(f'{sub_indent}{file}')
        if level >= 2:
            break
            
except Exception as e:
    print(f"❌ 错误: {e}")
