import os

def main():
    # 拆分D:\project\python\adk-python\adk-samples-zh\aaa.txt 文档内容
    markdwond_file = r"D:\project\python\adk-python\adk-samples-zh\aaa.txt"
    with open(markdwond_file, "r", encoding='utf-8') as f:
        lines = f.readlines()

    out_dir = r'D:\project\python\adk-python\adk-samples-zh'
    file_content = ''
    for line in lines:
        if line.startswith('```json'):
            continue
        if line.startswith("## 文件: "):
            if not file_content:
                continue
            file_path = out_dir + '\\' + line.split('## 文件: ')[1].strip()
            file_name = file_path.replace('\\', '/')
            file_path = '/'.join(file_name.split('/')[:-1])
            os.makedirs(file_path, exist_ok=True)
            if not file_name:
                print("="*90)
                print("没有文件名: ", line)
                file_name = ''
                continue
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(''.join(file_content))
            except Exception as e:
                print(f"写入文件 {file_name} 时出错: {e}")
            file_content = ''
        else:
            file_content += line


if __name__ == '__main__':
    main()
