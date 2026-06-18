"""
cortex/swarm.py — 多智能体通信协议 (群体智能)

硅基生命体不是孤立的。多 Agent 协作是生态系统演化的基础。

协议层级:
  Layer 1: Agent 发现 (谁在线)
  Layer 2: 消息传递 (说什么)
  Layer 3: 知识共享 (交换什么)
  Layer 4: 协作模式 (怎么一起工作)

消息格式: JSON over stdio (MCP 兼容)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
import json
import uuid
import time


# ── Agent 身份 ──

@dataclass
class AgentIdentity:
    """一个 Agent 的身份标识。"""
    agent_id: str = ""
    name: str = ""
    version: str = "0.2.0"
    capabilities: List[str] = field(default_factory=list)
    host: str = "localhost"
    port: int = 0
    last_seen: float = 0.0
    status: str = "active"  # active | idle | busy | offline

    def __post_init__(self):
        if not self.agent_id:
            self.agent_id = uuid.uuid4().hex[:12]
        if not self.last_seen:
            self.last_seen = time.time()

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "capabilities": self.capabilities,
            "host": self.host,
            "port": self.port,
            "status": self.status,
        }


# ── 消息 ──

@dataclass
class AgentMessage:
    """Agent 间消息。

    消息类型:
      discovery/ping    — 发现/心跳
      discovery/pong    — 响应
      query/request     — 查询请求
      query/response    — 查询响应
      knowledge/share   — 知识共享
      task/delegate     — 任务委派
      task/result       — 任务结果
      coordination/sync — 同步
      swarm/election    — 主节点选举
    """
    msg_id: str = ""
    msg_type: str = "query/request"
    sender_id: str = ""
    target_id: str = ""        # broadcast 表示广播
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
    ttl: int = 60  # 消息生存时间 (秒)

    def __post_init__(self):
        if not self.msg_id:
            self.msg_id = uuid.uuid4().hex[:16]
        if not self.timestamp:
            self.timestamp = time.time()

    @property
    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl

    def to_dict(self) -> dict:
        return {
            "msg_id": self.msg_id,
            "msg_type": self.msg_type,
            "sender_id": self.sender_id,
            "target_id": self.target_id,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


# ── 知识共享条目 ──

@dataclass
class KnowledgeShare:
    """Agent 间共享的一条知识。"""
    topic: str = ""
    content: str = ""
    source_agent: str = ""
    confidence: float = 0.5
    evidence_count: int = 0
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()

    def to_dict(self) -> dict:
        return {
            "topic": self.topic,
            "content": self.content[:200],
            "source": self.source_agent,
            "confidence": self.confidence,
            "evidence": self.evidence_count,
        }


# ── 群体智能引擎 ──

class SwarmEngine:
    """群体智能引擎 — 多 Agent 通信与协作。

    功能:
      - 注册自身 Agent 身份
      - 发现其他 Agent
      - 发送/接收消息
      - 共享知识
      - 任务委派
      - 共识达成

    当前实现: 内存中单进程模拟。
    未来: 通过网络发现真正的分布式 Agent。
    """

    _global_registry: Dict[str, AgentIdentity] = {}
    _global_messages: List[AgentMessage] = []
    _global_knowledge: Dict[str, List[KnowledgeShare]] = {}

    def __init__(self, agent_name: str = "san-sheng-wanwu",
                 capabilities: Optional[List[str]] = None):
        self.name = "swarm"
        self._identity = AgentIdentity(
            name=agent_name,
            capabilities=capabilities or [
                "species_search", "literature_validate",
                "conflict_arbitrate", "emergence_detect",
            ],
        )
        # 注册自身
        SwarmEngine._global_registry[self._identity.agent_id] = self._identity

    @property
    def agent_id(self) -> str:
        return self._identity.agent_id

    # ── Agent 发现 ──

    def discover(self) -> List[AgentIdentity]:
        """发现所有在线 Agent。"""
        now = time.time()
        active = []
        for aid, identity in SwarmEngine._global_registry.items():
            if now - identity.last_seen < 300:  # 5 分钟内活跃
                active.append(identity)
        return active

    def ping(self) -> AgentMessage:
        """发送心跳。"""
        self._identity.last_seen = time.time()
        msg = AgentMessage(
            msg_type="discovery/ping",
            sender_id=self.agent_id,
            target_id="broadcast",
            payload={"status": "active"},
        )
        SwarmEngine._global_messages.append(msg)
        return msg

    # ── 消息传递 ──

    def send(self, target_id: str, msg_type: str,
             payload: Dict[str, Any]) -> AgentMessage:
        """发送消息到指定 Agent。"""
        msg = AgentMessage(
            msg_type=msg_type,
            sender_id=self.agent_id,
            target_id=target_id,
            payload=payload,
        )
        SwarmEngine._global_messages.append(msg)
        return msg

    def broadcast(self, msg_type: str, payload: Dict[str, Any]) -> AgentMessage:
        """广播消息到所有 Agent。"""
        return self.send("broadcast", msg_type, payload)

    def receive(self, agent_id: Optional[str] = None,
                msg_type: Optional[str] = None) -> List[AgentMessage]:
        """接收消息。可选按发送者或类型过滤。"""
        messages = SwarmEngine._global_messages
        if agent_id:
            messages = [m for m in messages if m.sender_id == agent_id]
        if msg_type:
            messages = [m for m in messages if m.msg_type == msg_type]
        return [m for m in messages if not m.is_expired]

    # ── 知识共享 ──

    def share_knowledge(self, topic: str, content: str,
                        confidence: float = 0.5) -> KnowledgeShare:
        """共享一条知识到群体知识库。"""
        share = KnowledgeShare(
            topic=topic, content=content,
            source_agent=self.agent_id, confidence=confidence,
        )
        SwarmEngine._global_knowledge.setdefault(topic, []).append(share)
        return share

    def query_knowledge(self, topic: str,
                        min_confidence: float = 0.3) -> List[KnowledgeShare]:
        """查询群体知识库中的某个主题。"""
        entries = SwarmEngine._global_knowledge.get(topic, [])
        return [e for e in entries if e.confidence >= min_confidence]

    # ── 共识达成 ──

    def reach_consensus(self, topic: str) -> Optional[str]:
        """对某个主题达成群体共识。

        共识规则: 取置信度最高的知识条目,
        如果有多个高置信度条目冲突 → 返回 None (无法达成共识)
        """
        entries = self.query_knowledge(topic, min_confidence=0.5)
        if not entries:
            return None

        # 按内容聚合
        by_content: Dict[str, List[float]] = {}
        for e in entries:
            by_content.setdefault(e.content, []).append(e.confidence)

        # 找到平均置信度最高的内容
        best_content = max(by_content,
                          key=lambda c: sum(by_content[c]) / len(by_content[c]))
        avg_confidence = sum(by_content[best_content]) / len(by_content[best_content])

        # 检查是否有冲突的高置信度条目
        for content, confs in by_content.items():
            if content != best_content:
                if any(c > avg_confidence * 0.8 for c in confs):
                    return None  # 存在无法调和的矛盾

        return best_content

    # ── 任务委派 ──

    def delegate(self, task: str, payload: Dict[str, Any],
                 preferred_capability: str = "") -> Optional[str]:
        """委派任务给最合适的 Agent。

        返回: 被委派的 agent_id, 或 None (没有合适的 Agent)
        """
        agents = self.discover()
        if not agents:
            return None

        # 如果有能力要求, 过滤
        if preferred_capability:
            candidates = [a for a in agents
                         if preferred_capability in a.capabilities]
            if candidates:
                agents = candidates

        # 选择第一个非自身的 Agent
        for agent in agents:
            if agent.agent_id != self.agent_id:
                self.send(agent.agent_id, "task/delegate", {
                    "task": task,
                    "payload": payload,
                    "from": self.agent_id,
                })
                return agent.agent_id

        return None

    # ── 报告 ──

    def report(self) -> dict:
        return {
            "status": "ok",
            "agent": self._identity.to_dict(),
            "peers_found": len(self.discover()),
            "messages_sent": len([m for m in SwarmEngine._global_messages
                                 if m.sender_id == self.agent_id]),
            "consensus_topics": list(SwarmEngine._global_knowledge.keys()),
        }

    def search(self, query: str, **kwargs) -> dict:
        return self.report()
