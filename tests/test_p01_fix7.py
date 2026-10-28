#!/usr/bin/env python3
"""IA-P0-1-FIX7 对抗测试: 可信采集根与祖先路径校验(IA-F6-DEF-001)+内容绑定(IA-F6-RISK-002)。

真实项目模块(fixt/snapshot_builder/data_assembler/report_generator/
daily_prediction_observer/research_provenance)+临时目录+合成采集数据;
不mock内部逻辑,mock仅限外部API/GLM(本套件不含GLM调用)。

矩阵:
  A 规范路径: 正常目录/构建/回退/可信根原语/前缀形态差异/摘要记录;
  B 祖先符号链接: B1=FIX6验收报告原始反例精确复现(trusted/data→/outside,
    文件本身非链接、规范名、FIX6式realpath等式成立——新代码必须拒绝);
    B2 daily级链接/B3 文件链接/B4 多级祖先/B5 采集根本身经链接重定向/
    B6 realpath自洽但物理在可信根外/B7 构建端不读取/B8 全链路(装配器+周报预检);
  C 其他边界: 目录冒充/不存在/../与绝对路径/跨通道/非规范扩展名/损坏内容/正常对照;
  D 历史与临时目录兼容: TemporaryDirectory/自定义平铺目录/纯历史口径实体不虚报/
    无data_dir元数据边界/正式与历史口径授权差异;
  E 链路传播: CLI缺省可信根fail-closed/观察器拒绝/长期状态保护/测试参数非生产后门;
  R(IA-F6-RISK-002): 原始采集文件内容变异五场景的证据化验证(§9)。
"""
import copy
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from unittest import mock

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), 'scripts'))
sys.path.insert(0, _HERE)

import fixt                                    # noqa: E402
import snapshot_builder as sb                  # noqa: E402
import data_assembler as da                    # noqa: E402
import report_generator as rg                  # noqa: E402
import daily_prediction_observer as dpo        # noqa: E402
import research_provenance as rp               # noqa: E402

DAY = '20261024'
PREV = '20261023'
PASS_N, FAIL_N = 0, 0


def check(name, cond, detail=''):
    global PASS_N, FAIL_N
    if cond:
        PASS_N += 1
        print(f"  ✅ {name}")
    else:
        FAIL_N += 1
        print(f"  ❌ {name} [{detail}]")


def quiet(fn, *a, **kw):
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **kw)


def no_exception(fn, *a, **kw):
    try:
        return fn(*a, **kw), True
    except Exception:
        import traceback
        print(traceback.format_exc(limit=2))
        return None, False


class DT(datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 10, 24, 8, 0, 0)


print("=" * 72)
print("IA-P0-1-FIX7 对抗测试: 可信采集根/祖先路径校验/内容绑定")
print("=" * 72)

# 共享真实基线(fixture控制的可信沙箱根=BASE,§5.3授权缝)
BASE = tempfile.mkdtemp(prefix='fix7-base-')
SNAP, SNAP_PATH, PATHS = fixt.build_full_day(BASE, DAY)
BASE_DAILY = PATHS['daily']
PY = sys.executable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ssp(status_dict, data_dir=None, target=DAY, trusted_root=None):
    return rp.sources_status_problems(status_dict, target, data_dir,
                                      trusted_root=trusted_root)


def _b8_layout(trusted_root, outside_root, day=DAY):
    """FIX6验收反例布局: 真实规范文件物理在outside/daily;trusted/data→outside。

    文件本身不是符号链接、文件名规范、日期规范——唯一"异常"是祖先data组件
    经符号链接重定向出可信项目根。"""
    od = os.path.join(outside_root, 'daily')
    if not os.path.exists(os.path.join(od, f'global_{day}.json')):
        fixt.write_collectors(od, day)
    if not os.path.exists(os.path.join(trusted_root, 'data')):
        os.symlink(outside_root, os.path.join(trusted_root, 'data'))
    return os.path.join(trusted_root, 'data', 'daily'), od


# ════════════════════════════════════════════════════════════════════
print("\n── A. 规范路径(可信根内的正常采集结构必须零误伤)")

check("A1 真实构建日(data/daily结构,fixture可信根)三口径全过",
      ssp(SNAP['sources_status'], data_dir=BASE_DAILY, trusted_root=BASE) == []
      and rp.recompute_gate_a(SNAP, data_dir=BASE_DAILY,
                              trusted_root=BASE)['effective'] == SNAP['gate_a']['status']
      and rp.gate_status(SNAP, data_dir=BASE_DAILY, trusted_root=BASE)[0]
      == SNAP['gate_a']['status'],
      str(ssp(SNAP['sources_status'], data_dir=BASE_DAILY, trusted_root=BASE)[:1]))

ri, ok = no_exception(sb.resolve_inputs, DAY, BASE_DAILY, trusted_root=BASE)
check("A2 构建端EXACT: 四通道规范文件全选中",
      ok and isinstance(ri, dict)
      and all(ri[ch] is not None and ri[ch]['exact'] for ch in rp.SOURCE_CHANNELS),
      str({k: (v or {}).get('exact') for k, v in ri.items()} if isinstance(ri, dict) else ri))

with tempfile.TemporaryDirectory() as tdf:
    fixt.write_collectors(tdf, PREV)
    snap_fb, ok = no_exception(sb.build_snapshot, DAY, trusted_root=tdf,
                               data_dir=tdf, out_dir=tdf, as_of=fixt.as_of_for(DAY))
    check("A3 合法FALLBACK(真实回退lag=1)构建端接受且披露",
          ok and snap_fb is not None
          and snap_fb['sources_status']['global']['status'] == 'FALLBACK'
          and snap_fb['sources_status']['global']['lag_days'] == 1
          and '回退' in snap_fb['sources_status']['global'].get('disclosure', ''),
          str((snap_fb or {}).get('sources_status', {}).get('global')))

dtr = rp.default_trusted_root()
check("A4 可信根原语: 代码位置推导=真实目录/非链接/即项目根",
      os.path.isdir(dtr) and not os.path.islink(dtr)
      and os.path.basename(dtr) == os.path.basename(os.path.dirname(os.path.dirname(
          os.path.abspath(__file__))))
      and os.path.isdir(os.path.join(dtr, 'scripts')),
      dtr)

check("A5 采集目录==可信根(平铺沙箱)零问题",
      rp.trusted_dir_problems(BASE_DAILY, BASE_DAILY) == []
      and rp.trusted_dir_problems(BASE, BASE) == [],
      str(rp.trusted_dir_problems(BASE, BASE)[:1]))

with tempfile.TemporaryDirectory() as tdn:
    nested = os.path.join(tdn, 'proj', 'data', 'daily')
    os.makedirs(nested)
    check("A6 多级真实子目录(root/proj/data/daily)零问题",
          rp.trusted_dir_problems(nested, tdn) == [],
          str(rp.trusted_dir_problems(nested, tdn)[:1]))

    # 前缀形态差异(macOS /var→/private/var一类): 调用方给已解析形态,
    # 可信根给词法形态(或反之)——合法目录不得因前缀形态被误拒
    resolved_daily = os.path.realpath(nested)
    probs_mixed = rp.trusted_dir_problems(resolved_daily, tdn)
    check("A7 词法/解析前缀形态差异不误伤合法目录",
          probs_mixed == [],
          str(probs_mixed[:1]))

check("A8 构建即记录内容摘要(EXACT/FALLBACK通道含sha256,64位十六进制)",
      all(isinstance(SNAP['sources_status'][ch].get('sha256'), str)
          and len(SNAP['sources_status'][ch]['sha256']) == 64
          for ch in rp.SOURCE_CHANNELS),
      str({ch: SNAP['sources_status'][ch].get('sha256', '?')[:8]
           for ch in rp.SOURCE_CHANNELS}))

# ════════════════════════════════════════════════════════════════════
print("\n── B. 祖先符号链接(B1=FIX6验收报告原始反例精确复现)")

OUT1 = tempfile.mkdtemp(prefix='fix7-outside-')
TR1 = tempfile.mkdtemp(prefix='fix7-trusted-')
b8_dd, b8_out = _b8_layout(TR1, OUT1)
b8_full = os.path.join(b8_dd, f'global_{DAY}.json')
# B1 前提自证: 这正是FIX6被验收击穿的形态——文件非链接/规范名/realpath等式成立
check("B1a 反例前提成立(文件非链接+规范名+FIX6式realpath等式成立=旧检查必过)",
      os.path.isfile(b8_full) and not os.path.islink(b8_full)
      and rp.canonical_source_file('global', f'global_{DAY}.json') == DAY
      and os.path.realpath(b8_full) == os.path.join(os.path.realpath(b8_dd),
                                                    f'global_{DAY}.json'),
      f"isfile={os.path.isfile(b8_full)} link={os.path.islink(b8_full)}")

probs_b1 = ssp(SNAP['sources_status'], data_dir=b8_dd, trusted_root=TR1)
check("B1b 反例被拒: 可信根内data组件是符号链接→来源不可证明+点名信任边界",
      len(probs_b1) >= 1 and any(('符号链接' in p or '可信项目根' in p)
                                  for p in probs_b1),
      str(probs_b1[:1]))

st_b1 = rp.gate_status(SNAP, data_dir=b8_dd, trusted_root=TR1)
check("B1c 反例被拒: Gate A不可证明(None),绝不放行",
      st_b1[0] is None and ('符号链接' in st_b1[1] or '可信项目根' in st_b1[1]),
      str(st_b1[0]) + st_b1[1][:60])

# B2 daily组件是符号链接
OUT2 = tempfile.mkdtemp(prefix='fix7-outside2-')
TR2 = tempfile.mkdtemp(prefix='fix7-trusted2-')
fixt.write_collectors(OUT2, DAY)
os.makedirs(os.path.join(TR2, 'data'))
os.symlink(OUT2, os.path.join(TR2, 'data', 'daily'))
probs_b2 = ssp(SNAP['sources_status'], data_dir=os.path.join(TR2, 'data', 'daily'),
               trusted_root=TR2)
check("B2 daily组件是符号链接→拒(组件逐级核验)",
      any('符号链接' in p for p in probs_b2),
      str(probs_b2[:1]))

# B3 最终文件本身是符号链接(可信根内)
TR3 = tempfile.mkdtemp(prefix='fix7-trusted3-')
fixt.write_collectors(TR3, DAY)
os.rename(os.path.join(TR3, f'global_{DAY}.json'),
          os.path.join(TR3, f'global_{DAY}.real.json'))
os.symlink(os.path.join(TR3, f'global_{DAY}.real.json'),
           os.path.join(TR3, f'global_{DAY}.json'))
probs_b3 = ssp(SNAP['sources_status'], data_dir=TR3, trusted_root=TR3)
check("B3 最终来源文件是符号链接→拒(文件层既有语义在可信根框架下保持)",
      any('来源文件是符号链接' in p for p in probs_b3),
      str(probs_b3[:1]))

# B4 多级祖先: root/a/b 其中b是符号链接,daily在重定向之后
OUT4 = tempfile.mkdtemp(prefix='fix7-outside4-')
TR4 = tempfile.mkdtemp(prefix='fix7-trusted4-')
os.makedirs(os.path.join(OUT4, 'daily'))
fixt.write_collectors(os.path.join(OUT4, 'daily'), DAY)
os.makedirs(os.path.join(TR4, 'a'))
os.symlink(OUT4, os.path.join(TR4, 'a', 'b'))
dd4 = os.path.join(TR4, 'a', 'b', 'daily')
probs_b4 = ssp(SNAP['sources_status'], data_dir=dd4, trusted_root=TR4)
check("B4 多级祖先链接(a/b→outside,daily物理在外)→拒",
      any('符号链接' in p for p in probs_b4)
      and rp.gate_status(SNAP, data_dir=dd4, trusted_root=TR4)[0] is None,
      str(probs_b4[:1]))

# B5 采集目录本身经未批准符号链接传入(链接名位于可信根之内)
TR5 = tempfile.mkdtemp(prefix='fix7-trusted5-')
real5 = os.path.join(TR5, 'real_daily')
os.makedirs(real5)
fixt.write_collectors(real5, DAY)
os.symlink(real5, os.path.join(TR5, 'linked_daily'))
probs_b5 = ssp(SNAP['sources_status'], data_dir=os.path.join(TR5, 'linked_daily'),
               trusted_root=TR5)
check("B5 采集根自身经符号链接重定向(词法在可信根内)→拒",
      any('符号链接' in p for p in probs_b5),
      str(probs_b5[:1]))

# B6 无任何词法包含: data_dir直接=外部真实目录(非链接),realpath自洽
probs_b6 = ssp(SNAP['sources_status'], data_dir=b8_out, trusted_root=TR1)
check("B6 外部真实目录(无链接,realpath完全自洽)→拒:不建立外部存储白名单",
      any('不在可信项目根之内' in p for p in probs_b6),
      str(probs_b6[:1]))

# B7 构建端: B1布局下resolve_inputs不读取任何文件+build_snapshot不得产出PASS
ri_b7, ok_b7 = no_exception(sb.resolve_inputs, DAY, b8_dd, trusted_root=TR1)
with mock.patch('builtins.print'):
    snap_b7, ok_b7b = no_exception(sb.build_snapshot, DAY, b8_dd, b8_dd,
                                   trusted_root=TR1, as_of=fixt.as_of_for(DAY))
check("B7 构建端同拒: 不读取重定向目录任何文件,快照绝不PASS(§6.3上下游一致)",
      ok_b7 and isinstance(ri_b7, dict)
      and all(v is None for v in ri_b7.values())
      and ok_b7b and snap_b7 is not None
      and snap_b7['gate_a']['status'] != 'PASS'
      and all(snap_b7['sources_status'][ch]['status'] == 'MISSING'
              for ch in rp.SOURCE_CHANNELS),
      str(snap_b7['gate_a']['status']) if snap_b7 else 'build失败')

# B8 全链路: 装配器+周报预检(生产入口以模块配置锚定可信根,不传测试参数)
OUT8 = tempfile.mkdtemp(prefix='fix7-outside8-')
TR8 = tempfile.mkdtemp(prefix='fix7-trusted8-')
snap8, snap8_path, p8 = fixt.build_full_day(OUT8, DAY, skip={'pack', 'pack_meta'})
os.symlink(os.path.join(OUT8, 'data'), os.path.join(TR8, 'data'))
with mock.patch.object(da, 'DATA_DIR', os.path.join(TR8, 'data')), \
        mock.patch.object(da, 'datetime', DT):
    try:
        quiet(da.main)
        code8 = 0
    except SystemExit as e:
        code8 = e.code
pack8 = os.path.join(TR8, 'data', 'weekly', f'data_pack_{DAY}.md')
with mock.patch.object(rg, 'DATA_DIR', os.path.join(TR8, 'data')), \
        mock.patch.object(rg, 'datetime', DT):
    ok8, problems8, _ctx8 = quiet(rg.verify_research_inputs, DAY)
check("B8 全链路阻断: 装配器exit2/无数据包,周报预检拒(GLM前置即断,=0次调用)",
      code8 == 2 and not os.path.exists(pack8) and ok8 is False
      and any(('符号链接' in p or '可信项目根' in p) for p in problems8),
      f"exit={code8} pack={os.path.exists(pack8)} ok={ok8} {str(problems8)[:80]}")

# ════════════════════════════════════════════════════════════════════
print("\n── C. 其他边界(可信根框架下的文件层与身份层)")


def _ss_channel(ch, status='EXACT', file=None, file_date=DAY):
    """覆写单通道sources_status声明(其余通道保持真实EXACT)。"""
    ss = copy.deepcopy(SNAP['sources_status'])
    ss[ch] = {'status': status, 'file': file, 'file_date': file_date}
    return ss


with tempfile.TemporaryDirectory() as tdc:
    fixt.write_collectors(tdc, DAY)
    os.remove(os.path.join(tdc, f'global_{DAY}.json'))
    os.mkdir(os.path.join(tdc, f'global_{DAY}.json'))
    probs_c1 = ssp(SNAP['sources_status'], data_dir=tdc, trusted_root=tdc)
    check("C1 目录冒充JSON→拒", any('来源文件是目录' in p for p in probs_c1),
          str(probs_c1[:1]))

with tempfile.TemporaryDirectory() as tdc:
    fixt.write_collectors(tdc, DAY)
    os.remove(os.path.join(tdc, f'china_{DAY}.json'))
    probs_c2 = ssp(SNAP['sources_status'], data_dir=tdc, trusted_root=tdc)
    check("C2 声明文件不存在→拒(可诊断:通道+文件名+原因)",
          any('china' in p and '在采集目录不存在' in p for p in probs_c2),
          str(probs_c2[:1]))

ss_c3 = _ss_channel('global', file=f'../global_{DAY}.json')
check("C3 file含../路径成分→拒(身份层,无需文件系统)",
      any('路径成分' in p for p in ssp(ss_c3, BASE_DAILY, trusted_root=BASE)),
      str(ssp(ss_c3, BASE_DAILY, trusted_root=BASE)[:1]))

ss_c4 = _ss_channel('global', file=f'/etc/global_{DAY}.json')
check("C4 file为绝对路径→拒", any('路径成分' in p for p in ssp(ss_c4)),
      str(ssp(ss_c4)[:1]))

ss_c5 = _ss_channel('global', file=f'macro_{DAY}.json')
check("C5 跨通道文件(global声明macro文件)→拒",
      any('不符通道规范文件名' in p for p in ssp(ss_c5, BASE_DAILY, trusted_root=BASE)),
      str(ssp(ss_c5, BASE_DAILY, trusted_root=BASE)[:1]))

ss_c6 = _ss_channel('global', file=f'global_{DAY}.json.bak')
check("C6 非规范扩展名(.bak/.txt)→拒",
      any('不符通道规范文件名' in p for p in ssp(ss_c6)),
      str(ssp(ss_c6)[:1]))

with tempfile.TemporaryDirectory() as tdc:
    fixt.write_collectors(tdc, DAY)
    with open(os.path.join(tdc, f'global_{DAY}.json'), 'w') as f:
        f.write('THIS IS NOT JSON')
    snap_c7, ok_c7 = no_exception(sb.build_snapshot, DAY, tdc, tdc,
                                  trusted_root=tdc, as_of=fixt.as_of_for(DAY))
    check("C7 损坏内容(非JSON): 新建快照流程识别为READ_FAIL(可诊断error)",
          ok_c7 and snap_c7 is not None
          and snap_c7['sources_status']['global']['status'] == 'READ_FAIL'
          and isinstance(snap_c7['sources_status']['global'].get('error'), str)
          and snap_c7['gate_a']['status'] != 'PASS',
          str((snap_c7 or {}).get('sources_status', {}).get('global')))

check("C8 正常对照: 同一可信目录内正常文件零问题(不误伤)",
      ssp(SNAP['sources_status'], data_dir=BASE_DAILY, trusted_root=BASE) == [],
      str(ssp(SNAP['sources_status'], data_dir=BASE_DAILY, trusted_root=BASE)[:1]))

# ════════════════════════════════════════════════════════════════════
print("\n── D. 历史与临时目录兼容")

with tempfile.TemporaryDirectory() as tdd:
    fixt.write_collectors(tdd, DAY)
    snap_d1, ok_d1 = no_exception(sb.build_snapshot, DAY, tdd, tdd,
                                  trusted_root=tdd, as_of=fixt.as_of_for(DAY))
    probs_d1 = ssp(snap_d1['sources_status'], data_dir=tdd, trusted_root=tdd)
    check("D1 tempfile.TemporaryDirectory结构+显式fixture可信根正常工作",
          ok_d1 and snap_d1 is not None
          and snap_d1['gate_a']['status'] == 'PASS' and probs_d1 == [],
          str(probs_d1[:1]))

ri_d2, ok_d2 = no_exception(sb.resolve_inputs, DAY, BASE_DAILY, trusted_root=BASE)
check("D2 自定义平铺非符号链接测试目录(dir==可信根)正常",
      ok_d2 and ri_d2['global'] is not None and ri_d2['global']['exact'],
      str(ri_d2.get('global') if isinstance(ri_d2, dict) else ri_d2))

# D3 纯历史口径: 真实构建的合法回退快照,原始文件随后不可访问——
# 结构证据(facts/sources_status/fact-source批次绑定)仍可复算,不虚报实体核验
TDA = tempfile.mkdtemp(prefix='fix7-hist-')
fixt.write_collectors(TDA, PREV)          # 仅前一日文件(合法FALLBACK日)
snap_hist, ok_h = no_exception(sb.build_snapshot, DAY, TDA, TDA,
                               trusted_root=TDA, as_of=fixt.as_of_for(DAY))
for _f in os.listdir(TDA):                # 构建后删除全部原始采集文件
    os.remove(os.path.join(TDA, _f))
check("D3 纯历史口径(data_dir=None): 原始文件已删,结构复算仍过,不虚报实体/内容核验",
      ok_h and snap_hist is not None
      and snap_hist['gate_a']['status'] == 'PASS'
      and ssp(snap_hist['sources_status']) == []
      and rp.recompute_gate_a(snap_hist)['effective'] == 'PASS'
      and rp.gate_status(snap_hist)[0] == 'PASS',
      str(ssp(snap_hist['sources_status'])[:1]))

prov_d4 = rp.provenance_of(SNAP, os.path.basename(SNAP_PATH))
check("D4 裸文件名元数据边界: 无data_dir→纯重验口径(gate为结构重算值)",
      prov_d4['gate_a'] == SNAP['gate_a']['status']
      and prov_d4['snapshot_digest'] == rp.digest_snapshot(SNAP),
      str(prov_d4))

probs_d5_formal = ssp(snap_hist['sources_status'], data_dir=BASE_DAILY,
                      trusted_root=BASE)
check("D5 正式vs历史授权差异: 同一合法回退声明正式口径拒(BASE无该批次实体),"
      "历史口径结构过",
      any('在采集目录不存在' in p for p in probs_d5_formal)
      and ssp(snap_hist['sources_status']) == [],
      f"formal={len(probs_d5_formal)} hist={len(ssp(snap_hist['sources_status']))}")

# ════════════════════════════════════════════════════════════════════
print("\n── E. 链路传播与缺省fail-closed")

with tempfile.TemporaryDirectory() as tde:
    fixt.write_collectors(tde, DAY)
    r_e1 = subprocess.run(
        [PY, os.path.join(ROOT, 'scripts', 'snapshot_builder.py'),
         '--date', DAY, '--data-dir', tde, '--out-dir', tde],
        capture_output=True, text=True, timeout=120)
    check("E1 CLI缺省可信根fail-closed: 沙箱--data-dir不传--trusted-root"
          "→拒读+exit 2(生产默认=代码位置锚,测试参数非后门)",
          r_e1.returncode == 2 and 'FIX7信任边界' in r_e1.stdout,
          f"exit={r_e1.returncode} out={r_e1.stdout[:80]!r}")

views_e = os.path.join(OUT8, 'views.json')
with open(views_e, 'w', encoding='utf-8') as f:
    json.dump({'predictions': [
        {'pred_id': 'P1', 'status': 'observing', 'metric': 'SPX',
         'op': '>=', 'target': 7000, 'created': '2026-10-17'}]}, f, ensure_ascii=False)
views_bytes = open(views_e, 'rb').read()
anchors_e = json.load(open(p8['anchors'], encoding='utf-8'))
ch_e, n_e, st_e = dpo.observe(views_path=views_e, anchors=anchors_e,
                              today_str='2026-10-24', anchors_date=DAY,
                              anchors_path=os.path.join(TR8, 'data', 'daily',
                                                        f'anchors_{DAY}.json'),
                              trusted_root=TR8)
check("E2 观察器: 祖先链接采集目录的锚点批次→关键FAIL,长期状态字节不变",
      st_e == 'FAIL' and ch_e == [] and open(views_e, 'rb').read() == views_bytes,
      f"st={st_e} ch={len(ch_e)}")

# E3 无快照/无数据包产出: 既有正式报告与长期状态保持(B8已证exit2/预检拒);
# 此处补: 重定向下不产生新合格正式报告文件
weekly_e = os.path.join(TR8, 'data', 'weekly')
new_reports = [f for f in os.listdir(weekly_e) if f.startswith('weekly_report_')] \
    if os.path.isdir(weekly_e) else []
check("E3 重定向下零新增正式报告(既有报告/发布状态不受影响)",
      new_reports == [] and not os.path.exists(
          os.path.join(TR8, 'data', 'weekly', f'data_pack_{DAY}.md')),
      str(new_reports))

st_e4 = rp.gate_status(SNAP, data_dir=BASE_DAILY)
check("E4 测试参数非生产后门: 直调不传trusted_root→按缺省代码锚fail-closed拒",
      st_e4[0] is None and '不在可信项目根之内' in st_e4[1],
      str(st_e4[0]) + st_e4[1][:60])

# ════════════════════════════════════════════════════════════════════
print("\n── R. IA-F6-RISK-002: 原始采集文件内容变异(证据化验证,§9)")

with tempfile.TemporaryDirectory() as tdr:
    fixt.write_collectors(tdr, DAY)
    snap_r, _ = no_exception(sb.build_snapshot, DAY, tdr, tdr,
                             trusted_root=tdr, as_of=fixt.as_of_for(DAY))
    # R1 变异为非JSON(保留文件名/路径)
    with open(os.path.join(tdr, f'global_{DAY}.json'), 'w') as f:
        f.write('THIS IS NOT JSON')
    st_r1 = rp.gate_status(snap_r, data_dir=tdr, trusted_root=tdr)
    check("R1 既有快照复核: 内容→非JSON(文件名/日期不变)→摘要失配拒绝",
          st_r1[0] is None and '摘要' in st_r1[1],
          str(st_r1[0]) + st_r1[1][:80])

    snap_r1b, ok_r1b = no_exception(sb.build_snapshot, DAY, tdr,
                                    os.path.join(tdr, 'out2'),
                                    trusted_root=tdr, as_of=fixt.as_of_for(DAY))
    check("R1b 新建快照流程识别解析失败(READ_FAIL+error留痕,不吞异常)",
          ok_r1b and snap_r1b['sources_status']['global']['status'] == 'READ_FAIL'
          and snap_r1b['gate_a']['status'] != 'PASS',
          str((snap_r1b or {}).get('sources_status', {}).get('global')))

with tempfile.TemporaryDirectory() as tdr:
    fixt.write_collectors(tdr, DAY)
    snap_r2, _ = no_exception(sb.build_snapshot, DAY, tdr, tdr,
                              trusted_root=tdr, as_of=fixt.as_of_for(DAY))
    _raw = json.load(open(os.path.join(tdr, f'global_{DAY}.json'), encoding='utf-8'))
    _raw['data']['SPX']['close'] = 99999.0   # 仍是合法JSON,数值被改
    json.dump(_raw, open(os.path.join(tdr, f'global_{DAY}.json'), 'w',
                         encoding='utf-8'), ensure_ascii=False)
    st_r2 = rp.gate_status(snap_r2, data_dir=tdr, trusted_root=tdr)
    check("R2 内容改为仍合法JSON(数值篡改)→摘要失配拒绝",
          st_r2[0] is None and '摘要' in st_r2[1], str(st_r2[0]))

with tempfile.TemporaryDirectory() as tdr:
    fixt.write_collectors(tdr, DAY)
    snap_r3, _ = no_exception(sb.build_snapshot, DAY, tdr, tdr,
                              trusted_root=tdr, as_of=fixt.as_of_for(DAY))
    st_r3 = rp.gate_status(snap_r3, data_dir=tdr, trusted_root=tdr)
    check("R3 内容未变→复核通过(摘要一致,零误伤)",
          st_r3[0] == snap_r3['gate_a']['status'], str(st_r3[0]))

with tempfile.TemporaryDirectory() as tdr:
    fixt.write_collectors(tdr, DAY)
    snap_r4, _ = no_exception(sb.build_snapshot, DAY, tdr, tdr,
                              trusted_root=tdr, as_of=fixt.as_of_for(DAY))
    os.remove(os.path.join(tdr, f'global_{DAY}.json'))   # 历史原始文件不可访问
    st_r4f = rp.gate_status(snap_r4, data_dir=tdr, trusted_root=tdr)
    st_r4h = rp.gate_status(snap_r4)
    check("R4 原始文件不可访问: 正式口径拒(不存在),纯历史口径不受影响",
          st_r4f[0] is None and '在采集目录不存在' in st_r4f[1]
          and st_r4h[0] == snap_r4['gate_a']['status'],
          f"formal={st_r4f[0]} hist={st_r4h[0]}")

with tempfile.TemporaryDirectory() as tdr:
    fixt.write_collectors(tdr, DAY)
    snap_r5, _ = no_exception(sb.build_snapshot, DAY, tdr, tdr,
                              trusted_root=tdr, as_of=fixt.as_of_for(DAY))
    for ch in rp.SOURCE_CHANNELS:   # 剥离摘要字段=FIX7前历史快照形态
        snap_r5['sources_status'][ch].pop('sha256', None)
    with open(os.path.join(tdr, f'global_{DAY}.json'), 'w') as f:
        f.write('THIS IS NOT JSON')
    probs_r5 = ssp(snap_r5['sources_status'], data_dir=tdr, trusted_root=tdr)
    st_r5 = rp.gate_status(snap_r5, data_dir=tdr, trusted_root=tdr)
    check("R5 历史快照(无摘要字段): 不虚报内容核验,实体核验照常(证据边界如实)",
          not any('摘要' in p for p in probs_r5) and st_r5[0] == 'PASS',
          f"probs={probs_r5[:1]} st={st_r5[0]}")

# ════════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
if FAIL_N == 0:
    print(f"FIX7 结果: {PASS_N}通过 / 0失败")
else:
    print(f"FIX7 结果: {PASS_N}通过 / {FAIL_N}失败")
    sys.exit(1)
