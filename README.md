# 呆头鹅AI - Goose-Ai

基于Python 和Vue构建的智能AI应用平台，支持多模态对话、PDF文档智能问答、预约推荐等功能。

## 项目简介

傻子AI是一个综合性的AI应用平台，利用Python框架集成了多种AI服务（包括阿里通义千问、Ollama等），提供了智能对话、文档理解和课程推荐等功能。项目采用前后端分离架构，后端使用python/fastapi + ，前端使用Vue.js构建。

<img src=".\img\Snipaste_2026-01-27_16-53-55.png"  />

<img src="D:\code\goose-ai\img\Snipaste_2026-01-26_11-32-15.png" alt="Snipaste_2026-01-26_11-32-15"  />

![Snipaste_2026-01-27_16-54-10](.\img\Snipaste_2026-01-27_16-54-10.png)

![Snipaste_2026-01-27_16-54-36](.\img\Snipaste_2026-01-27_16-54-36.png)

![Snipaste_2026-01-27_16-55-44](.\img\Snipaste_2026-01-27_16-55-44.png)

![Snipaste_2026-01-27_16-56-11](.\img\Snipaste_2026-01-27_16-56-11.png)



## 功能特性

- 🤖 **智能对话** - 支持基于文本和多模态（图片、文件）的AI对话
- 📄 **PDF智能问答** - 上传PDF文档，实现基于文档内容的智能问答
- 📚 **预约推荐** - 基于AI的预约查询和推荐系统
- 🎓 **天气查询** - 查询天气信息(基于心知天气)
- 📝 **客服服务** - 智能生成回复
- 🧠 **向量检索** - 基于向量数据库的相似性搜索
- 🔗 **多AI模型支持** - 支持阿里通义千问、Ollama等多种AI模型

## 技术栈

### 后端技术
- **核心框架**: Python/FastApi
- **AI框架**: Langchain
- **向量库**: redis-stack
- **数据库**: MySQL
- **开发语言**: python3/Vue
- **构建工具**: ~

### AI相关技术
- **大语言模型**: 阿里通义千问 (Qwen-Max-Latest)
- **嵌入模型**: 文本嵌入 (text-embedding-v3)
- **向量存储**: 向量数据库
- **PDF处理**: PDF文档读取与解析
- **多模态支持**: 图像识别和处理

### 前端技术
- **框架**: Vue.js + Vite
- **构建工具**: Vite
- **UI组件**: 静态资源文件

## 项目结构

```

```

## 环境要求

- **JDK**: 17+
- **Python**: 3.13+
- **Maven**: 3.6+
- **MySQL**: 5.7+ 或 8.0+
- **Node.js**: 用于前端资源构建（如果需要）
- **Ollama** (可选): 用于本地AI模型部署

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd goose-ai

> server
.venv\Scripts\Activate.ps1

uvicorn main:app --reload    
 
fastapi dev main.py
```

### 2. 数据库配置

拉取redis-stack向量数据库

```dockerfile
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```

### 3. 修改配置

编辑 `.env` 文件，根据你的环境修改数据库连接信息：

```yaml

```

### 4. 构建项目

```bash
```

### 5. 启动应用

```powershell
# server
.venv\Scripts\Activate.ps1
Get-Command python

# client
npm install --ignore-scripts --legacy-peer-deps
npm run dev
```

或者在IDE中直接运行 `main.py` 类的 `main` 方法。

### 6. 访问应用

- 应用启动后，默认访问地址：[http://localhost:8080](http://localhost:8080)

## API接口

### 聊天接口

- **POST** `/ai/chat` - 智能聊天接口
  - 参数：
    - `prompt`: 用户输入的问题
    - `chatId`: 聊天会话ID
    - `files`: 可选，上传的文件（支持多模态）

### PDF文档接口

- **POST** `/ai/pdf/upload/{chatId}` - 上传PDF文档
  - 参数：
    - `chatId`: 聊天会话ID
    - `file`: PDF文件
- **GET** `/ai/pdf/chat` - PDF文档问答
  - 参数：
    - `prompt`: 问题
    - `chatId`: 聊天会话ID
- **GET** `/ai/pdf/file/{chatId}` - 下载PDF文件

## AI模型配置

项目支持多种AI模型：

1. **阿里通义千问** (默认)
   - 在 `application.yaml` 中配置阿里云API密钥
   - 使用 `qwen-max-latest` 模型

2. **Ollama本地模型**()
   - 需要本地安装并运行Ollama
   - 配置 `deepseek-r1:7b` 模型

## 核心功能介绍

### 1. 智能对话系统

支持普通文本对话和多模态对话（带图片、文档等附件）。系统会自动维护对话历史，保持上下文连贯。

### 2. PDF文档智能问答

用户可以上传PDF文档，然后针对文档内容提问。系统会利用向量检索技术，从文档中找到相关信息并生成答案。

### 3. AI工具调用

系统内置了多种AI工具：
- 预约查询工具
- 案件查询工具  
- 服务点预约工具

这些工具可以让AI根据用户需求执行特定操作。

### 4. 向量检索系统

基于向量数据库的相似性搜索，能够高效地从大量文档中找到与用户查询最相关的内容。

## 扩展开发

### 添加新的AI工具

创建一个新的工具类，

```java
@mcp.tools

```

### 自定义AI模型

项目中包含了自定义的 `AiChatModel`，可以根据需要调整模型行为。

## 部署说明

### 生产环境部署

1. 修改 `` 中的配置参数
2. 执行 `` 构建项目
3. 运行生成的JAR包

### Docker部署（可选）

如需使用Docker部署，可以创建Dockerfile：

```dockerfile
FROM openjdk:17-jdk-slim

```

## 注意事项

1. **API密钥安全** - 生产环境中应妥善保管API密钥，建议使用环境变量等方式管理
2. **数据库初始化** - 首次运行前确保数据库已创建并正确配置
3. **AI模型费用** - 使用在线AI服务可能会产生费用，请关注API调用成本
4. **文件上传限制** - 注意服务器文件上传大小限制

## 贡献指南

欢迎提交Issue和Pull Request来改进项目。

## 许可证

本项目仅供学习交流使用。

## 开发者

野猪佩奇 AI 团队
