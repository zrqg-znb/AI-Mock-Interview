import math
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

    def build_recommendation_reason(self, candidate: dict, position: dict, matched_tags: list[str], missing_tags: list[str], score: int):
        headline = candidate.get("headline") or candidate.get("target_position") or "候选人"
        matched_text = "、".join(matched_tags[:3]) or "你的核心经历"
        missing_text = "、".join(missing_tags[:2]) or "可继续补充岗位案例"
        return (
            f"{headline} 与 {position.get('title')} 的匹配度为 {score} 分，"
            f"当前命中的核心点包括 {matched_text}。"
            f"建议在正式模拟前补强 {missing_text}，可明显提高面试报告中的岗位匹配与表达完整度。"
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
                "question": f"请用 1 分钟做一个与 {position.get('title')} 高度相关的自我介绍，并突出你最有代表性的项目经历。",
            },
            {
                "index": 2,
                "stage": "experience",
                "focus": focus_tags[0] if focus_tags else "核心项目",
                "question": f"结合你的简历，详细讲讲你最能体现 {position.get('title')} 胜任力的一次项目实践，你负责了什么、如何推进、结果如何？",
            },
            {
                "index": 3,
                "stage": "scenario",
                "focus": focus_tags[1] if len(focus_tags) > 1 else "问题拆解",
                "question": f"如果你入职后需要在两周内交付一个围绕 {position.get('category') or position.get('title')} 的关键任务，你会如何拆解目标、安排节奏并验证结果？",
            },
            {
                "index": 4,
                "stage": "stress",
                "focus": focus_tags[2] if len(focus_tags) > 2 else "临场稳定度",
                "question": f"当项目推进受阻、资源不足且时间紧时，你通常如何沟通风险、争取资源并稳定团队节奏？",
            },
            {
                "index": 5,
                "stage": "closing",
                "focus": "岗位动机",
                "question": f"最后请你总结一下：为什么你适合 {position.get('title')}，以及你接下来 90 天最想交付的成果是什么？",
            },
        ]
        questions = questions[:total_rounds]
        return {
            "persona": {
                "name": "Astra 面试官",
                "style": "冷静、专业、会追问业务细节",
                "tone": "高级感、数据导向、表达克制",
            },
            "evaluation_focus": scoring_dimensions or DEFAULT_SCORING_DIMENSIONS,
            "questions": questions,
            "opening": f"你好，我是今天负责 {position.get('title')} 模拟面试的 AI 面试官，我们会围绕岗位胜任力、表达结构与业务理解展开。",
        }

    async def build_question_plan(self, candidate: dict, position: dict, jd: dict | None, total_rounds: int):
        fallback = self.build_fallback_question_plan(candidate, position, jd, total_rounds)
        if not interview_ai_adapter.enabled:
            return fallback
        system_prompt = "你是资深招聘官，请根据岗位JD与简历，生成结构化模拟面试题计划，仅返回 JSON。"
        user_prompt = (
            f"岗位：{position}\n候选人：{candidate}\nJD：{jd}\n"
            f"请返回 persona、evaluation_focus、opening、questions 四个字段，questions 生成 {total_rounds} 题。"
        )
        result = await interview_ai_adapter.generate_json(system_prompt, user_prompt)
        if not result or not isinstance(result.get("questions"), list):
            return fallback
        result.setdefault("persona", fallback["persona"])
        result.setdefault("evaluation_focus", fallback["evaluation_focus"])
        result.setdefault("opening", fallback["opening"])
        result["questions"] = result["questions"][:total_rounds]
        return result

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
        if next_index > session.get("total_rounds", 5):
            return {"completed": True}
        if isinstance(plan, list) and len(plan) >= next_index:
            question_item = plan[next_index - 1]
        else:
            fallback_plan = self.build_fallback_question_plan({}, position, jd, session.get("total_rounds", 5))
            question_item = fallback_plan["questions"][next_index - 1]
        return {
            "completed": False,
            "round_no": next_index,
            "question": question_item.get("question"),
            "focus": question_item.get("focus"),
            "stage": question_item.get("stage"),
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
        dimension_scores = {}
        for index, name in enumerate(dimension_names):
            dimension_scores[name] = values_seed[index % len(values_seed)]
        total_score = round(sum(dimension_scores.values()) / max(len(dimension_scores), 1))
        matched_keywords = live_metrics.get("matched_keywords", [])
        highlights = [
            f"回答中较多命中了 {position.get('title')} 所需的业务关键词。",
            "表达节奏稳定，能维持连续作答。",
            "项目叙述具备一定结果导向意识。",
        ]
        if matched_keywords:
            highlights[0] = f"回答中命中了 {', '.join(matched_keywords[:3])} 等岗位关键词。"
        risks = [
            "高压场景回答还可以进一步量化结果。",
            "部分回答的结构化程度可以继续加强。",
            "若补充更具体的数据指标，报告说服力会更高。",
        ]
        suggestions = [
            "下一轮训练建议优先补强 STAR 结构表达。",
            f"针对 {position.get('title')} 的关键能力，准备 2 个可量化项目案例。",
            "在结尾主动总结业务价值与落地结果，提升高级感。",
        ]
        recommended_positions = [position.get("title")]
        if position.get("category") and position.get("category") != position.get("title"):
            recommended_positions.append(position.get("category"))
        overview = (
            f"本次模拟面试整体表现为 {total_score} 分。候选人在 {position.get('title')} 相关问题上展示了较好的岗位理解，"
            f"其中关键词命中率为 {live_metrics['keyword_hit_rate']}%，表达完整度为 {live_metrics['completeness']}%。"
            "若能进一步补强案例量化与压力场景拆解，正式面试通过率会更高。"
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
            },
        }
        if interview_ai_adapter.enabled:
            system_prompt = "你是资深面试官，请根据面试对话生成结构化面试报告，仅返回 JSON。"
            user_prompt = f"场次：{session}\n候选人：{candidate}\n岗位：{position}\nJD：{jd}\n对话：{turns}"
            ai_result = await interview_ai_adapter.generate_json(system_prompt, user_prompt)
            if ai_result and isinstance(ai_result, dict):
                payload.update({key: value for key, value in ai_result.items() if key in payload or key == 'dimension_scores'})
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
        opening = plan.get("opening") or "欢迎来到 AI 模拟面试，现在我们开始第一题。"
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
