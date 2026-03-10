from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `candidate_profile` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `user_id` INT NOT NULL UNIQUE COMMENT '关联用户ID',
    `avatar` VARCHAR(255)   COMMENT '头像地址',
    `headline` VARCHAR(120)   COMMENT '职业标题',
    `resume_text` LONGTEXT   COMMENT '简历正文',
    `skill_tags` JSON NOT NULL  COMMENT '技能标签',
    `work_years` INT NOT NULL  COMMENT '工作年限' DEFAULT 0,
    `education` VARCHAR(120)   COMMENT '教育信息',
    `target_position` VARCHAR(120)   COMMENT '目标岗位',
    `target_city` VARCHAR(60)   COMMENT '目标城市',
    `job_status` VARCHAR(30) NOT NULL  COMMENT '求职状态' DEFAULT 'open',
    `strengths` LONGTEXT   COMMENT '个人优势',
    `is_active` BOOL NOT NULL  COMMENT '是否启用' DEFAULT 1,
    KEY `idx_candidate_p_created_674bdb` (`created_at`),
    KEY `idx_candidate_p_updated_ef2dd3` (`updated_at`),
    KEY `idx_candidate_p_user_id_c8fe49` (`user_id`),
    KEY `idx_candidate_p_work_ye_85072d` (`work_years`),
    KEY `idx_candidate_p_target__0956a2` (`target_position`),
    KEY `idx_candidate_p_target__33fb6b` (`target_city`),
    KEY `idx_candidate_p_job_sta_ccf45a` (`job_status`),
    KEY `idx_candidate_p_is_acti_f36346` (`is_active`)
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `interview_position` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `title` VARCHAR(120) NOT NULL  COMMENT '岗位名称',
    `category` VARCHAR(60)   COMMENT '岗位类别',
    `level` VARCHAR(60)   COMMENT '岗位职级',
    `department` VARCHAR(60)   COMMENT '所属部门',
    `tags` JSON NOT NULL  COMMENT '岗位标签',
    `difficulty` VARCHAR(20) NOT NULL  COMMENT '面试难度' DEFAULT 'middle',
    `cover_image` VARCHAR(255)   COMMENT '岗位封面',
    `summary` LONGTEXT   COMMENT '岗位简介',
    `highlight` JSON NOT NULL  COMMENT '亮点卖点',
    `is_recommended` BOOL NOT NULL  COMMENT '是否推荐' DEFAULT 1,
    `status` VARCHAR(20) NOT NULL  COMMENT '岗位状态' DEFAULT 'online',
    KEY `idx_interview_p_created_fcec8e` (`created_at`),
    KEY `idx_interview_p_updated_8569e4` (`updated_at`),
    KEY `idx_interview_p_title_89963f` (`title`),
    KEY `idx_interview_p_categor_db5975` (`category`),
    KEY `idx_interview_p_level_dfdcbd` (`level`),
    KEY `idx_interview_p_departm_bc5fdc` (`department`),
    KEY `idx_interview_p_difficu_863d93` (`difficulty`),
    KEY `idx_interview_p_is_reco_371170` (`is_recommended`),
    KEY `idx_interview_p_status_e79b9f` (`status`)
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `interview_report` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `session_id` INT NOT NULL UNIQUE COMMENT '场次ID',
    `candidate_id` INT NOT NULL  COMMENT '候选人档案ID',
    `position_id` INT NOT NULL  COMMENT '岗位ID',
    `total_score` INT NOT NULL  COMMENT '总分' DEFAULT 0,
    `dimension_scores` JSON NOT NULL  COMMENT '维度分数字典',
    `overview` LONGTEXT   COMMENT '综合评价',
    `highlights` JSON NOT NULL  COMMENT '亮点',
    `risks` JSON NOT NULL  COMMENT '风险点',
    `suggestions` JSON NOT NULL  COMMENT '改进建议',
    `recommended_positions` JSON NOT NULL  COMMENT '推荐岗位',
    `archive_status` VARCHAR(20) NOT NULL  COMMENT '归档状态' DEFAULT 'archived',
    `pdf_url` VARCHAR(255)   COMMENT 'PDF链接',
    `report_payload` JSON NOT NULL  COMMENT '完整报告内容',
    KEY `idx_interview_r_created_93e389` (`created_at`),
    KEY `idx_interview_r_updated_a33e48` (`updated_at`),
    KEY `idx_interview_r_session_f93c08` (`session_id`),
    KEY `idx_interview_r_candida_475bd0` (`candidate_id`),
    KEY `idx_interview_r_positio_7a1f9a` (`position_id`),
    KEY `idx_interview_r_total_s_bcd587` (`total_score`),
    KEY `idx_interview_r_archive_edef4d` (`archive_status`)
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `interview_session` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `session_no` VARCHAR(40) NOT NULL UNIQUE COMMENT '场次编号',
    `candidate_id` INT NOT NULL  COMMENT '候选人档案ID',
    `user_id` INT NOT NULL  COMMENT '关联用户ID',
    `position_id` INT NOT NULL  COMMENT '岗位ID',
    `jd_id` INT   COMMENT 'JD ID',
    `status` VARCHAR(20) NOT NULL  COMMENT '状态' DEFAULT 'pending',
    `current_round` INT NOT NULL  COMMENT '当前轮次' DEFAULT 0,
    `total_rounds` INT NOT NULL  COMMENT '总轮次' DEFAULT 5,
    `started_at` DATETIME(6)   COMMENT '开始时间',
    `ended_at` DATETIME(6)   COMMENT '结束时间',
    `question_plan` JSON NOT NULL  COMMENT '题目计划',
    `context_summary` LONGTEXT   COMMENT '上下文摘要',
    `ai_persona` JSON NOT NULL  COMMENT 'AI面试官人格',
    `latest_metrics` JSON NOT NULL  COMMENT '实时指标',
    KEY `idx_interview_s_created_d00cfc` (`created_at`),
    KEY `idx_interview_s_updated_1a4a5d` (`updated_at`),
    KEY `idx_interview_s_session_21439e` (`session_no`),
    KEY `idx_interview_s_candida_a5077e` (`candidate_id`),
    KEY `idx_interview_s_user_id_19af1d` (`user_id`),
    KEY `idx_interview_s_positio_f7c805` (`position_id`),
    KEY `idx_interview_s_jd_id_35b4a1` (`jd_id`),
    KEY `idx_interview_s_status_8f8915` (`status`),
    KEY `idx_interview_s_started_a3c33a` (`started_at`),
    KEY `idx_interview_s_ended_a_9cb038` (`ended_at`)
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `interview_turn` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `session_id` INT NOT NULL  COMMENT '场次ID',
    `round_no` INT NOT NULL  COMMENT '轮次' DEFAULT 1,
    `speaker` VARCHAR(20) NOT NULL  COMMENT '说话方',
    `content` LONGTEXT NOT NULL  COMMENT '文本内容',
    `source` VARCHAR(30) NOT NULL  COMMENT '内容来源' DEFAULT 'segment',
    `segment_index` INT NOT NULL  COMMENT '分段序号' DEFAULT 0,
    KEY `idx_interview_t_created_8d8df8` (`created_at`),
    KEY `idx_interview_t_updated_5e2d63` (`updated_at`),
    KEY `idx_interview_t_session_681eb3` (`session_id`),
    KEY `idx_interview_t_round_n_6c7512` (`round_no`),
    KEY `idx_interview_t_speaker_ccaf1e` (`speaker`),
    KEY `idx_interview_t_source_e0c47e` (`source`),
    KEY `idx_interview_t_segment_59b634` (`segment_index`)
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `position_jd` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `position_id` INT NOT NULL  COMMENT '岗位ID',
    `version` INT NOT NULL  COMMENT 'JD版本' DEFAULT 1,
    `jd_text` LONGTEXT NOT NULL  COMMENT 'JD正文',
    `must_have_tags` JSON NOT NULL  COMMENT '必备技能标签',
    `bonus_tags` JSON NOT NULL  COMMENT '加分项标签',
    `scoring_dimensions` JSON NOT NULL  COMMENT '评分维度配置',
    `prompt_hint` LONGTEXT   COMMENT 'Prompt提示词',
    `is_active` BOOL NOT NULL  COMMENT '是否启用' DEFAULT 1,
    KEY `idx_position_jd_created_4e519f` (`created_at`),
    KEY `idx_position_jd_updated_77bb7b` (`updated_at`),
    KEY `idx_position_jd_positio_326eed` (`position_id`),
    KEY `idx_position_jd_version_9cf5a1` (`version`),
    KEY `idx_position_jd_is_acti_fee898` (`is_active`)
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `position_jd`;
        DROP TABLE IF EXISTS `candidate_profile`;
        DROP TABLE IF EXISTS `interview_report`;
        DROP TABLE IF EXISTS `interview_position`;
        DROP TABLE IF EXISTS `interview_session`;
        DROP TABLE IF EXISTS `interview_turn`;"""
