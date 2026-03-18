#!/bin/bash

# Render部署准备脚本

echo "=========================================="
echo "  量化策略回测平台 - Render部署准备"
echo "=========================================="
echo ""

# 检查Git仓库
if [ ! -d ".git" ]; then
    echo "❌ 当前目录不是Git仓库"
    echo "正在初始化Git仓库..."
    git init
    echo "✅ Git仓库初始化完成"
else
    echo "✅ Git仓库已存在"
fi

echo ""
echo "=========================================="
echo "  检查必需文件"
echo "=========================================="

files_ok=true

# 检查后端文件
echo ""
echo "📁 检查后端文件..."
if [ -f "backend/app.py" ]; then
    echo "  ✅ backend/app.py"
else
    echo "  ❌ backend/app.py - 缺失"
    files_ok=false
fi

if [ -f "backend/strategy_adapter.py" ]; then
    echo "  ✅ backend/strategy_adapter.py"
else
    echo "  ❌ backend/strategy_adapter.py - 缺失"
    files_ok=false
fi

if [ -f "backend/Procfile" ]; then
    echo "  ✅ backend/Procfile"
else
    echo "  ❌ backend/Procfile - 缺失"
    files_ok=false
fi

if [ -f "backend/runtime.txt" ]; then
    echo "  ✅ backend/runtime.txt"
else
    echo "  ❌ backend/runtime.txt - 缺失"
    files_ok=false
fi

# 检查前端文件
echo ""
echo "📁 检查前端文件..."
if [ -f "frontend/package.json" ]; then
    echo "  ✅ frontend/package.json"
else
    echo "  ❌ frontend/package.json - 缺失"
    files_ok=false
fi

if [ -f "frontend/vite.config.js" ]; then
    echo "  ✅ frontend/vite.config.js"
else
    echo "  ❌ frontend/vite.config.js - 缺失"
    files_ok=false
fi

# 检查根目录文件
echo ""
echo "📁 检查根目录文件..."
if [ -f "requirements.txt" ]; then
    echo "  ✅ requirements.txt"
else
    echo "  ❌ requirements.txt - 缺失"
    files_ok=false
fi

if [ -f "render.yaml" ]; then
    echo "  ✅ render.yaml"
else
    echo "  ⚠️  render.yaml - 可选"
fi

echo ""
echo "=========================================="

if [ "$files_ok" = false ]; then
    echo "❌ 文件检查失败！请确保所有必需文件都存在。"
    exit 1
fi

echo "✅ 所有必需文件检查通过！"
echo ""

# 检查是否已配置远程仓库
if git remote get-url origin > /dev/null 2>&1; then
    echo "📦 已配置远程仓库: $(git remote get-url origin)"
else
    echo ""
    echo "⚠️  尚未配置远程仓库"
    echo ""
    echo "请按以下步骤操作："
    echo "1. 在GitHub上创建新仓库"
    echo "2. 运行以下命令连接仓库："
    echo ""
    echo "   git remote add origin https://github.com/你的用户名/仓库名.git"
    echo ""
    read -p "是否现在配置远程仓库？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "请输入GitHub仓库URL: " repo_url
        git remote add origin "$repo_url"
        echo "✅ 远程仓库配置完成"
    else
        echo "❌ 请先配置远程仓库后再运行此脚本"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "  准备提交代码"
echo "=========================================="

# 添加所有文件
echo ""
echo "📝 添加文件到暂存区..."
git add .

# 检查是否有更改
if git diff --cached --quiet; then
    echo "⚠️  没有新的更改需要提交"
    echo ""
    echo "如果要强制部署，可以使用："
    echo "  git commit --amend --no-edit"
    echo "  git push -f origin main"
    exit 0
fi

# 提交
echo "✅ 文件已添加到暂存区"
echo ""
read -p "请输入提交信息 (默认: Deploy to Render): " commit_msg
commit_msg=${commit_msg:-"Deploy to Render"}

echo ""
echo "📤 提交代码: $commit_msg"
git commit -m "$commit_msg"

echo ""
echo "=========================================="
echo "  推送到GitHub"
echo "=========================================="

echo ""
echo "🚀 正在推送到GitHub..."
git push -u origin main

echo ""
echo "=========================================="
echo "✅ 代码已成功推送到GitHub！"
echo "=========================================="
echo ""
echo "下一步："
echo ""
echo "1. 访问 https://dashboard.render.com"
echo "2. 点击 'New +' → 'Blueprint'"
echo "3. 连接您的GitHub仓库"
echo "4. 选择 render.yaml 文件"
echo "5. 点击 'Apply Blueprint'"
echo ""
echo "或手动部署（参考 Render部署指南.md）"
echo ""
echo "=========================================="
