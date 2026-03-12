import json
import re
from datetime import datetime
from typing import Any

from fastapi import HTTPException
from tortoise.expressions import Q

from app.controllers.candidate import candidate_controller
from app.controllers.interview import interview_controller
from app.controllers.jd import jd_controller
from app.controllers.position import position_controller
from app.controllers.report import report_controller
from app.models.interview import InterviewPosition, PositionJD
from app.schemas.interviews import DEFAULT_SCORING_DIMENSIONS
from app.services.interview_ai import interview_ai_adapter


_WORD_PATTERN = re.compile(r"[A-Za-z0-9+#\.]{2,}|[\u4e00-\u9fff]{1,}")


class MockInterviewService:
    @staticmethod
    def _extract_terms(*parts: Any) -> set[str]:
        terms: set[str] = set()
        for part in parts:
            if not part:
                continue
            if isinstance(part, list):
                for item in part:
                    if item:
                        terms.add(str(item).strip().lower())
                continue
            text = str(part).lower()
            for token in _WORD_PATTERN.findall(text):
                token = token.strip()
                if len(token) >= 2:
                    terms.add(token)
        return terms

    def _candidate_terms(self, candidate: dict) -> set[str]:
        return self._extract_terms(
            candidate.get("skill_tags", []),
            candidate.get("target_position"),
            candidate.get("target_city"),
            candidate.get("resume_text"),
            candidate.get("strengths"),
            candidate.get("education"),
        )

    def _jd_terms(self, position: dict, jd: dict | None) -> tuple[set[str], list[str], list[str]]:
        must_have = jd.get("must_have_tags", []) if jd else []
        bonus = jd.get("bonus_tags", []) if jd else []
        base_terms = self._extract_terms(
            position.get("title"),
            position.get("category"),
            position.get("level"),
            position.get("department"),
            position.get("tags", []),
            position.get("summary"),
            must_have,
            bonus,
        )
        return base_terms, must_have, bonus

    @staticmethod
    def _json_dump(data: Any) -> str:
        try:
            return json.dumps(data, ensure_ascii=False)
        except TypeError:
            return str(data)

    @staticmethod
    def _safe_text(value: Any, default: str = "") -> str:
        if value is None:
            return default
        text = str(value).strip()
        return text or default

    @staticmethod
    def _normalize_string_list(value: Any, limit: int = 5) -> list[str]:
        if not value:
            return []
        if isinstance(value, str):
            raw_items = re.split(r"[，,、\n]", value)
        elif isinstance(value, list):
            raw_items = value
        else:
            return []
        items: list[str] = []
        seen: set[str] = set()
        for item in raw_items:
            text = str(item).strip()
            if not text or text in seen:
                continue
            seen.add(text)
            items.append(text)
            if len(items) >= limit:
                break
        return items

    def _normalize_evaluation_focus(self, value: Any, fallback: list[str]) -> list[str]:
        result = self._normalize_string_list(value, limit=6)
        return result or fallback

    def _normalize_question_plan(self, questions: Any, fallback_questions: list[dict], total_rounds: int) -> list[dict[str, Any]]:
        raw_questions = questions if isinstance(questions, list) else []
        normalized: list[dict[str, Any]] = []
        for index in range(total_rounds):
            fallback = fallback_questions[index] if index < len(fallback_questions) else {
                "index": index + 1,
                "stage": "experience",
                "focus": "岗位匹配",
                "question": "请结合经历继续展开说明。",
            }
            source = raw_questions[index] if index < len(raw_questions) and isinstance(raw_questions[index], dict) else {}
            item = {
                "index": index + 1,
                "stage": self._safe_text(source.get("stage"), fallback.get("stage", "experience")),
                "focus": self._safe_text(source.get("focus"), fallback.get("focus", "岗位匹配")),
                "question": self._safe_text(source.get("question"), fallback.get("question", "请结合经历继续展开说明。")),
            }
            expected_points = self._normalize_string_list(source.get("expected_points"), limit=4)
            if expected_points:
                item["expected_points"] = expected_points
            normalized.append(item)
        return normalized

    def _normalize_dimension_scores(
        self,
        value: Any,
        dimension_names: list[str],
        fallback: dict[str, int],
    ) -> dict[str, int]:
        if not isinstance(value, dict):
            return fallback
        normalized: dict[str, int] = {}
        has_named_keys = any(name in value for name in dimension_names)
        ordered_values = list(value.values())
        for index, name in enumerate(dimension_names):
            raw = value.get(name) if has_named_keys else ordered_values[index] if index < len(ordered_values) else fallback.get(name, 0)
            try:
                score = int(round(float(raw)))
            except (TypeError, ValueError):
                score = fallback.get(name, 0)
            normalized[name] = max(0, min(100, score))
        return normalized

    def build_recommendation_reason(self, candidate: dict, position: dict, matched_tags: list[str], missing_tags: list[str], score: int):
        headline = candidate.get("headline") or candidate.get("target_position") or "候选人"
        matched_text = "、".join(matched_tags[:3]) or "你的核心经历"
        missing_text = "、".join(missing_tags[:2]) or "可继续补充岗位案例"
        return (
            f"{headline} 与 {position.get('title')} 的匹配度为 {score} 分，"
            f"当前命中的核心点包括 {matched_text}。"
            f"建议在正式面试前补强 {missing_text}，可明显提高面试报告中的岗位匹配与表达完整度。"
        )

    def calculate_position_score(self, candidate: dict, position: dict, jd: dict | None):
        candidate_terms = self._candidate_terms(candidate)
        base_terms, must_have, bonus = self._jd_terms(position, jd)
        matched_base = sorted([term for term in position.get("tags", []) if str(term).lower() in candidate_terms])
        matched_must = sorted([term for term in must_have if str(term).lower() in candidate_terms])
        matched_bonus = sorted([term for term in bonus if str(term).lower() in candidate_terms])
        target_bonus = 10 if (candidate.get("target_position") or "") and (candidate.get("target_position") or "") in (position.get("title") or "") else 0
        tag_score = (len(matched_base) / max(len(position.get("tags", [])), 1)) * 30 if position.get("tags") else 12
        must_score = (len(matched_must) / max(len(must_have), 1)) * 45 if must_have else 18
        bonus_score = (len(matched_bonus) / max(len(bonus), 1)) * 10 if bonus else 6
        resume_score = min(10, len(candidate.get("resume_text") or "") // 80)
        exp_score = min(10, int(candidate.get("work_years") or 0) * 2)
        total_score = min(98, round(tag_score + must_score + bonus_score + resume_score + exp_score + target_bonus))
        heat_map = [
            {"label": "技能重合", "value": min(100, round(tag_score * 2.8))},
            {"label": "JD必备命中", "value": min(100, round(must_score * 2.2))},
            {"label": "经验成熟度", "value": min(100, round((resume_score + exp_score) * 5))},
        ]
        missing_tags = [term for term in must_have if term not in matched_must]
        return {
            "score": total_score,
            "matched_tags": matched_base + matched_must + matched_bonus,
            "missing_tags": missing_tags[:4],
            "heat_map": heat_map,
            "rule_terms": sorted(base_terms)[:12],
        }

    def build_fallback_question_plan(self, candidate: dict, position: dict, jd: dict | None, total_rounds: int):
        must_tags = jd.get("must_have_tags", []) if jd else []
        scoring_dimensions = jd.get("scoring_dimensions") if jd else []
        focus_tags = must_tags[: max(1, min(3, total_rounds))]
        questions = [
            {
                "index": 1,
                "stage": "opening",
                "focus": "自我介绍",
                "question": f"请先用 1 分钟做一个自我介绍，尽量围绕 {position.get('title')} 相关的经历展开。",
            },
            {
                "index": 2,
                "stage": "experience",
                "focus": focus_tags[0] if focus_tags else "核心项目",
                "question": f"结合你的简历，详细讲讲一段最能体现你胜任 {position.get('title')} 的项目经历。你做了什么，结果如何？",
            },
            {
                "index": 3,
                "stage": "scenario",
                "focus": focus_tags[1] if len(focus_tags) > 1 else "问题拆解",
                "question": f"如果你入职后需要在两周内推进一个围绕 {position.get('category') or position.get('title')} 的关键任务，你会怎么拆解目标、安排节奏并判断是否做对了？",
            },
            {
                "index": 4,
                "stage": "stress",
                "focus": focus_tags[2] if len(focus_tags) > 2 else "沟通与稳定度",
                "question": "当项目推进受阻、资源不足且时间紧时，你通常会如何沟通风险、争取资源，并保证事情继续往前走？",
            },
            {
                "index": 5,
                "stage": "closing",
                "focus": "岗位动机",
                "question": f"最后请你总结一下：为什么你适合 {position.get('title')}，以及入职后的前 90 天你最想交付什么结果？",
            },
        ]
        questions = questions[:total_rounds]
        return {
            "persona": {
                "name": "模拟面试官",
                "style": "提问清晰，关注经历细节",
                "tone": "专业、直接、尊重候选人",
            },
            "evaluation_focus": scoring_dimensions or DEFAULT_SCORING_DIMENSIONS,
            "questions": questions,
            "opening": f"你好，今天我们围绕 {position.get('title')} 做一场岗位练习。我会重点关注你的项目经历、岗位理解和表达结构。",
        }

    async def build_question_plan(self, candidate: dict, position: dict, jd: dict | None, total_rounds: int):
        fallback = self.build_fallback_question_plan(candidate, position, jd, total_rounds)
        if not interview_ai_adapter.enabled:
            return fallback
        system_prompt = (
            "你是一位资深招聘面试官，请根据岗位信息、JD 和候选人简历，生成一轮真实、克制、像人工面试官的中文模拟面试题计划。"
            "不要出现 AI、模型、算法、引擎 等表述，只返回 JSON 对象。"
        )
        user_prompt = (
            "请严格返回如下 JSON 结构："
            '{"persona":{"name":"...","style":"...","tone":"..."},'
            '"evaluation_focus":["..."],"opening":"...",'
            '"questions":[{"index":1,"stage":"opening","focus":"...","question":"...","expected_points":["..."]}]}'
            f"\n题目数量：{total_rounds}"
            f"\n岗位信息：{self._json_dump(position)}"
            f"\n候选人信息：{self._json_dump(candidate)}"
            f"\nJD 信息：{self._json_dump(jd or {})}"
            "\n要求：1. 题目要贴近真实招聘场景；2. 每题只问一个核心问题；3. 尽量结合候选人经历和岗位重点生成。"
        )
        result = await interview_ai_adapter.generate_json(
            system_prompt,
            user_prompt,
            temperature=0.55,
            scenario="question_plan",
            metadata={"position_id": position.get("id"), "total_rounds": total_rounds},
        )
        if not result or not isinstance(result, dict):
            return fallback
        persona_raw = result.get("persona") if isinstance(result.get("persona"), dict) else {}
        questions = self._normalize_question_plan(result.get("questions"), fallback["questions"], total_rounds)
        if not questions:
            return fallback
        return {
            "persona": {
                "name": self._safe_text(persona_raw.get("name"), fallback["persona"]["name"]),
                "style": self._safe_text(persona_raw.get("style"), fallback["persona"]["style"]),
                "tone": self._safe_text(persona_raw.get("tone"), fallback["persona"]["tone"]),
            },
            "evaluation_focus": self._normalize_evaluation_focus(result.get("evaluation_focus"), fallback["evaluation_focus"]),
            "opening": self._safe_text(result.get("opening"), fallback["opening"]),
            "questions": questions,
        }

    def build_live_metrics(self, jd: dict | None, user_turns: list[dict]):
        user_text = " ".join(turn.get("content", "") for turn in user_turns)
        user_terms = self._extract_terms(user_text)
        must_have = jd.get("must_have_tags", []) if jd else []
        matched = [item for item in must_have if str(item).lower() in user_terms or str(item) in user_text]
        total_len = len(user_text)
        answer_count = max(len(user_turns), 1)
        keyword_hit_rate = min(100, round(len(matched) / max(len(must_have), 1) * 100)) if must_have else min(95, 55 + total_len // 15)
        completeness = min(100, 35 + total_len // 12)
        expression_pace = min(100, 48 + answer_count * 9)
        communication_stability = min(100, 58 + total_len // 30)
        return {
            "keyword_hit_rate": keyword_hit_rate,
            "completeness": completeness,
            "expression_pace": expression_pace,
            "communication_stability": communication_stability,
            "matched_keywords": matched[:6],
            "answer_chars": total_len,
        }

    async def build_next_question(self, session: dict, position: dict, jd: dict | None, turns: list[dict]):
        plan = session.get("question_plan") or []
        next_index = session.get("current_round", 0) + 1
        total_rounds = session.get("total_rounds", 5)
        if next_index > total_rounds:
            return {"completed": True}
        if isinstance(plan, list) and len(plan) >= next_index:
            question_item = plan[next_index - 1]
        else:
            fallback_plan = self.build_fallback_question_plan({}, position, jd, total_rounds)
            question_item = fallback_plan["questions"][next_index - 1]
        fallback_result = {
            "completed": False,
            "round_no": next_index,
            "question": question_item.get("question"),
            "focus": question_item.get("focus"),
            "stage": question_item.get("stage"),
        }
        if not interview_ai_adapter.enabled:
            return fallback_result
        system_prompt = (
            "你是一位真实招聘场景中的面试官。请基于已给出的面试计划和已有对话，为下一轮生成一个自然、克制、聚焦的中文问题。"
            "不要出现 AI、模型、算法 等字样，只返回 JSON 对象。"
        )
        user_prompt = (
            '请返回 JSON：{"question":"...","focus":"...","stage":"..."}'
            f"\n当前轮次：{next_index}/{total_rounds}"
            f"\n岗位信息：{self._json_dump(position)}"
            f"\nJD 信息：{self._json_dump(jd or {})}"
            f"\n面试计划：{self._json_dump(plan)}"
            f"\n建议方向：{self._json_dump(question_item)}"
            f"\n最近对话：{self._json_dump(turns[-8:])}"
            "\n要求：1. 问题只保留一个核心问题；2. 尽量承接候选人刚才的回答；3. 题目长度控制在 80 字以内。"
        )
        ai_result = await interview_ai_adapter.generate_json(
            system_prompt,
            user_prompt,
            temperature=0.5,
            scenario="next_question",
            metadata={"position_id": position.get("id"), "round_no": next_index},
        )
        if not ai_result or not isinstance(ai_result, dict):
            return fallback_result
        return {
            "completed": False,
            "round_no": next_index,
            "question": self._safe_text(ai_result.get("question"), fallback_result["question"]),
            "focus": self._safe_text(ai_result.get("focus"), fallback_result["focus"]),
            "stage": self._safe_text(ai_result.get("stage"), fallback_result["stage"]),
        }

    async def build_report(self, session: dict, candidate: dict, position: dict, jd: dict | None, turns: list[dict]):
        user_turns = [turn for turn in turns if turn.get("speaker") == "user"]
        live_metrics = self.build_live_metrics(jd, user_turns)
        scoring_dimensions = jd.get("scoring_dimensions") if jd else []
        dimension_names = scoring_dimensions or DEFAULT_SCORING_DIMENSIONS
        values_seed = [
            live_metrics["keyword_hit_rate"],
            round((live_metrics["completeness"] + live_metrics["expression_pace"]) / 2),
            min(98, live_metrics["keyword_hit_rate"] + 8),
            live_metrics["communication_stability"],
        ]
        dimension_scores: dict[str, int] = {}
        for index, name in enumerate(dimension_names):
            dimension_scores[name] = values_seed[index % len(values_seed)]
        total_score = round(sum(dimension_scores.values()) / max(len(dimension_scores), 1))
        matched_keywords = live_metrics.get("matched_keywords", [])
        highlights = [
            f"在 {position.get('title')} 相关问题上能较快进入主题。",
            "回答节奏比较稳定，能够连续表达主要观点。",
            "项目叙述中体现出一定的结果意识。",
        ]
        if matched_keywords:
            highlights[0] = f"回答中提到了 {', '.join(matched_keywords[:3])} 等岗位关键词。"
        risks = [
            "部分回答还可以补充更具体的数据或结果。",
            "复杂情景题的拆解顺序可以再清晰一些。",
            "少数表述偏概括，建议补上关键动作和判断依据。",
        ]
        suggestions = [
            "下次练习优先用 STAR 结构整理 2 个核心项目案例。",
            f"围绕 {position.get('title')} 再准备 1 到 2 个可量化成果，回答会更有说服力。",
            "结尾可以主动总结业务结果和个人贡献，让回答更完整。",
        ]
        recommended_positions = [position.get("title")]
        if position.get("category") and position.get("category") != position.get("title"):
            recommended_positions.append(position.get("category"))
        overview = (
            f"这次 {position.get('title')} 练习总体得分 {total_score} 分。候选人在岗位关键词覆盖、表达完整度和沟通稳定性方面表现较稳。"
            "如果能补充更具体的数据结果，并在情景题里把判断过程讲清楚，整体表现还会更进一步。"
        )
        payload = {
            "total_score": total_score,
            "dimension_scores": dimension_scores,
            "overview": overview,
            "highlights": highlights,
            "risks": risks,
            "suggestions": suggestions,
            "recommended_positions": recommended_positions,
            "archive_status": "archived",
            "report_payload": {
                "live_metrics": live_metrics,
                "persona": session.get("ai_persona", {}),
                "question_plan": session.get("question_plan", []),
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ai_model": interview_ai_adapter.model_name if interview_ai_adapter.enabled else "",
                "ai_generated": False,
            },
        }
        if interview_ai_adapter.enabled:
            system_prompt = (
                "你是一位资深招聘面试官，请基于岗位信息、简历和面试对话，生成一份真实、克制、可落地的中文面试复盘。"
                "不要出现 AI、模型、算法 等表述，不要编造未出现的经历，只返回 JSON 对象。"
            )
            user_prompt = (
                '请严格返回 JSON：'
                '{"total_score":80,"dimension_scores":{"专业能力":80},"overview":"...",'
                '"highlights":["..."],"risks":["..."],"suggestions":["..."],"recommended_positions":["..."]}'
                f"\n评分维度请使用：{self._json_dump(dimension_names)}"
                f"\n场次信息：{self._json_dump(session)}"
                f"\n候选人信息：{self._json_dump(candidate)}"
                f"\n岗位信息：{self._json_dump(position)}"
                f"\nJD 信息：{self._json_dump(jd or {})}"
                f"\n面试对话：{self._json_dump(turns)}"
                f"\n实时指标：{self._json_dump(live_metrics)}"
                "\n要求：1. 结论要像真实面试复盘；2. 每个列表控制在 3 条以内；3. 建议要具体可执行。"
            )
            ai_result = await interview_ai_adapter.generate_json(
                system_prompt,
                user_prompt,
                temperature=0.35,
                scenario="report_generation",
                metadata={"session_id": session.get("id"), "position_id": position.get("id")},
            )
            if ai_result and isinstance(ai_result, dict):
                payload["dimension_scores"] = self._normalize_dimension_scores(
                    ai_result.get("dimension_scores"),
                    dimension_names,
                    payload["dimension_scores"],
                )
                ai_total = ai_result.get("total_score")
                if ai_total is None:
                    payload["total_score"] = round(
                        sum(payload["dimension_scores"].values()) / max(len(payload["dimension_scores"]), 1)
                    )
                else:
                    try:
                        payload["total_score"] = max(0, min(100, int(round(float(ai_total)))))
                    except (TypeError, ValueError):
                        payload["total_score"] = round(
                            sum(payload["dimension_scores"].values()) / max(len(payload["dimension_scores"]), 1)
                        )
                payload["overview"] = self._safe_text(ai_result.get("overview"), payload["overview"])
                payload["highlights"] = self._normalize_string_list(ai_result.get("highlights"), limit=3) or payload["highlights"]
                payload["risks"] = self._normalize_string_list(ai_result.get("risks"), limit=3) or payload["risks"]
                payload["suggestions"] = self._normalize_string_list(ai_result.get("suggestions"), limit=3) or payload["suggestions"]
                payload["recommended_positions"] = (
                    self._normalize_string_list(ai_result.get("recommended_positions"), limit=3)
                    or payload["recommended_positions"]
                )
                payload["report_payload"]["ai_generated"] = True
        return payload

    async def get_dashboard(self, user_id: int):
        candidate = await candidate_controller.get_by_user_id(user_id)
        if not candidate:
            return {
                "profile_ready": False,
                "readiness_score": 0,
                "interview_count": 0,
                "report_count": 0,
                "average_score": 0,
                "latest_report": None,
                "featured_positions": [],
            }
        candidate_data = await candidate_controller.serialize(candidate)
        report_total, report_objs = await report_controller.list(
            page=1,
            page_size=3,
            search=Q(candidate_id=candidate.id),
            order=["-created_at"],
        )
        latest_report = await report_controller.serialize(report_objs[0]) if report_objs else None
        all_reports = await report_controller.model.filter(candidate_id=candidate.id).all()
        average_score = round(sum(report.total_score for report in all_reports) / len(all_reports)) if all_reports else 0
        featured_positions = await self.list_recommendations(user_id=user_id, page_size=3)
        profile_fields = [
            candidate_data.get("resume_text"),
            candidate_data.get("target_position"),
            candidate_data.get("target_city"),
            candidate_data.get("skill_tags"),
            candidate_data.get("headline"),
        ]
        filled_count = sum(1 for item in profile_fields if item)
        readiness_score = min(98, filled_count * 18 + min(8, candidate_data.get("work_years", 0) * 2))
        return {
            "profile_ready": filled_count >= 3,
            "readiness_score": readiness_score,
            "interview_count": candidate_data.get("interview_count", 0),
            "report_count": report_total,
            "average_score": average_score,
            "latest_report": latest_report,
            "featured_positions": featured_positions,
        }

    async def list_recommendations(self, user_id: int, page_size: int = 12, keyword: str = ""):
        candidate = await candidate_controller.get_by_user_id(user_id)
        if not candidate:
            return []
        candidate_data = await candidate.to_dict()
        position_query = position_controller.model.filter(status="online", is_recommended=True)
        if keyword:
            position_query = position_query.filter(Q(title__contains=keyword) | Q(category__contains=keyword) | Q(department__contains=keyword))
        positions = await position_query.order_by("-updated_at").limit(page_size * 2).all()
        recommendations = []
        for position in positions:
            position_data = await position.to_dict()
            active_jd = await jd_controller.get_active_by_position(position.id)
            jd_data = await active_jd.to_dict() if active_jd else None
            match_result = self.calculate_position_score(candidate_data, position_data, jd_data)
            position_data.update(match_result)
            position_data["recommend_reason"] = self.build_recommendation_reason(
                candidate_data,
                position_data,
                match_result["matched_tags"],
                match_result["missing_tags"],
                match_result["score"],
            )
            if active_jd:
                position_data["active_jd"] = jd_data
            recommendations.append(position_data)
        recommendations.sort(key=lambda item: item.get("score", 0), reverse=True)
        return recommendations[:page_size]

    async def get_position_detail(self, user_id: int, position_id: int):
        recommendations = await self.list_recommendations(user_id=user_id, page_size=50)
        for item in recommendations:
            if item.get("id") == position_id:
                return item
        position = await position_controller.get(id=position_id)
        position_data = await position_controller.serialize(position)
        active_jd = await jd_controller.get_active_by_position(position_id)
        if active_jd:
            position_data["active_jd"] = await active_jd.to_dict()
        return position_data

    async def start_interview(self, user_id: int, position_id: int, total_rounds: int):
        candidate = await candidate_controller.get_by_user_id(user_id)
        if not candidate:
            raise HTTPException(status_code=400, detail="请先完善候选人简历档案")
        position = await position_controller.get(id=position_id)
        active_jd = await jd_controller.get_active_by_position(position_id)
        candidate_data = await candidate.to_dict()
        position_data = await position.to_dict()
        jd_data = await active_jd.to_dict() if active_jd else None
        plan = await self.build_question_plan(candidate_data, position_data, jd_data, total_rounds)
        session = await interview_controller.create_session(
            obj_in={
                "candidate_id": candidate.id,
                "position_id": position_id,
                "jd_id": active_jd.id if active_jd else None,
                "status": "running",
                "current_round": 1,
                "total_rounds": total_rounds,
                "question_plan": plan.get("questions", []),
                "context_summary": plan.get("opening"),
                "ai_persona": plan.get("persona", {}),
                "latest_metrics": {},
                "started_at": datetime.now(),
            }
        )
        opening = plan.get("opening") or "欢迎来到面试练习，我们先从第一题开始。"
        await interview_controller.add_turn(
            session_id=session.id,
            round_no=1,
            speaker="ai",
            content=opening,
            source="opening",
            segment_index=0,
        )
        first_question = (plan.get("questions") or [{}])[0]
        if first_question.get("question"):
            await interview_controller.add_turn(
                session_id=session.id,
                round_no=1,
                speaker="ai",
                content=first_question.get("question"),
                source="question",
                segment_index=0,
            )
        session_data = await interview_controller.serialize(session, include_turns=True)
        session_data["ai_persona"] = plan.get("persona", {})
        session_data["opening"] = opening
        session_data["current_question"] = first_question
        session_data["position_match"] = self.calculate_position_score(candidate_data, position_data, jd_data)
        return session_data

    async def submit_segment(self, user_id: int, session_id: int, content: str, segment_index: int):
        session = await interview_controller.get(id=session_id)
        if session.user_id != user_id:
            raise HTTPException(status_code=403, detail="无权提交该场次内容")
        if session.status != "running":
            raise HTTPException(status_code=400, detail="该场次未处于进行中状态")
        turn = await interview_controller.add_turn(
            session_id=session.id,
            round_no=max(session.current_round, 1),
            speaker="user",
            content=content,
            source="segment",
            segment_index=segment_index,
        )
        turns = await interview_controller.get_turns(session.id)
        jd = await jd_controller.get(id=session.jd_id) if session.jd_id else None
        jd_data = await jd.to_dict() if jd else None
        serialized_turns = [await interview_controller.serialize_turn(item) for item in turns if item.speaker == "user"]
        metrics = self.build_live_metrics(jd_data, serialized_turns)
        await interview_controller.update(
            id=session.id,
            obj_in={"latest_metrics": metrics},
        )
        return {
            "turn": await interview_controller.serialize_turn(turn),
            "metrics": metrics,
        }

    async def next_question(self, user_id: int, session_id: int):
        session = await interview_controller.get(id=session_id)
        if session.user_id != user_id:
            raise HTTPException(status_code=403, detail="无权操作该场次")
        turns = [await interview_controller.serialize_turn(item) for item in await interview_controller.get_turns(session.id)]
        position = await position_controller.get(id=session.position_id)
        jd = await jd_controller.get(id=session.jd_id) if session.jd_id else None
        result = await self.build_next_question(
            await session.to_dict(),
            await position.to_dict(),
            await jd.to_dict() if jd else None,
            turns,
        )
        if result.get("completed"):
            return result
        await interview_controller.update(
            id=session.id,
            obj_in={"current_round": result["round_no"]},
        )
        await interview_controller.add_turn(
            session_id=session.id,
            round_no=result["round_no"],
            speaker="ai",
            content=result["question"],
            source="question",
            segment_index=0,
        )
        updated_session = await interview_controller.get(id=session.id)
        return {
            **result,
            "session": await interview_controller.serialize(updated_session),
        }

    async def finish_interview(self, user_id: int, session_id: int):
        session = await interview_controller.get(id=session_id)
        if session.user_id != user_id:
            raise HTTPException(status_code=403, detail="无权结束该场次")
        candidate = await candidate_controller.get(id=session.candidate_id)
        position = await position_controller.get(id=session.position_id)
        jd = await jd_controller.get(id=session.jd_id) if session.jd_id else None
        turns = [await interview_controller.serialize_turn(item) for item in await interview_controller.get_turns(session.id)]
        report_payload = await self.build_report(
            await session.to_dict(),
            await candidate.to_dict(),
            await position.to_dict(),
            await jd.to_dict() if jd else None,
            turns,
        )
        report_payload["pdf_url"] = f"/ai-interview/reports/session/{session.id}?export=pdf"
        report = await report_controller.upsert_by_session(session, report_payload)
        await interview_controller.update(
            id=session.id,
            obj_in={
                "status": "completed",
                "ended_at": datetime.now(),
                "latest_metrics": report_payload.get("report_payload", {}).get("live_metrics", {}),
            },
        )
        updated_session = await interview_controller.get(id=session.id)
        return {
            "session": await interview_controller.serialize(updated_session),
            "report": await report_controller.serialize(report),
        }

    async def get_report(self, user_id: int, report_id: int | None = None, session_id: int | None = None):
        report = None
        if report_id is not None:
            report = await report_controller.get(id=report_id)
        elif session_id is not None:
            report = await report_controller.get_by_session_id(session_id)
        if not report:
            raise HTTPException(status_code=404, detail="报告不存在")
        session = await interview_controller.get(id=report.session_id)
        if session.user_id != user_id:
            raise HTTPException(status_code=403, detail="无权查看该报告")
        return await report_controller.serialize(report)


mock_interview_service = MockInterviewService()
