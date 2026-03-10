from tortoise import fields

from .base import BaseModel, TimestampMixin


class CandidateProfile(BaseModel, TimestampMixin):
    user_id = fields.IntField(unique=True, description="关联用户ID", index=True)
    avatar = fields.CharField(max_length=255, null=True, description="头像地址")
    headline = fields.CharField(max_length=120, null=True, description="职业标题")
    resume_text = fields.TextField(null=True, description="简历正文")
    skill_tags = fields.JSONField(default=list, description="技能标签")
    work_years = fields.IntField(default=0, description="工作年限", index=True)
    education = fields.CharField(max_length=120, null=True, description="教育信息")
    target_position = fields.CharField(max_length=120, null=True, description="目标岗位", index=True)
    target_city = fields.CharField(max_length=60, null=True, description="目标城市", index=True)
    job_status = fields.CharField(max_length=30, default="open", description="求职状态", index=True)
    strengths = fields.TextField(null=True, description="个人优势")
    is_active = fields.BooleanField(default=True, description="是否启用", index=True)

    class Meta:
        table = "candidate_profile"


class InterviewPosition(BaseModel, TimestampMixin):
    title = fields.CharField(max_length=120, description="岗位名称", index=True)
    category = fields.CharField(max_length=60, null=True, description="岗位类别", index=True)
    level = fields.CharField(max_length=60, null=True, description="岗位职级", index=True)
    department = fields.CharField(max_length=60, null=True, description="所属部门", index=True)
    tags = fields.JSONField(default=list, description="岗位标签")
    difficulty = fields.CharField(max_length=20, default="middle", description="面试难度", index=True)
    cover_image = fields.CharField(max_length=255, null=True, description="岗位封面")
    summary = fields.TextField(null=True, description="岗位简介")
    highlight = fields.JSONField(default=list, description="亮点卖点")
    is_recommended = fields.BooleanField(default=True, description="是否推荐", index=True)
    status = fields.CharField(max_length=20, default="online", description="岗位状态", index=True)

    class Meta:
        table = "interview_position"


class PositionJD(BaseModel, TimestampMixin):
    position_id = fields.IntField(description="岗位ID", index=True)
    version = fields.IntField(default=1, description="JD版本", index=True)
    jd_text = fields.TextField(description="JD正文")
    must_have_tags = fields.JSONField(default=list, description="必备技能标签")
    bonus_tags = fields.JSONField(default=list, description="加分项标签")
    scoring_dimensions = fields.JSONField(default=list, description="评分维度配置")
    prompt_hint = fields.TextField(null=True, description="Prompt提示词")
    is_active = fields.BooleanField(default=True, description="是否启用", index=True)

    class Meta:
        table = "position_jd"


class InterviewSession(BaseModel, TimestampMixin):
    session_no = fields.CharField(max_length=40, unique=True, description="场次编号", index=True)
    candidate_id = fields.IntField(description="候选人档案ID", index=True)
    user_id = fields.IntField(description="关联用户ID", index=True)
    position_id = fields.IntField(description="岗位ID", index=True)
    jd_id = fields.IntField(null=True, description="JD ID", index=True)
    status = fields.CharField(max_length=20, default="pending", description="状态", index=True)
    current_round = fields.IntField(default=0, description="当前轮次")
    total_rounds = fields.IntField(default=5, description="总轮次")
    started_at = fields.DatetimeField(null=True, description="开始时间", index=True)
    ended_at = fields.DatetimeField(null=True, description="结束时间", index=True)
    question_plan = fields.JSONField(default=list, description="题目计划")
    context_summary = fields.TextField(null=True, description="上下文摘要")
    ai_persona = fields.JSONField(default=dict, description="AI面试官人格")
    latest_metrics = fields.JSONField(default=dict, description="实时指标")

    class Meta:
        table = "interview_session"


class InterviewTurn(BaseModel, TimestampMixin):
    session_id = fields.IntField(description="场次ID", index=True)
    round_no = fields.IntField(default=1, description="轮次", index=True)
    speaker = fields.CharField(max_length=20, description="说话方", index=True)
    content = fields.TextField(description="文本内容")
    source = fields.CharField(max_length=30, default="segment", description="内容来源", index=True)
    segment_index = fields.IntField(default=0, description="分段序号", index=True)

    class Meta:
        table = "interview_turn"


class InterviewReport(BaseModel, TimestampMixin):
    session_id = fields.IntField(unique=True, description="场次ID", index=True)
    candidate_id = fields.IntField(description="候选人档案ID", index=True)
    position_id = fields.IntField(description="岗位ID", index=True)
    total_score = fields.IntField(default=0, description="总分", index=True)
    dimension_scores = fields.JSONField(default=dict, description="维度分数字典")
    overview = fields.TextField(null=True, description="综合评价")
    highlights = fields.JSONField(default=list, description="亮点")
    risks = fields.JSONField(default=list, description="风险点")
    suggestions = fields.JSONField(default=list, description="改进建议")
    recommended_positions = fields.JSONField(default=list, description="推荐岗位")
    archive_status = fields.CharField(max_length=20, default="archived", description="归档状态", index=True)
    pdf_url = fields.CharField(max_length=255, null=True, description="PDF链接")
    report_payload = fields.JSONField(default=dict, description="完整报告内容")

    class Meta:
        table = "interview_report"
