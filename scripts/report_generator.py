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
    """加载当日数据包(第七轮: 报告输入仅限当日研究快照渲染的数据包)。

    缺当日包即失败——不得静默回退"最新文件"(文件最新≠数据最新,旧包冒充当日
    输入正是第七轮根因B)。需重生成历史报告时显式传date_str。
    """
    weekly_dir = os.path.join(DATA_DIR, 'weekly')

    if not date_str:
        date_str = datetime.now().strftime('%Y%m%d')
    filepath = os.path.join(weekly_dir, f'data_pack_{date_str}.md')

    if not os.path.exists(filepath):
        others = sorted([f for f in os.listdir(weekly_dir)
                         if f.startswith('data_pack_')], reverse=True) \
            if os.path.exists(weekly_dir) else []
        hint = f"(目录里最新的是 {others[0]})" if others else "(目录为空)"
        print(f"❌ 当日数据包不存在: data_pack_{date_str}.md {hint}")
        print("   报告输入仅限当日研究快照渲染的数据包,不得回退旧包 — 请先运行 run_weekly.py")
        return None

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
（每个资产小节末尾加一行"配置观点: 评级|确信度★"，评级只能取: 超配/标配/低配/观望(标配=与理论基准一致的中性仓位,不用"中性"一词)；
触发器纪律: 只有上方观点库标注"✅已触发"的引擎核验条件才可写成已触发,"❓待验证"的条件必须标注待验证,不得当作已发生,"⏳持续确认中"的条件须待连续周数满额才算触发；
若本周该资产的升降级条件被引擎核验为已触发，才输出"调整提案"：动作与理由、证据及反证、风险与最大容忍损失、失效条件、下一复核日；未触发则只维持原评级；
【研究链路要求】每个资产小节不得从体制评分直接跳到配置建议，须依次回答:
当前宏观环境对该资产产生什么影响→传导机制是什么(无法量化的机制明确标注"研究假设",不得伪装成已证实事实)→这些影响是已经发生还是未来可能发生→市场价格是否已反映相关预期→有哪些相反力量(反证)→为什么当前评级合理(无充分新增证据时允许维持原观点)→什么新数据会改变评级→调整及失效条件(当前配置的调整触发器、失效条件与下一复核日,无充分新证据时输出"维持原观点+复核日"也是合法结论,不得为生成报告制造配置变化)。
不得直接从资产相关性推断因果关系。)

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
3. 状态是否需要变更（进行中/待观察/已验证/已失效）
4. 用一句话说明本周证据
5. 报告正文全部结束后，必须另起一行输出"论点状态块"（HTML注释包裹，渲染时不可见，供脚本解析回写thesis.json），
   格式严格如下，每个论点一行、共9行、一行一个JSON对象、不得包裹代码块围栏：

<!--THESIS_STATUS
{{"id":1,"status":"进行中","confidence":3,"note":"≤40字本周证据","evidence":[{{"metric":"macro.data.TIPS_10Y.value","value":2.1,"obs_date":"2026-10-09","mechanism":"利率与流动性"}}]}}
{{"id":2,"status":"待观察","confidence":2,"note":"..."}}
THESIS_STATUS-->

status只能取: 进行中/待观察/已验证/已失效；confidence为1-5整数；id与thesis.json一致。
evidence数组可选但强烈建议提供，格式与配置观点块相同(锚点指标ID+数值+观测日+机制类别)，程序按同一套证据分级v2规则核验：
- 【状态终态门禁】→已失效/→已验证为终态判定：须该论点的失效/升级触发器被引擎核验为已触发，或本周≥2项新增独立支持证据通过程序验证；否则保留原状态，模型判断降级为提案留档。
- 【终态退出门禁】已失效/已验证论点不得直接改回进行中/待观察：重新启用须≥2项新增独立证据且原失效条件经引擎复核未触发；已验证重新开启须invalidation触发器已触发或≥2项新增独立反证。实质上形成新假设时应建议创建关联新版本论点（在note中标注），不得改写原论点历史结论。
- 【确信度门禁】上调不得超过程序验证星级；下调不受限。
- 论点引用历史数值时必须在note中带原始观测日期(如"实际利率2.5%(2026-09-30观测)")——同一指标旧值再次引用不算新增证据。
- 论点失效不自动改变关联资产评级：关联观点须各自过证据门禁。

6. 紧跟THESIS_STATUS块之后，输出"配置观点块"（HTML注释，同格式，每个资产一行、共9行）：

<!--ALLOCATION_STATUS
{{"id":1,"rating":"标配","confidence":2,"note":"≤40字本周理由","evidence":[{{"metric":"macro.data.CCC_OAS.value","value":10.30,"obs_date":"2026-10-15","mechanism":"信用"}}]}}
{{"id":2,"rating":"低配","confidence":3,"note":"..."}}
ALLOCATION_STATUS-->

rating只能取: 超配/标配/低配/观望（不用"中性"，中性=标配）；id与allocation_views.json一致（1美股/2利率久期/3信用/4美元/5贵金属/6能源/7A股港股/8加密/9现金短债）。
确信度变化与评级变化相互独立：评级未变但证据增减时应调confidence（1-5整数），二者程序会分别记录。
【证据分级v2程序校验】evidence数组为结构化证据，每项含metric(锚点指标ID)/value(数值,须与观点块或数据包中该指标的锚点值一致)/obs_date(观测日,必填且须与锚点观测日完全一致——缺失、不可解析、与锚点不符或以采集日as_of替代的证据整项拒收,不参与星级与评级)/mechanism(机制类别:增长/通胀/利率与流动性/信用/避险与估值/供应与库存/资金流)；可加"contrary":true表示反证、"explained":true表示反证已解释、"neutral":true表示相关但不能直接支持方向(数值照常核验,但不计入支持数量)。
程序按以下规则核验并执行门禁（不满足会被拒写）：
- 同一底层指标多次引用只计1项独立证据；同一月度指标连续四周重复引用不等于多次独立观察。
- 星级门槛: 1★=1项 / 2★=2项 / 3★=3项且覆盖2类机制 / 4★=4项且3类机制且跨2个观察期 / 5★=5项且3类机制且跨3个观察期（5★不要求必须存在反证；但若存在重大反证，必须已解释——存在未解释反证时封顶3★）。反对证据(contrary)不计入支持数量，只参与反证校验。
- 【评级变更门禁】新评级须满足: 引擎核验为"✅已触发"的同向触发器，或≥2项通过程序验证的新增evidence；否则保留原评级、提案留档。被拒提案会在观点块公示，勿无新证据重复提交。
- 【确信度门禁】上调不得超过程序验证星级；下调不受限。评级变更/确信度上调必须走上述门禁，评级变化是需证据支持的研究判断修正，不是数值状态更新。
仅当本周发生评级变更时，在该行附加预测字段（方向+期限+可计算规格）：
{{"id":5,"rating":"标配","confidence":3,"note":"...","pred":"若XXX则两周内YYY","pred_weeks":2,"pred_metric":"macro.data.CCC_OAS.value","pred_op":">=","pred_target":10.0,"pred_mode":"expiry"}}
pred_metric/pred_op/pred_target为可选的机器可校验规格（锚点指标ID、比较符>=/<=/>/<、目标值）；pred_mode取expiry(截止日达到,默认)或touch(观察期内触及,两者不得混淆)；价格类touch预测可附pred_basis指定比较口径: close(收盘价达到,默认)/high(盘中最高触及)/low(盘中最低触及)——"盘中触及"必须写high/low口径，收盘价不能证明盘中未触及；还可附前提规格pred_premise_metric/pred_premise_op/pred_premise_target(条件预测: 前提兑现才开始结果观察期,截止日不顺延)。带完整规格的预测到期由程序按每日观察记录自动裁决。

7. 若观点库中有"⏰已到期"的预测，先在报告第七节给出裁决，并在最后输出预测裁决块：

<!--PREDICTION_STATUS
{{"pred_id":1,"status":"hit","note":"GOLD 4310≥4300(观测日2026-10-16)"}}
PREDICTION_STATUS-->

status只能取: hit(已命中)/miss(已证伪)/inconclusive(无法裁决)/not_yet_triggered(前提未发生,预测未生效)。
裁决纪律:
- note必须引用具体数值与观测日作为证据；无证据或无数值的hit/miss会被程序拒绝回写。
- 引用的数值与观测日必须落在该预测的观察窗内(观察起点~截止日)且与已记录的观测吻合；窗口结束后的数据不得用于裁决。
- expiry模式在截止日未到时不得提前裁决；touch模式触及即可判hit。
- 引擎已按观察记录自动裁决的预测，你的裁决只能与之一致，不得用自然语言说明覆盖程序客观结果。
- 前提条件未兑现的预测应判not_yet_triggered或inconclusive并说明，不得判hit。

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

# ============ 月报/季报触发(P4 v2, 2026-10-11第二轮审查#3.2/#3.4) ============
# v1缺陷: "月末最后一个周五"在期间结束前生成月报(如10-30出10月报,10月还剩1天);
# 更严重的是12-25(12月最后一个周五)会提前生成Q4季报——Q4还剩6天。
# v2: 只在期间**自然结束之后**的第一个周五触发,复盘对象是已完结的上一期间。
# v3(2026-10-17): 周报改为周六生成(覆盖完整一周含周五收盘——原周五08:00生成时
# 美股/商品只有周四收盘),触发日同步改为"期间结束后第一个周六"(自然结束后更晚,更安全)。
def pending_completed_month(d=None):
    """今天是否为"上个自然月结束后的第一个周六"。是→返回上月YYYYMM,否则None。"""
    d = d or datetime.now()
    if d.weekday() != 5 or d.day > 7:   # 周六且在当月第一周
        return None
    y, m = (d.year - 1, 12) if d.month == 1 else (d.year, d.month - 1)
    return f"{y}{m:02d}"

def pending_completed_quarter(d=None):
    """今天是否为"上个自然季结束后的第一个周六"。是→返回上季'YYYYQn',否则None。
    只可能在1/4/7/10月的第一周周六出现(自然季结束后)。"""
    d = d or datetime.now()
    if d.weekday() != 5 or d.day > 7:
        return None
    if d.month not in (1, 4, 7, 10):
        return None
    q = ((d.month - 4) // 3) % 4 + 1    # 上一季的季号: 1月→Q4, 4月→Q1, 7月→Q2, 10月→Q3
    y = d.year - 1 if d.month == 1 else d.year
    return f"{y}Q{q}"

def _has_numeric_errors(warnings):
    """P0修复(六.7): 数值类错误(严重错误/偏差超容差)应阻止论点状态回写。
    样式类警告(如A股口径标注)不阻止——那不影响判断依据的数字本身。"""
    for w in warnings:
        if w.startswith('🚨') or (w.startswith('❌') and ('偏差' in w or '锚点' in w or '超出合理范围' in w)):
            return True
    return False

def update_thesis_status(report_text, thesis_path=None, today_str=None, anchors=None):
    """解析报告末尾的THESIS_STATUS块,回写 config/thesis.json(第四轮P0-4: 与配置观点共用证据门禁)。

    门禁(与allocation_engine统一):
    - 状态→已失效: 须引擎核验"已触发"的失效触发器(thesis.quant_triggers
      direction=invalidation),或≥2项本周新增独立支持证据; 否则保留原状态+提案留档。
    - 状态→已验证: 同上(upgrade触发器或≥2项新增支持证据)。
    - 进行中↔待观察等过程状态: 允许(记录审计)。
    - 确信度上调: 不得超过程序验证星级(证据分级v2,只计支持证据); 下调自由。
    - 每次变化记录 last_change{date,from,to,via,evidence} 审计;
      证据台账 evidence_ledger 与配置观点同构(新增判定用)。
    - 论点失效落地时提示检查关联论点(不自动改任何配置观点评级)。
    (thesis_path/today_str/anchors参数供E2E测试隔离注入)"""
    import allocation_engine as ae
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
        for line in block.split('\n'):
            line = line.strip().rstrip(',')
            if line.startswith('{') and line.endswith('}'):
                try:
                    objs.append(json.loads(line))
                except Exception:
                    pass
        if not objs:
            for mm in re.finditer(r'\{[^{}]*\}', block):
                try:
                    objs.append(json.loads(mm.group(0)))
                except Exception:
                    pass

    if not objs:
        print("⚠️ THESIS_STATUS块解析失败(无有效JSON),论点状态未回写")
        return []

    thesis_path = thesis_path or os.path.join(CONFIG_DIR, 'thesis.json')
    with open(thesis_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    today = datetime.strptime(today_str, '%Y-%m-%d') if today_str else datetime.now()
    today_iso = today.strftime('%Y-%m-%d')
    tag = f"{today.month}/{today.day}"
    updates = []

    # 每周核验全部论点触发器(与配置观点同构): sustain类连续周数在thesis.json逐周累积,
    # 不依赖模型是否恰好提出终态变更 — 无结构化触发器的论点跳过
    trig_data = {'views': [{'id': t['id'],
                            'quant_triggers': t.get('quant_triggers') or [],
                            'trigger_state': t.get('trigger_state') or {}}
                           for t in data['theses'] if t.get('quant_triggers')]}
    all_trig_rows = ae.evaluate_quant_triggers(
        trig_data, anchors, today_str=today_iso, persist=True)
    for v in trig_data['views']:
        t = next(x for x in data['theses'] if x['id'] == v['id'])
        t['trigger_state'] = v.get('trigger_state') or {}

    for o in objs:
        tid = o.get('id')
        t = next((x for x in data['theses'] if x.get('id') == tid), None)
        if t is None:
            continue

        new_status = str(o.get('status', '')).strip()
        conf = o.get('confidence')
        note = str(o.get('note', '')).strip()[:60]

        # 证据程序验证(与配置观点同构)
        verified, ev_rejects = ae.verify_evidence_items(o.get('evidence'), anchors, today_iso)
        supporting, contrary, unexplained, neutral_ev = ae.split_evidence_direction(verified)
        star_max, star_desc = ae.star_level_from_evidence(verified)
        new_support = ae.new_supporting_metrics(t, supporting, today_iso)

        # 状态变更门禁(第四轮P0-4进入终态门禁 + 第五轮P0-4终态退出门禁):
        # 进入已失效/已验证: 须invalidation/upgrade触发器引擎核验已触发,或≥2项新增独立支持证据;
        # 退出终态(已失效/已验证→进行中/待观察): 重新启用/重新开启同样有门禁,不得宽松放行。
        old_status = t.get('status')
        if new_status in ALLOWED_STATUS and new_status != old_status:
            if old_status in ('已失效', '已验证') and new_status in ('进行中', '待观察'):
                # ── 终态退出: 重新启用(自已失效)/重新开启(自已验证) ──
                trig_rows = all_trig_rows.get(tid, [])
                if old_status == '已失效':
                    orig_fired = [r for r in trig_rows
                                  if r['direction'] == 'invalidation' and r['status'] == 'triggered']
                    if orig_fired:
                        reason = (f"原失效条件经引擎复核仍在触发"
                                  f"({'+'.join(r['trig_id'] for r in orig_fired)}) — "
                                  f"重新启用须先否定原失效依据;实质新假设应创建关联新版本论点")
                        ae._record_proposal(t, new_status, reason,
                                            json.dumps(o.get('evidence'), ensure_ascii=False)[:160],
                                            today_iso)
                        updates.append(f"论点#{tid}{t.get('name', '')[:10]}: 重新启用被拒"
                                       f"[{reason[:70]}],保留已失效")
                        print(f"   🚫 论点#{tid}重新启用被拒: {reason}")
                    elif len(new_support) >= 2:
                        t['status'] = new_status
                        via = (f"重新启用: 新增独立证据{len(new_support)}项经验证"
                               f"+原失效条件复核未触发({star_desc[:40]})")
                        t['last_change'] = {'date': today_iso, 'from': old_status, 'to': new_status,
                                            'via': via, 'evidence': supporting[:5], 'note': note}
                        updates.append(f"论点#{tid}{t.get('name', '')[:10]}: {old_status}→{new_status} (经{via})")
                    else:
                        reason = (f"已失效论点重新启用须同时满足: 重新启用原因+≥2项独立新增证据"
                                  f"(本周{len(new_support)}项)+原失效条件重新评估(未触发),"
                                  f"并给出新的有效条件与观察期限;实质上已形成新假设时应创建"
                                  f"关联新版本论点,不得改写原论点历史结论")
                        if ev_rejects:
                            reason += "; 证据拒收: " + "; ".join(rj for rj, _ in ev_rejects[:3])
                        ae._record_proposal(t, new_status, reason,
                                            json.dumps(o.get('evidence'), ensure_ascii=False)[:160],
                                            today_iso)
                        updates.append(f"论点#{tid}{t.get('name', '')[:10]}: 重新启用被拒"
                                       f"[{reason[:70]}],保留已失效")
                        print(f"   🚫 论点#{tid}重新启用被拒: {reason}")
                else:  # 已验证 → 重新开启
                    inv_fired = [r for r in trig_rows
                                 if r['direction'] == 'invalidation' and r['status'] == 'triggered']
                    new_contrary = ae.new_contrary_metrics(t, contrary, today_iso)
                    if inv_fired:
                        t['status'] = new_status
                        via = (f"重新开启: invalidation触发器"
                               f"{'+'.join(r['trig_id'] for r in inv_fired)}(引擎核验已触发)")
                        t['last_change'] = {'date': today_iso, 'from': old_status, 'to': new_status,
                                            'via': via, 'evidence': contrary[:5], 'note': note}
                        updates.append(f"论点#{tid}{t.get('name', '')[:10]}: {old_status}→{new_status} (经{via})")
                    elif len(new_contrary) >= 2:
                        t['status'] = new_status
                        via = f"重新开启: 新增独立反证{len(new_contrary)}项经验证({star_desc[:40]})"
                        t['last_change'] = {'date': today_iso, 'from': old_status, 'to': new_status,
                                            'via': via, 'evidence': contrary[:5], 'note': note}
                        updates.append(f"论点#{tid}{t.get('name', '')[:10]}: {old_status}→{new_status} (经{via})")
                    else:
                        reason = (f"已验证论点重新开启须invalidation触发器引擎核验已触发,"
                                  f"或≥2项本周新增独立反证(本周新增反证{len(new_contrary)}项) — "
                                  f"终态退出不得绕过门禁;实质新假设应创建关联新版本论点")
                        if ev_rejects:
                            reason += "; 证据拒收: " + "; ".join(rj for rj, _ in ev_rejects[:3])
                        ae._record_proposal(t, new_status, reason,
                                            json.dumps(o.get('evidence'), ensure_ascii=False)[:160],
                                            today_iso)
                        updates.append(f"论点#{tid}{t.get('name', '')[:10]}: 重新开启被拒"
                                       f"[{reason[:70]}],保留已验证")
                        print(f"   🚫 论点#{tid}重新开启被拒: {reason}")
            elif new_status in ('已失效', '已验证'):
                # ── 进入终态(自过程状态或对侧终态) ──
                want_dir = 'invalidation' if new_status == '已失效' else 'upgrade'
                trig_rows = all_trig_rows.get(tid, [])
                fired = [r for r in trig_rows if r['direction'] == want_dir and r['status'] == 'triggered']
                if fired:
                    old = t.get('status')
                    t['status'] = new_status
                    via = f"{want_dir}触发器{'+'.join(r['trig_id'] for r in fired)}(引擎核验已触发)"
                    t['last_change'] = {'date': today_iso, 'from': old, 'to': new_status,
                                        'via': via, 'evidence': supporting[:5], 'note': note}
                    updates.append(f"论点#{tid}{t.get('name', '')[:10]}: {old}→{new_status} (经{via})")
                elif len(new_support) >= 2:
                    old = t.get('status')
                    t['status'] = new_status
                    via = f"新增独立支持证据{len(new_support)}项经验证({star_desc[:60]})"
                    t['last_change'] = {'date': today_iso, 'from': old, 'to': new_status,
                                        'via': via, 'evidence': supporting[:5], 'note': note}
                    updates.append(f"论点#{tid}{t.get('name', '')[:10]}: {old}→{new_status} (经{via})")
                else:
                    reason = (f"'{new_status}'为终态判定,须invalidation/upgrade触发器已触发"
                              f"或≥2项本周新增独立支持证据(本周新增{len(new_support)}项;"
                              f"{star_desc[:60]})")
                    if ev_rejects:
                        reason += "; 证据拒收: " + "; ".join(rj for rj, _ in ev_rejects[:3])
                    ae._record_proposal(t, new_status, reason,
                                        json.dumps(o.get('evidence'), ensure_ascii=False)[:160],
                                        today_iso)
                    updates.append(f"论点#{tid}{t.get('name', '')[:10]}: 状态→{new_status}被拒"
                                   f"[{reason[:60]}],保留{t.get('status')}")
                    print(f"   🚫 论点#{tid}状态变更被拒: {reason}")
            else:
                # 过程状态(进行中↔待观察): 允许,仍记录审计
                old = t.get('status')
                t['status'] = new_status
                t['last_change'] = {'date': today_iso, 'from': old, 'to': new_status,
                                    'via': '过程状态调整(非终态)', 'evidence': supporting[:5], 'note': note}
                updates.append(f"#{tid}{t.get('name', '')[:10]}: 状态→{new_status}")

        # 确信度门禁: 上调须星级支撑,下调自由
        if isinstance(conf, (int, float)) and conf == int(conf) and 1 <= int(conf) <= 5:
            conf = int(conf)
            if conf > (t.get('confidence') or 0) and conf > star_max:
                reason = f"证据仅支撑{star_max}★({star_desc[:60]}),不足以授予{conf}★"
                ae._record_proposal(t, f"确信度{conf}★", reason,
                                    json.dumps(o.get('evidence'), ensure_ascii=False)[:160],
                                    today_iso)
                updates.append(f"论点#{tid}: 确信度→{conf}★被拒[{reason[:60]}],保留{t.get('confidence')}★")
                print(f"   🚫 论点#{tid}确信度上调被拒: {reason}")
            else:
                t['confidence'] = conf

        # 证据台账写入(第五轮P1-1: 放在门禁判定**之后** — 同日重跑时,
        # 早前运行写入的(指标,观测日)已在已知集合内,同批数据不会再次计为新增)
        if verified:
            ledger = t.setdefault('evidence_ledger', [])
            ledger.append({'date': today_iso, 'verified': len(verified),
                           'supporting': len(supporting), 'contrary': len(contrary),
                           'unexplained': len(unexplained), 'neutral': len(neutral_ev),
                           'new_support': sorted(new_support),
                           'star_max': star_max, 'desc': star_desc[:200],
                           'obs_pairs': sorted({(i['metric'], str(i.get('obs_date'))[:10])
                                                for i in verified})})
            t['evidence_ledger'] = ledger[-12:]

        # 论点失效 → 提示检查关联论点(不自动改任何配置观点)
        if t.get('status') == '已失效' and t.get('last_change', {}).get('date') == today_iso:
            rel = t.get('related_theses') or []
            if rel:
                updates.append(f"论点#{tid}已失效 — 请检查关联论点{rel}及对应资产观点"
                               f"(失效不自动推导评级变更,须各自过证据门禁)")

        # history追加(同日重复运行不重复记)
        hist = t.setdefault('history', [])
        lc = t.get('last_change') or {}
        if lc.get('date') == today_iso and lc.get('from') != lc.get('to'):
            line = f"{tag} {t.get('status', '进行中')} {t.get('confidence', 0)}★ " \
                   f"[{lc.get('from')}→{lc.get('to')} {str(lc.get('via', ''))[:40]}] {note}".rstrip()
        else:
            line = f"{tag} {t.get('status', '进行中')} {t.get('confidence', 0)}★ {note}".rstrip()
        if hist and hist[-1].startswith(f"{tag} "):
            hist[-1] = line
        else:
            hist.append(line)
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
    """用最新锚点(与报告同日生成)校验刚生成的报告,结果落 logs/validation_*.log 并附注到报告尾部。

    第二轮审查#4: 返回 (classification, warnings),classification ∈ PASS/DEGRADED/FAIL。
    FAIL = 无锚点/锚点非同日/数值类错误 → 调用方禁止一切长期状态回写。"""
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    anchor_files = sorted(glob.glob(os.path.join(ROOT_DIR, 'data', 'daily', 'anchors_*.json')))
    date_str = datetime.now().strftime('%Y%m%d')

    if not anchor_files:
        classification, warnings = "FAIL", []
        print("⛔ 无锚点文件 — 数字未经证实,校验分级FAIL,禁止状态回写")
        _append_validation_note(md_path, date_str, "FAIL(无锚点)")
        return classification, warnings

    anchors_same_day = date_str in os.path.basename(anchor_files[-1])

    with open(anchor_files[-1], 'r', encoding='utf-8') as f:
        anchors = json.load(f)

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import data_validator

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        warnings = data_validator.validate_report(md_path, anchors)

    classification, reason = data_validator.classify_result(
        has_anchors=True, anchors_same_day=anchors_same_day,
        warnings=warnings, numeric_errors=_has_numeric_errors(warnings))

    log_path = os.path.join(PROJECT_DIR, 'logs', f'validation_{date_str}.log')
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f"报告校验 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"报告: {md_path}\n锚点: {anchor_files[-1]}\n")
        f.write(f"校验分级: {classification} ({reason})\n")
        f.write("=" * 60 + "\n")
        f.write(buf.getvalue())
        if warnings:
            f.write("\n" + "=" * 60 + "\n⚠️ 警告汇总:\n")
            for w in warnings:
                f.write(f"  {w}\n")

    _append_validation_note(md_path, date_str,
                            f"{classification}" + (f"({len(warnings)}项警告)" if warnings else ""))
    print(f"✅ 生成后校验完成: 分级={classification} {reason}"
          f"{' | 全部通过' if not warnings else f' | {len(warnings)}项警告'} (详情: {log_path})")
    for w in warnings:
        print(f"   {w[:100]}")
    return classification, warnings


def _append_validation_note(md_path, date_str, summary):
    """报告尾部附一行不可见的校验摘要"""
    with open(md_path, 'a', encoding='utf-8') as f:
        f.write(f"\n<!-- 校验{date_str}: {summary} 详情: logs/validation_{date_str}.log -->\n")

def apply_status_updates(report, classification, anchors=None, today_str=None,
                         thesis_path=None, views_path=None):
    """校验分级后的状态回写调度(第四轮P0-4/测试#19):
    PASS/DEGRADED → 论点回写 + 配置观点回写(共用同一批锚点,统一研究截止时间);
    FAIL → 两类长期状态都不修改(基于错误数字的升降级不得污染thesis.json/allocation_views.json)。
    (thesis_path/views_path供E2E测试隔离注入)返回 (thesis_updates, fail_blocked)。"""
    if classification == "FAIL":
        print("⛔ 校验分级FAIL(无锚点/锚点过期/数值错误),本轮跳过thesis.json与allocation_views.json回写(请人工核对后再决定)")
        return [], True
    _today = today_str or datetime.now().strftime('%Y-%m-%d')
    thesis_updates = update_thesis_status(report, today_str=_today, anchors=anchors,
                                          thesis_path=thesis_path)
    allocation_engine.update_allocation_status(report, views_path=views_path,
                                               anchors=anchors, today_str=_today)
    return thesis_updates, False


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

    # 第0.55步：加载配置观点库(P2) — 连同最新锚点一并喂给引擎做触发器核验
    views_data = allocation_engine.load_views()
    latest_anchors = {}
    _anchor_json = sorted(glob.glob(os.path.join(DATA_DIR, 'daily', 'anchors_*.json')))
    if _anchor_json:
        try:
            with open(_anchor_json[-1], 'r', encoding='utf-8') as f:
                latest_anchors = json.load(f)
        except Exception as e:
            print(f"⚠️ 锚点JSON读取失败({e}),触发器按'待验证'处理")
    views_block = allocation_engine.render_views_block(
        views_data, today_str=datetime.now().strftime('%Y-%m-%d'),
        anchors=latest_anchors) if views_data else ""
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
    # 第二轮#2/#4: 无锚点/锚点非同日/数值错误 → FAIL,禁止一切长期状态回写
    classification, warnings = validate_generated_report(md_path)

    # 第3.6步：论点状态回写 — 校验分级FAIL则禁止回写,
    # 防止基于错误数字的升降级污染thesis.json/allocation_views.json
    # (第四轮P0-4: 两类长期状态共用同一批已验证锚点与统一研究截止时间)
    apply_status_updates(report, classification, anchors=latest_anchors)

    # 第4步：预览前30行
    print("\n" + "=" * 60)
    print("📖 报告预览（前30行）:")
    print("=" * 60)
    lines = report.split('\n')
    for line in lines[:30]:
        print(line)
    if len(lines) > 30:
        print(f"\n... 共 {len(lines)} 行，完整报告请查看输出文件")

    # 第5步(P4 v2, 第二轮#3.2/#3.4; v3 2026-10-17随周报改周六): 上个自然月/季
    # **结束后**的第一个周六 → 追加月报/季报
    # (v1在月末最后一个周五触发,会在期间结束前生成,如12-25提前生成Q4季报——已废除)
    # 周报已完成并落盘,附加报告失败不影响周报(独立进程,失败仅记日志)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    done_month = pending_completed_month()
    if done_month:
        print(f"\n📅 {done_month}已完结(今天是其后第一个周六),启动月度复盘(monthly_review.py)...")
        try:
            r = subprocess.run([sys.executable, os.path.join(script_dir, 'monthly_review.py'),
                                '--month', done_month],
                               timeout=1800, capture_output=True, text=True)
            print(r.stdout[-800:] if r.stdout else "", end="")
            if r.returncode != 0:
                print(f"⚠️ 月度复盘失败(exit {r.returncode}): {r.stderr[-300:]}")
        except subprocess.TimeoutExpired:
            print("⚠️ 月度复盘超时30分钟,已终止(周报不受影响)")
    done_quarter = pending_completed_quarter()
    if done_quarter:
        print(f"\n📅 {done_quarter}已完结(今天是其后第一个周六),启动季度展望(quarterly_outlook.py)...")
        try:
            r = subprocess.run([sys.executable, os.path.join(script_dir, 'quarterly_outlook.py'),
                                '--quarter', done_quarter],
                               timeout=1800, capture_output=True, text=True)
            print(r.stdout[-800:] if r.stdout else "", end="")
            if r.returncode != 0:
                print(f"⚠️ 季度展望失败(exit {r.returncode}): {r.stderr[-300:]}")
        except subprocess.TimeoutExpired:
            print("⚠️ 季度展望超时30分钟,已终止(周报不受影响)")

    print("\n🎉 周报生成完成！")
