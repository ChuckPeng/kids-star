"""Task template presets."""
from fastapi import APIRouter

router = APIRouter(prefix="/templates", tags=["templates"])

PRESETS = [
    {"title": "整理书包", "description": "按课表整理第二天需要的书本和文具", "task_type": "daily_habit", "difficulty": "required", "category": "生活习惯", "base_points": 3, "repeat_type": "daily"},
    {"title": "刷牙洗脸", "description": "早晚各一次，认真刷牙3分钟", "task_type": "daily_habit", "difficulty": "required", "category": "生活习惯", "base_points": 2, "repeat_type": "daily"},
    {"title": "叠被子", "description": "起床后自己叠好被子", "task_type": "daily_habit", "difficulty": "required", "category": "生活习惯", "base_points": 3, "repeat_type": "daily"},
    {"title": "整理房间", "description": "收拾玩具、整理书桌、扫地", "task_type": "chore", "difficulty": "required", "category": "家务", "base_points": 5, "repeat_type": "weekly"},
    {"title": "完成作业", "description": "按时完成当天所有作业", "task_type": "homework", "difficulty": "required", "category": "学习", "base_points": 5, "repeat_type": "daily"},
    {"title": "阅读30分钟", "description": "选择一本喜欢的书，安静阅读", "task_type": "daily_habit", "difficulty": "required", "category": "学习", "base_points": 4, "repeat_type": "daily"},
    {"title": "运动30分钟", "description": "跑步、跳绳、打球等户外运动", "task_type": "daily_habit", "difficulty": "required", "category": "健康", "base_points": 5, "repeat_type": "daily"},
    {"title": "帮忙洗碗", "description": "吃完饭后帮忙收拾碗筷并洗碗", "task_type": "chore", "difficulty": "challenge", "category": "家务", "base_points": 10, "repeat_type": "daily"},
    {"title": "背单词20个", "description": "记忆并默写20个英语单词", "task_type": "homework", "difficulty": "challenge", "category": "学习", "base_points": 8, "repeat_type": "daily"},
    {"title": "练字一页", "description": "认真临摹字帖一页", "task_type": "homework", "difficulty": "required", "category": "学习", "base_points": 4, "repeat_type": "daily"},
    {"title": "照顾宠物", "description": "喂食、换水、清理宠物区域", "task_type": "chore", "difficulty": "required", "category": "家务", "base_points": 4, "repeat_type": "daily"},
    {"title": "早睡早起", "description": "晚上9:30前睡觉，早上7:00前起床", "task_type": "daily_habit", "difficulty": "challenge", "category": "健康", "base_points": 8, "repeat_type": "daily"},
]


@router.get("")
async def list_templates():
    return PRESETS
