#!/usr/bin/env python3
"""Charter 5 S7 新增套件②: usage_log 实际值捕获(S2 实质违规修复的行为锁)。

S2 违规事实(修复前): usage_log/登记行回显硬编码登记默认端点/模型名,而非
本进程实际生效的配置值——记录失真(换了端点日志仍显示旧默认)。
行为锁:
- ① run_live_conclusion 用量记录 rec.model/rec.endpoint_host=env_config
  实际配置值(合成桩注入,零真实出站;预期值=测试自设字面量);
- ② 三参不齐(只设 MODEL_API_KEY)→ rec.model/rec.endpoint_host 如实 null,
  绝不回退任何默认端点/模型名;
- ③ 登记行 render_registry_row 模型@端点=实际配置值,零默认端点字面量;
- ④ 模块源码级: 零硬编码默认端点/模型名常量,echo 无厂商键,
  执行门常量=MODEL_API_KEY/RUN_MODEL_LIVE;
- ⑤ 执行门只认 MODEL_API_KEY: 误设旧变量名不开门。
预期值全部独立硬编码,不用被测模块自算。
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import model_conclusion_client as mcc            # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_p03_w2_model_g4 as g4mod             # noqa: E402 (fixture 复用,禁复制分叉)

SRC = os.path.join(ROOT, 'scripts', 'model_conclusion_client.py')
MODULE_SOURCE = open(SRC, encoding='utf-8').read()

FAKE_MODEL = 'my-custom-model-7b'
FAKE_BASE = 'https://my-endpoint.example.test/v1'
FAKE_HOST = 'my-endpoint.example.test'          # 手工推导: strip scheme+path
CRED = 'sk-USAGE-TEST-SENTINEL'

PASS, FAIL = 0, 0


def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}  {detail}")


class StubFactory:
    """合成桩(零真实出站): 每次调用回一个合法缺席输出,驱动编排走完整链。"""

    def __init__(self):
        self.calls = 0

    def __call__(self):
        return type('StubClient', (), {})()


class OkStream:
    """流式桩协议: 一段合法 JSON 正文+usage。"""

    def __init__(self, payload):
        self._payload = payload
        self._sent = False
        self.usage = type('U', (), {'prompt_tokens': 10,
                                    'completion_tokens': 5})()

    def __iter__(self):
        return self

    def __next__(self):
        if self._sent:
            raise StopIteration
        self._sent = True
        delta = type('D', (), {'content': json.dumps(self._payload)})()
        choice = type('C', (), {'delta': delta})()
        return type('E', (), {'choices': [choice], 'usage': self.usage})()


def ok_factory(payload):
    def _factory():
        return _OkClient(payload)
    return _factory


class _OkClient:
    def __init__(self, payload):
        self._payload = payload
        self.chat = self

    @property
    def completions(self):
        return self

    def create(self, **kw):
        return OkStream(self._payload)


VALID_ABSENT_OUTPUT = None   # 延迟初始化(g4mod fixture,见下)


print("═" * 64)
print("Charter5 S7-② usage_log 实际值捕获(S2 修复行为锁)")
print("═" * 64)

_saved = {k: os.environ.get(k) for k in
          ('RUN_MODEL_LIVE', 'MODEL_API_KEY', 'MODEL_BASE_URL', 'MODEL_NAME',
           'GLM_API_KEY')}
os.environ.pop('GLM_API_KEY', None)


# fixture 复用(禁复制分叉): 输入与合法缺席输出均来自 g4 套件既有合成面
make_inp = g4mod.build_absent_inp
VALID_ABSENT_OUTPUT = g4mod.build_valid_output(absent=True)


try:
    os.environ['RUN_MODEL_LIVE'] = '1'
    os.environ['MODEL_API_KEY'] = CRED
    os.environ['MODEL_BASE_URL'] = FAKE_BASE
    os.environ['MODEL_NAME'] = FAKE_MODEL

    # ── ① 用量记录记实际配置值(合成桩,零真实出站) ──
    with tempfile.TemporaryDirectory() as td:
        log = os.path.join(td, 'usage.jsonl')
        mcc.run_live_conclusion(make_inp(), client_factory=ok_factory(VALID_ABSENT_OUTPUT),
                                today_iso='2026-11-09',
                                usage_log_path=log)
        with open(log, encoding='utf-8') as fh:
            recs = [json.loads(x) for x in fh if x.strip()]
        check("用量记录在场(≥1 行)", len(recs) >= 1, str(len(recs)))
        r0 = recs[0]
        check(f"rec.model=实际配置值({FAKE_MODEL})",
              r0.get('model') == FAKE_MODEL, repr(r0.get('model')))
        check(f"rec.endpoint_host=base_url 派生主机({FAKE_HOST})",
              r0.get('endpoint_host') == FAKE_HOST, repr(r0.get('endpoint_host')))
        check("整份日志零旧默认端点字面量(bigmodel 不出现)",
              'bigmodel' not in open(log, encoding='utf-8').read().lower())

    # ── ② 三参不齐(缺 MODEL_NAME/BASE_URL)→ 如实 null,零默认回填 ──
    os.environ.pop('MODEL_BASE_URL', None)
    os.environ.pop('MODEL_NAME', None)
    with tempfile.TemporaryDirectory() as td:
        log = os.path.join(td, 'usage2.jsonl')
        mcc.run_live_conclusion(make_inp(), client_factory=ok_factory(VALID_ABSENT_OUTPUT),
                                today_iso='2026-11-09',
                                usage_log_path=log)
        recs = [json.loads(x) for x in
                open(log, encoding='utf-8') if x.strip()]
        check("三参不齐→rec.model 如实 null(不回填默认模型名)",
              recs and recs[0].get('model') is None, repr(recs[:1]))
        check("三参不齐→rec.endpoint_host 如实 null(不回填默认端点)",
              recs and recs[0].get('endpoint_host') is None)

    # ── ③ 登记行=实际配置值 ──
    os.environ['MODEL_BASE_URL'] = FAKE_BASE
    os.environ['MODEL_NAME'] = FAKE_MODEL
    row = mcc.render_registry_row(
        7, face='T', purpose='实际值测试(合成)', outbound_count=1, cost_usd=0.02,
        breaker_state=mcc.CircuitBreaker(day_utc='2026-11-09').state(),
        ts_utc='2026-11-09T00:00:00Z')
    check("登记行含实际模型@端点", f'{FAKE_MODEL} @ {FAKE_BASE}' in row, row)
    check("登记行零旧默认端点", 'bigmodel' not in row.lower())

    # ── ④ 源码级: 零硬编码默认端点/模型名,echo 无厂商键,门常量中性 ──
    check("模块源码零默认端点 URL(bigmodel.cn 不出现)",
          'bigmodel' not in MODULE_SOURCE.lower())
    echo = mcc.echo_params()
    check("echo 无厂商残留键", not any('glm' in k for k in echo), str(list(echo)))
    check("echo.credential_env=MODEL_API_KEY", echo['credential_env'] == 'MODEL_API_KEY')
    check("echo.live_gate_env=RUN_MODEL_LIVE", echo['live_gate_env'] == 'RUN_MODEL_LIVE')

    # ── ⑤ 执行门只认 MODEL_API_KEY: 误设旧变量名不开门 ──
    os.environ.pop('MODEL_API_KEY', None)
    os.environ['GLM_API_KEY'] = CRED          # 旧变量名误设(值同)——不得开门
    try:
        mcc.run_live_conclusion(make_inp(), client_factory=ok_factory(VALID_ABSENT_OUTPUT),
                                today_iso='2026-11-09')
        gate_refused = False
    except mcc.LiveGateRefused:
        gate_refused = True
    check("执行门只认 MODEL_API_KEY(旧变量名不开门)",
          gate_refused is True)
finally:
    for k, v in _saved.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v

sys.exit(0 if FAIL == 0 else 1)
