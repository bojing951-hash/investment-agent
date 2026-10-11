"""
投资周报生成器
调用智谱 GLM API，基于数据包 + 分析框架生成周报初稿
生成后: ①解析论点状态块回写 thesis.json ②用同日锚点校验报告数值
"""

import os
import sys
import json
import glob
import re
import shutil
import io
import subprocess
import contextlib
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from env_config import GLM_API_KEY, GLM_BASE_URL, GLM_MODEL
import allocation_engine  # P2/P3 配置研究引擎(同目录)

# ============ 路径配置 ============
PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')
DATA_DIR = os.path.join(PROJECT_DIR, 'data')
CONFIG_DIR = os.path.join(PROJECT_DIR, 'config')
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'output', 'weekly')

# ============ 分析框架（从外部文件加载） ============
ANALYSIS_FRAMEWORK = None  # 将从外部文件加载

# ============ 系统提示词(配置化, 2026-10-11 P1) ============
# 提示词外移到 config/prompts/*.md,热加载:改文件即生效,无需改代码。
# v2角色: "首席宏观研究员兼投资委员会秘书"(用户提供,外部AI协助设计)
PROMPTS_DIR = os.path.join(CONFIG_DIR, 'prompts')

def load_prompt(name):
    """加载 config/prompts/ 下的提示词文件。缺失即硬中断——
    宁可流水线失败报警(六.2已保证exit code传播),也不静默用旧提示词生成。"""
    path = os.path.join(PROMPTS_DIR, name)
    if not os.path.exists(path):
        print(f"❌ 提示词文件缺失: {path}")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    print(f"✅ 已加载提示词 {name} ({len(content)} 字符)")
    return content

def load_framework():
    """从外部文件加载分析框架"""
    framework_path = os.path.join(CONFIG_DIR, 'framework.md')

    if os.path.exists(framework_path):
        with open(framework_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ 已加载分析框架: {framework_path}")
        print(f"   大小: {len(content)} 字符")
        return content
    else:
        print(f"⚠️ 框架文件不存在: {framework_path}")
        print("   将使用默认框架")
        return """
## 默认分析框架
- HY OAS > 400bp：信用恶化
- VIX > 25：恐慌
- DXY < 100：美元弱势
- 10Y实际利率 > 2.5%：压制黄金和成长股
"""

def load_theses():
    """加载论点追踪文件"""
    thesis_path = os.path.join(CONFIG_DIR, 'thesis.json')

    if os.path.exists(thesis_path):
        with open(thesis_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        theses = data.get('theses', [])
        print(f"✅ 已加载论点: {len(theses)} 个")

        # 转为文本供AI阅读
        lines = []
        lines.append("## 当前活跃论点")
        lines.append(f"最后更新: {data.get('last_updated', '未知')}")
        lines.append("")

        for t in theses:
            stars = "★" * t.get('confidence', 0) + "☆" * (5 - t.get('confidence', 0))
            lines.append(f"### 论点#{t['id']}: {t.get('name', t.get('title', '未知'))}")
            lines.append(f"- 状态: {t.get('status', '进行中')} | 确信度: {stars}")
            lines.append(f"- 方向: {t.get('direction', '-')}")
            lines.append(f"- 逻辑: {t.get('core_logic', t.get('logic', '-'))}")
            lines.append(f"- 关键数据: {t.get('key_data', '-')}")
            # 失效/降级规则 (v2.0格式)
            inv = t.get('invalidation_rules', {})
            if inv:
                lines.append(f"- 降级条件: {inv.get('downgrade_to_观察', '-')}")
                fail_conditions = inv.get('失效条件', [])
                if fail_conditions:
                    lines.append(f"- 失效条件: {'; '.join(fail_conditions)}")
            # 旧格式兼容
            elif t.get('trigger_downgrade'):
                lines.append(f"- 降级触发: {t['trigger_downgrade']}")
            lines.append(f"- 升级触发: {t.get('upgrade_trigger', t.get('trigger_upgrade', '-'))}")
            related = t.get('related_theses', [])
            if related:
                notes = t.get('relation_notes', '')
                lines.append(f"- 关联论点: #{', #'.join(map(str, related))} ({notes})")
            lines.append(f"- 历史: {'; '.join(t.get('history', []))}")
            lines.append("")

        return '\n'.join(lines)
    else:
        print("⚠️ 论点文件不存在，跳过论点追踪")
        return ""

def load_previous_report():
    """加载上一期周报摘要，供AI对比"""
    output_dir = os.path.join(PROJECT_DIR, 'output', 'weekly')

    if not os.path.exists(output_dir):
        print("⚠️ 无历史报告")
        return ""

    files = sorted([f for f in os.listdir(output_dir) if f.startswith('weekly_report_')], reverse=True)

    if len(files) < 1:
        print("⚠️ 无历史报告")
        return ""

    # 2026-10-11修复: 原逻辑"多份时取第二新"假设最新的是本次要覆盖的,但正常周节奏下
    # 最新一份就是上期报告(本次的还没生成),导致下周五会跳过上期、加载两周前的。
    # 正确逻辑: 排除今天将生成/覆盖的同名文件后,取最新一份。
    today_name = f"weekly_report_{datetime.now().strftime('%Y%m%d')}.md"
    candidates = [f for f in files if f != today_name]
    if not candidates:
        print("⚠️ 无历史报告(仅有今日文件)")
        return ""
    target_file = candidates[0]

    filepath = os.path.join(output_dir, target_file)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 只取前60行作为摘要: 控制输入长度(过长会触发GLM 1301风控且拖慢思考)
        lines = content.split('\n')
        summary = '\n'.join(lines[:60])

        if len(lines) > 60:
            summary += f"\n\n... [上期报告共{len(lines)}行，此处截取前60行]"

        print(f"✅ 已加载上期报告: {target_file}")
        print(f"   原始 {len(lines)} 行，截取 {min(60, len(lines))} 行")
        return summary

    except Exception as e:
        print(f"⚠️ 读取上期报告失败: {e}")
        return ""

def load_data_pack(date_str=None):
    """加载最新的数据包"""
    weekly_dir = os.path.join(DATA_DIR, 'weekly')

    if date_str:
        filepath = os.path.join(weekly_dir, f'data_pack_{date_str}.md')
    else:
        # 找最新的数据包
        files = [f for f in os.listdir(weekly_dir) if f.startswith('data_pack_')]
        if not files:
            print("❌ 未找到数据包，请先运行 data_assembler.py")
            return None
        files.sort(reverse=True)
        filepath = os.path.join(weekly_dir, files[0])

    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"✅ 已加载数据包: {filepath}")
    print(f"   大小: {len(content)} 字符")
    return content

def load_technical_notes():
    """加载用户的技术面笔记"""
    notes_path = os.path.join(CONFIG_DIR, 'technical_notes.md')

    if os.path.exists(notes_path):
        with open(notes_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 截断到2000字符: 模板占位为主时全文只会增加token和风控风险
        if len(content) > 2000:
            content = content[:2000] + "\n... [技术面笔记已截断]"

        # 检查是否还是模板（没有实际内容）
        if '[你填写]' in content or '[你的判断]' in content:
            # 统计已填写的部分
            unfilled = content.count('[你填写]') + content.count('[你的判断]')
            filled = content.count('---') - 1  # 粗略估计有内容的部分
            print(f"✅ 已加载技术面笔记: {notes_path}")
            print(f"   ⚠️ 部分内容待填写（{unfilled}处未填）")
        else:
            print(f"✅ 已加载技术面笔记: {notes_path}")
            print(f"   大小: {len(content)} 字符")

        return content
    else:
        print("⚠️ 技术面笔记不存在，报告中技术面将由AI标注为待补充")
        return ""

def load_news_summary():
    """加载最近7天的新闻摘要并去重(含合规脱敏)

    2026-10-11修复: 此前只取最新一天的news_summary,周一至周四的新闻全部丢弃。
    同一标题会在多天重复出现(持续性事件),按标题精确去重,保留首次出现(旧→新排列)。
    """
    news_dir = os.path.join(DATA_DIR, 'news')

    if not os.path.exists(news_dir):
        print("⚠️ 无新闻数据")
        return ""

    cutoff = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
    files = sorted([f for f in os.listdir(news_dir)
                    if f.startswith('news_summary_') and f[-11:-3] >= cutoff])
    if not files:
        print("⚠️ 近7天无新闻摘要文件")
        return ""

    seen, blocks, total, dup = set(), [], 0, 0
    for fname in files:  # 旧→新
        try:
            with open(os.path.join(news_dir, fname), 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            continue
        day = fname[-11:-3]
        day_lines = [f"### {day} 新闻"]
        for line in sanitize_news(content).split('\n'):
            s = line.strip()
            if s.startswith('- '):          # 新闻条目:跨天去重
                if s in seen:
                    dup += 1
                    continue
                seen.add(s)
            elif not (s.startswith('#') or s.startswith('生成时间') or s == '---' or not s):
                continue                     # 跳过标题/元信息行
            elif s.startswith('#'):
                continue
            day_lines.append(line)
        # 只保留有实际条目的日子
        if sum(1 for l in day_lines if l.strip().startswith('- ')) > 0:
            blocks.append('\n'.join([l for l in day_lines if l.strip()]))
            total += 1

    # 超长时从最旧的一天开始丢弃(保新弃旧),仍超长才硬截断
    while blocks and sum(len(b) for b in blocks) > 9000:
        dropped = blocks.pop(0)
        print(f"   ⚠️ 新闻过长,丢弃最旧一天({dropped.splitlines()[0][:20]}...)")
    merged = '\n\n'.join(blocks)
    if len(merged) > 9000:  # 单日也超长的极端情况,控制长度防GLM 1301风控
        merged = merged[:9000] + "\n... [本周新闻过长已截断]"

    print(f"✅ 已加载近7天新闻: {total}天文件, 去重{dup}条重复, {len(merged)}字符")
    return merged


def sanitize_news(text):
    """新闻脱敏: 板块白名单 + 敏感词黑名单(2026-09-30)
    智谱GLM内容风控(1301)会拦截战争/军事/敏感组织类内容,原Reuters新闻标题常触发。
    只保留财经板块,并过滤军事冲突相关条目。地缘因素对市场的影响仍可从油价等数据侧体现。
    """
    import re
    ALLOWED_SECTIONS = ['美联储/利率', '信用/债务', '美股/科技', '黄金/商品', '美元/外汇', '中国/亚洲', '实体经济', '能源/石油']
    SENSITIVE = re.compile(
        r'(?i)hamas|gaza|hezbollah|houthi|ukraine|ukrainian|north korean|朝鲜|west bank|settler|'
        r'netanyahu|putin|zelensky|\bwar\b|\bwars\b|missile|explosive|\bpow\b|military|airstrike|'
        r'袭击|空袭|击毙|战争|导弹|阵亡|\biran\b|iranian|israel|以色列|'
        r'sanction|制裁|defense minister|pentagon')
    out, current_allowed = [], False
    for line in text.split('\n'):
        if line.startswith('### '):
            current_allowed = any(s in line for s in ALLOWED_SECTIONS)
            if current_allowed:
                out.append(line)
            continue
        if not current_allowed:
            continue
        if line.strip().startswith('- ') and SENSITIVE.search(line):
            continue
        out.append(line)
    return '\n'.join(out)

def generate_report(data_pack, framework=None, theses=None, prev_report=None, tech_notes=None, news_summary=None, views_block=None):
    """调用智谱 GLM 生成周报(views_block: P2配置观点库,渲染自allocation_views.json)"""

    today = datetime.now()
    # 计算本周的周一和周日
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    week_range = f"{monday.strftime('%Y%m%d')}-{sunday.strftime('%Y%m%d')}"

    # P1(2026-10-11): 提示词改为 config/prompts/ 热加载
    system_prompt = load_prompt('system_prompt.md')
    style_constraint = load_prompt('style_constraints.md')

    user_prompt = f"""请基于以下数据和分析框架，生成本周（{week_range}）的投资周报。

{style_constraint}

## 分析框架
{framework or ANALYSIS_FRAMEWORK or '见系统提示词'}

## 上期报告摘要（供对比参考）
{prev_report if prev_report else '无上期报告，这是第一期。'}

## 配置观点库（上期各资产评级，供第五节各资产小节与第七节引用）
{views_block if views_block else '观点库缺失，本周跳过配置观点，各资产小节不标注评级。'}

## 用户技术面观察
{tech_notes if tech_notes else '用户未提供技术面笔记，技术面部分请标注[待用户补充]'}

## 本周重要新闻
{news_summary if news_summary else '无新闻数据'}

## 本周市场数据
{data_pack}

## 输出要求

请严格按照以下结构输出：

### 一、本周摘要（3-5句话概括核心变化）

### 二、宏观体制判断
- 当前体制及判断依据
- 与上周相比是否有变化

### 三、本周新闻叙事
**主线新闻**：本周最重要的1-2条新闻事件及其市场影响
**次要新闻**：其他值得关注的新闻（2-3条）
**新闻驱动的市场变化**：哪些资产价格/板块因新闻而发生显著变化

### 四、资产表现总览
（整理为表格，包含资产名称、收盘价、周涨跌幅、关键信号）

### 五、分资产深度分析
（每个资产小节末尾加一行"配置观点: 评级|确信度★"，评级取自上方配置观点库的超配/标配/中性/低配/观望；
若本周触发该资产的升降级条件，才输出"调整提案"：动作与理由、证据及反证、风险与最大容忍损失、失效条件、下一复核日；未触发则只维持原评级）

#### 5.1 美股
- 指数表现与技术位置
- 关键驱动因素
- 技术面分析（结合用户技术面笔记，如用户已提供关键支撑/阻力/形态则直接使用，未提供则标注[待用户补充]）

#### 5.2 利率与久期
- 收益率曲线变化
- 实际利率与通胀预期分解
- 对其他资产的影响

#### 5.3 信用市场
- HY OAS 水平及阈值距离
- 分评级利差变化
- 私募信贷/CLO 风险信号

#### 5.4 美元
- DXY 水平与趋势
- "Sell America"信号检查
- 对新兴市场和商品的影响

#### 5.5 贵金属
- 金价驱动分解（实际利率 vs 避险 vs 美元）
- 金银比信号
- ETF/央行持仓（如有数据）

#### 5.6 能源
- 油价水平与供需
- Brent-WTI 价差
- 对通胀预期的传导

#### 5.7 A股与港股
- 指数表现
- 南向资金动态
- 成交量与底部条件检查

#### 5.8 加密货币
- BTC 表现与趋势信号

### 六、核心矛盾与风险
- 列出 2-3 个当前市场最主要的矛盾
- 每个矛盾的两面力量和可能的解决方向

### 七、下周关注
- 关键事件日历
- 需要监控的阈值和触发条件
- 情景概率判断

### 八、论点追踪
{theses if theses else '暂无历史论点'}

请根据本周数据，对每个论点进行以下判断：
1. 确信度是否需要调整（升/降/维持）
2. 是否触发了升级或降级条件
3. 状态是否需要变更（进行中/已验证/已失效/观察中）
4. 用一句话说明本周证据
5. 报告正文全部结束后，必须另起一行输出"论点状态块"（HTML注释包裹，渲染时不可见，供脚本解析回写thesis.json），
   格式严格如下，每个论点一行、共9行、一行一个JSON对象、不得包裹代码块围栏：

<!--THESIS_STATUS
{{"id":1,"status":"进行中","confidence":3,"note":"≤40字本周证据"}}
{{"id":2,"status":"待观察","confidence":2,"note":"..."}}
THESIS_STATUS-->

status只能取: 进行中/待观察/已验证/已失效；confidence为1-5整数；id与thesis.json一致。

6. 紧跟THESIS_STATUS块之后，输出"配置观点块"（HTML注释，同格式，每个资产一行、共9行）：

<!--ALLOCATION_STATUS
{{"id":1,"rating":"中性","confidence":2,"note":"≤40字本周理由"}}
{{"id":2,"rating":"低配","confidence":3,"note":"..."}}
ALLOCATION_STATUS-->

rating只能取: 超配/标配/中性/低配/观望；id与allocation_views.json一致（1美股/2利率久期/3信用/4美元/5贵金属/6能源/7A股港股/8加密/9现金短债）。
仅当本周发生评级变更时，在该行附加预测字段（方向+期限）：
{{"id":5,"rating":"标配","confidence":3,"note":"...","pred":"若XXX则两周内YYY","pred_weeks":2}}

7. 若观点库中有"⏰已到期"的预测，先在报告第七节给出命中/证伪判断，并在最后输出预测裁决块：

<!--PREDICTION_STATUS
{{"pred_id":1,"status":"hit","note":"≤30字裁决依据"}}
PREDICTION_STATUS-->

status只能取: hit/miss/expired。

注意：
- 所有数字精确到小数点后两位
- 每个判断标注确信度（★ 到 ★★★★★）
- 技术分析部分标注"[待用户补充]"
- 如果数据不足以支撑某个判断，明确说明
"""

    print("\n🤖 正在调用智谱 GLM 生成周报...")
    print(f"   模型: {GLM_MODEL} (智谱v4通道·流式)")
    print(f"   输入长度: 约 {len(system_prompt) + len(user_prompt)} 字符")

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            report_text = _call_glm(system_prompt, user_prompt)
            if not report_text or len(report_text.strip()) < 500:
                raise ValueError(f"返回内容过短({len(report_text or '')}字符),疑似被截断")
            print(f"✅ 生成完成！报告长度: {len(report_text)} 字符")
            return report_text

        except Exception as e:
            print(f"❌ 第{attempt}次调用失败: {str(e)[:200]}")
            if attempt < max_attempts:
                import time
                wait = attempt * 15
                print(f"   {wait}秒后重试...")
                time.sleep(wait)

    print("❌ GLM API 连续3次调用失败,放弃")
    return None


def _call_glm(system_prompt, user_prompt, max_tokens=32000, timeout=900):
    """调用智谱GLM(paas/v4 OpenAI兼容通道, 流式)

    实测踩坑记录(2026-09-30, glm-5.3):
    1. 非流式长时间生成会被网关断连(RemoteDisconnected) → 必须流式
    2. glm-5.3思考不可关闭,会吃光max_tokens导致正文为空 → reasoning_effort=low控制思考档位
    3. 过长的旧报告/笔记输入会触发1301内容风控 → load_previous_report/load_technical_notes已做截断,
       新闻已做sanitize_news脱敏
    """
    from openai import OpenAI

    client = OpenAI(api_key=GLM_API_KEY, base_url=GLM_BASE_URL, timeout=timeout)
    stream = client.chat.completions.create(
        model=GLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.3,
        extra_body={"reasoning_effort": "low"},
        stream=True,
        stream_options={"include_usage": True},
    )
    chunks = []
    for ev in stream:
        if ev.choices and ev.choices[0].delta and ev.choices[0].delta.content:
            chunks.append(ev.choices[0].delta.content)
    text = "".join(chunks)
    if not text.strip():
        raise RuntimeError("流式返回正文为空(疑似思考耗尽或风控拦截)")
    return text

def save_report(report_text, date_str=None):
    """保存报告"""
    if not date_str:
        date_str = datetime.now().strftime('%Y%m%d')

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 保存 Markdown(GLM输出自带标题,这里只写一行元信息避免双标题)
    md_path = os.path.join(OUTPUT_DIR, f'weekly_report_{date_str}.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"<!-- 生成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {GLM_MODEL} | investment-agent -->\n\n")
        f.write(report_text)

    print(f"\n📄 报告已保存:")
    print(f"   Markdown: {md_path}")
    print(f"   大小: {os.path.getsize(md_path)} 字节")

    return md_path

# ============ 生成后闭环(2026-10-11) ============
# 此前两个缺口:
#  ① 论点状态只活在报告散文里,thesis.json自2026-04-12从未更新 → 靠解析状态块回写
#  ② validate_report每天07:00校验的是"昨天的报告vs今天的锚点",报告生成后无人校验 → 生成后立即用同日锚点校验

ALLOWED_STATUS = {'进行中', '待观察', '已验证', '已失效'}

# ============ 月报/季报触发(P4, 2026-10-11) ============
def is_last_friday_of_month(d=None):
    """月末最后一个周五(月报触发条件)。非周五直接False。"""
    d = d or datetime.now()
    if d.weekday() != 4:
        return False
    return (d + timedelta(days=7)).month != d.month

def is_last_friday_of_quarter(d=None):
    """季末月(3/6/9/12)的最后一个周五(季报触发条件)。"""
    d = d or datetime.now()
    return is_last_friday_of_month(d) and d.month in (3, 6, 9, 12)

def _has_numeric_errors(warnings):
    """P0修复(六.7): 数值类错误(严重错误/偏差超容差)应阻止论点状态回写。
    样式类警告(如A股口径标注)不阻止——那不影响判断依据的数字本身。"""
    for w in warnings:
        if w.startswith('🚨') or (w.startswith('❌') and ('偏差' in w or '锚点' in w or '超出合理范围' in w)):
            return True
    return False

def update_thesis_status(report_text):
    """解析报告末尾的THESIS_STATUS块,回写 config/thesis.json 的 status/confidence/history"""
    m = re.search(r'<!--\s*THESIS_STATUS\s*(.*?)\s*THESIS_STATUS\s*-->', report_text, re.DOTALL)
    if not m:
        print("⚠️ 报告中未找到THESIS_STATUS块,论点状态未回写(下期仍以上期报告散文衔接)")
        return []

    block = m.group(1).replace('```json', '').replace('```', '')
    objs = []
    try:
        parsed = json.loads(block.strip())
        objs = parsed if isinstance(parsed, list) else [parsed]
    except Exception:
        for mm in re.finditer(r'\{[^{}]*\}', block):
            try:
                objs.append(json.loads(mm.group(0)))
            except Exception:
                pass

    if not objs:
        print("⚠️ THESIS_STATUS块解析失败(无有效JSON),论点状态未回写")
        return []

    thesis_path = os.path.join(CONFIG_DIR, 'thesis.json')
    with open(thesis_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    today = datetime.now()
    tag = f"{today.month}/{today.day}"
    updates = []
    for o in objs:
        tid = o.get('id')
        t = next((x for x in data['theses'] if x.get('id') == tid), None)
        if t is None:
            continue

        new_status = str(o.get('status', '')).strip()
        conf = o.get('confidence')
        note = str(o.get('note', '')).strip()[:60]

        if new_status in ALLOWED_STATUS and new_status != t.get('status'):
            t['status'] = new_status
            updates.append(f"#{tid}{t.get('name', '')[:10]}: 状态→{new_status}")
        if isinstance(conf, (int, float)) and conf == int(conf) and 1 <= int(conf) <= 5:
            t['confidence'] = int(conf)

        # history追加(同日重复运行不重复记)
        hist = t.setdefault('history', [])
        if hist and hist[-1].startswith(f"{tag} "):
            hist[-1] = f"{tag} {t.get('status', '进行中')} {t.get('confidence', 0)}★ {note}".rstrip()
        else:
            hist.append(f"{tag} {t.get('status', '进行中')} {t.get('confidence', 0)}★ {note}".rstrip())
        t['history'] = hist[-12:]  # 每论点只留最近12条

    data['last_updated'] = today.strftime('%Y-%m-%d')

    # 备份旧版+原子写回
    shutil.copy(thesis_path, thesis_path + '.bak')
    tmp = thesis_path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, thesis_path)

    print(f"✅ thesis.json 已回写(备份: thesis.json.bak)")
    for u in updates:
        print(f"   {u}")
    return updates

def validate_generated_report(md_path):
    """用最新锚点(与报告同日生成)校验刚生成的报告,结果落 logs/validation_*.log 并附注到报告尾部"""
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    anchor_files = sorted(glob.glob(os.path.join(ROOT_DIR, 'data', 'daily', 'anchors_*.json')))
    if not anchor_files:
        print("⚠️ 无锚点文件,跳过校验")
        return []

    with open(anchor_files[-1], 'r', encoding='utf-8') as f:
        anchors = json.load(f)

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import data_validator

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        warnings = data_validator.validate_report(md_path, anchors)

    date_str = datetime.now().strftime('%Y%m%d')
    log_path = os.path.join(PROJECT_DIR, 'logs', f'validation_{date_str}.log')
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f"报告校验 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"报告: {md_path}\n锚点: {anchor_files[-1]}\n")
        f.write("=" * 60 + "\n")
        f.write(buf.getvalue())
        if warnings:
            f.write("\n" + "=" * 60 + "\n⚠️ 警告汇总:\n")
            for w in warnings:
                f.write(f"  {w}\n")

    # 报告尾部附一行不可见的校验摘要
    with open(md_path, 'a', encoding='utf-8') as f:
        f.write(f"\n<!-- 校验{date_str}: {'全部通过' if not warnings else f'{len(warnings)}项警告'}"
                f"{' | ' + '; '.join(w.replace(chr(10), ' ')[:80] for w in warnings[:3]) if warnings else ''}"
                f" 详情: logs/validation_{date_str}.log -->\n")

    print(f"✅ 生成后校验完成: {'全部通过' if not warnings else f'{len(warnings)}项警告'}"
          f"(详情: {log_path})")
    for w in warnings:
        print(f"   {w[:100]}")
    return warnings

# ============ 主程序 ============
if __name__ == '__main__':
    print("=" * 60)
    print("📊 投资周报生成器")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 第0步：加载分析框架
    framework = load_framework()

    # 第0.5步：加载论点
    theses = load_theses()

    # 第0.55步：加载配置观点库(P2)
    views_data = allocation_engine.load_views()
    views_block = allocation_engine.render_views_block(views_data) if views_data else ""
    if views_data:
        print(f"   配置观点: {len(views_data.get('views', []))} 资产 / "
              f"{len(views_data.get('predictions', []))} 预测"
              f"({len(allocation_engine.due_predictions(views_data))} 条已到期待裁决)")

    # 第0.6步：加载上期报告
    prev_report = load_previous_report()

    # 第0.7步：加载技术面笔记
    tech_notes = load_technical_notes()

    # 第0.8步：加载新闻摘要
    news_summary = load_news_summary()

    # 第1步：加载数据包
    data_pack = load_data_pack()
    if not data_pack:
        print("\n请先运行: python3 scripts/data_assembler.py")
        sys.exit(1)

    # 第1.5步：读取数据锚点（如果存在）
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    anchor_prompt_files = sorted(glob.glob(os.path.join(ROOT_DIR, 'data', 'daily', 'anchor_prompt_*.md')))
    if anchor_prompt_files:
        with open(anchor_prompt_files[-1], 'r', encoding='utf-8') as f:
            anchor_block = f.read()
        # 在发送给AI的prompt中，将锚点块插入数据包之前
        data_pack = anchor_block + "\n\n---\n\n" + data_pack
        print(f"✅ 数据锚点已加载 ({len(anchor_block)} 字符)")

    # 第2步：生成报告
    report = generate_report(data_pack, framework, theses, prev_report, tech_notes, news_summary, views_block)
    if not report:
        print("\n❌ 报告生成失败")
        sys.exit(1)

    # 第3步：保存
    md_path = save_report(report)

    # 第3.5步：同日锚点校验(2026-10-11) — 必须先于论点回写
    warnings = validate_generated_report(md_path)

    # 第3.6步：论点状态回写(2026-10-11) — 数值校验不过关则禁止回写,
    # 防止基于错误数字的升降级污染thesis.json(升级提示词缺陷清单第7条)
    # P2(2026-10-11): 观点库回写同门禁
    if _has_numeric_errors(warnings):
        print("⛔ 存在数值类校验错误,本轮跳过thesis.json与allocation_views.json回写(请人工核对后再决定)")
    else:
        update_thesis_status(report)
        allocation_engine.update_allocation_status(report)

    # 第4步：预览前30行
    print("\n" + "=" * 60)
    print("📖 报告预览（前30行）:")
    print("=" * 60)
    lines = report.split('\n')
    for line in lines[:30]:
        print(line)
    if len(lines) > 30:
        print(f"\n... 共 {len(lines)} 行，完整报告请查看输出文件")

    # 第5步(P4, 2026-10-11): 月末/季末最后一个周五 → 追加月报/季报
    # 周报已完成并落盘,附加报告失败不影响周报(独立进程,失败仅记日志)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if is_last_friday_of_month():
        print("\n📅 今天是月末最后一个周五,启动月度复盘(monthly_review.py)...")
        try:
            r = subprocess.run([sys.executable, os.path.join(script_dir, 'monthly_review.py')],
                               timeout=1800, capture_output=True, text=True)
            print(r.stdout[-800:] if r.stdout else "", end="")
            if r.returncode != 0:
                print(f"⚠️ 月度复盘失败(exit {r.returncode}): {r.stderr[-300:]}")
        except subprocess.TimeoutExpired:
            print("⚠️ 月度复盘超时30分钟,已终止(周报不受影响)")
    if is_last_friday_of_quarter():
        print("\n📅 今天是季末最后一个周五,启动季度展望(quarterly_outlook.py)...")
        try:
            r = subprocess.run([sys.executable, os.path.join(script_dir, 'quarterly_outlook.py')],
                               timeout=1800, capture_output=True, text=True)
            print(r.stdout[-800:] if r.stdout else "", end="")
            if r.returncode != 0:
                print(f"⚠️ 季度展望失败(exit {r.returncode}): {r.stderr[-300:]}")
        except subprocess.TimeoutExpired:
            print("⚠️ 季度展望超时30分钟,已终止(周报不受影响)")

    print("\n🎉 周报生成完成！")
