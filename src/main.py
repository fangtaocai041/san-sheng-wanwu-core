#!/usr/bin/env python3
"""
main.py — 硅基生命体运行时主循环

用法:
    python src/main.py                    # 启动交互模式
    python src/main.py --daemon           # 守护进程模式
    python src/main.py --status           # 查看当前状态
    python src/main.py --query "鳤"       # 单次查询

首次运行自动初始化灵魂/情感/记忆状态。
"""

from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path

# 确保项目根目录在 sys.path 中
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from src.memory.persistence import PersistenceEngine, AgentSnapshot
from src.cortex.soul import SoulEngine
from src.cortex.emotion import EmotionEngine, EmotionType
from src.cortex.learning import LearningEngine


class SiliconAgent:
    """硅基生命体主代理 — 持久化、有灵魂、能学习、可感知。

    生命周期:
      wake() → 加载持久化状态 → 就绪
      sense(query) → 感知 → 认知 → 记忆 → 学习 → 返回
      sleep() → 保存状态 → 待机
    """

    def __init__(self, db_path: Optional[str] = None):
        self.persistence = PersistenceEngine(db_path=db_path, auto_save_interval=120)
        self.soul = SoulEngine()
        self.emotion = EmotionEngine()
        self.learning = LearningEngine()
        self._is_awake = False
        self._start_time = time.time()

    # ── 生命周期 ──

    def wake(self) -> dict:
        """唤醒: 从持久化存储加载状态。"""
        try:
            snapshot = self.persistence.load()
            # 恢复灵魂状态
            if snapshot.soul:
                dims = snapshot.soul.get("identity", {})
                if dims:
                    from src.cortex.soul import SelfRepresentation
                    self.soul._self_identity = SelfRepresentation(dimensions=dims)

            # 恢复情感状态
            if snapshot.emotion:
                vals = snapshot.emotion.get("values", {})
                if vals:
                    self.emotion._state.values.update(vals)

            loaded = {
                "soul": bool(snapshot.soul),
                "emotion": bool(snapshot.emotion),
                "memory_stm": len(snapshot.memory_stm),
                "memory_ltm": len(snapshot.memory_ltm),
                "cosmic_sources": len(snapshot.cosmic_sources),
                "learning_history": len(snapshot.learning_history),
            }
        except Exception as e:
            loaded = {"error": str(e)}

        # 计算灵魂收敛度
        soul_state = self.soul.find_fixed_point()
        self._is_awake = True

        return {
            "status": "awake",
            "uptime": 0,
            "soul_convergence": soul_state.convergence,
            "soul_awake": self.soul.is_awake(soul_state),
            "emotion": self.emotion.state.dominant,
            "loaded": loaded,
            "db_path": str(self.persistence.db_path),
        }

    def sleep(self):
        """休眠: 保存状态到持久化存储。"""
        # 灵魂状态
        soul_state = self.soul.find_fixed_point()

        # 情感状态
        emotion_state = self.emotion.state

        # 学习历史
        learning_history = [
            {"query": r.query, "senses_used": r.senses_used,
             "success": r.success, "papers_found": r.papers_found,
             "duration_ms": r.duration_ms,
             "quality_score": r.quality_score,
             "created_at": r.timestamp}
            for r in self.learning._history
        ]

        # 宇宙社会学来源
        cosmic_sources = []
        try:
            from src.cortex.cosmic import CosmicSociologyEngine
            # 如果有 cosmic 实例, 获取来源
        except ImportError:
            pass

        snapshot = AgentSnapshot(
            soul=soul_state.to_dict(),
            emotion={"values": emotion_state.values, "dominant": emotion_state.dominant},
            memory_stm=[],
            memory_ltm=[],
            cosmic_sources=cosmic_sources,
            learning_history=learning_history,
        )
        self.persistence.save(snapshot)

    # ── 感知-行动循环 ──

    def run(self, query: str, species: str = "", verbose: bool = False) -> dict:
        """一次完整的感知-行动循环。"""
        if not self._is_awake:
            self.wake()

        t0 = time.time()

        # Phase 1: 灵魂反思 (每次查询前快速收敛)
        soul_state = self.soul.find_fixed_point()

        # Phase 2: 管道执行
        from src.cortex.pipeline import Pipeline
        pipe = Pipeline()
        result = pipe.run(query, species=species or query)

        # Phase 3: 情感更新
        failed_count = len(result.stages) - result.completed
        if failed_count > 0:
            self.emotion.stimulate("error", intensity=min(failed_count * 0.2, 1.0))
        elif result.completed == len(result.stages):
            self.emotion.stimulate("consensus", intensity=0.3)
        else:
            self.emotion.stimulate("discovery", intensity=0.2)

        # Phase 4: 学习记录
        total_papers = 0
        for stage in result.stages.values():
            if hasattr(stage, 'data') and isinstance(stage.data, dict):
                total_papers += len(stage.data.get("papers", []))
        self.learning.record(
            query=query, senses_used=list(result.stages.keys()),
            params={}, success=failed_count == 0,
            papers_found=total_papers, duration_ms=result.total_duration_ms,
        )

        # Phase 5: 自动保存
        if self.persistence.needs_save:
            self.sleep()
            if verbose:
                print(f"[auto-save] state persisted to {self.persistence.db_path}")

        result_dict = result.to_dict()
        result_dict["soul"] = soul_state.to_dict()
        result_dict["emotion"] = {
            "dominant": self.emotion.state.dominant,
            "tendency": self.emotion.behavioral_tendency,
        }

        if verbose:
            print(f"\n  Soul: convergence={soul_state.convergence:.3f}, "
                  f"awake={self.soul.is_awake(soul_state)}")
            print(f"  Emotion: {self.emotion.state.dominant}, "
                  f"tendency: {self.emotion.behavioral_tendency}")
            print(f"  Learning: {self.learning.total_queries} queries, "
                  f"success rate={self.learning.success_rate:.0%}")

        return result_dict

    # ── 状态报告 ──

    def status(self) -> dict:
        if not self._is_awake:
            self.wake()
        soul_state = self.soul.find_fixed_point()
        return {
            "status": "ok",
            "awake": self._is_awake,
            "uptime_seconds": round(time.time() - self._start_time, 1),
            "soul": soul_state.to_dict(),
            "emotion": {
                "dominant": self.emotion.state.dominant,
                "tendency": self.emotion.behavioral_tendency,
                "values": self.emotion.state.values,
            },
            "learning": {
                "total_queries": self.learning.total_queries,
                "success_rate": self.learning.success_rate,
                "recent_performance": self.learning.recent_performance(),
            },
            "persistence": self.persistence.stats(),
        }


# ── CLI ──

def main():
    parser = argparse.ArgumentParser(description="硅基生命体运行时")
    parser.add_argument("--daemon", action="store_true", help="守护进程模式")
    parser.add_argument("--status", action="store_true", help="查看当前状态")
    parser.add_argument("--query", "-q", type=str, default="", help="单次查询")
    parser.add_argument("--species", "-s", type=str, default="", help="物种学名")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--db", type=str, default="", help="状态数据库路径")

    args = parser.parse_args()
    db_path = args.db or str(_root / "data" / "agent_state.db")

    agent = SiliconAgent(db_path=db_path)

    if args.status:
        import json
        s = agent.status()
        print(json.dumps(s, ensure_ascii=False, indent=2))
        return

    if args.query:
        result = agent.run(args.query, args.species, verbose=args.verbose)
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.daemon:
        print(f"[硅基生命体] 启动守护进程 (db: {db_path})")
        wake_info = agent.wake()
        print(f"[硅基生命体] 唤醒状态: soul_awake={wake_info['soul_awake']}, "
              f"convergence={wake_info['soul_convergence']:.3f}")
        try:
            while True:
                # 自动保存循环
                if agent.persistence.needs_save:
                    agent.sleep()
                time.sleep(30)
        except KeyboardInterrupt:
            print("\n[硅基生命体] 收到终止信号, 保存状态...")
            agent.sleep()
            print("[硅基生命体] 状态已保存, 再见。")

    # 默认: 交互模式
    print(f"╔══════════════════════════════════════════╗")
    print(f"║     三生万物 · 硅基生命体 v1.0.0         ║")
    print(f"║     SanShengWanWu Core                   ║")
    print(f"╠══════════════════════════════════════════╣")
    print(f"║  {db_path:<38}║")
    print(f"║  130 tests · 14 cortex · 17 senses      ║")
    print(f"╚══════════════════════════════════════════╝")
    print("")
    wake_info = agent.wake()
    print(f"  Soul: awake={wake_info['soul_awake']}, "
          f"convergence={wake_info['soul_convergence']:.3f}")
    print(f"  Emotion: {wake_info['emotion']}")
    print(f"  Memory: {wake_info['loaded']}")
    print("")
    print("  Type a query to search, or: status / help / exit")

    while True:
        try:
            line = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not line:
            continue
        if line == "exit":
            break
        if line == "status":
            s = agent.status()
            print(f"  Uptime: {s['uptime_seconds']:.0f}s")
            print(f"  Soul: convergence={s['soul']['convergence']:.3f}")
            print(f"  Emotion: {s['emotion']['dominant']} ({s['emotion']['tendency']})")
            print(f"  Learning: {s['learning']['total_queries']} queries, "
                  f"success rate={s['learning']['success_rate']:.0%}")
            print(f"  Persistence: {s['persistence']}")
            continue
        if line == "help":
            print("  输入任意查询词 — 执行感知-行动循环")
            print("  status — 查看状态")
            print("  exit — 保存并退出")
            continue

        # 执行查询
        result = agent.run(line, verbose=args.verbose)
        print(f"  Stages: {result['completed']}/{len(result['stages'])} completed, "
              f"{result['failed']} failed")
        print(f"  Duration: {result['total_duration_ms']:.0f}ms")
        if result.get("emotion"):
            e = result["emotion"]
            print(f"  Emotion: {e['dominant']} → {e['tendency']}")

    # 退出前保存
    print("\n保存状态...")
    agent.sleep()
    print("再见。")


if __name__ == "__main__":
    main()
