# TARGET_PROTECTION_PREP — main 保护/必需检查配置准备件(Product Convergence Phase 1)

> 产出目的: 章程§八「main 分支保护/Ruleset/必需检查=外部权限项」——本档把
> 需要仓库所有者(GitHub 网页)操作的全部步骤收敛为**唯一清单**,并给出可复制的
> 配置值;除此外零用户操作。仓库内哈希守卫(scripts/target_integrity_guard.py)
> 的诚实边界=开发Agent可改注册表本身,真强制力仅来自本档项落地。

## 一、唯一需用户操作清单(三步,约 3 分钟)

1. 打开 `https://github.com/bojing951-hash/investment-agent/settings/rulesets/new`
   (须 Owner 权限;URL 即直达新建 Ruleset 页)。
2. 按下方§二「Ruleset 配置值」逐字段填入→Create。
3. 回本档底部§四勾选落地日期(或告知操作者席代记),守卫套件 §A 不依赖此步
   (它测的是仓库内注册表一致性,本档=其诚实边界的真门)。

## 二、Ruleset 配置值(可复制)

- **Rule set name**: `main-protection`
- **Enforcement status**: Active
- **Target branches**: Include by pattern → `main`
- **Rules**:
  - ☑ Require a pull request before merging
    - Required approvals: **0**(单人仓库;PR=留审阅痕,合并者=所有者本人)
    - ☑ Require review from Code Owners(无 CODEOWNERS 时忽略)
  - ☑ Require status checks to pass
    - Required checks 搜索框输入: `test`(选中本仓 CI job 名;若 job 名
      为 `tests` 即选之)——**先推送本分支后首跑 CI 才能在下拉出现 job 名**
    - ☑ Require branches to be up to date before merging
  - ☑ Block force pushes
  - ☑ Restrict deletions
- **不勾**: Require signed commits(本仓提交均 GPG 无签名,勾选即全堵)。
  Require linear history(可选;若勾,操作者席并轨须 rebase 形态,R32 判例
  的 merge--no-ff 将不可用——建议不勾,保留撞号并轨的 merge 语义)。

## 三、落地后的行为变化(如实预告)

- 操作者席/引擎席不能再直接 `git push origin HEAD:main`;须开 PR→CI 绿→
  所有者点 merge(或所有者授权的本地 merge+PR 自并)。既有 IA 波次合并授权
  的执行形态将受此约束=**这正是章程要的**:合并 main 的每次落地都有所有者
  可见的 PR 痕迹。
- CI 红=真堵(当前 CI 文件存在但无保护=推送即落,CI 红不影响合并)。
- 目标/验收契约被擅改→即使 PR 也过不了 target_integrity 守卫的红。

## 四、落地登记(用户操作后填)

- [ ] 落地日期: ____ ;操作者: 用户本人
- [ ] 落地后验证: 操作者席跑 `gh api repos/.../rulesets` 记录 id+enforcement
- [ ] 首个走 PR 的并轨轮次号: ____

> 未落地期间: 仓库内守卫(13 判)+双口径终验+七项门=现有防线,如实计为
> PARTIAL 强制力,不冒称已保护。
