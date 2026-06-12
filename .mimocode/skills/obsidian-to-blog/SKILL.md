---
name: obsidian-to-blog
description: 将 Obsidian 笔记导入 Astro 博客并发布（import → fix → build → git push）
---

# Obsidian 笔记 → 博客发布

将一篇 Obsidian 笔记通过 `npm run import` 导入 Astro 博客项目，修复格式问题，构建验证，然后 git commit + push。

## 适用场景

用户给出一个 Obsidian 笔记路径（如 `D:\Obsidian\笔记\Redis\xxx.md`），要求导入博客并发布。

## 前置条件

- 博客项目目录下有 `scripts/import-post.cjs` 和 `npm run import` 脚本
- 博客项目使用 Astro + `src/content/posts/` 目录结构
- Obsidian 笔记为 `.md` 格式，含 frontmatter（title, date 等）

## 工作流程

### Step 1: 导入笔记

```bash
npm run import "<Obsidian笔记的完整路径>"
```

在博客项目根目录执行。脚本会：
- 读取 Obsidian 笔记内容
- 处理 `![[image.png]]` 格式的图片引用，复制到 `public/images/`
- 修正日期格式（`2026-5-14` → `2026-05-14`）
- 生成 slug 并写入 `src/content/posts/<slug>.md`

### Step 2: 检查导入结果

Read 导入后的文件，检查：

1. **frontmatter 完整性**：`title`, `date`, `description` 是否正确
2. **slug 质量**：文件名是否为英文、可读的 kebab-case（如 `redis-cluster.md`）
3. **图片引用**：`![[...]]` 是否已正确转换为 `![...](/images/...)`
4. **格式问题**：Obsidian 特有语法（callout、双链等）是否需要手动修复

### Step 3: 修复问题

常见修复：

- **中文文件名 → 英文 slug**：`mv src/content/posts/中文.md src/content/posts/english-slug.md`
- **frontmatter 补全**：添加 `description` 字段（从文章首段提取摘要）
- **日期格式**：确认 `date` 为 `YYYY-MM-DD` 格式
- **标题层级**：Obsidian 笔记可能以 `# Title` 开头，但 frontmatter 的 `title` 已包含标题时，移除重复的 `# Title`

### Step 4: 构建验证

```bash
npm run build
```

确认无报错。如果构建失败，根据错误信息修复。

### Step 5: Git 提交并推送

```bash
git add src/content/posts/<slug>.md public/images/
git commit -m "feat: add <文章标题> article"
git push
```

commit message 格式：`feat: add <title> article`（英文）或 `feat: 添加<标题>文章`（中文）。

## 注意事项

- 如果 Obsidian 笔记路径含空格，务必用双引号包裹
- 图片文件会被复制到 `public/images/`，文件名中的中文会被转为 kebab-case
- 多篇笔记批量导入时，每篇单独 commit 便于追溯
- 如果 `git push` 失败（网络问题），检查代理设置后重试
