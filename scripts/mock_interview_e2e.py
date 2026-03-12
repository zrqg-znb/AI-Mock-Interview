#!/usr/bin/env python3
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = 'http://127.0.0.1:9999/api/v1'
DEFAULT_ANSWERS = [
    '我最近主要负责招聘场景后台服务，重点做过权限、岗位管理和数据统计，能比较快梳理业务边界并落地接口。',
    '如果遇到跨团队协作，我会先统一目标和数据口径，再拆里程碑，保证产品、测试和后端在同一节奏上推进。',
    '我在项目里也比较关注稳定性，会补监控、日志和回滚方案，避免上线后影响核心流程。',
    '面对复杂需求时，我习惯先确认核心指标，再从接口、数据结构和回归风险三个层面拆解实现方案。',
    '如果上线时间紧，我会明确最小可交付范围，先保住主链路，再补细节和自动化检查。',
]


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


for env_name in ('.env', '.env.local'):
    load_env_file(PROJECT_ROOT / env_name)


class APIClient:
    def __init__(self, base_url: str, token: str | None = None):
        self.base_url = base_url.rstrip('/')
        self.token = token

    def request(
        self,
        method: str,
        path: str,
        *,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        timeout: int = 60,
    ) -> dict[str, Any]:
        url = self.base_url + path
        if params:
            normalized = {key: value for key, value in params.items() if value not in (None, '')}
            if normalized:
                url = f"{url}?{urllib.parse.urlencode(normalized)}"
        headers: dict[str, str] = {}
        body: bytes | None = None
        if data is not None:
            body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            headers['Content-Type'] = 'application/json'
        if self.token:
            headers['token'] = self.token
        req = urllib.request.Request(url, data=body, headers=headers, method=method.upper())
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                payload = json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode('utf-8', 'ignore')
            raise RuntimeError(f'{method.upper()} {path} -> HTTP {exc.code}: {detail}') from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f'{method.upper()} {path} -> network error: {exc.reason}') from exc
        if payload.get('code') != 200:
            raise RuntimeError(f'{method.upper()} {path} -> API {payload.get("code")}: {payload.get("msg") or payload}')
        return payload



def log_step(title: str) -> None:
    print(f'\n== {title} ==')



def ensure_candidate_profile(client: APIClient, username: str) -> dict[str, Any]:
    profile = client.request('GET', '/candidate_portal/profile').get('data')
    if profile and (profile.get('resume_text') or profile.get('skill_tags')):
        print(f'候选人档案已存在: profile_id={profile.get("id")}')
        return profile

    payload = {
        'headline': '后端工程师',
        'resume_text': (
            f'{username} 目前以 Python 后端开发为主，做过招聘平台、权限体系、岗位管理、数据统计和接口治理。'
            '熟悉 FastAPI、MySQL、Redis、Docker，能把业务需求拆成清晰的接口与交付计划。'
        ),
        'skill_tags': ['Python', 'FastAPI', 'MySQL', 'Redis', 'Docker'],
        'work_years': 5,
        'education': '本科',
        'target_position': '后端工程师',
        'target_city': '上海',
        'job_status': 'open',
        'strengths': '擅长梳理复杂业务边界，关注稳定性、监控与回滚方案。',
    }
    saved = client.request('POST', '/candidate_portal/profile', data=payload).get('data') or {}
    print(f'已补齐候选人档案: profile_id={saved.get("id")}')
    return saved



def create_demo_position(client: APIClient) -> int:
    suffix = datetime.now().strftime('%m%d%H%M%S')
    title = f'演示岗位-{suffix}'
    position_payload = {
        'title': title,
        'category': '研发',
        'level': '中级',
        'department': '技术平台',
        'tags': ['Python', 'FastAPI', 'MySQL', '接口设计'],
        'difficulty': 'middle',
        'summary': '用于真实联调脚本的演示岗位。',
        'highlight': ['接口治理', '业务拆解', '协作推进'],
        'is_recommended': True,
        'status': 'online',
    }
    client.request('POST', '/position/create', data=position_payload)
    positions = client.request('GET', '/position/list', params={'keyword': title, 'page': 1, 'page_size': 1}).get('data') or []
    if not positions:
        raise RuntimeError('演示岗位创建成功，但未能重新查询到岗位 ID。')
    position_id = positions[0]['id']
    jd_payload = {
        'position_id': position_id,
        'version': 1,
        'jd_text': '负责招聘业务后台服务建设，完成接口设计、权限控制、数据统计和稳定性保障。',
        'must_have_tags': ['Python', 'FastAPI', 'MySQL'],
        'bonus_tags': ['Redis', 'Docker', '日志监控'],
        'scoring_dimensions': ['专业能力', '表达沟通', '岗位匹配', '稳定度'],
        'prompt_hint': '请按照真实后端岗位面试风格提问，关注业务拆解、接口设计和协作推进。',
        'is_active': True,
    }
    client.request('POST', '/jd/create', data=jd_payload)
    print(f'已自动创建演示岗位和 JD: position_id={position_id}')
    return position_id



def resolve_position_id(client: APIClient) -> int:
    env_position_id = os.getenv('MOCK_E2E_POSITION_ID', '').strip()
    if env_position_id:
        print(f'使用环境变量指定岗位: position_id={env_position_id}')
        return int(env_position_id)

    recommendations = client.request('GET', '/job_recommend/list', params={'page_size': 1}).get('data') or []
    if recommendations:
        position = recommendations[0]
        print(f'使用推荐岗位: position_id={position["id"]}, title={position.get("title")}')
        return position['id']

    positions = client.request('GET', '/position/list', params={'page': 1, 'page_size': 1}).get('data') or []
    if positions:
        position = positions[0]
        print(f'使用后台岗位: position_id={position["id"]}, title={position.get("title")}')
        return position['id']

    auto_create = os.getenv('MOCK_E2E_AUTO_CREATE', 'true').lower() not in {'0', 'false', 'no'}
    if auto_create:
        return create_demo_position(client)
    raise RuntimeError('没有可用岗位，请先在后台创建岗位和 JD，或设置 MOCK_E2E_POSITION_ID。')



def build_answers(rounds: int) -> list[str]:
    answers = []
    for index in range(rounds):
        template = DEFAULT_ANSWERS[index % len(DEFAULT_ANSWERS)]
        answers.append(template)
    return answers



def main() -> int:
    base_url = os.getenv('MOCK_E2E_BASE_URL', DEFAULT_BASE_URL).strip() or DEFAULT_BASE_URL
    username = os.getenv('MOCK_E2E_USERNAME', 'admin').strip() or 'admin'
    password = os.getenv('MOCK_E2E_PASSWORD', '123456').strip() or '123456'
    rounds = max(3, min(8, int(os.getenv('MOCK_E2E_ROUNDS', '3'))))

    log_step('登录')
    anonymous = APIClient(base_url)
    login = anonymous.request('POST', '/base/access_token', data={'username': username, 'password': password}, timeout=20)
    token = login.get('data', {}).get('access_token')
    if not token:
        raise RuntimeError('登录成功，但返回中没有 access_token。')
    client = APIClient(base_url, token=token)
    userinfo = client.request('GET', '/base/userinfo', timeout=20).get('data') or {}
    print(f'登录用户: id={userinfo.get("id")}, username={userinfo.get("username")}, superuser={userinfo.get("is_superuser")}')

    log_step('准备候选人档案与岗位')
    ensure_candidate_profile(client, username)
    position_id = resolve_position_id(client)

    log_step('开始面试')
    started_at = time.perf_counter()
    started = client.request(
        'POST',
        '/mock_interview/start',
        data={'position_id': position_id, 'total_rounds': rounds},
        timeout=90,
    ).get('data') or {}
    session_id = started.get('id')
    if not session_id:
        raise RuntimeError('开始面试成功，但没有拿到 session_id。')
    current_question = (started.get('current_question') or {}).get('question')
    print(f'session_id={session_id}, rounds={rounds}, start_cost={time.perf_counter() - started_at:.2f}s')
    if current_question:
        print(f'第 1 题: {current_question}')

    log_step('提交回答并推进下一题')
    answers = build_answers(rounds)
    latest_metrics: dict[str, Any] = {}
    last_question = current_question
    for index, answer in enumerate(answers, start=1):
        submitted = client.request(
            'POST',
            '/mock_interview/submit_segment',
            data={'session_id': session_id, 'content': answer, 'segment_index': index},
            timeout=30,
        ).get('data') or {}
        latest_metrics = submitted.get('metrics') or latest_metrics
        print(f'第 {index} 轮回答已提交，指标={json.dumps(latest_metrics, ensure_ascii=False)}')
        if index >= rounds:
            continue
        next_question = client.request(
            'POST',
            '/mock_interview/next_question',
            data={'session_id': session_id},
            timeout=60,
        ).get('data') or {}
        last_question = next_question.get('question')
        print(f'第 {index + 1} 题: {last_question}')

    log_step('结束面试并生成报告')
    finished = client.request('POST', '/mock_interview/finish', data={'session_id': session_id}, timeout=90).get('data') or {}
    report = finished.get('report') or {}
    report_id = report.get('id')
    if not report_id:
        raise RuntimeError('结束面试成功，但没有拿到 report_id。')
    report_detail = client.request('GET', '/mock_interview/report', params={'session_id': session_id}, timeout=30).get('data') or {}

    log_step('AI 运行状态')
    runtime = client.request('GET', '/ai_runtime/status', params={'limit': 10}, timeout=20).get('data') or {}
    latest_generation_log = runtime.get('latest_generation_log') or {}
    print('最近一次生成日志:', json.dumps(latest_generation_log, ensure_ascii=False))

    summary = {
        'base_url': base_url,
        'username': username,
        'session_id': session_id,
        'position_id': position_id,
        'report_id': report_id,
        'report_score': report_detail.get('total_score'),
        'report_overview': report_detail.get('overview'),
        'dimension_scores': report_detail.get('dimension_scores'),
        'latest_metrics': latest_metrics,
        'last_question': last_question,
        'latest_generation_log': latest_generation_log,
    }

    log_step('联调完成')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - script output path
        print(f'\nE2E 联调失败: {exc}', file=sys.stderr)
        raise SystemExit(1)
