# 换行符问题修复说明

## 问题描述
在Windows系统中使用Git时，可能会遇到以下警告：
```
warning: in the working copy of 'start_backend.sh', LF will be replaced by CRLF the next time Git touches it
```

## 问题原因
- **Linux/Unix系统** 使用 LF (`\n`) 作为换行符
- **Windows系统** 使用 CRLF (`\r\n`) 作为换行符
- Git在不同操作系统间处理文件时会自动转换换行符

## 解决方案

### 1. 已创建 `.gitattributes` 文件
项目根目录已创建 `.gitattributes` 文件，统一处理换行符：
- Shell脚本 (`.sh`) 使用 LF 换行符
- 批处理文件 (`.bat`) 使用 CRLF 换行符
- Python文件 (`.py`) 使用 LF 换行符

### 2. 已修复的文件
以下文件已修复换行符问题：
- `start_backend.sh`
- `deploy-auth.sh`
- `fix_frontend.sh`
- `rebuild.sh`
- `start.sh`

### 3. Git配置建议
在Windows系统中，建议配置Git：
```bash
git config core.autocrlf true
```

## 验证修复
可以使用以下命令验证换行符：
```bash
# 检查文件换行符类型
file start_backend.sh

# 或使用hexdump查看
hexdump -C start_backend.sh | head
```

## 注意事项
- 所有Shell脚本现在都使用标准的Unix换行符 (LF)
- 在Windows中编辑这些文件时，建议使用支持Unix换行符的编辑器
- VS Code默认会正确处理换行符转换

## 后续维护
- 新增Shell脚本时，确保使用LF换行符
- 新增批处理文件时，使用CRLF换行符
- `.gitattributes` 文件会自动处理换行符转换