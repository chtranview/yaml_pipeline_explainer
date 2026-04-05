"""
ExpertAI Course Engine — Runtime 入口
用法：python -m runtime.main [command] [options]
"""

import argparse
import sys
from pathlib import Path

from .loader import PipelineLoader
from .router import CommandRouter
from .utils import setup_logging, get_project_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ExpertAI_Course_Engine",
        description="AI 課程自動化生成系統 — CLI 入口",
    )
    parser.add_argument(
        "command",
        choices=["build", "outline", "verify"],
        help="要執行的指令（對應 _index.yaml 中的 commands）",
    )
    parser.add_argument("--topic", type=str, help="課程主題")
    parser.add_argument("--days", type=int, default=2, help="課程天數（預設 2）")
    parser.add_argument(
        "--level",
        choices=["beginner", "intermediate", "advanced"],
        default="intermediate",
        help="受眾程度",
    )
    parser.add_argument("--modules", type=int, default=4, help="模組數量（預設 4）")
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warn", "error"],
        default="info",
        help="日誌等級",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = get_project_root()
    logger = setup_logging(args.log_level, project_root)

    logger.info("ExpertAI Course Engine 啟動")
    logger.info(f"指令：/{args.command}")

    # 載入 pipeline 定義
    loader = PipelineLoader(project_root)
    index = loader.load_index()
    if index is None:
        logger.error("無法載入 _index.yaml")
        return 1

    # 路由到對應模組
    router = CommandRouter(loader, project_root, logger)
    params = {
        "course_topic": args.topic or "",
        "duration_days": args.days,
        "audience_level": args.level,
        "module_count": args.modules,
    }

    success = router.dispatch(args.command, params)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
