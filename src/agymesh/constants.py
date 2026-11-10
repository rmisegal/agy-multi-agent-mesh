# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""Immutable protocol constants shared by the hub, the clients and the instruction templates."""

# Hub operations (the "op" field of a request).
OP_HELLO = "hello"
OP_JOIN = "join"
OP_LEAVE = "leave"
OP_SEND = "send"
OP_RECV = "recv"
OP_AWAIT = "await"
OP_PEERS = "peers"
OP_STATS = "stats"
OP_SHUTDOWN = "shutdown"
OP_BOARD_ADD = "board_add"
OP_BOARD_CLAIM = "board_claim"
OP_BOARD_DONE = "board_done"
OP_BOARD_LIST = "board_list"
OP_BOARD_CLEAR = "board_clear"

# Message kinds.
KIND_TASK = "task"
KIND_PING = "ping"
KIND_MESHCHECK = "meshcheck"
KIND_REPLY = "reply"
KINDS = (KIND_TASK, KIND_PING, KIND_MESHCHECK, KIND_REPLY)
PING_TEXT = "PING"

# Session states shown by `peers`.
STATE_LISTENING = "listening"
STATE_BUSY = "busy"
STATE_STALE = "stale"

# Error codes returned by the hub.
ERR_BAD_REQUEST = "bad_request"
ERR_UNKNOWN_PEER = "unknown_peer"
ERR_RATE_LIMITED = "rate_limited"
ERR_MAILBOX_FULL = "mailbox_full"
ERR_NOT_IN_SESSION = "not_in_session"

# Queue overflow strategies.
OVERFLOW_REJECT_OLDEST = "reject_oldest"
OVERFLOW_REJECT_NEWEST = "reject_newest"

# Environment variables that override config/setup.json.
ENV_CONFIG_DIR = "AGYMESH_CONFIG_DIR"
ENV_TEAM = "AGYMESH_TEAM"
ENV_HOST = "AGYMESH_HOST"
ENV_PORT = "AGYMESH_PORT"

# Instruction file read by every agy session.
INSTRUCTION_FILE = "AGY.md"
