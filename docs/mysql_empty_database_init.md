# 空库一键初始化（MySQL）

在**无任何表**的数据库中执行以下脚本，创建与 `backend/app/models` 一致的结构，并插入默认管理员账号。

- 库 / 连接字符集请使用 `utf8mb4`（例如连接串加 `?charset=utf8mb4`）。
- `external_api_scene_bindings` 中三个 `TEXT` 字段在 MySQL 中不设默认值（`TEXT`/`BLOB` 在多数配置下不能带 `DEFAULT`），由应用层写入；与 ORM 的 Python 侧默认值 `[]` 行为一致。
- 若已由应用 `DB_AUTO_CREATE_TABLES` 建表，请勿重复执行建表；仅需按需插入 `users` 或改用 `DB_RUN_SEED`。
- 首次登录后请立即修改默认密码。
- `tasks.created_at` 表示任务记录创建时间。
- `tasks.enqueued_at` 表示任务成功进入分发/入队流程的时间，可用于计算排队耗时。
- `tasks.updated_at` 表示任务最近一次状态或内容更新的时间；任务完成后可结合 `created_at` 估算总耗时。

## 关键字段说明

下面只列出后续排查问题、查任务链路、核对配置时最常用的字段语义。

### `users`

- `id`: 用户主键。
- `business_id`: 对外业务 ID，32 位十六进制字符串；API、JWT、管理端与客户端统一使用这个字段，不直接暴露内部整型主键。
- `username`: 登录用户名；当前库中允许重复用户名历史数据，因此登录时更建议优先使用邮箱。
- `email`: 唯一邮箱，可为空。
- `email_verified`: 邮箱是否已验证。
- `role`: 角色，常见值为 `user`、`admin`、`superadmin`。
- `status`: 账号状态，常见值为 `active`、`disabled`。
- `is_whitelisted`: 是否白名单用户。
- `credits`: 当前积分余额。
- `created_at` / `updated_at`: 用户创建时间、最后更新时间。

### `tasks`

- `id`: 任务内部主键，仅用于数据库内部关联与排障。
- `business_id`: 任务对外业务 ID，32 位十六进制字符串；任务创建响应、轮询接口、历史展示和日志追踪统一使用该字段。
- `user_id`: 发起任务的用户。
- `model`: 生成所用模型或场景模型标识。
- `mode`: 任务模式，当前主要为 `generate` 或 `inpaint`。
- `prompt`: 任务提示词。
- `num_images`: 任务声明的图片数量；当前实际生成链路里通常按单图子任务落库。
- `size`: 宽高比，例如 `1:1`、`3:4`。
- `resolution`: 分辨率档位，例如 `2K`、`4K`。
- `custom_size`: 自定义尺寸文本。
- `reference_images`: 参考图列表，JSON 字符串形式存储。
- `source_image`: 图编辑原图地址。
- `mask_image`: 图编辑蒙版地址。
- `credit_cost`: 单任务积分消耗。
- `status`: 任务状态，常见值为 `pending`、`queued`、`processing`、`success`、`failed`。
- `error_message`: 失败原因或最近一次错误信息。
- `created_at`: 任务记录写入数据库时间。
- `enqueued_at`: 任务成功进入分发/入队流程时间。
- `updated_at`: 任务最后一次状态更新时间；成功或失败后会更新。

### `images`

- `id`: 图片主键。
- `task_id`: 所属任务。
- `image_url`: 最终图片地址。
- `preview_url`: 预览图地址；在最终结果落存储前可能暂时有值。
- `image_format`: 图片格式，例如 `png`、`jpeg`。
- `image_size_bytes`: 图片大小，单位字节。
- `status`: 图片状态，常见值为 `pending`、`success`、`failed`。
- `error_message`: 单张图片失败原因。
- `is_deleted`: 是否逻辑删除。
- `deleted_at`: 逻辑删除时间。
- `created_at`: 图片记录创建时间。

### `credit_logs`

- `id`: 积分流水主键。
- `user_id`: 积分归属用户。
- `amount`: 积分变化量；负数通常表示消耗，正数通常表示返还或发放。
- `type`: 流水类型，当前常见为 `consume`、`allocate`。
- `description`: 流水说明。
- `operator_id`: 操作人；管理员手工加减积分时会用到。
- `task_id`: 关联任务；任务消费和返还时很关键。
- `created_at`: 流水创建时间。

### `prompt_history`

- `user_id`: 提示词归属用户。
- `prompt`: 历史提示词。
- `mode`: 对应任务模式。
- `source_image`: 图编辑场景关联原图。
- `created_at`: 记录时间。

### `templates`

- `prompt`: 模板提示词。
- `model`: 模板默认模型。
- `reference_images`: 模板参考图列表，文本形式存储。
- `size` / `resolution` / `custom_size`: 模板默认尺寸参数。
- `num_images`: 模板默认生成数量。
- `result_image`: 模板结果图。
- `sort_order`: 模板排序。

### `api_keys`

- `key`: 站点通用配置项中的主 Key。
- `tongyi_key`: 通义相关密钥。
- `cos_secret_id` / `cos_secret_key`: 腾讯云 COS 凭证。
- `cos_bucket` / `cos_region` / `cos_public_base_url`: COS 存储配置。
- `announcement_enabled` / `announcement_content` / `announcement_updated_at`: 公告配置。
- `updated_at`: 配置最后更新时间。

### `external_api_configs`

- `name`: 配置名称，唯一。
- `group_name`: 配置分组。
- `model_key`: 模型标识。
- `model_label` / `model_description`: 前台展示文案。
- `request_url`: 实际调用地址。
- `headers_json`: 请求头模板。
- `payload_json`: 请求体模板。
- `response_json`: 响应示例或结构模板。
- `result_base64_field`: 响应中图片 base64 的提取路径。
- `supports_generation` / `supports_inpaint` / `supports_prompt_reverse`: 功能支持矩阵。
- `is_active_generation` / `is_active_inpaint` / `is_active_prompt_reverse`: 是否启用。
- `status`: 配置状态，常见为 `enabled`。

### `external_api_scene_bindings`

- `scene_key`: 场景唯一键，例如不同生图、编辑或反推场景。
- `scene_type`: 场景类型。
- `scene_label` / `scene_description`: 场景文案。
- `api_config_id`: 绑定的接口配置。
- `display_name` / `subtitle`: 前端展示名称与副标题。
- `credit_cost`: 该场景的积分成本。
- `hide_aspect_ratio` / `hide_resolution` / `hide_custom_size`: 前端是否隐藏相关参数。
- `aspect_ratio_options_json` / `image_size_options_json` / `custom_size_options_json`: 可选参数列表。
- `status`: 场景状态，常见为 `enabled`。

### `regenerate_logs`

- `image_id`: 被重绘的原图片 ID。
- `old_image_url`: 重绘前图片地址。
- `new_image_url`: 重绘后图片地址。
- `created_at`: 重绘记录时间。

## 任务耗时计算口径

以下口径与当前后端日志和字段语义保持一致。

### 推荐口径

- 排队耗时：`enqueued_at - created_at`
- 总耗时：`updated_at - created_at`
- 实际处理耗时：`updated_at - enqueued_at`

### 说明

- `created_at` 记录任务写入数据库的时间。
- `enqueued_at` 记录任务成功进入分发/入队流程的时间。
- `updated_at` 记录任务最近一次状态变化的时间；任务最终完成或失败后可视为结束时间。
- 若 `enqueued_at` 为空，通常表示任务尚未成功分发，或该记录产生于旧版本逻辑。
- `实际处理耗时` 目前是基于数据库时间字段估算；若要做到最精确分析，建议后续再增加 `started_at` / `finished_at` 字段。

### 常用 SQL 示例

```sql
-- 查看最近任务的排队耗时、处理耗时、总耗时（毫秒）
SELECT
  id,
  user_id,
  status,
  created_at,
  enqueued_at,
  updated_at,
  CASE
    WHEN enqueued_at IS NOT NULL THEN TIMESTAMPDIFF(MICROSECOND, created_at, enqueued_at) / 1000
    ELSE NULL
  END AS queue_duration_ms,
  CASE
    WHEN enqueued_at IS NOT NULL THEN TIMESTAMPDIFF(MICROSECOND, enqueued_at, updated_at) / 1000
    ELSE NULL
  END AS processing_duration_ms,
  TIMESTAMPDIFF(MICROSECOND, created_at, updated_at) / 1000 AS total_duration_ms
FROM tasks
ORDER BY id DESC
LIMIT 50;

-- 查看失败任务及其耗时
SELECT
  id,
  user_id,
  model,
  mode,
  status,
  error_message,
  TIMESTAMPDIFF(MICROSECOND, created_at, updated_at) / 1000 AS total_duration_ms
FROM tasks
WHERE status = 'failed'
ORDER BY id DESC
LIMIT 50;

-- 按用户统计平均排队耗时与总耗时
SELECT
  user_id,
  COUNT(*) AS task_count,
  AVG(
    CASE
      WHEN enqueued_at IS NOT NULL THEN TIMESTAMPDIFF(MICROSECOND, created_at, enqueued_at) / 1000
      ELSE NULL
    END
  ) AS avg_queue_duration_ms,
  AVG(TIMESTAMPDIFF(MICROSECOND, created_at, updated_at) / 1000) AS avg_total_duration_ms
FROM tasks
GROUP BY user_id
ORDER BY task_count DESC;
```

## 默认账号

| 用户名 | 初始密码 | 角色 |
|--------|----------|------|
| `administrator` | `administrator123` | `superadmin`（超级管理员） |
| `admin` | `admin123` | `admin`（管理员） |

## SQL

```sql
SET NAMES utf8mb4;

CREATE TABLE api_keys (
  id INT NOT NULL AUTO_INCREMENT,
  `key` VARCHAR(255) NOT NULL,
  tongyi_key VARCHAR(255) NOT NULL,
  contact_qr_image VARCHAR(500) NOT NULL,
  cos_secret_id VARCHAR(255) NOT NULL,
  cos_secret_key VARCHAR(255) NOT NULL,
  cos_bucket VARCHAR(255) NOT NULL,
  cos_region VARCHAR(100) NOT NULL,
  cos_public_base_url VARCHAR(500) NOT NULL,
  announcement_enabled INT NOT NULL,
  announcement_content VARCHAR(5000) NOT NULL,
  announcement_updated_at DATETIME NULL,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE external_api_configs (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  description VARCHAR(255) NOT NULL,
  group_name VARCHAR(100) NOT NULL,
  model_key VARCHAR(50) NOT NULL,
  model_label VARCHAR(100) NOT NULL,
  model_description VARCHAR(255) NOT NULL,
  sort_order INT NOT NULL,
  hide_resolution TINYINT(1) NOT NULL,
  request_url VARCHAR(500) NOT NULL,
  headers_json TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  response_json TEXT NOT NULL,
  result_base64_field VARCHAR(255) NOT NULL,
  supports_generation TINYINT(1) NOT NULL,
  supports_inpaint TINYINT(1) NOT NULL,
  supports_prompt_reverse TINYINT(1) NOT NULL,
  is_active_generation TINYINT(1) NOT NULL,
  is_active_inpaint TINYINT(1) NOT NULL,
  is_active_prompt_reverse TINYINT(1) NOT NULL,
  status VARCHAR(20) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_external_api_configs_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE template_tags (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(50) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE templates (
  id INT NOT NULL AUTO_INCREMENT,
  prompt TEXT NOT NULL,
  model VARCHAR(50) DEFAULT NULL,
  reference_images TEXT,
  size VARCHAR(20) DEFAULT NULL,
  resolution VARCHAR(10) DEFAULT NULL,
  custom_size VARCHAR(50) DEFAULT NULL,
  num_images INT DEFAULT NULL,
  result_image VARCHAR(255) DEFAULT NULL,
  sort_order INT DEFAULT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE users (
  id INT NOT NULL AUTO_INCREMENT,
  business_id VARCHAR(32) NOT NULL,
  username VARCHAR(50) NOT NULL,
  email VARCHAR(255) DEFAULT NULL,
  email_verified TINYINT(1) NOT NULL DEFAULT 0,
  password_hash VARCHAR(255) NOT NULL,
  avatar_url VARCHAR(500) DEFAULT NULL,
  `role` VARCHAR(20) DEFAULT NULL,
  status VARCHAR(10) DEFAULT NULL,
  is_whitelisted TINYINT(1) NOT NULL DEFAULT 0,
  credits INT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_users_business_id (business_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE external_api_scene_bindings (
  id INT NOT NULL AUTO_INCREMENT,
  scene_key VARCHAR(50) NOT NULL,
  scene_type VARCHAR(30) NOT NULL DEFAULT 'generate',
  scene_label VARCHAR(100) NOT NULL DEFAULT '',
  scene_description VARCHAR(255) NOT NULL DEFAULT '',
  sort_order INT NOT NULL DEFAULT 0,
  hide_aspect_ratio TINYINT(1) NOT NULL DEFAULT 0,
  hide_resolution TINYINT(1) NOT NULL DEFAULT 0,
  hide_custom_size TINYINT(1) NOT NULL DEFAULT 1,
  status VARCHAR(20) NOT NULL DEFAULT 'enabled',
  api_config_id INT DEFAULT NULL,
  display_name VARCHAR(100) NOT NULL DEFAULT '',
  subtitle VARCHAR(255) NOT NULL DEFAULT '',
  credit_cost INT NOT NULL DEFAULT 0,
  aspect_ratio_options_json TEXT NOT NULL,
  image_size_options_json TEXT NOT NULL,
  custom_size_options_json TEXT NOT NULL,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_external_api_scene_bindings_scene_key (scene_key),
  CONSTRAINT fk_scene_api_config FOREIGN KEY (api_config_id) REFERENCES external_api_configs (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE prompt_history (
  id INT NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  prompt VARCHAR(2000) NOT NULL,
  mode VARCHAR(20) NOT NULL DEFAULT 'generate',
  source_image VARCHAR(500) NOT NULL DEFAULT '',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_prompt_history_user_id (user_id),
  CONSTRAINT fk_prompt_history_user FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tasks (
  id INT NOT NULL AUTO_INCREMENT,
  business_id VARCHAR(32) NOT NULL,
  user_id INT NOT NULL,
  model VARCHAR(50) DEFAULT NULL,
  mode VARCHAR(20) DEFAULT NULL,
  prompt TEXT,
  num_images INT DEFAULT NULL,
  size VARCHAR(20) DEFAULT NULL,
  resolution VARCHAR(10) DEFAULT NULL,
  custom_size VARCHAR(50) DEFAULT NULL,
  reference_image VARCHAR(500) DEFAULT NULL,
  reference_images TEXT,
  source_image VARCHAR(500) DEFAULT NULL,
  mask_image VARCHAR(500) DEFAULT NULL,
  credit_cost INT NOT NULL DEFAULT 0,
  status VARCHAR(20) DEFAULT NULL,
  error_message TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  enqueued_at DATETIME DEFAULT NULL,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_tasks_business_id (business_id),
  CONSTRAINT fk_tasks_user FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE template_tag_relations (
  template_id INT NOT NULL,
  tag_id INT NOT NULL,
  PRIMARY KEY (template_id, tag_id),
  CONSTRAINT fk_ttr_template FOREIGN KEY (template_id) REFERENCES templates (id),
  CONSTRAINT fk_ttr_tag FOREIGN KEY (tag_id) REFERENCES template_tags (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE credit_logs (
  id INT NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  amount INT NOT NULL,
  type VARCHAR(20) NOT NULL,
  description VARCHAR(500) DEFAULT NULL,
  operator_id INT DEFAULT NULL,
  task_id INT DEFAULT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_credit_logs_user_id (user_id),
  CONSTRAINT fk_credit_logs_user FOREIGN KEY (user_id) REFERENCES users (id),
  CONSTRAINT fk_credit_logs_operator FOREIGN KEY (operator_id) REFERENCES users (id),
  CONSTRAINT fk_credit_logs_task FOREIGN KEY (task_id) REFERENCES tasks (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE images (
  id INT NOT NULL AUTO_INCREMENT,
  task_id INT NOT NULL,
  image_url VARCHAR(255) DEFAULT NULL,
  preview_url VARCHAR(500) DEFAULT NULL,
  image_format VARCHAR(20) DEFAULT NULL,
  image_size_bytes INT DEFAULT NULL,
  status VARCHAR(20) DEFAULT NULL,
  error_message VARCHAR(2000) DEFAULT NULL,
  is_deleted TINYINT(1) NOT NULL DEFAULT 0,
  deleted_at DATETIME DEFAULT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_images_task FOREIGN KEY (task_id) REFERENCES tasks (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE regenerate_logs (
  id INT NOT NULL AUTO_INCREMENT,
  image_id INT NOT NULL,
  old_image_url VARCHAR(255) DEFAULT NULL,
  new_image_url VARCHAR(255) DEFAULT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_regenerate_logs_image FOREIGN KEY (image_id) REFERENCES images (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE INDEX ix_users_username ON users (username);
CREATE UNIQUE INDEX ix_template_tags_name ON template_tags (name);

INSERT INTO users (
  business_id, username, email, email_verified, password_hash, avatar_url,
  `role`, status, is_whitelisted, credits, created_at, updated_at
) VALUES
('11111111111111111111111111111111', 'administrator', NULL, 0, '$2b$12$CR1qnIGjLbi46hgFXXrxQOoPge5g0aWWuLga1fWGDC5GOBiIFY0vK', '', 'superadmin', 'active', 0, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('22222222222222222222222222222222', 'admin', NULL, 0, '$2b$12$gGceM8aYPCpT9Kz0GJQvje0cvIS5y6HEFrXTGyeu4AzNbD7ANX..C', '', 'admin', 'active', 0, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
```
