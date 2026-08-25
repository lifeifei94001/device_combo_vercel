# 3C Matrix - 3C数码机型基本信息排列组合系统 (Vercel 云端部署版)

一键部署到 Vercel 的 3C 数码机型信息多维笛卡尔积排列组合在线系统。

---

## 🌟 云端部署特性

- 🌐 **全球高速 CDN 托管**：前端单页由 Vercel 全球边缘节点分发，手机/电脑浏览器秒开。
- ⚡ **Serverless 云端微服务**：后端算法通过 Python Serverless 函数执行，免去自建服务器和运维烦恼。
- 💾 **免数据库云端/本地记忆**：草稿记录与表单状态自动同步至浏览器 `localStorage`，刷新或下次打开数据不丢失。
- 📱 **3C 全系多维排列组合**：手机&平板（TB单位/三价格）、笔记本（四维顿号组合）、智能手表（六维组合与国行置顶）。

---

## 🚀 Vercel 部署指南 (3 步搞定)

### 步骤 1：上传至 GitHub
将本文件夹解压，把全部内容推送到你的 GitHub 仓库（设为 Private 隐私仓库即可）：
```bash
git init
git add .
git commit -m "feat: 3C Matrix Vercel Serverless Deploy"
git branch -M main
git remote add origin https://github.com/你的用户名/你的仓库名.git
git push -u origin main
```

### 步骤 2：在 Vercel 中一键导入
1. 访问 [Vercel 控制台](https://vercel.com/) 并使用 GitHub 账号登录。
2. 点击 **`Add New...` ➡️ `Project`**。
3. 选择刚才推送的 GitHub 仓库，点击 **`Import`**。
4. 无需修改任何环境变量或配置，直接点击 **`Deploy`**。

### 步骤 3：部署完成
约 1 分钟后，Vercel 会生成一个专属公网网址（例如 `https://3c-matrix.vercel.app`），即可直接在线使用并分享给团队！
