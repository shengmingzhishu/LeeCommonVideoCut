# 前后端联调 Checklist

> 每次跨端联调时逐项检查

---

## 1. 环境准备

- [ ] 后端已启动（`http://localhost:8000`）
- [ ] 前端已启动（`http://localhost:5173`）
- [ ] `GET /api/health` 返回 `{ code: 0, msg: "ok", data: { status: "ok" } }`
- [ ] ffmpeg/ffprobe 在系统 PATH 中可用（`ffmpeg -version`）
- [ ] edge-tts 可用（后端依赖）

## 2. CORS 验证

- [ ] 前端控制台无 CORS 报错
- [ ] 后端 CORS 配置允许 `http://localhost:5173`
- [ ] Vite proxy `/api` → `http://localhost:8000` 生效

## 3. 接口验证

- [ ] 请求方法（GET/POST/PUT/DELETE）与契约一致
- [ ] 请求路径与契约一致
- [ ] 请求体字段名与契约附录 A 一致（camelCase）
- [ ] 响应体结构为 `{ code, msg, data }`
- [ ] 响应字段名经 to_camel 转换后与前端类型一致
- [ ] 错误码在约定区间内（40xxx/50xxx/60xxx）

## 4. TraceId 验证

- [ ] 前端请求带 `X-Trace-Id` header
- [ ] 后端日志中出现该 traceId
- [ ] 响应头回传 `X-Trace-Id`

## 5. 步骤流程验证

- [ ] Step1: POST /api/step1/load 可加载素材
- [ ] Step2: POST /api/step2/analyze 返回关键词拆解
- [ ] Step3: POST /api/step3/generate 返回口播文案
- [ ] Step4: POST /api/step4/audio 返回 taskId，轮询可完成
- [ ] Step4: POST /api/step4/markers 返回标记列表
- [ ] Step5: PUT /api/step5/save 可保存编辑后标记
- [ ] Step6: POST /api/step6/cut 返回 taskId，轮询可完成
- [ ] Step7: POST /api/step7/compose 返回 taskId，轮询可完成

## 6. 长任务验证

- [ ] 任务提交立即返回 taskId
- [ ] GET /api/task/{id} 可查询状态
- [ ] 任务进度 (progress) 正常更新
- [ ] 任务完成后状态变为 completed
- [ ] 任务取消接口可中断正在执行的任务
- [ ] 页面卸载后轮询停止（无 setState on unmounted 报错）

## 7. 错误处理验证

- [ ] 参数缺失返回 40xxx 错误码
- [ ] 项目不存在返回 40003
- [ ] 步骤锁定冲突返回 40010
- [ ] LLM 异常返回 50001
- [ ] ffmpeg 异常返回 50004
- [ ] 任务失败返回 60001
- [ ] 前端正确展示错误信息（msg 字段）

## 8. 虚拟预览验证（Step5）

- [ ] 预览阶段无 ffmpeg IO 操作
- [ ] `<video>.currentTime` 可正常 seek
- [ ] 标记片段串播流畅
- [ ] 标记可增删改
- [ ] 切换项目/步骤后 `<video>` src 被释放

## 9. 文件交互验证

- [ ] GET /api/file/preview 可预览视频文件
- [ ] GET /api/file/download 可下载文件
- [ ] GET /api/dir/browse 可浏览目录
- [ ] 路径遍历攻击被阻止（如 `../../../etc/passwd`）

## 10. 项目管理验证

- [ ] GET /api/projects 返回项目列表
- [ ] POST /api/projects 可创建项目
- [ ] PUT /api/projects/{id} 可更新项目
- [ ] DELETE /api/projects/{id} 可删除项目
- [ ] POST /api/projects/{id}/duplicate 可复制项目
- [ ] GET /api/history 返回生成历史
- [ ] POST /api/history/{id}/rollback 可回滚
