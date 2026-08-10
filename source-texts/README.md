# 黑塞德文原版（source-texts）

> 2026-08-10 从 gutenberg.org（美国站）恢复下载。
> 背景：旧路径 hesse-knowledge-graph.BACKUP-20260515/source-texts/ 在 6/26 迁徙中丢失，本目录为重建。
> 第二批（2026-08-10 晚）：补齐 5 部，当前共 9 部。

## 文件清单

| 书名 | 文件 | PG ebook ID | 版本信息 |
|------|------|-------------|---------|
| Der Steppenwolf | Steppenwolf_75802.txt | 75802 | Gesammelte Werke 版（标题页） |
| Demian | Demian_41907.txt | 41907 | S. Fischer Verlag, Berlin, 1921（27.-36. Auflage） |
| Siddhartha | Siddhartha_2499.txt | 2499 | 1922 年原版扫描（PG 制作说明） |
| Narziß und Goldmund | NarzissGoldmund_79173.txt | 79173 | Gesammelte Werke 版（标题页） |
| Peter Camenzind | PeterCamenzind_41051.txt | 41051 | 德语原版（第二批补齐） |
| Unterm Rad | UntermRad_49908.txt | 49908 | 德语原版（第二批补齐） |
| Gertrud | Gertrud_61266.txt | 61266 | 德语原版（第二批补齐） |
| Rosshalde | Rosshalde_64466.txt | 64466 | 德语原版（第二批补齐） |
| Klingsors letzter Sommer | Klingsor_42338.txt | 42338 | 德语原版（第二批补齐） |

## 尚未恢复（版权限制）

| 书名 | 年份 | 原因 |
|------|------|------|
| Die Morgenlandfahrt | 1932 | 德国版权 70 年 → 2032 到期；美国站无德文版 |
| Das Glasperlenspiel | 1943 | 德国版权 70 年 → 2043 到期；美国站无德文版 |

> 这两部在合法免费源（PG 美国站 / projekt-gutenberg.org / spiegel 镜像）均无德文全文。
> 旧库曾有（BACKUP-20260515 索引标注 Suhrkamp 版行号），6/26 迁徙丢失且 git 无残留。
> 可替代：德语实体书（燕妮手头）/ 图书馆电子资源。

## 用途与限制

- ✅ 可满足：德文引文**逐字核对**（文字验证）。已实测：论文《故乡》德米安"该隐之印"三处引文的德文原版全部在原版文本中定位成功：
  - "Leute mit Mut und Charakter sind den anderen Menschen immer unheimlich"（有勇气和个性的人，在他人看来总是骇人）→ Kain 章，>Zeichen< 段落
  - "der Kain war ein famoser Kerl, und bloß, weil man Angst vor ihm hatte, hängte man ihm diese Geschichte an"（是个卓越的人。人们因为怕他，才编出这种故事）
  - "Das Zeichen"（记号）解释段落
- ❌ 不满足：**实体书页码**引用。PG 文本无分页，只有行号。页码仍需实体书（燕妮待补清单）或 5/31 初稿已验证的德文页码。

## 版权说明

- Hesse 1962 年去世，德国版权 70 年 → 2032 年才到期（德国站点 projekt-gutenberg.org 被 Cloudflare 拦截、gutenberg.spiegel.de 超时）。
- 美国版权法下四本书（1922-1930 出版）2026 年已全部进入公有领域，gutenberg.org 合法提供德文全文。

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
