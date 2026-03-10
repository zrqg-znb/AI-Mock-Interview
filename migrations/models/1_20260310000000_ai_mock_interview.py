from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `candidate_profile` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `user_id` INT NOT NULL UNIQUE COMMENT '关联用户ID',
    `avatar` VARCHAR(255) COMMENT '头像地址',
    `headline` VARCHAR(120) COMMENT '职业标题',
    `resume_text` LONGTEXT COMMENT '简历正文',
    `skill_tags` JSON COMMENT '技能标签',
    `work_years` INT NOT NULL DEFAULT 0 COMMENT '工作年限',
    `education` VARCHAR(120) COMMENT '教育信息',
    `target_position` VARCHAR(120) COMMENT '目标岗位',
    `target_city` VARCHAR(60) COMMENT '目标城市',
    `job_status` VARCHAR(30) NOT NULL DEFAULT 'open' COMMENT '求职状态',
    `strengths` LONGTEXT COMMENT '个人优势',
    `is_active` BOOL NOT NULL DEFAULT 1 COMMENT '是否启用',
    KEY `idx_candidate_profile_created_at` (`created_at`),
    KEY `idx_candidate_profile_updated_at` (`updated_at`),
    KEY `idx_candidate_profile_user_id` (`user_id`),
    KEY `idx_candidate_profile_work_years` (`work_years`),
    KEY `idx_candidate_profile_target_position` (`target_position`),
    KEY `idx_candidate_profile_target_city` (`target_city`),
    KEY `idx_candidate_profile_job_status` (`job_status`),
    KEY `idx_candidate_profile_is_active` (`is_active`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `interview_position` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `title` VARCHAR(120) NOT NULL COMMENT '岗位名称',
    `category` VARCHAR(60) COMMENT '岗位类别',
    `level` VARCHAR(60) COMMENT '岗位职级',
    `department` VARCHAR(60) COMMENT '所属部门',
    `tags` JSON COMMENT '岗位标签',
    `difficulty` VARCHAR(20) NOT NULL DEFAULT 'middle' COMMENT '面试难度',
    `cover_image` VARCHAR(255) COMMENT '岗位封面',
    `summary` LONGTEXT COMMENT '岗位简介',
    `highlight` JSON COMMENT '亮点卖点',
    `is_recommended` BOOL NOT NULL DEFAULT 1 COMMENT '是否推荐',
    `status` VARCHAR(20) NOT NULL DEFAULT 'online' COMMENT '岗位状态',
    KEY `idx_interview_position_created_at` (`created_at`),
    KEY `idx_interview_position_updated_at` (`updated_at`),
    KEY `idx_interview_position_title` (`title`),
    KEY `idx_interview_position_category` (`category`),
    KEY `idx_interview_position_level` (`level`),
    KEY `idx_interview_position_department` (`department`),
    KEY `idx_interview_position_difficulty` (`difficulty`),
    KEY `idx_interview_position_is_recommended` (`is_recommended`),
    KEY `idx_interview_position_status` (`status`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `position_jd` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `position_id` INT NOT NULL COMMENT '岗位ID',
    `version` INT NOT NULL DEFAULT 1 COMMENT 'JD版本',
    `jd_text` LONGTEXT NOT NULL COMMENT 'JD正文',
    `must_have_tags` JSON COMMENT '必备技能标签',
    `bonus_tags` JSON COMMENT '加分项标签',
    `scoring_dimensions` JSON COMMENT '评分维度配置',
    `prompt_hint` LONGTEXT COMMENT 'Prompt提示词',
    `is_active` BOOL NOT NULL DEFAULT 1 COMMENT '是否启用',
    KEY `idx_position_jd_created_at` (`created_at`),
    KEY `idx_position_jd_updated_at` (`updated_at`),
    KEY `idx_position_jd_position_id` (`position_id`),
    KEY `idx_position_jd_version` (`version`),
    KEY `idx_position_jd_is_active` (`is_active`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `interview_session` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `session_no` VARCHAR(40) NOT NULL UNIQUE COMMENT '场次编号',
    `candidate_id` INT NOT NULL COMMENT '候选人档案ID',
    `user_id` INT NOT NULL COMMENT '关联用户ID',
    `position_id` INT NOT NULL COMMENT '岗位ID',
    `jd_id` INT COMMENT 'JD ID',
    `status` VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '状态',
    `current_round` INT NOT NULL DEFAULT 0 COMMENT '当前轮次',
    `total_rounds` INT NOT NULL DEFAULT 5 COMMENT '总轮次',
    `started_at` DATETIME(6) COMMENT '开始时间',
    `ended_at` DATETIME(6) COMMENT '结束时间',
    `question_plan` JSON COMMENT '题目计划',
    `context_summary` LONGTEXT COMMENT '上下文摘要',
    `ai_persona` JSON COMMENT 'AI面试官人格',
    `latest_metrics` JSON COMMENT '实时指标',
    KEY `idx_interview_session_created_at` (`created_at`),
    KEY `idx_interview_session_updated_at` (`updated_at`),
    KEY `idx_interview_session_session_no` (`session_no`),
    KEY `idx_interview_session_candidate_id` (`candidate_id`),
    KEY `idx_interview_session_user_id` (`user_id`),
    KEY `idx_interview_session_position_id` (`position_id`),
    KEY `idx_interview_session_jd_id` (`jd_id`),
    KEY `idx_interview_session_status` (`status`),
    KEY `idx_interview_session_started_at` (`started_at`),
    KEY `idx_interview_session_ended_at` (`ended_at`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `interview_turn` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `session_id` INT NOT NULL COMMENT '场次ID',
    `round_no` INT NOT NULL DEFAULT 1 COMMENT '轮次',
    `speaker` VARCHAR(20) NOT NULL COMMENT '说话方',
    `content` LONGTEXT NOT NULL COMMENT '文本内容',
    `source` VARCHAR(30) NOT NULL DEFAULT 'segment' COMMENT '内容来源',
    `segment_index` INT NOT NULL DEFAULT 0 COMMENT '分段序号',
    KEY `idx_interview_turn_created_at` (`created_at`),
    KEY `idx_interview_turn_updated_at` (`updated_at`),
    KEY `idx_interview_turn_session_id` (`session_id`),
    KEY `idx_interview_turn_round_no` (`round_no`),
    KEY `idx_interview_turn_speaker` (`speaker`),
    KEY `idx_interview_turn_source` (`source`),
    KEY `idx_interview_turn_segment_index` (`segment_index`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `interview_report` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `session_id` INT NOT NULL UNIQUE COMMENT '场次ID',
    `candidate_id` INT NOT NULL COMMENT '候选人档案ID',
    `position_id` INT NOT NULL COMMENT '岗位ID',
    `total_score` INT NOT NULL DEFAULT 0 COMMENT '总分',
    `dimension_scores` JSON COMMENT '维度分数字典',
    `overview` LONGTEXT COMMENT '综合评价',
    `highlights` JSON COMMENT '亮点',
    `risks` JSON COMMENT '风险点',
    `suggestions` JSON COMMENT '改进建议',
    `recommended_positions` JSON COMMENT '推荐岗位',
    `archive_status` VARCHAR(20) NOT NULL DEFAULT 'archived' COMMENT '归档状态',
    `pdf_url` VARCHAR(255) COMMENT 'PDF链接',
    `report_payload` JSON COMMENT '完整报告内容',
    KEY `idx_interview_report_created_at` (`created_at`),
    KEY `idx_interview_report_updated_at` (`updated_at`),
    KEY `idx_interview_report_session_id` (`session_id`),
    KEY `idx_interview_report_candidate_id` (`candidate_id`),
    KEY `idx_interview_report_position_id` (`position_id`),
    KEY `idx_interview_report_total_score` (`total_score`),
    KEY `idx_interview_report_archive_status` (`archive_status`)
) CHARACTER SET utf8mb4;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `interview_report`;
        DROP TABLE IF EXISTS `interview_turn`;
        DROP TABLE IF EXISTS `interview_session`;
        DROP TABLE IF EXISTS `position_jd`;
        DROP TABLE IF EXISTS `interview_position`;
        DROP TABLE IF EXISTS `candidate_profile`;
    """
