# 黑塞德文原版（source-texts）

> 2026-08-10 从 gutenberg.org（美国站）恢复下载 + 群聊文件恢复（Sky 5/11 提供）。
> 背景：旧路径 hesse-knowledge-graph.BACKUP-20260515/source-texts/ 在 6/26 迁徙中丢失，本目录为重建。
> 第二批（2026-08-10 晚）：补齐 5 部 PG 版。
> 第三批（2026-08-10 晚）：**从飞书群聊恢复 3 部版权期内作品**（Sky 2026-05-11 在黑塞图谱群提供 z-library 版）。
> **11/11 全部恢复完成** ✅

## 文件清单（11 部全）

| 书名 | 文件 | 来源 | 版本信息 |
|------|------|------|---------|
| Der Steppenwolf | Steppenwolf_75802.txt | PG 75802 | Gesammelte Werke 版（标题页） |
| Demian | Demian_41907.txt | PG 41907 | S. Fischer Verlag, Berlin, 1921（27.-36. Auflage） |
| Siddhartha | Siddhartha_2499.txt | PG 2499 | 1922 年原版扫描（PG 制作说明） |
| Narziß und Goldmund | NarzissGoldmund_79173.txt | PG 79173 | Gesammelte Werke 版（标题页） |
| **Narziß und Goldmund** | **NarzissGoldmund_Suhrkamp_zlib.txt** | **群聊 Sky 5/11** | **Suhrkamp Verlag, Erste Buchausgabe Berlin 1930；3,316 行 = 5c ledger Bd. 8 记录** |
| **Narziß und Goldmund** | **NarzissGoldmund_Suhrkamp_zlib.epub** | **群聊 Sky 5/11** | epub 格式同版 |
| Peter Camenzind | PeterCamenzind_41051.txt | PG 41051 | 德语原版 |
| Unterm Rad | UntermRad_49908.txt | PG 49908 | 德语原版 |
| Gertrud | Gertrud_61266.txt | PG 61266 | 德语原版 |
| Rosshalde | Rosshalde_64466.txt | PG 64466 | 德语原版 |
| Klingsors letzter Sommer | Klingsor_42338.txt | PG 42338 | 德语原版 |
| **Die Morgenlandfahrt** | **Morgenlandfahrt_zlib.txt** | **群聊 Sky 5/11** | **505 行 = 5c ledger Bd. 8 记录（Suhrkamp 2001 全集）** |
| **Das Glasperlenspiel** | **Glasperlenspiel_zlib.txt** | **群聊 Sky 5/11** | **4,941 行 = 5c ledger Bd. 9 记录（Suhrkamp 2001 全集）；1.18MB 全本** |

## 恢复历史

1. **第一批（08-10 下午）**：PG 下载 4 部（Steppenwolf/Demian/Siddhartha/NarzissGoldmund）——论文《故乡》需要的核心
2. **第二批（08-10 晚）**：PG 下载 5 部（Camenzind/UntermRad/Gertrud/Rosshalde/Klingsor）
3. **第三批（08-10 晚）**：**群聊恢复 3 部版权期内作品**——Sky 2026-05-11 在黑塞图谱群提供 z-library 下载：
   - Narziss und Goldmund（txt + epub，Suhrkamp 版）
   - Die Morgenlandfahrt（txt）
   - Das Glasperlenspiel（txt）

## 验证记录

- **行号锚定**：3 部 z-library 文件行数与 5c 深读台账（Codex 2026-05-19 v2.0）记录的 Suhrkamp 版行数**完全一致**：
  - Glasperlenspiel = 4,941 行（Suhrkamp 2001 Ges. Werke Bd. 9）
  - Narziss = 3,316 行（Bd. 8）
  - Morgenlandfahrt = 505 行（Bd. 8）
  → 这就是 5/19 深读时用的原始文件，可继续用于论文引文逐字核对
- **关键词命中**：Magister Ludi ×626（GP）/ Morgenlandfahrt ×101（MF）/ Goldmund ×663（Narziss）
- **5/11 历史教训**：早期下载源曾贴错内容（Narziss=高尔基忏悔录英译本/Morgenlandfahrt=瑞典丹麦语小说/Glasperlenspiel=英语法律杂文）——Sky 提供的 z-library 版为**修正后正确版本**，已实测验证

## 用途与限制

- ✅ 可满足：德文引文**逐字核对**（文字验证）。已实测：论文《故乡》德米安"该隐之印"三处引文的德文原版全部在原版文本中定位成功：
  - "Leute mit Mut und Charakter sind den anderen Menschen immer unheimlich"（有勇气和个性的人，在他人看来总是骇人）→ Kain 章，>Zeichen< 段落
  - "der Kain war ein famoser Kerl, und bloß, weil man Angst vor ihm hatte, hängte man ihm diese Geschichte an"（是个卓越的人。人们因为怕他，才编出这种故事）
  - "Das Zeichen"（记号）解释段落
- ❌ 不满足：**实体书页码**引用。文本无分页，只有行号。页码仍需实体书（燕妮待补清单）或 5/31 初稿已验证的德文页码。

## 版权说明

- Hesse 1962 年去世，德国版权 70 年 → 2032 年才到期（德国站点 projekt-gutenberg.org 被 Cloudflare 拦截、gutenberg.spiegel.de 超时）。
- 美国版权法下 1922-1930 出版作品 2026 年已全部进入公有领域，gutenberg.org 合法提供德文全文。
- 3 部版权期内作品（Narziss 1930/Morgenlandfahrt 1932/Glasperlenspiel 1943）来自 Sky 本人提供的 z-library 文件（个人研究使用）。

## 验证方法

```bash
# 正文提取（跳过 PG header）
python3 -c "
import re
txt = open('Demian_41907.txt', encoding='utf-8').read()
m = re.search(r'\*\*\* START OF THE PROJECT GUTENBERG EBOOK.*?\*\*\*', txt)
print(txt[m.end():])
"
```
