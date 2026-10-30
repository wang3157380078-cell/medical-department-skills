# 科室病历 Skills 总库

本公开仓库按科室独立组织。每个 `departments/<科室标识>/` 含完整的 `skill/` 与原始 `plugin.zip`；修改、选择或复制某科室时无需改动其他目录。

## 科室目录（共16科）

| 科室 | 独立目录 | 精确调用名称 |
|---|---|---|
| 骨科 | [`write-orthopedic-medical-records`](departments/write-orthopedic-medical-records/) | `$write-orthopedic-medical-records` |
| 心内科 | [`cardiology-inpatient-records`](departments/cardiology-inpatient-records/) | `$cardiology-inpatient-records` |
| 老年内科 | [`geriatrics-inpatient-records`](departments/geriatrics-inpatient-records/) | `$geriatrics-inpatient-records` |
| 神经内科（含介入） | [`neurology-inpatient-records`](departments/neurology-inpatient-records/) | `$neurology-inpatient-records` |
| 神经外科 | [`neurosurgery-inpatient-records`](departments/neurosurgery-inpatient-records/) | `$neurosurgery-inpatient-records` |
| 呼吸内科 | [`pulmonology-inpatient-records`](departments/pulmonology-inpatient-records/) | `$pulmonology-inpatient-records` |
| 内分泌科 | [`endocrinology-inpatient-records`](departments/endocrinology-inpatient-records/) | `$endocrinology-inpatient-records` |
| 消化内科（含胃肠镜） | [`gastroenterology-inpatient-records`](departments/gastroenterology-inpatient-records/) | `$gastroenterology-inpatient-records` |
| 普外科（肝胆胰脾胃肠肛肠） | [`general-surgery-inpatient-records`](departments/general-surgery-inpatient-records/) | `$general-surgery-inpatient-records` |
| 普外科（甲状腺甲旁腺乳腺） | [`thyroid-breast-surgery-records`](departments/thyroid-breast-surgery-records/) | `$thyroid-breast-surgery-records` |
| 肾内科 | [`nephrology-inpatient-records`](departments/nephrology-inpatient-records/) | `$nephrology-inpatient-records` |
| 泌尿外科 | [`urology-inpatient-records`](departments/urology-inpatient-records/) | `$urology-inpatient-records` |
| 麻醉科 | [`anesthesiology-medical-records`](departments/anesthesiology-medical-records/) | `$anesthesiology-medical-records` |
| 儿科 | [`pediatrics-inpatient-records`](departments/pediatrics-inpatient-records/) | `$pediatrics-inpatient-records` |
| 皮肤科 | [`dermatology-medical-records`](departments/dermatology-medical-records/) | `$dermatology-medical-records` |
| 妇产科 | [`obstetrics-gynecology-records`](departments/obstetrics-gynecology-records/) | `$obstetrics-gynecology-records` |

## 单独接入

从目标目录下载 `plugin.zip`，按目标平台的插件安装流程导入；部分科室还提供单科 `skill.zip`；或将目标目录的 `skill/` 完整复制为相应环境的独立 Skill 目录，并以表中的名称明确调用。不能只复制 `SKILL.md`：它还引用本目录中的 `references/` 等文件。不同 AI 平台的安装和发现方式各异，GitHub 连接本身不会自动安装或执行 Skill。

各科目录彼此独立，运行时只选择需要的科室；宿主 AI 的自动调用、上下文和其他已安装插件由宿主控制，不能保证所有平台绝不会调用其他技能。GitHub 的访问权限通常按仓库授予，并非按文件夹隔离；若不同使用者只能访问各自科室，应另建权限独立的仓库。

## 后续增加科室

在 `departments/` 下新增唯一的科室标识目录，包含 `skill/SKILL.md`、其全部相对路径依赖和单科 `plugin.zip`，验证后在上表添加一行。不得覆盖其他科室目录；保持技能名称唯一。

病历使用应遵循各科 Skill 中的真实资料和医师审核要求，避免把患者资料或病历产出提交到仓库。
