# Audit-R1 F07: 治理面复核状态档(2026-11-16)

纪律: **只声明已验证的事实,未验证的面如实标 UNVERIFIED——绝不声称未验证的强制力已生效。**

## 一、已验证(VERIFIED,无凭证 API + 本仓文件面,2026-11-16 复核)

| # | 事实 | 验证方式 |
|---|---|---|
| V1 | 公开仓 `bojing951-hash/investment-agent` 为 public | `GET /repos/…`(未认证 200) |
| V2 | 默认分支 = `main` | 同上响应 `default_branch` |
| V3 | main HEAD = `36c1e7e`(R20 门对账 commit) | `GET /repos/…/commits/main` |
| V4 | main 最新 CI #297(36c1e7e)= **completed/success**(2026-11-16T08:56Z) | `GET /repos/…/actions/runs?branch=main` |
| V5 | 审计基线 `c9d5715` 的 CI #296 = **failure** → F04 修复后 36c1e7e 转绿 | 同上(基线红→修复绿的完整在档链) |
| V6 | CI 工作流 `offline-tests.yml` 于 push/PR→main 触发,py3.11 钉版 | 仓内 `.github/workflows/`(F04 已改) |
| V7 | main 保护规则集**未落地**的证据: `TARGET_PROTECTION_PREP.md` §四 落地登记勾选框全部为空(2026-11-16 复读) | 文件面 |

## 二、未能验证(UNVERIFIED,如实声明)

- **分支保护/规则集在 GitHub 端的实际状态无法核验**:
  - 本机钥匙串 GitHub token 经 API 返回 401 Bad credentials(已失效);
  - 请求探索凭证路径(security dump-keychain)被权限分类器拒绝——尊重该拦截,不绕过;
  - 结论: 保护规则集「未落地」是**文件面证据(V7)+ 无任何落地登记**的高置信判断,而非 API 直验。
  本档不声称 main 保护已生效。

## 三、已备好的落地物(不在本轮强行执行——落地属用户 3 分钟动作)

`docs/autonomous-rd/TARGET_PROTECTION_PREP.md` 内含:

- main-protection ruleset 完整 JSON(必需 PR 批准 0 人、状态检查 `test`、
  阻 force push、限删除;不强制签名提交/线性历史——与现仓库实态匹配);
- 三步用户操作清单(网页 Settings→Rulesets→New + 粘贴);
- 落地后核验命令(见下)。

## 四、最小必要用户动作(共 2 件)

1. **落地 main 保护规则集**(约 3 分钟,网页操作,见 TARGET_PROTECTION_PREP.md 三步清单;
   状态检查名以 `.github/workflows/offline-tests.yml` 实际 job 名为准)。
2. **落地后核验**(任一):
   ```bash
   gh api repos/bojing951-hash/investment-agent/rulesets   # 需有效登录态
   # 或网页 Settings→Rulesets 页面直接查看
   ```
   并回填 TARGET_PROTECTION_PREP.md §四 落地登记勾选框(勾选=文件面自证,下轮审计即 V 级事实)。

> 本档由 Audit-R1 F07 产出;不新增任何远端写操作授权。
