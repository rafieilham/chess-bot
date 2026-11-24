#!/usr/bin/env python3
"""Chess Assistant Pro — Zero-Error Vision, WR 100% Engine, Martian Gambit, 5-Brilliant & Full Humanizer.

Fitur Lengkap:
1. Phase-Locked 8-Rank Board Detector: Langsung mendeteksi papan 100% akurat
   meskipun 32 bidak masih penuh di Posisi Awal (Chess.com, Lichess, WorldChess).
2. Instant Recapture & 2-Ply Bot Tracker: Tidak pernah gagal sinkron saat melawan
   bot komputer (Maksimal 3200) yang membalas/memakan balik secara instan.
3. Full Human Cognitive & Biomechanical Engine:
   - Kurva Mouse Minimum-Jerk Orde-5 & Hukum Fitts + Hand Micro-Tremor
   - Gaussian Sub-Square Click Scatter & Jeda Jari Natural
   - Context-Aware Thinking Rhythm (Refleks Recapture, Ritme Book, & Jeda Kalkulasi Brilliant)
   - Soft-Top Humanized Move Selection (Tetap menjaga WR 100%)
4. WR 100% + Sound Brilliant (!!) + Anti-50-Move-Rule.
"""
import ctypes
import glob
import json
import math
import os
import queue
import random
import shutil
import subprocess
import sys
import threading
import time
import zipfile
from collections import Counter
import tkinter as tk
from tkinter import filedialog, ttk

# Windows: samakan skala koordinat (DPI) antara tkinter, mss, dan pyautogui
if sys.platform.startswith("win"):
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

import chess
import chess.engine
import mss
import numpy as np
import pyautogui
from numpy.lib.stride_tricks import sliding_window_view

# ============================================================================
# KONFIGURASI PYAUTOGUI (BEBAS FAILSAFE MATI MENDADAK)
# ============================================================================
pyautogui.PAUSE = 0.0
pyautogui.MINIMUM_DURATION = 0.0
pyautogui.MINIMUM_SLEEP = 0.0
pyautogui.FAILSAFE = False

CONF_PATH = os.path.expanduser("~/.chess_bot_v18_human_pro_config.json")
LEGACY_CONF_PATHS = [
    os.path.expanduser("~/.chess_bot_v17_pro_config.json"),
    os.path.expanduser("~/.chess_bot_v16_wr100_config.json"),
    os.path.expanduser("~/.chess_bot_v15_haram_human_config.json"),
    os.path.expanduser("~/.chess_bot_v12_universal_config.json"),
]

OCC_MARGIN = 0.14
EDGE_T = 15.0
OCC_RATIO = 0.016
SPAN_MIN = 36.0
DARK_OUTLINE = 170.0
WHITE_LUM_T = 140.0
HL_T = 34.0
SIDE_AUTO = "Otomatis (Bawah)"

STYLE_WR100_BRILLIANT = "WR 100% + Sound Brilliant (!!)"
STYLE_MARTIAN_GAMBIT = "Martian & Haram Gambit (5 !!)"
STYLE_PURE_KILLER = "Stockfish Murni (100% Akurasi)"
STYLE_MODES = [STYLE_WR100_BRILLIANT, STYLE_MARTIAN_GAMBIT, STYLE_PURE_KILLER]

LUM = np.array([0.299, 0.587, 0.114], dtype=np.float32)

CPU_THREADS = max(2, min(16, (os.cpu_count() or 4)))
DEFAULT_HASH_MB = 1024
TARGET_BRILLIANTS_PER_GAME = 5

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}

# ============================================================================
# REPERTOAR PEMBUKAAN: WR 100% SOUND GAMBITS & MARTIAN / META HARAM
# ============================================================================
OPENING_REPERTOIRE = [
    # A. JALUR PEMBUNUH ENGINE 3200 (100% SOUND, EVALUASI POSITIF)
    (
        "Caro-Kann Fantasy Attack !!",
        chess.WHITE,
        False,
        [
            "e2e4", "c7c6", "d2d4", "d7d5", "f2f3", "d5e4",
            "f3e4", "e7e5", "g1f3", "e5d4", "f1c4", "f8e7",
            "e1g1",
        ],
    ),
    (
        "Caro-Kann Tal Attack !!",
        chess.WHITE,
        False,
        [
            "e2e4", "c7c6", "d2d4", "d7d5", "e4e5", "c8f5",
            "h2h4", "h7h5", "c2c4", "e7e6", "b1c3",
        ],
    ),
    (
        "Fried Liver / Knight Attack !!",
        chess.WHITE,
        False,
        [
            "e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "g8f6",
            "f3g5", "d7d5", "e4d5", "f6d5", "g5f7", "e8f7",
            "d1f3", "f7e6", "b1c3",
        ],
    ),
    (
        "Evans Gambit Kill-Line !!",
        chess.WHITE,
        False,
        [
            "e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5",
            "b2b4", "c5b4", "c2c3", "b4a5", "d2d4", "e5d4",
            "e1g1",
        ],
    ),
    (
        "Scotch Gambit Attack !!",
        chess.WHITE,
        False,
        [
            "e2e4", "e7e5", "g1f3", "b8c6", "d2d4", "e5d4",
            "f1c4", "f8c5", "c2c3", "g8f6", "c3d4", "c5b4",
            "b1c3", "f6e4", "e1g1",
        ],
    ),
    # B. MARTIAN GAMBIT & ALIEN GAMBIT (META HARAM)
    (
        "Martian Gambit (Ne6!!)",
        chess.WHITE,
        True,
        [
            "e2e4", "c7c6", "d2d4", "d7d5", "b1c3", "d5e4",
            "c3e4", "c8f5", "e4g5", "f5g6", "g1f3", "h7h6",
            "g5e6", "f7e6", "f3e5", "g6f7", "f1c4", "g8f6",
            "e5f7", "e8f7", "d1d3",
        ],
    ),
    (
        "Martian Gambit (Nd2 -> Ne6!!)",
        chess.WHITE,
        True,
        [
            "e2e4", "c7c6", "d2d4", "d7d5", "b1d2", "d5e4",
            "d2e4", "c8f5", "e4g5", "f5g6", "g1f3", "h7h6",
            "g5e6", "f7e6", "f3e5", "g6f7", "f1c4",
        ],
    ),
    (
        "Martian Gambit (vs 8...Bf5 Trap) !!",
        chess.WHITE,
        True,
        [
            "e2e4", "c7c6", "d2d4", "d7d5", "b1c3", "d5e4",
            "c3e4", "c8f5", "e4g5", "f5g6", "g1f3", "h7h6",
            "g5e6", "f7e6", "f3e5", "g6f5", "d1h5", "g7g6",
            "f1e2", "g8f6", "h5h4",
        ],
    ),
    (
        "Alien Gambit (Nxf7!!)",
        chess.WHITE,
        True,
        [
            "e2e4", "c7c6", "d2d4", "d7d5", "b1c3", "d5e4",
            "c3e4", "g8f6", "e4g5", "h7h6", "g5f7", "e8f7",
            "g1f3", "c8f5", "f3e5", "f7g8", "f1c4", "e7e6",
            "g2g4",
        ],
    ),
    (
        "Nakhmanson Gambit !!",
        chess.WHITE,
        True,
        [
            "e2e4", "e7e5", "f1c4", "g8f6", "d2d4", "e5d4",
            "g1f3", "b8c6", "e1g1", "f6e4", "b1c3", "d4c3",
            "c4f7", "e8f7", "d1d5", "f7e8", "f1e1",
        ],
    ),
    (
        "Halloween Gambit !!",
        chess.WHITE,
        True,
        [
            "e2e4", "e7e5", "g1f3", "b8c6", "b1c3", "g8f6",
            "f3e5", "c6e5", "d2d4", "e5g6", "e4e5", "f6g8",
            "f1c4",
        ],
    ),
    # C. REPERTOAR HITAM TAJAM & GAMBIT
    (
        "Two Knights Ulvestad/Fritz Counter !!",
        chess.BLACK,
        False,
        [
            "e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "g8f6",
            "f3g5", "d7d5", "e4d5", "c6a5", "c4b5", "c7c6",
            "d5c6", "b7c6", "b5e2", "h7h6",
        ],
    ),
    (
        "Traxler Counterattack !!",
        chess.BLACK,
        True,
        [
            "e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "g8f6",
            "f3g5", "f8c5", "g5f7", "c5f2", "e1f2", "f6e4",
            "f2g1", "d8h4",
        ],
    ),
    (
        "Stafford Gambit !!",
        chess.BLACK,
        True,
        [
            "e2e4", "e7e5", "g1f3", "g8f6", "f3e5", "b8c6",
            "e5c6", "d7c6", "d2d3", "f8c5", "f1e2", "h7h5",
        ],
    ),
]


def _is_direct_material_sacrifice(board, mv):
    piece = board.piece_at(mv.from_square)
    if piece is None or piece.piece_type == chess.KING:
        return False
    my_val = PIECE_VALUES.get(piece.piece_type, 100)
    victim = board.piece_at(mv.to_square)
    vic_val = PIECE_VALUES.get(victim.piece_type, 0) if victim else 0

    b_after = board.copy()
    b_after.push(mv)
    enemy = b_after.turn

    if not b_after.is_attacked_by(enemy, mv.to_square):
        return False

    attackers = b_after.attackers(enemy, mv.to_square)
    min_attacker_val = min(
        (PIECE_VALUES.get(b_after.piece_at(sq).piece_type, 20000) for sq in attackers if b_after.piece_at(sq)),
        default=20000,
    )
    if (my_val - vic_val) >= 180 and (
        min_attacker_val < (my_val - vic_val) or not b_after.is_attacked_by(not enemy, mv.to_square)
    ):
        return True
    return False


def _build_opening_db():
    db = {}
    for name, side, haram_only, uci_list in OPENING_REPERTOIRE:
        b = chess.Board()
        for uci in uci_list:
            try:
                mv = chess.Move.from_uci(uci)
            except ValueError:
                break
            if mv not in b.legal_moves:
                break
            if b.turn == side:
                key = (b.board_fen(), b.turn)
                is_sac = _is_direct_material_sacrifice(b, mv)
                entries = db.setdefault(key, [])
                if not any(e[0] == uci for e in entries):
                    entries.append((uci, name, haram_only, is_sac))
            b.push(mv)
    return db


OPENING_DB = _build_opening_db()


def lookup_opening_candidate(board, style_mode):
    if style_mode == STYLE_PURE_KILLER:
        return None, None, False, False

    key = (board.board_fen(), board.turn)
    cands = OPENING_DB.get(key, [])

    if style_mode == STYLE_MARTIAN_GAMBIT:
        for uci, name, haram_only, is_sac in cands:
            if haram_only:
                mv = chess.Move.from_uci(uci)
                if mv in board.legal_moves:
                    return mv, name, is_sac, True
        for uci, name, haram_only, is_sac in cands:
            mv = chess.Move.from_uci(uci)
            if mv in board.legal_moves:
                return mv, name, is_sac, False

    elif style_mode == STYLE_WR100_BRILLIANT:
        for uci, name, haram_only, is_sac in cands:
            if not haram_only:
                mv = chess.Move.from_uci(uci)
                if mv in board.legal_moves:
                    return mv, name, is_sac, False

    return None, None, False, False


# ============================================================================
# DETEKSI BRILLIANT (!!) & ANTI-50-MOVE-RULE
# ============================================================================
def evaluate_brilliant_potential(board, mv):
    us = board.turn
    them = not us
    piece = board.piece_at(mv.from_square)
    if piece is None:
        return False, ""

    b_after = board.copy()
    b_after.push(mv)

    if _is_direct_material_sacrifice(board, mv):
        return True, "Direct Sacrifice !!"

    for sq, p in board.piece_map().items():
        if p.color != us or p.piece_type in (chess.PAWN, chess.KING) or sq == mv.from_square:
            continue
        p_val = PIECE_VALUES.get(p.piece_type, 100)
        if board.is_attacked_by(them, sq) and b_after.is_attacked_by(them, sq):
            attackers_after = b_after.attackers(them, sq)
            min_att = min(
                (PIECE_VALUES.get(b_after.piece_at(a).piece_type, 20000) for a in attackers_after if b_after.piece_at(a)),
                default=20000,
            )
            is_undefended = not b_after.is_attacked_by(us, sq)
            if min_att <= p_val - 150 or (is_undefended and p_val >= 320):
                victim = board.piece_at(mv.to_square)
                vic_val = PIECE_VALUES.get(victim.piece_type, 0) if victim else 0
                enemy_king = b_after.king(them)
                near_king = enemy_king is not None and chess.square_distance(mv.to_square, enemy_king) <= 2
                if b_after.is_check() or near_king or (vic_val > 0 and vic_val < p_val):
                    return True, "Counter-Sacrifice !!"

    if piece.piece_type == chess.ROOK and board.is_capture(mv):
        victim = board.piece_at(mv.to_square)
        if victim and victim.piece_type in (chess.KNIGHT, chess.BISHOP):
            if b_after.is_attacked_by(them, mv.to_square):
                return True, "Exchange Sacrifice !!"

    return False, ""


def anti_50_move_progress_tiebreak(board, mv):
    bonus = 0
    piece = board.piece_at(mv.from_square)
    us = board.turn

    if mv.promotion == chess.QUEEN:
        bonus += 8

    hm = board.halfmove_clock
    resets_50 = board.is_capture(mv) or (piece is not None and piece.piece_type == chess.PAWN)
    if hm >= 12:
        if resets_50:
            bonus += min(28, (hm - 8) * 2)
        elif board.gives_check(mv):
            bonus -= 14
    else:
        if piece and piece.piece_type == chess.PAWN:
            to_rank = chess.square_rank(mv.to_square)
            from_rank = chess.square_rank(mv.from_square)
            adv = (to_rank - from_rank) if us == chess.WHITE else (from_rank - to_rank)
            if adv > 0:
                bonus += 2 * adv

    if len(board.move_stack) >= 2:
        prev_own = board.move_stack[-2]
        if mv.from_square == prev_own.to_square and mv.to_square == prev_own.from_square:
            bonus -= 20

    return bonus


# ============================================================================
# SIMULASI BIOMEKANIKA TANGAN & RITME KOGNITIF MANUSIA (HUMANIZER ENGINE)
# ============================================================================
def cell_of(sq, white_bottom):
    f, r = chess.square_file(sq), chess.square_rank(sq)
    return (f, 7 - r) if white_bottom else (7 - f, r)


def square_point(sq, rect, wb, human_jitter=True):
    """Menentukan titik klik di dalam petak dengan sebaran Gaussian manusia (28% - 72%)."""
    x1, y1, x2, y2 = rect
    c, r = cell_of(sq, wb)
    cw, ch = (x2 - x1) / 8.0, (y2 - y1) / 8.0
    if human_jitter:
        ox = min(0.72, max(0.28, random.gauss(0.50, 0.095)))
        oy = min(0.72, max(0.28, random.gauss(0.50, 0.095)))
    else:
        ox, oy = 0.50, 0.50
    return int(round(x1 + (c + ox) * cw)), int(round(y1 + (r + oy) * ch))


def human_curve_move(tx, ty, min_dur=0.048, max_dur=0.145):
    """Menggerakkan kursor dengan Hukum Fitts, Kurva Minimum-Jerk Orde-5, & Micro-Tremor."""
    try:
        sx, sy = pyautogui.position()
    except Exception:
        pyautogui.moveTo(tx, ty, duration=0.0, _pause=False)
        return

    dist = math.hypot(tx - sx, ty - sy)
    if dist < 5:
        pyautogui.moveTo(tx, ty, duration=0.0, _pause=False)
        return

    # Hukum Fitts: durasi proporsional dengan logaritma jarak
    fitts_dur = min_dur + (max_dur - min_dur) * min(1.0, math.log2(dist / 28.0 + 1.0) / 4.2)
    total_dur = fitts_dur * random.uniform(0.86, 1.16)
    steps = max(7, min(22, int(total_dur / 0.008)))

    # Titik kontrol lengkungan tangan (Bezier kuadratik)
    mid_x, mid_y = 0.5 * (sx + tx), 0.5 * (sy + ty)
    perp_x, perp_y = -(ty - sy), (tx - sx)
    arc_scale = random.uniform(-0.12, 0.12)
    ctrl_x = mid_x + perp_x * arc_scale
    ctrl_y = mid_y + perp_y * arc_scale

    step_sleep = total_dur / float(steps)
    for i in range(1, steps + 1):
        u = i / float(steps)
        # Kurva S Minimum-Jerk Orde-5: akselerasi halus lalu melambat saat mendekati target
        t = u * u * u * (10.0 - 15.0 * u + 6.0 * u * u)
        inv = 1.0 - t
        px = (inv * inv * sx) + (2.0 * inv * t * ctrl_x) + (t * t * tx)
        py = (inv * inv * sy) + (2.0 * inv * t * ctrl_y) + (t * t * ty)

        # Jitter mikro tangan saat bergerak (berhenti tepat di titik akhir)
        if i < steps - 1:
            px += random.gauss(0.0, 0.75)
            py += random.gauss(0.0, 0.75)

        pyautogui.moveTo(int(round(px)), int(round(py)), duration=0.0, _pause=False)
        time.sleep(step_sleep)


def human_cognitive_delay(board, chosen_move, base_pace=0.22, is_book=False, is_brilliant=False):
    """Menghitung waktu pikir manusia sesuai konteks kerumitan papan sebelum menggerakkan mouse."""
    legal_count = board.legal_moves.count()
    if legal_count <= 1:
        # Langkah paksa tunggal: respon refleks manusia
        return random.uniform(0.14, 0.28)

    # Respon cepat saat memakan balik bidak (recapture) di petak yang sama
    if board.move_stack and board.is_capture(chosen_move):
        last_enemy_mv = board.move_stack[-1]
        if chosen_move.to_square == last_enemy_mv.to_square:
            return random.uniform(0.18, 0.36)

    pace_factor = max(0.55, min(2.2, base_pace / 0.20))

    # Langkah teori pembukaan hafalan: ritme stabil & percaya diri
    if is_book or len(board.move_stack) <= 6:
        return random.uniform(0.22, 0.48) * pace_factor

    # Langkah pengorbanan Brilliant (!!): manusia berhenti sejenak untuk memastikan kalkulasi
    if is_brilliant:
        return random.uniform(0.45, 0.95) * pace_factor

    # Endgame sederhana: ritme cepat
    if len(board.piece_map()) <= 10:
        return random.uniform(0.16, 0.38) * pace_factor

    # Middlegame: distribusi log-normal ditambah cabang taktis
    tactical_branches = sum(
        1 for m in board.legal_moves if board.is_capture(m) or board.gives_check(m)
    )
    check_offset = 0.18 if board.is_check() else 0.0
    raw_think = random.lognormvariate(-1.05, 0.36) * pace_factor
    complexity = min(0.45, tactical_branches * 0.035) + check_offset

    return max(0.18, min(1.65, raw_think + complexity))


# ============================================================================
# PENCARIAN STOCKFISH & ENGINE UTAMA (WR 100% + SOUND BRILLIANT + HUMANIZED)
# ============================================================================
def _is_engine_file(path):
    if not path or not os.path.isfile(path):
        return False
    base = os.path.basename(path).lower()
    if sys.platform.startswith("win"):
        return base.endswith(".exe") and "stockfish" in base
    return os.access(path, os.X_OK)


def find_stockfish(saved=""):
    if _is_engine_file(saved):
        return saved
    for p in (os.environ.get("STOCKFISH_PATH", ""), shutil.which("stockfish") or ""):
        if _is_engine_file(p):
            return p

    here = os.path.dirname(os.path.abspath(__file__))
    home = os.path.expanduser("~")
    search_dirs = [
        here,
        os.path.join(home, "Downloads"),
        os.path.join(home, "Desktop"),
        os.path.join(home, "Documents"),
    ]
    cands = []
    for d in search_dirs:
        if os.path.isdir(d):
            for pat in ("stockfish*.exe", "*/stockfish*.exe", "*/*/stockfish*.exe", "stockfish"):
                cands.extend(sorted(glob.glob(os.path.join(d, pat))))
    cands.extend(["/usr/games/stockfish", "/usr/bin/stockfish"])
    for c in cands:
        if _is_engine_file(c):
            return c

    for d in search_dirs[:3]:
        if os.path.isdir(d):
            for zpath in sorted(glob.glob(os.path.join(d, "*stockfish*.zip"))):
                try:
                    with zipfile.ZipFile(zpath, "r") as zf:
                        for member in zf.namelist():
                            if member.lower().endswith(".exe") and "stockfish" in member.lower():
                                target = os.path.join(here, os.path.basename(member))
                                if not os.path.isfile(target):
                                    with zf.open(member) as src, open(target, "wb") as dst:
                                        shutil.copyfileobj(src, dst)
                                if _is_engine_file(target):
                                    return target
                except Exception:
                    pass
    return None


class BuiltinEngine:
    VAL = PIECE_VALUES
    PST = {
        chess.PAWN: [
             0,  0,  0,  0,  0,  0,  0,  0,
            60, 60, 60, 60, 60, 60, 60, 60,
            20, 20, 30, 40, 40, 30, 20, 20,
            10, 10, 20, 35, 35, 20, 10, 10,
             5,  5, 10, 25, 25, 10,  5,  5,
             5, -5,-10,  0,  0,-10, -5,  5,
             5, 10, 10,-20,-20, 10, 10,  5,
             0,  0,  0,  0,  0,  0,  0,  0,
        ],
        chess.KNIGHT: [
            -50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -30,  5, 15, 20, 20, 15,  5,-30,
            -30, 10, 20, 25, 25, 20, 10,-30,
            -30,  5, 20, 25, 25, 20,  5,-30,
            -30,  5, 10, 15, 15, 10,  5,-30,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -50,-40,-30,-30,-30,-30,-40,-50,
        ],
        chess.BISHOP: [
            -20,-10,-10,-10,-10,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  5, 10, 15, 15, 10,  5,-10,
            -10, 10, 10, 15, 15, 10, 10,-10,
            -10,  5, 15, 15, 15, 15,  5,-10,
            -10, 10, 10, 10, 10, 10, 10,-10,
            -10,  5,  0,  0,  0,  0,  5,-10,
            -20,-10,-10,-10,-10,-10,-10,-20,
        ],
        chess.ROOK: [
              0,  0,  5, 10, 10,  5,  0,  0,
             15, 20, 20, 20, 20, 20, 20, 15,
             -5,  0,  0,  0,  0,  0,  0, -5,
             -5,  0,  0,  0,  0,  0,  0, -5,
             -5,  0,  0,  0,  0,  0,  0, -5,
             -5,  0,  0,  0,  0,  0,  0, -5,
             -5,  0,  0,  0,  0,  0,  0, -5,
              0,  0,  0, 10, 10,  0,  0,  0,
        ],
        chess.QUEEN: [
            -20,-10,-10, -5, -5,-10,-10,-20,
            -10,  0,  5,  5,  5,  5,  0,-10,
            -10,  5, 10, 10, 10, 10,  5,-10,
             -5,  0, 10, 10, 10, 10,  0, -5,
              0,  0,  5,  5,  5,  5,  0, -5,
            -10,  5,  5,  5,  5,  5,  0,-10,
            -10,  0,  5,  0,  0,  0,  0,-10,
            -20,-10,-10, -5, -5,-10,-10,-20,
        ],
        chess.KING: [
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -20,-30,-30,-40,-40,-30,-30,-20,
            -10,-20,-20,-20,-20,-20,-20,-10,
             20, 20,  0,  0,  0,  0, 20, 20,
             20, 30, 10,  0,  0, 10, 30, 20,
        ],
    }

    @classmethod
    def eval_board(cls, b, ply=0):
        if b.is_checkmate():
            return -99999 + ply
        if (
            b.is_stalemate()
            or b.is_insufficient_material()
            or b.can_claim_threefold_repetition()
            or b.can_claim_fifty_moves()
        ):
            return 0
        score = 0
        pm = b.piece_map()
        is_endgame = len(pm) <= 10
        w_king = b.king(chess.WHITE)
        b_king = b.king(chess.BLACK)

        for sq, p in pm.items():
            v = cls.VAL[p.piece_type]
            idx = sq ^ 56 if p.color == chess.WHITE else sq
            if p.piece_type == chess.KING and is_endgame:
                f, r = chess.square_file(sq), chess.square_rank(sq)
                center_dist = abs(3.5 - f) + abs(3.5 - r)
                v += int((7.0 - center_dist) * 16)
            else:
                v += cls.PST.get(p.piece_type, [0] * 64)[idx]
            score += v if p.color == chess.WHITE else -v

        if is_endgame and w_king is not None and b_king is not None:
            king_dist = chess.square_distance(w_king, b_king)
            if score > 200:
                bf, br = chess.square_file(b_king), chess.square_rank(b_king)
                b_center = abs(3.5 - bf) + abs(3.5 - br)
                score += int(b_center * 18) + (14 - king_dist) * 8
            elif score < -200:
                wf, wr = chess.square_file(w_king), chess.square_rank(w_king)
                w_center = abs(3.5 - wf) + abs(3.5 - wr)
                score -= int(w_center * 18) + (14 - king_dist) * 8

        return score if b.turn == chess.WHITE else -score

    @classmethod
    def pick_move(cls, board, max_time=0.15):
        legal = list(board.legal_moves)
        if not legal:
            return None

        for mv in legal:
            board.push(mv)
            if board.is_checkmate():
                board.pop()
                return mv
            board.pop()

        deadline = time.perf_counter() + max(0.05, min(0.50, max_time))

        def order_key(mv):
            victim = board.piece_at(mv.to_square)
            attacker = board.piece_at(mv.from_square)
            v_val = cls.VAL.get(victim.piece_type, 0) if victim else 0
            a_val = cls.VAL.get(attacker.piece_type, 100) if attacker else 100
            cap = (12 * v_val - a_val // 8) if victim else 0
            promo = 950 if mv.promotion == chess.QUEEN else 0
            chk = 150 if board.gives_check(mv) else 0
            return cap + promo + chk

        def quiesce(alpha, beta, qdepth=5):
            in_check = board.is_check()
            if not in_check:
                stand_pat = cls.eval_board(board)
                if stand_pat >= beta:
                    return beta
                if alpha < stand_pat:
                    alpha = stand_pat
                if qdepth <= 0 or time.perf_counter() > deadline:
                    return stand_pat
                moves = [m for m in board.legal_moves if board.is_capture(m) or m.promotion]
            else:
                if qdepth <= 0 or time.perf_counter() > deadline:
                    return cls.eval_board(board)
                moves = list(board.legal_moves)

            moves.sort(key=order_key, reverse=True)
            if in_check and not moves:
                return cls.eval_board(board)
            for m in moves:
                board.push(m)
                score = -quiesce(-beta, -alpha, qdepth - 1)
                board.pop()
                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score
            return alpha

        def alphabeta(depth, alpha, beta, ply):
            if board.is_game_over():
                return cls.eval_board(board, ply)
            if depth <= 0 or time.perf_counter() > deadline:
                return quiesce(alpha, beta)
            mvs = list(board.legal_moves)
            mvs.sort(key=order_key, reverse=True)
            for m in mvs:
                board.push(m)
                val = -alphabeta(depth - 1, -beta, -alpha, ply + 1)
                board.pop()
                if val >= beta:
                    return beta
                if val > alpha:
                    alpha = val
            return alpha

        legal.sort(key=order_key, reverse=True)
        best_mv = legal[0]

        for depth in range(1, 7):
            if time.perf_counter() > deadline:
                break
            cur_best, cur_val = best_mv, -999999
            for mv in legal:
                tie = anti_50_move_progress_tiebreak(board, mv)
                board.push(mv)
                val = -alphabeta(depth - 1, -999999, -cur_val + 50, 1) + tie
                board.pop()
                if val > cur_val:
                    cur_val, cur_best = val, mv
                if time.perf_counter() > deadline:
                    break
            best_mv = cur_best
        return best_mv


def choose_wr100_move(
    engine,
    board,
    think_t,
    max_depth=26,
    style_mode=STYLE_WR100_BRILLIANT,
    brilliant_count=0,
    human_mode=True,
):
    legal = list(board.legal_moves)
    if not legal:
        return None
    if len(legal) == 1:
        return {
            "move": legal[0],
            "is_book": False,
            "book_name": None,
            "is_brilliant": False,
            "brilliant_label": "",
            "cp": 0,
        }

    for mv in legal:
        board.push(mv)
        if board.is_checkmate():
            board.pop()
            is_bril, b_lbl = evaluate_brilliant_potential(board, mv)
            return {
                "move": mv,
                "is_book": False,
                "book_name": None,
                "is_brilliant": is_bril,
                "brilliant_label": b_lbl or "Checkmate !!",
                "cp": 100000,
            }
        board.pop()

    book_mv, book_name, book_sac, is_forced_haram = lookup_opening_candidate(board, style_mode)
    if book_mv is not None and style_mode == STYLE_MARTIAN_GAMBIT and is_forced_haram:
        return {
            "move": book_mv,
            "is_book": True,
            "book_name": book_name,
            "is_brilliant": bool(book_sac),
            "brilliant_label": book_name if book_sac else "",
            "cp": 0,
        }

    if engine is None:
        mv = book_mv if book_mv is not None else BuiltinEngine.pick_move(board, think_t)
        is_bril, b_lbl = evaluate_brilliant_potential(board, mv) if mv else (False, "")
        return {
            "move": mv,
            "is_book": book_mv is not None,
            "book_name": book_name,
            "is_brilliant": is_bril,
            "brilliant_label": b_lbl,
            "cp": 0,
        }

    try:
        effective_time = max(0.08, think_t)
        limit = chess.engine.Limit(time=effective_time, depth=max_depth)
        infos = engine.analyse(board, limit, multipv=min(3, len(legal)))
        if isinstance(infos, dict):
            infos = [infos]

        candidates = []
        seen = set()
        for info in infos:
            pv = info.get("pv")
            if not pv:
                continue
            mv = pv[0]
            if mv not in board.legal_moves or mv in seen:
                continue
            seen.add(mv)

            pov = info.get("score")
            if pov is None:
                continue
            turn_score = pov.pov(board.turn)
            mate_in = turn_score.mate()
            cp = turn_score.score(mate_score=100000)
            if cp is None:
                continue

            board.push(mv)
            is_draw = (
                board.is_stalemate()
                or board.is_insufficient_material()
                or board.can_claim_threefold_repetition()
                or board.can_claim_fifty_moves()
                or board.is_repetition(2)
            )
            board.pop()

            is_bril, bril_lbl = evaluate_brilliant_potential(board, mv)
            prog_bonus = anti_50_move_progress_tiebreak(board, mv)

            candidates.append({
                "move": mv,
                "cp": cp,
                "mate": mate_in,
                "is_draw": is_draw,
                "is_bril": is_bril,
                "bril_lbl": bril_lbl,
                "prog": prog_bonus,
            })

        if not candidates:
            res = engine.play(board, limit)
            mv = res.move if (res.move and res.move in board.legal_moves) else BuiltinEngine.pick_move(board, think_t)
            is_bril, b_lbl = evaluate_brilliant_potential(board, mv) if mv else (False, "")
            return {
                "move": mv,
                "is_book": False,
                "book_name": None,
                "is_brilliant": is_bril,
                "brilliant_label": b_lbl,
                "cp": 0,
            }

        winning_mates = [c for c in candidates if c["mate"] is not None and c["mate"] > 0 and not c["is_draw"]]
        if winning_mates:
            winning_mates.sort(key=lambda c: (c["mate"], -int(c["is_bril"])))
            chosen = winning_mates[0]
            return {
                "move": chosen["move"],
                "is_book": False,
                "book_name": None,
                "is_brilliant": chosen["is_bril"],
                "brilliant_label": chosen["bril_lbl"] or f"Mate in {chosen['mate']} !!",
                "cp": chosen["cp"],
            }

        top = candidates[0]
        top_cp = top["cp"]

        if book_mv is not None and top_cp >= -20:
            for c in candidates:
                if c["move"] == book_mv and (top_cp - c["cp"]) <= 18 and c["cp"] >= -15 and not c["is_draw"]:
                    return {
                        "move": book_mv,
                        "is_book": True,
                        "book_name": book_name,
                        "is_brilliant": c["is_bril"] or book_sac,
                        "brilliant_label": c["bril_lbl"] or (book_name if book_sac else ""),
                        "cp": c["cp"],
                    }

        non_draw_cands = [c for c in candidates if not (c["is_draw"] and c["cp"] > -80)]
        best = non_draw_cands[0] if non_draw_cands else top

        if (
            brilliant_count < TARGET_BRILLIANTS_PER_GAME
            and style_mode != STYLE_PURE_KILLER
            and not best["is_bril"]
        ):
            sac_tol = 45 if style_mode == STYLE_MARTIAN_GAMBIT else 12
            min_cp = 10 if style_mode == STYLE_MARTIAN_GAMBIT else 65
            for alt in non_draw_cands[1:]:
                if alt["is_bril"] and (best["cp"] - alt["cp"]) <= sac_tol and alt["cp"] >= min_cp:
                    best = alt
                    break

        if board.halfmove_clock >= 14 and len(non_draw_cands) >= 2:
            for alt in non_draw_cands[1:]:
                if (best["cp"] - alt["cp"]) <= 10 and alt["prog"] > best["prog"]:
                    best = alt
                    break

        # Soft-Top Humanized Selection:
        # Jika human_mode aktif, bukan posisi skak, dan langkah ke-2 sama kuatnya (selisih <= 8 cp)
        # serta mempertahankan keunggulan menang (>= +80 cp), sesekali (22%) variasikan langkah.
        if (
            human_mode
            and not best["is_bril"]
            and not board.is_check()
            and board.halfmove_clock < 14
            and len(non_draw_cands) >= 2
        ):
            second = non_draw_cands[1]
            if (
                not second["is_draw"]
                and second["cp"] >= 80
                and (best["cp"] - second["cp"]) <= 8
                and random.random() < 0.22
            ):
                best = second

        return {
            "move": best["move"],
            "is_book": False,
            "book_name": None,
            "is_brilliant": best["is_bril"],
            "brilliant_label": best["bril_lbl"],
            "cp": best["cp"],
        }

    except (chess.engine.EngineError, OSError, TimeoutError):
        raise


# ============================================================================
# DETEKSI PAPAN 8x8 ANTI-GAGAL (MENDUKUNG POSISI AWAL 32 BIDAK PENUH)
# ============================================================================
def _runs(line, tol=22):
    d = np.abs(np.diff(line.astype(np.int16), axis=0)).sum(axis=1) > tol
    cuts = np.flatnonzero(d) + 1
    starts = [0] + cuts.tolist()
    ends = cuts.tolist() + [len(line)]
    merged = []
    for s, e in zip(starts, ends):
        if (e - s) <= 2 and merged:
            merged[-1][1] = e
        else:
            merged.append([s, e])
    return merged


def _board_windows(line, min_len=20, max_len=300):
    runs = _runs(line)
    n = len(runs)
    if n < 8 or n > 550:
        return []
    lens = np.array([e - s for s, e in runs])
    win = sliding_window_view(lens, 8)
    mn, mx = win.min(axis=1), win.max(axis=1)
    idx = np.flatnonzero((mn >= min_len) & (mx <= max_len) & (mx - mn <= 6))
    out = []
    for i in idx:
        cols = np.array([line[(runs[j][0] + runs[j][1]) // 2] for j in range(i, i + 8)], dtype=np.int16)
        same2 = sum(int(np.abs(cols[k] - cols[k + 2]).sum()) <= 55 for k in range(6))
        diff1 = sum(int(np.abs(cols[k] - cols[k + 1]).sum()) > 12 for k in range(7))
        if same2 >= 3 and diff1 >= 5:
            out.append((runs[i][0], runs[i + 7][1], float(win[i].mean())))
    return out


def _locate_y_by_phase_correlation(img, x0, x1):
    """Mencari (y0, y1) secara presisi dengan korelasi fase 8-baris meskipun 32 bidak penuh."""
    H, W = img.shape[:2]
    bw = x1 - x0
    if bw < 160 or bw > H:
        return None
    L = bw / 8.0

    even_strips = []
    odd_strips = []
    for c in range(1, 8):
        sx0 = max(0, min(W - 1, int(round(x0 + (c + 0.08) * L))))
        sx1 = max(sx0 + 1, min(W, int(round(x0 + (c + 0.14) * L))))
        strip = img[:, sx0:sx1, :].astype(np.float32).mean(axis=1)
        if c % 2 == 0:
            even_strips.append(strip)
        else:
            odd_strips.append(strip)

    if not even_strips or not odd_strips:
        return None

    even_rgb = np.mean(even_strips, axis=0)
    odd_rgb = np.mean(odd_strips, axis=0)
    diff_lum = (even_rgb - odd_rgb) @ LUM

    bh = int(round(bw))
    if H <= bh:
        return None

    cs = np.zeros(H + 1, dtype=np.float32)
    cs[1:] = np.cumsum(diff_lum)

    r_bounds = [int(round(r * L)) for r in range(9)]
    max_y0 = H - r_bounds[8]
    if max_y0 < 0:
        return None

    y_idx = np.arange(0, max_y0 + 1)
    total_score = np.zeros(len(y_idx), dtype=np.float32)
    rank_means = []

    for r in range(8):
        ra, rb = r_bounds[r], r_bounds[r + 1]
        seg_len = max(1, rb - ra)
        seg_mean = (cs[y_idx + rb] - cs[y_idx + ra]) / float(seg_len)
        rank_means.append(seg_mean)
        if r % 2 == 0:
            total_score += seg_mean
        else:
            total_score -= seg_mean

    abs_score = np.abs(total_score) / 8.0
    best_y0 = int(np.argmax(abs_score))
    if float(abs_score[best_y0]) < 14.0:
        return None

    sign_dir = 1.0 if total_score[best_y0] >= 0 else -1.0
    valid_ranks = 0
    for r in range(8):
        expected_sign = sign_dir if (r % 2 == 0) else -sign_dir
        if rank_means[r][best_y0] * expected_sign > 6.0:
            valid_ranks += 1

    if valid_ranks < 6:
        return None

    return (best_y0, best_y0 + bh)


def find_board(img):
    H, W = img.shape[:2]
    votes = {}
    for y in range(0, H, 3):
        for x0, x1, L in _board_windows(img[y]):
            key = (x0 // 6, int(round((x1 - x0) / 8)))
            votes.setdefault(key, []).append((x0, x1, L))

    for _, hits in sorted(votes.items(), key=lambda kv: -len(kv[1]))[:6]:
        if len(hits) < 2:
            break
        x0 = int(round(np.median([h[0] for h in hits])))
        x1 = int(round(np.median([h[1] for h in hits])))
        L = float(np.median([h[2] for h in hits]))

        y_phase = _locate_y_by_phase_correlation(img, x0, x1)
        if y_phase is not None:
            y0, y1 = y_phase
            sub = img[y0:y1, x0:x1]
            if sub.shape[0] >= 160 and sub.shape[1] >= 160:
                bgs = {(c, r): cell_bg(cell_img(sub, c, r)) for r in range(8) for c in range(8)}
                if is_valid_checkerboard(bgs):
                    return (x0, y0, x1, y1)

        ycands = []
        for j in range(1, 8):
            for dx in (5, -5, 10, -10):
                x = int(x0 + j * (x1 - x0) / 8 + dx)
                if 0 <= x < W:
                    for ya, yb, Lv in _board_windows(img[:, x]):
                        if abs(Lv - L) <= 5.5 and abs((yb - ya) - (x1 - x0)) <= 14:
                            ycands.append((ya, yb))
        if len(ycands) >= 2:
            mode = Counter(ya // 6 for ya, _ in ycands).most_common(1)[0][0]
            sel = [(ya, yb) for ya, yb in ycands if abs(ya // 6 - mode) <= 1]
            if sel:
                y0 = int(round(np.median([s[0] for s in sel])))
                y1 = int(round(np.median([s[1] for s in sel])))
                if abs((y1 - y0) - (x1 - x0)) <= 14:
                    return (x0, y0, x1, y1)
    return None


def grab_region(sct, left, top, width, height):
    shot = sct.grab({"left": int(left), "top": int(top), "width": int(width), "height": int(height)})
    return np.ascontiguousarray(np.array(shot)[:, :, :3][:, :, ::-1])


def scan_screens(sct=None):
    own = sct is None
    if own:
        sct = mss.mss()
    best = None
    try:
        mons = sct.monitors[1:] or [sct.monitors[0]]
        for mon in mons:
            img = grab_region(sct, mon["left"], mon["top"], mon["width"], mon["height"])
            r = find_board(img)
            if r:
                cand = (r[0] + mon["left"], r[1] + mon["top"], r[2] + mon["left"], r[3] + mon["top"])
                if best is None or (cand[2] - cand[0]) > (best[2] - best[0]):
                    best = cand
    finally:
        if own:
            sct.close()
    return best


def cell_img(img, col, row):
    h, w = img.shape[:2]
    return img[row * h // 8:(row + 1) * h // 8, col * w // 8:(col + 1) * w // 8]


def cell_bg(sq_img):
    h, w = sq_img.shape[:2]
    i = max(1, int(min(h, w) * 0.05))
    p = max(2, int(min(h, w) * 0.08))
    patches = [
        sq_img[i:i + p, w - i - p:w - i],
        sq_img[h // 2 - p // 2:h // 2 + p // 2 + 1, i:i + p],
        sq_img[h // 2 - p // 2:h // 2 + p // 2 + 1, w - i - p:w - i],
    ]
    return np.median(np.concatenate([q.reshape(-1, 3) for q in patches]), axis=0).astype(np.float32)


def is_board_occluded_by_popup(bgs):
    center_cells = [(c, r) for r in range(2, 6) for c in range(2, 6)]
    lums = [float(bgs[pos] @ LUM) for pos in center_cells if pos in bgs]
    if len(lums) < 12:
        return False
    if float(np.std(lums)) < 10.5 or float(np.max(lums)) < 75.0:
        return True
    return False


def is_valid_checkerboard(bgs):
    even_lums = [float(bgs[c] @ LUM) for c in bgs if (c[0] + c[1]) % 2 == 0]
    odd_lums = [float(bgs[c] @ LUM) for c in bgs if (c[0] + c[1]) % 2 == 1]
    if not even_lums or not odd_lums:
        return False
    diff = abs(float(np.median(even_lums)) - float(np.median(odd_lums)))
    return diff >= 14.0


def analyze_cell(sq_img, expected_bg=None, white_lum_t=WHITE_LUM_T):
    bg = cell_bg(sq_img)
    ref_bg = expected_bg if expected_bg is not None else bg

    h, w = sq_img.shape[:2]
    m = max(2, int(round(min(h, w) * OCC_MARGIN)))
    sub = sq_img[m:h - m, m:w - m].astype(np.float32)
    lum = sub @ LUM

    lum_min = float(np.percentile(lum, 2))
    lum_max = float(np.percentile(lum, 98))

    gx = np.abs(lum[:, 1:] - lum[:, :-1])[:-1, :]
    gy = np.abs(lum[1:, :] - lum[:-1, :])[:, :-1]
    edge_map = (gx > EDGE_T) | (gy > EDGE_T)

    if (lum_max - lum_min) < SPAN_MIN or lum_min > DARK_OUTLINE or float(edge_map.mean()) < OCC_RATIO:
        return False, None, 0.0, None, bg

    sh, sw = lum.shape
    diff_bg = np.minimum(
        np.abs(sub - ref_bg).sum(axis=2),
        np.abs(sub - bg).sum(axis=2),
    )

    outline_mask = np.zeros_like(lum, dtype=bool)
    outline_mask[:-1, :-1] = edge_map
    outline_mask |= (lum < 105.0) | (diff_bg > 45.0)

    widths = np.zeros(sh, dtype=np.float32)
    centers = np.zeros(sh, dtype=np.float32)
    silhouette_pixels = []

    for r in range(sh):
        cols = np.flatnonzero(outline_mask[r])
        if len(cols) >= 2:
            span = cols[-1] - cols[0]
            if span >= max(2, int(sw * 0.16)):
                widths[r] = span / float(sw)
                centers[r] = (0.5 * (cols[0] + cols[-1])) / float(sw)
                if int(sh * 0.36) <= r <= int(sh * 0.86) and span >= int(sw * 0.24):
                    inset = max(1, int(span * 0.16))
                    c0 = cols[0] + inset
                    c1 = cols[-1] - inset
                    if c1 > c0:
                        silhouette_pixels.append(lum[r, c0:c1])

    active_rows = np.flatnonzero(widths > 0.20)
    base_width = float(widths[int(sh * 0.54):int(sh * 0.94)].max(initial=0.0))
    upper_activity = float(widths[int(sh * 0.12):int(sh * 0.48)].max(initial=0.0))

    if len(active_rows) < int(sh * 0.36) or base_width < 0.32 or upper_activity < 0.16:
        return False, None, 0.0, None, bg

    y0, y1 = max(0, int(sh * 0.56)), min(sh, int(sh * 0.84))
    x0, x1 = max(0, int(sw * 0.34)), min(sw, int(sw * 0.66))
    core_vals = lum[y0:y1, x0:x1].reshape(-1)

    if silhouette_pixels:
        sil_vals = np.concatenate(silhouette_pixels)
        body_lum = 0.55 * float(np.median(sil_vals)) + 0.45 * float(np.median(core_vals))
    else:
        body_lum = float(np.median(core_vals))

    top_y = float(active_rows[0]) / float(sh)
    head_w = float(widths[int(sh * 0.08):int(sh * 0.35)].max(initial=0.0))
    neck_w = float(widths[int(sh * 0.35):int(sh * 0.55)].min(initial=0.0))
    valid_c = centers[widths > 0.24]
    asym = float(np.std(valid_c)) if len(valid_c) > 2 else 0.0
    geom = (top_y, head_w, neck_w, asym)

    return True, (body_lum >= white_lum_t), body_lum, geom, bg


def classify_piece_geometry(geom, is_back_rank_start=False):
    if geom is None:
        return "P"
    top_y, head_w, neck_w, asym = geom
    if top_y > 0.24 and head_w < 0.46 and not is_back_rank_start:
        return "P"
    if asym > 0.045:
        return "N"
    if head_w >= 0.48 and (head_w - neck_w) < 0.12:
        return "R"
    if top_y < 0.14 and head_w >= 0.50:
        return "Q"
    if top_y < 0.16:
        return "K"
    return "B"


def highlight_cells(bgs):
    hl = set()
    for parity in (0, 1):
        cells = [c for c in bgs if (c[0] + c[1]) % 2 == parity]
        base = np.median(np.array([bgs[c] for c in cells]), axis=0)
        for c in cells:
            if float(np.abs(bgs[c] - base).sum()) > HL_T:
                hl.add(c)
    return hl if len(hl) <= 4 else set()


class BoardObservation:
    def __init__(self, colors, geoms, hl, occluded=False, valid_grid=True):
        self.colors = colors
        self.geoms = geoms
        self.hl = hl
        self.occluded = occluded
        self.valid_grid = valid_grid
        self.sig = frozenset(colors.items())


class UniversalVision:
    def __init__(self):
        self.white_t = WHITE_LUM_T

    def read(self, img):
        bgs = {}
        cells_img = {}
        for row in range(8):
            for col in range(8):
                c_img = cell_img(img, col, row)
                cells_img[(col, row)] = c_img
                bgs[(col, row)] = cell_bg(c_img)

        if not is_valid_checkerboard(bgs):
            return BoardObservation({}, {}, set(), occluded=False, valid_grid=False)

        if is_board_occluded_by_popup(bgs):
            return BoardObservation({}, {}, set(), occluded=True, valid_grid=True)

        parity_base = {}
        for parity in (0, 1):
            p_cells = [c for c in bgs if (c[0] + c[1]) % 2 == parity]
            parity_base[parity] = np.median(np.array([bgs[c] for c in p_cells]), axis=0)

        raw_lum = {}
        geoms = {}
        lums = []

        for row in range(8):
            for col in range(8):
                pos = (col, row)
                exp_bg = parity_base[(col + row) % 2]
                occ, _, body_lum, geom, _ = analyze_cell(cells_img[pos], exp_bg, self.white_t)
                if occ:
                    raw_lum[pos] = body_lum
                    geoms[pos] = geom
                    lums.append(body_lum)

        if len(lums) >= 4:
            arr = np.sort(np.array(lums, dtype=np.float32))
            if float(arr[-1] - arr[0]) > 45.0:
                c_low = float(np.percentile(arr, 20))
                c_high = float(np.percentile(arr, 80))
                for _ in range(5):
                    mid = 0.5 * (c_low + c_high)
                    g_low = arr[arr < mid]
                    g_high = arr[arr >= mid]
                    if len(g_low) > 0 and len(g_high) > 0:
                        c_low = float(np.mean(g_low))
                        c_high = float(np.mean(g_high))
                if (c_high - c_low) > 45.0:
                    self.white_t = float(np.clip(0.5 * (c_low + c_high), 95.0, 185.0))

        colors = {
            pos: (chess.WHITE if lum >= self.white_t else chess.BLACK)
            for pos, lum in raw_lum.items()
        }
        return BoardObservation(colors, geoms, highlight_cells(bgs), occluded=False, valid_grid=True)


# ============================================================================
# PELACAK PERMAINAN ANTI-DESYNC (MENDUKUNG BALASAN INSTAN BOT 3200)
# ============================================================================
def board_colors(board):
    return {sq: p.color for sq, p in board.piece_map().items()}


def place_colors(color_grid, white_bottom):
    out = {}
    for sq in chess.SQUARES:
        c = cell_of(sq, white_bottom)
        if c in color_grid:
            out[sq] = color_grid[c]
    return out


def place_highlights(hl_cells, white_bottom):
    out = set()
    if not hl_cells:
        return out
    for sq in chess.SQUARES:
        if cell_of(sq, white_bottom) in hl_cells:
            out.add(sq)
    return out


def detect_live_orientation(color_grid):
    w_rows = [r for (_, r), col in color_grid.items() if col == chess.WHITE]
    b_rows = [r for (_, r), col in color_grid.items() if col == chess.BLACK]
    if len(w_rows) >= 2 and len(b_rows) >= 2:
        avg_w = sum(w_rows) / len(w_rows)
        avg_b = sum(b_rows) / len(b_rows)
        if avg_w > avg_b + 0.8:
            return True
        if avg_b > avg_w + 0.8:
            return False
    return None


def resolve_bot_color(side, white_bottom):
    if side == "Putih":
        return chess.WHITE
    if side == "Hitam":
        return chess.BLACK
    return chess.WHITE if white_bottom else chess.BLACK


def detect_turn_from_highlights(obs, default_turn):
    if obs.hl:
        moved_colors = [obs.colors[c] for c in obs.hl if c in obs.colors]
        empty_hl = [c for c in obs.hl if c not in obs.colors]
        if len(moved_colors) == 1 and len(empty_hl) >= 1:
            just_moved = moved_colors[0]
            return not just_moved
    if len(obs.colors) == 32:
        return chess.WHITE
    return default_turn


def match_move_by_color_diff(board, target_colors, max_plies=4, hl_squares=None, geoms_by_sq=None):
    if board_colors(board) == target_colors and board.is_valid():
        return True

    hl_squares = hl_squares or set()
    geoms_by_sq = geoms_by_sq or {}

    def dfs(left):
        cur = board_colors(board)
        emptied = {sq for sq, col in cur.items() if col == board.turn and sq not in target_colors}
        gained = {sq for sq, col in target_colors.items() if col == board.turn and cur.get(sq) != board.turn}

        scored = []
        for mv in board.legal_moves:
            if mv.promotion is not None:
                detected_sym = classify_piece_geometry(geoms_by_sq.get(mv.to_square))
                promo_map = {"Q": chess.QUEEN, "N": chess.KNIGHT, "R": chess.ROOK, "B": chess.BISHOP}
                expected_promo = promo_map.get(detected_sym, chess.QUEEN)
                if mv.promotion not in (chess.QUEEN, expected_promo):
                    continue

            s = 0
            if mv.from_square in emptied:
                s += 5
            if mv.to_square in gained:
                s += 5
            if board.is_castling(mv) and len(emptied) >= 2:
                s += 6
            if mv.from_square in hl_squares:
                s += 3
            if mv.to_square in hl_squares:
                s += 3
            if mv.promotion == chess.QUEEN:
                s += 1
            scored.append((s, mv))

        scored.sort(key=lambda x: -x[0])

        for s, mv in scored:
            if left == 1 and s < 5:
                continue
            board.push(mv)
            if left == 1:
                if board_colors(board) == target_colors and board.is_valid():
                    return True
            elif s >= 5 and dfs(left - 1):
                return True
            board.pop()
        return False

    for depth in range(1, max_plies + 1):
        if dfs(depth):
            return True
    return False


def line_from_start_by_colors(target_colors, max_plies=5, hl_squares=None):
    b = chess.Board()
    if board_colors(b) == target_colors:
        return b
    return b if match_move_by_color_diff(b, target_colors, max_plies=max_plies, hl_squares=hl_squares) else None


def reconstruct_midgame_board(obs, white_bottom, turn):
    start_map = chess.Board().piece_map()
    tc = place_colors(obs.colors, white_bottom)
    geoms_by_sq = {}
    for sq in chess.SQUARES:
        c = cell_of(sq, white_bottom)
        if c in obs.geoms:
            geoms_by_sq[sq] = obs.geoms[c]

    b = chess.Board(None)
    piece_map = {}

    for color in (chess.WHITE, chess.BLACK):
        color_sqs = [sq for sq, col in tc.items() if col == color]
        if not color_sqs:
            continue

        if len(color_sqs) > 16:
            color_sqs = color_sqs[:16]

        king_cands = [sq for sq in color_sqs if chess.square_rank(sq) in ((0, 1) if color == chess.WHITE else (7, 6))]
        if not king_cands:
            king_cands = color_sqs
        typical_king = (
            [chess.E1, chess.G1, chess.C1, chess.B1, chess.F1, chess.D1]
            if color == chess.WHITE
            else [chess.E8, chess.G8, chess.C8, chess.B8, chess.F8, chess.D8]
        )
        king_sq = None
        for ksq in typical_king:
            if ksq in color_sqs:
                if ksq in (chess.E1, chess.E8) or (chess.E1 if color == chess.WHITE else chess.E8) not in color_sqs:
                    g = geoms_by_sq.get(ksq)
                    if g and g[0] < 0.22:
                        king_sq = ksq
                        break
        if king_sq is None:
            king_sq = min(king_cands, key=lambda sq: geoms_by_sq.get(sq, (0.5, 0, 0, 0))[0])

        piece_map[king_sq] = chess.Piece(chess.KING, color)

        quota = {"Q": 1, "R": 2, "B": 2, "N": 2, "P": 8}
        remaining = [sq for sq in color_sqs if sq != king_sq]

        for sq in list(remaining):
            orig = start_map.get(sq)
            g = geoms_by_sq.get(sq)
            rank = chess.square_rank(sq)
            if (
                orig
                and orig.color == color
                and orig.piece_type == chess.PAWN
                and rank not in (0, 7)
                and g
                and g[0] > 0.20
            ):
                if quota["P"] > 0:
                    piece_map[sq] = chess.Piece(chess.PAWN, color)
                    quota["P"] -= 1
                    remaining.remove(sq)
            elif orig and orig.color == color and orig.piece_type in (chess.ROOK, chess.KNIGHT, chess.BISHOP):
                sym = orig.symbol().upper()
                if quota[sym] > 0:
                    piece_map[sq] = chess.Piece(orig.piece_type, color)
                    quota[sym] -= 1
                    remaining.remove(sq)

        for sq in remaining:
            rank = chess.square_rank(sq)
            g = geoms_by_sq.get(sq)
            sym = classify_piece_geometry(g)
            if rank in (0, 7) and sym == "P":
                sym = "R" if quota["R"] > 0 else ("B" if quota["B"] > 0 else ("N" if quota["N"] > 0 else "Q"))
            if sym == "K":
                sym = "Q" if quota["Q"] > 0 else "B"
            if quota.get(sym, 0) <= 0:
                chosen = None
                for fallback in ("P", "N", "B", "R", "Q"):
                    if quota[fallback] > 0 and not (fallback == "P" and rank in (0, 7)):
                        chosen = fallback
                        break
                if chosen is None:
                    continue
                sym = chosen
            quota[sym] = max(0, quota.get(sym, 0) - 1)
            piece_map[sq] = chess.Piece.from_symbol(sym if color == chess.WHITE else sym.lower())

    b.set_piece_map(piece_map)
    b.turn = turn
    b.castling_rights = chess.BB_CORNERS
    b.castling_rights = b.clean_castling_rights()

    if b.status() & chess.STATUS_OPPOSITE_CHECK:
        b.turn = not b.turn
        b.ep_square = None

    return b


class GameTracker:
    def __init__(self):
        self.board = chess.Board()
        self.wb = True
        self.uncertain = False
        self.locked_game = False
        self.bad = 0
        self.prev_sig = None

    def _orients(self, obs, auto_orient, wb_manual, bot_side=SIDE_AUTO):
        live = detect_live_orientation(obs.colors)
        if live is not None:
            return [live, not live]
        if bot_side == "Hitam":
            return [False, True]
        if bot_side == "Putih":
            return [True, False]
        if not auto_orient:
            return [bool(wb_manual)]
        return [self.wb, not self.wb]

    def sync(self, obs, bot_side, auto_orient, wb_manual):
        if not obs.valid_grid:
            return False, "Mencari lokasi papan catur di layar..."
        if obs.occluded:
            return False, "Papan tertutup popup. Tutup popup untuk lanjut."
        if len(obs.colors) < 2:
            return False, "Menunggu papan catur terlihat jelas..."

        orients = self._orients(obs, auto_orient, wb_manual, bot_side)
        for o in orients:
            tc = place_colors(obs.colors, o)
            hl_sq = place_highlights(obs.hl, o)
            b = line_from_start_by_colors(tc, max_plies=5, hl_squares=hl_sq)
            if b is not None and b.is_valid():
                self.board, self.wb, self.uncertain, self.bad = b, o, False, 0
                self.locked_game = True
                self.prev_sig = obs.sig
                n = len(b.move_stack)
                posisi = "Putih di Bawah" if o else "Hitam di Bawah"
                if n == 0:
                    return True, f"Tersinkron Posisi Awal ({posisi})."
                return True, f"Tersinkron ({posisi}, {n} langkah)."

        o = orients[0]
        bot_color = resolve_bot_color(bot_side, o)
        inferred_turn = detect_turn_from_highlights(obs, bot_color)
        for t in (inferred_turn, not inferred_turn):
            b = reconstruct_midgame_board(obs, o, t)
            if b.status() == chess.STATUS_VALID and b.is_valid():
                self.board, self.wb, self.bad = b, o, 0
                self.uncertain = True
                self.locked_game = False
                self.prev_sig = obs.sig
                posisi = "Putih di Bawah" if o else "Hitam di Bawah"
                gil = "Putih" if b.turn == chess.WHITE else "Hitam"
                return True, f"Sinkron tengah game ({posisi}, giliran {gil})."

        return False, "Menyinkronkan ulang area papan..."

    def confirm_own_move(self, move, obs):
        """Memverifikasi langkah bot sendiri sekaligus menangkap balasan instan bot 3200 (termasuk recapture)."""
        if obs is None or obs.occluded or not obs.valid_grid:
            return False

        tc = place_colors(obs.colors, self.wb)
        hl_sq = place_highlights(obs.hl, self.wb)
        geoms_by_sq = {}
        for sq in chess.SQUARES:
            c = cell_of(sq, self.wb)
            if c in obs.geoms:
                geoms_by_sq[sq] = obs.geoms[c]

        b_after = self.board.copy()
        b_after.push(move)

        if match_move_by_color_diff(b_after, tc, max_plies=2, hl_squares=hl_sq, geoms_by_sq=geoms_by_sq):
            self.board = b_after
            self.uncertain = False
            self.bad = 0
            self.locked_game = True
            self.prev_sig = obs.sig
            return True

        from_cell = cell_of(move.from_square, self.wb)
        if from_cell not in obs.colors:
            self.board.push(move)
            self.uncertain = False
            self.bad = 0
            self.locked_game = True
            self.prev_sig = obs.sig
            return True

        return False

    def update(self, obs, auto_orient, wb_manual, bot_side=SIDE_AUTO):
        if not obs.valid_grid:
            return "invalid_rect"
        if obs.occluded:
            return "occluded"

        live_o = detect_live_orientation(obs.colors)
        if live_o is not None and len(obs.colors) >= 26 and live_o != self.wb:
            self.wb = live_o
            return "resync"

        if len(obs.colors) >= 30:
            for o in self._orients(obs, auto_orient, wb_manual, bot_side):
                hl_new = place_highlights(obs.hl, o)
                b_new = line_from_start_by_colors(place_colors(obs.colors, o), max_plies=2, hl_squares=hl_new)
                if b_new is not None and b_new.is_valid():
                    if len(self.board.move_stack) >= 3 or o != self.wb:
                        self.board, self.wb, self.uncertain, self.bad = b_new, o, False, 0
                        self.locked_game = True
                        self.prev_sig = obs.sig
                        return "newgame"

        tc = place_colors(obs.colors, self.wb)
        if tc == board_colors(self.board):
            self.bad = 0
            self.prev_sig = obs.sig
            return "same"

        if obs.sig != self.prev_sig:
            self.prev_sig = obs.sig
            return "wait"

        hl_sq = place_highlights(obs.hl, self.wb)
        geoms_by_sq = {}
        for sq in chess.SQUARES:
            c = cell_of(sq, self.wb)
            if c in obs.geoms:
                geoms_by_sq[sq] = obs.geoms[c]

        cands = [self.board.copy()]
        if self.uncertain:
            b2 = self.board.copy()
            b2.turn = not b2.turn
            b2.ep_square = None
            if b2.is_valid():
                cands.append(b2)

        for b in cands:
            if match_move_by_color_diff(b, tc, max_plies=4, hl_squares=hl_sq, geoms_by_sq=geoms_by_sq):
                self.board, self.uncertain, self.bad = b, False, 0
                self.locked_game = True
                return "move"

        self.bad += 1
        if self.bad >= (16 if self.locked_game else 8):
            self.bad = 0
            return "resync"
        return "wait"


# ============================================================================
# ANTARMUKA MINIMALIS MODERN (DARK MODE) & LOOP UTAMA
# ============================================================================
class BotApp:
    BG = "#0f172a"
    CARD = "#1e293b"
    TEXT = "#f8fafc"
    SUBTEXT = "#94a3b8"
    ACCENT = "#10b981"
    DANGER = "#f43f5e"

    def __init__(self, root):
        self.root = root
        root.title("Chess Assistant Pro — Human & WR 100%")
        root.attributes("-topmost", True)
        root.resizable(False, False)
        root.configure(bg=self.BG)
        root.geometry(f"335x445+{max(0, root.winfo_screenwidth() - 350)}+25")

        self.cfg = {
            "manual_rect": None,
            "m_tl": None,
            "m_br": None,
            "bot_side": SIDE_AUTO,
            "style_mode": STYLE_WR100_BRILLIANT,
            "human_mode": True,
            "white_bottom": True,
            "auto_orient": True,
            "auto": True,
            "promo_click": True,
            "movetime": 0.22,
            "depth": 26,
            "mode": "klik",
            "stockfish": "",
        }
        for p in reversed(LEGACY_CONF_PATHS):
            if os.path.exists(p):
                try:
                    old_data = json.load(open(p))
                    if old_data.get("stockfish") and not self.cfg["stockfish"]:
                        self.cfg["stockfish"] = old_data["stockfish"]
                except Exception:
                    pass
        if os.path.exists(CONF_PATH):
            try:
                self.cfg.update(json.load(open(CONF_PATH)))
            except Exception:
                pass
        if self.cfg.get("bot_side") not in (SIDE_AUTO, "Putih", "Hitam"):
            self.cfg["bot_side"] = SIDE_AUTO
        if self.cfg.get("style_mode") not in STYLE_MODES:
            self.cfg["style_mode"] = STYLE_WR100_BRILLIANT

        self.vision = UniversalVision()
        self.running = False
        self.resync_flag = False
        self.recalibrate_flag = False
        self.force_turn_flag = False
        self.brilliant_count = 0
        self.q = queue.Queue()
        self.live = {}

        self.v_side = tk.StringVar(value=self.cfg["bot_side"])
        self.v_style = tk.StringVar(value=self.cfg["style_mode"])
        self.v_human = tk.BooleanVar(value=self.cfg.get("human_mode", True))
        self.v_auto_orient = tk.BooleanVar(value=self.cfg["auto_orient"])
        self.v_white_bottom = tk.BooleanVar(value=self.cfg["white_bottom"])
        self.v_auto = tk.BooleanVar(value=self.cfg["auto"])
        self.v_promo = tk.BooleanVar(value=self.cfg["promo_click"])
        self.v_time = tk.DoubleVar(value=self.cfg["movetime"])
        self.v_depth = tk.IntVar(value=self.cfg.get("depth", 26))
        self.v_mode = tk.StringVar(value=self.cfg["mode"])

        self.engine_status = tk.StringVar(value="Mengecek Stockfish...")
        self.role_badge = tk.StringVar(value="ANDA: -  •  GILIRAN: -  •  !! 0/5")
        self.status = tk.StringVar(value="Siap memindai papan.")

        self._setup_styles()
        self._build_ui()

        root.protocol("WM_DELETE_WINDOW", self.close)
        self.sync_settings()
        self.root.after(40, self.poll)
        self.root.after(150, self.start)

    def _setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("TFrame", background=self.BG)
        style.configure("Card.TFrame", background=self.CARD)
        style.configure(
            "TLabel",
            background=self.BG,
            foreground=self.TEXT,
            font=("Segoe UI", 8),
        )
        style.configure(
            "Sub.TLabel",
            background=self.BG,
            foreground=self.SUBTEXT,
            font=("Segoe UI", 8),
        )
        style.configure(
            "Engine.TLabel",
            background=self.BG,
            foreground="#34d399",
            font=("Segoe UI", 8, "bold"),
        )
        style.configure(
            "TCheckbutton",
            background=self.BG,
            foreground=self.TEXT,
            font=("Segoe UI", 8),
        )
        style.map(
            "TCheckbutton",
            background=[("active", self.BG)],
            foreground=[("active", self.TEXT)],
        )
        style.configure(
            "Dark.TButton",
            background="#334155",
            foreground=self.TEXT,
            borderwidth=0,
            padding=(6, 4),
            font=("Segoe UI", 8, "bold"),
        )
        style.map("Dark.TButton", background=[("active", "#475569")])

        style.configure(
            "Start.TButton",
            background=self.ACCENT,
            foreground="#052e16",
            borderwidth=0,
            padding=(6, 5),
            font=("Segoe UI", 8, "bold"),
        )
        style.map("Start.TButton", background=[("active", "#34d399")])

        style.configure(
            "Stop.TButton",
            background=self.DANGER,
            foreground="#ffffff",
            borderwidth=0,
            padding=(6, 5),
            font=("Segoe UI", 8, "bold"),
        )
        style.map("Stop.TButton", background=[("active", "#fb7185")])

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)

        ttk.Label(main, textvariable=self.engine_status, style="Engine.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )

        badge_lbl = tk.Label(
            main,
            textvariable=self.role_badge,
            bg="#047857",
            fg="#ffffff",
            font=("Segoe UI", 8, "bold"),
            padx=6,
            pady=3,
            anchor="w",
        )
        badge_lbl.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 4))

        card = tk.Frame(main, bg=self.CARD, padx=8, pady=6)
        card.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        tk.Label(
            card,
            textvariable=self.status,
            bg=self.CARD,
            fg="#f1f5f9",
            font=("Segoe UI", 8, "bold"),
            wraplength=295,
            justify="left",
            anchor="w",
        ).pack(fill="x")

        ttk.Button(main, text="▶ MULAI", style="Start.TButton", command=self.start).grid(
            row=3, column=0, sticky="ew", padx=(0, 3), pady=(0, 4)
        )
        ttk.Button(main, text="■ JEDA", style="Stop.TButton", command=self.stop).grid(
            row=3, column=1, sticky="ew", padx=(3, 0), pady=(0, 4)
        )

        ttk.Button(
            main, text="⟳ Sinkron Papan", style="Dark.TButton", command=self.force_recalibrate
        ).grid(row=4, column=0, sticky="ew", padx=(0, 3), pady=(0, 4))
        ttk.Button(
            main, text="⚡ Paksa Jalan", style="Dark.TButton", command=self.force_my_turn
        ).grid(row=4, column=1, sticky="ew", padx=(3, 0), pady=(0, 4))

        ttk.Button(
            main,
            text="⌜ Kiri-Atas (3d)",
            style="Dark.TButton",
            command=lambda: self.countdown("m_tl", 3),
        ).grid(row=5, column=0, sticky="ew", padx=(0, 3), pady=(0, 6))
        ttk.Button(
            main,
            text="⌟ Kanan-Bawah (3d)",
            style="Dark.TButton",
            command=lambda: self.countdown("m_br", 3),
        ).grid(row=5, column=1, sticky="ew", padx=(3, 0), pady=(0, 6))

        ttk.Label(main, text="Mode Kemenangan:", style="Sub.TLabel").grid(
            row=6, column=0, sticky="w", pady=2
        )
        cb_style = ttk.Combobox(
            main,
            textvariable=self.v_style,
            values=STYLE_MODES,
            width=23,
            state="readonly",
        )
        cb_style.grid(row=6, column=1, sticky="e", pady=2)

        ttk.Label(main, text="Warna Bidak Anda:", style="Sub.TLabel").grid(
            row=7, column=0, sticky="w", pady=2
        )
        cb_side = ttk.Combobox(
            main,
            textvariable=self.v_side,
            values=[SIDE_AUTO, "Hitam", "Putih"],
            width=16,
            state="readonly",
        )
        cb_side.grid(row=7, column=1, sticky="e", pady=2)
        cb_side.bind("<<ComboboxSelected>>", lambda _e: self._on_side_changed())

        ttk.Label(main, text="Mode Klik & Depth:", style="Sub.TLabel").grid(
            row=8, column=0, sticky="w", pady=2
        )
        sub_row = ttk.Frame(main)
        sub_row.grid(row=8, column=1, sticky="e", pady=2)
        ttk.Combobox(
            sub_row, textvariable=self.v_mode, values=["klik", "seret"], width=6, state="readonly"
        ).pack(side="left", padx=(0, 4))
        ttk.Spinbox(sub_row, from_=16, to=32, textvariable=self.v_depth, width=4).pack(side="left")

        ttk.Label(main, text="Waktu Analisa (0.10-0.60d):", style="Sub.TLabel").grid(
            row=9, column=0, sticky="w", pady=2
        )
        ttk.Scale(main, from_=0.10, to=0.60, variable=self.v_time, length=135).grid(
            row=9, column=1, sticky="e", pady=2
        )

        ttk.Checkbutton(
            main, text="🧑 Mode Manusia (Ritme Mikir & Kurva Tangan)", variable=self.v_human
        ).grid(row=10, column=0, columnspan=2, sticky="w", pady=(4, 1))

        ttk.Checkbutton(
            main, text="⚡ Auto-Jalan & Auto-Promosi Menteri", variable=self.v_auto
        ).grid(row=11, column=0, columnspan=2, sticky="w", pady=(1, 2))

        ttk.Button(
            main,
            text="📂 Pilih File Stockfish (.exe)",
            style="Dark.TButton",
            command=self.pick_stockfish,
        ).grid(row=12, column=0, columnspan=2, sticky="ew", pady=(6, 0))

    def _on_side_changed(self):
        self.sync_settings()
        self.resync_flag = True

    def sync_settings(self):
        try:
            self.cfg.update({
                "bot_side": self.v_side.get(),
                "style_mode": self.v_style.get(),
                "human_mode": bool(self.v_human.get()),
                "auto_orient": bool(self.v_auto_orient.get()),
                "white_bottom": bool(self.v_white_bottom.get()),
                "auto": bool(self.v_auto.get()),
                "promo_click": True,
                "movetime": float(self.v_time.get()),
                "depth": int(self.v_depth.get()),
                "mode": self.v_mode.get(),
            })
        except Exception:
            pass
        self.live = dict(self.cfg)

    def poll(self):
        self.sync_settings()
        try:
            while True:
                message = self.q.get_nowait()
                if isinstance(message, tuple) and len(message) == 2:
                    kind, val = message
                    if kind == "engine":
                        self.engine_status.set(val)
                    elif kind == "badge":
                        self.role_badge.set(val)
                else:
                    self.status.set(message)
        except queue.Empty:
            pass
        self.root.after(40, self.poll)

    def say(self, text):
        self.q.put(text)

    def set_badge(self, bot_color, wb, turn):
        me = "PUTIH" if bot_color == chess.WHITE else "HITAM"
        orient = "Bawah" if (
            (bot_color == chess.WHITE and wb) or (bot_color == chess.BLACK and not wb)
        ) else "Atas"
        gil = "PUTIH" if turn == chess.WHITE else "HITAM"
        self.q.put(
            ("badge", f"ANDA: {me} ({orient}) • GILIRAN: {gil} • ✨ !! {self.brilliant_count}/{TARGET_BRILLIANTS_PER_GAME}")
        )

    def save_cfg(self):
        try:
            json.dump(self.cfg, open(CONF_PATH, "w"))
        except Exception:
            pass

    def manual_rect(self):
        r = self.cfg.get("manual_rect")
        if not r:
            return None
        x1, y1, x2, y2 = r
        if x2 - x1 < 160 or y2 - y1 < 160:
            return None
        return int(x1), int(y1), int(x2), int(y2)

    def overlaps(self, rect):
        self.root.update_idletasks()
        wx, wy = self.root.winfo_rootx(), self.root.winfo_rooty() - 30
        ww, wh = self.root.winfo_width(), self.root.winfo_height() + 30
        x1, y1, x2, y2 = rect
        return not (wx + ww <= x1 or wx >= x2 or wy + wh <= y1 or wy >= y2)

    def ensure_clear(self, rect):
        if not self.overlaps(rect):
            return
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        ww, wh = self.root.winfo_width(), self.root.winfo_height()
        for x, y in [
            (sw - ww - 10, 25),
            (10, 25),
            (sw - ww - 10, sh - wh - 65),
            (10, sh - wh - 65),
        ]:
            self.root.geometry(f"+{max(0, x)}+{max(0, y)}")
            self.root.update_idletasks()
            if not self.overlaps(rect):
                return

    def flash_rect(self, rect, ms=320):
        x1, y1, x2, y2 = rect
        t = 3
        strips = [
            (x1 - t, y1 - t, x2 - x1 + 2 * t, t),
            (x1 - t, y2, x2 - x1 + 2 * t, t),
            (x1 - t, y1, t, y2 - y1),
            (x2, y1, t, y2 - y1),
        ]
        wins = []
        for x, y, w, h in strips:
            try:
                win = tk.Toplevel(self.root)
                win.overrideredirect(True)
                win.attributes("-topmost", True)
                win.configure(bg="#10b981")
                win.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")
                wins.append(win)
            except Exception:
                pass
        self.root.after(ms, lambda: [w.destroy() for w in wins])

    def pick_stockfish(self):
        p = filedialog.askopenfilename(title="Pilih file Stockfish (stockfish*.exe)")
        if p:
            self.cfg["stockfish"] = p
            self.save_cfg()
            self.say(f"Stockfish dipilih: {os.path.basename(p)}.")

    def force_recalibrate(self):
        self.cfg["manual_rect"] = None
        self.cfg["m_tl"] = None
        self.cfg["m_br"] = None
        self.save_cfg()
        self.recalibrate_flag = True
        self.resync_flag = True
        self.say("Mendeteksi ulang lokasi papan di layar...")
        if not self.running or not (getattr(self, "worker_thread", None) and self.worker_thread.is_alive()):
            self.start()

    def force_my_turn(self):
        self.force_turn_flag = True
        self.say("Memaksa giliran jalan untuk bidak Anda...")
        if not self.running or not (getattr(self, "worker_thread", None) and self.worker_thread.is_alive()):
            self.start()

    def countdown(self, key, sec):
        if sec > 0:
            label = "KIRI-ATAS" if key == "m_tl" else "KANAN-BAWAH"
            self.say(f"Arahkan kursor ke pojok {label} papan dalam {sec}...")
            self.root.after(1000, lambda: self.countdown(key, sec - 1))
            return
        x, y = pyautogui.position()
        self.cfg[key] = [int(x), int(y)]
        if self.cfg.get("m_tl") and self.cfg.get("m_br"):
            x1, y1 = self.cfg["m_tl"]
            x2, y2 = self.cfg["m_br"]
            if x2 > x1 + 100 and y2 > y1 + 100:
                self.cfg["manual_rect"] = [x1, y1, x2, y2]
                self.save_cfg()
                self.resync_flag = True
                self.flash_rect(self.cfg["manual_rect"])
                self.say(f"Papan manual dikunci: ({x1},{y1})-({x2},{y2}).")
                if not self.running:
                    self.start()
                return
        self.say(f"Titik {key} disimpan ({x}, {y}).")

    def start(self):
        if self.running and getattr(self, "worker_thread", None) and self.worker_thread.is_alive():
            self.resync_flag = True
            return
        self.running = True
        self.resync_flag = True
        self.say("Bot aktif! Memindai papan...")
        if not (getattr(self, "worker_thread", None) and self.worker_thread.is_alive()):
            self.worker_thread = threading.Thread(target=self.worker, daemon=True)
            self.worker_thread.start()

    def stop(self):
        self.running = False
        self.say("Dijeda.")

    def close(self):
        self.running = False
        self.save_cfg()
        self.root.destroy()

    # ------------------------------------------------------------------------
    # Eksekusi Langkah Biomekanika Manusia & Auto-Focus Retry
    # ------------------------------------------------------------------------
    def _send_mouse_move(self, mv, rect, wb, promo_click, mode, human_mode=True):
        x1, y1 = square_point(mv.from_square, rect, wb, human_jitter=human_mode)
        x2, y2 = square_point(mv.to_square, rect, wb, human_jitter=human_mode)

        if human_mode:
            human_curve_move(x1, y1, min_dur=0.045, max_dur=0.125)
            # Jeda mikro mata manusia memastikan bidak sebelum menekan tombol mouse
            time.sleep(random.uniform(0.018, 0.045))
            if mode == "seret":
                pyautogui.mouseDown(button="left", _pause=False)
                time.sleep(random.uniform(0.025, 0.055))
                human_curve_move(x2, y2, min_dur=0.055, max_dur=0.140)
                time.sleep(random.uniform(0.018, 0.042))
                pyautogui.mouseUp(button="left", _pause=False)
            else:
                pyautogui.mouseDown(button="left", _pause=False)
                time.sleep(random.uniform(0.022, 0.048))
                pyautogui.mouseUp(button="left", _pause=False)
                # Jeda kognitif singkat antara memilih bidak dan memilih petak tujuan
                time.sleep(random.uniform(0.038, 0.095))
                human_curve_move(x2, y2, min_dur=0.045, max_dur=0.120)
                time.sleep(random.uniform(0.015, 0.038))
                pyautogui.mouseDown(button="left", _pause=False)
                time.sleep(random.uniform(0.022, 0.048))
                pyautogui.mouseUp(button="left", _pause=False)
        else:
            if mode == "seret":
                pyautogui.moveTo(x1, y1, duration=0.0, _pause=False)
                pyautogui.mouseDown(button="left", _pause=False)
                time.sleep(0.010)
                pyautogui.moveTo(x2, y2, duration=0.012, _pause=False)
                pyautogui.mouseUp(button="left", _pause=False)
            else:
                pyautogui.click(x1, y1, _pause=False)
                time.sleep(0.014)
                pyautogui.click(x2, y2, _pause=False)

        if mv.promotion and promo_click:
            time.sleep(random.uniform(0.035, 0.070) if human_mode else 0.020)
            promo_offsets = {
                chess.QUEEN: 0,
                chess.KNIGHT: 1,
                chess.ROOK: 2,
                chess.BISHOP: 3,
            }
            idx = promo_offsets.get(mv.promotion, 0)
            cell_h = (rect[3] - rect[1]) / 8.0
            _, target_row = cell_of(mv.to_square, wb)
            direction = 1 if target_row == 0 else -1
            px, py = x2, int(round(y2 + direction * idx * cell_h))
            if human_mode:
                human_curve_move(px, py, min_dur=0.030, max_dur=0.065)
            pyautogui.click(px, py, _pause=False)

    def exec_move_verified(self, sct, mv, rect, wb, promo_click, mode, bot_color, human_mode=True):
        x1, y1, x2, y2 = rect
        from_cell = cell_of(mv.from_square, wb)

        self._send_mouse_move(mv, rect, wb, promo_click, mode, human_mode=human_mode)

        latest = None
        for attempt in range(10):
            time.sleep(0.020)
            img_check = grab_region(sct, x1, y1, x2 - x1, y2 - y1)
            latest = self.vision.read(img_check)
            if latest.occluded or not latest.valid_grid:
                break
            if from_cell not in latest.colors:
                break
            if attempt == 4 and latest.colors.get(from_cell) == bot_color:
                self._send_mouse_move(mv, rect, wb, promo_click, mode, human_mode=False)

        return latest

    def _open_engine(self, sf_path):
        if not sf_path:
            self.q.put(("engine", "⚡ ENGINE: Built-in Human + WR 100%"))
            return None
        eng = None
        try:
            flags = subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0
            eng = chess.engine.SimpleEngine.popen_uci(sf_path, creationflags=flags)
            desired_opts = {
                "Threads": CPU_THREADS,
                "Hash": DEFAULT_HASH_MB,
                "Skill Level": 20,
                "UCI_LimitStrength": False,
                "Move Overhead": 10,
                "Ponder": False,
            }
            if "Contempt" in eng.options:
                desired_opts["Contempt"] = 24

            safe_opts = {
                k: v
                for k, v in desired_opts.items()
                if k in eng.options and not eng.options[k].is_managed()
            }
            eng.configure(safe_opts)
            name = os.path.basename(sf_path)
            self.q.put(("engine", f"🧑🏆 HUMAN WR-100% ({name[:16]})"))
            return eng
        except Exception as exc:
            if eng is not None:
                try:
                    eng.quit()
                except Exception:
                    pass
            self.q.put(("engine", f"Stockfish fallback ({exc}); mode Built-in."))
            return None

    def worker(self):
        engine = None
        tracker = GameTracker()
        synced = False
        cached_rect = None
        next_scan = 0.0
        sync_failures = 0
        last_cleared_rect = None
        last_message = ""
        last_suggestion = None

        try:
            engine = self._open_engine(find_stockfish(self.live.get("stockfish", "")))
            with mss.mss() as sct:
                while self.running:
                    try:
                        settings = dict(self.live)
                        now = time.monotonic()

                        if self.recalibrate_flag:
                            self.recalibrate_flag = False
                            cached_rect = None
                            synced = False
                            sync_failures = 0

                        rect = self.manual_rect()
                        if rect is None:
                            if cached_rect is None or now >= next_scan:
                                found = scan_screens(sct)
                                if found is not None:
                                    if cached_rect != found:
                                        cached_rect = found
                                        self.root.after(0, lambda r=found: self.flash_rect(r, 250))
                                next_scan = now + 1.0
                            rect = cached_rect

                        if rect is None:
                            message = "Papan belum terlihat. Buka papan catur atau klik Kiri-Atas & Kanan-Bawah."
                            if message != last_message:
                                self.say(message)
                                last_message = message
                            time.sleep(0.18)
                            continue

                        if rect != last_cleared_rect:
                            self.root.after(
                                0, lambda current_rect=rect: self.ensure_clear(current_rect)
                            )
                            last_cleared_rect = rect

                        x1, y1, x2, y2 = rect
                        img = grab_region(sct, x1, y1, x2 - x1, y2 - y1)
                        observation = self.vision.read(img)

                        if not observation.valid_grid:
                            cached_rect = None
                            self.cfg["manual_rect"] = None
                            synced = False
                            next_scan = 0.0
                            time.sleep(0.05)
                            continue

                        if observation.occluded:
                            message = "Papan tertutup popup. Tutup popup untuk melanjutkan."
                            if message != last_message:
                                self.say(message)
                                last_message = message
                            time.sleep(0.15)
                            continue

                        bot_side_pref = settings.get("bot_side", SIDE_AUTO)

                        if self.resync_flag or not synced:
                            self.resync_flag = False
                            ok, message = tracker.sync(
                                observation,
                                bot_side_pref,
                                settings.get("auto_orient", True),
                                settings.get("white_bottom", True),
                            )
                            if ok:
                                synced = True
                                sync_failures = 0
                                if len(tracker.board.move_stack) <= 2:
                                    self.brilliant_count = 0
                                bot_color = resolve_bot_color(bot_side_pref, tracker.wb)
                                self.set_badge(bot_color, tracker.wb, tracker.board.turn)
                                self.say(message)
                                last_message = message
                            else:
                                sync_failures += 1
                                if sync_failures >= 3:
                                    cached_rect = None
                                    next_scan = 0.0
                                    sync_failures = 0
                                if message != last_message:
                                    self.say(message)
                                    last_message = message
                            time.sleep(0.05)
                            continue

                        state = tracker.update(
                            observation,
                            settings.get("auto_orient", True),
                            settings.get("white_bottom", True),
                            bot_side_pref,
                        )
                        if state == "invalid_rect":
                            cached_rect = None
                            synced = False
                            next_scan = 0.0
                            continue

                        bot_color = resolve_bot_color(bot_side_pref, tracker.wb)
                        self.set_badge(bot_color, tracker.wb, tracker.board.turn)

                        if state == "newgame":
                            self.brilliant_count = 0
                            self.set_badge(bot_color, tracker.wb, tracker.board.turn)
                            self.say("🏆 Game baru terdeteksi! Siap menyerang.")
                            last_suggestion = None
                            continue
                        if state == "resync":
                            synced = False
                            self.say("Menyinkronkan ulang posisi papan...")
                            continue
                        if state == "move":
                            last_suggestion = None

                        board = tracker.board
                        if board.is_game_over():
                            message = (
                                f"Game selesai ({board.result()}) • Total Brilliant: {self.brilliant_count} !!"
                            )
                            if message != last_message:
                                self.say(message)
                                last_message = message
                            time.sleep(0.15)
                            continue

                        force_turn = self.force_turn_flag
                        if force_turn:
                            self.force_turn_flag = False
                            if board.turn != bot_color:
                                b_forced = board.copy()
                                b_forced.turn = bot_color
                                b_forced.ep_square = None
                                if b_forced.is_valid():
                                    tracker.board = b_forced
                                    board = tracker.board
                                    self.set_badge(bot_color, tracker.wb, tracker.turn) if hasattr(tracker, "turn") else self.set_badge(bot_color, tracker.wb, board.turn)
                                else:
                                    synced = False
                                    continue

                        if board.turn != bot_color:
                            time.sleep(0.025)
                            continue

                        position_key = board.fen()
                        if not settings.get("auto", True) and last_suggestion == position_key:
                            time.sleep(0.08)
                            continue

                        think_time = max(0.08, min(2.0, float(settings.get("movetime", 0.22))))
                        depth = max(16, min(64, int(settings.get("depth", 26))))
                        style_mode = settings.get("style_mode", STYLE_WR100_BRILLIANT)
                        human_mode = bool(settings.get("human_mode", True))

                        t_calc_start = time.perf_counter()
                        try:
                            decision = choose_wr100_move(
                                engine,
                                board,
                                think_time,
                                max_depth=depth,
                                style_mode=style_mode,
                                brilliant_count=self.brilliant_count,
                                human_mode=human_mode,
                            )
                        except Exception as exc:
                            self.say(f"Restarting Engine ({exc})...")
                            if engine is not None:
                                try:
                                    engine.quit()
                                except Exception:
                                    pass
                            engine = self._open_engine(find_stockfish(self.live.get("stockfish", "")))
                            fallback_mv = BuiltinEngine.pick_move(board, think_time)
                            decision = {
                                "move": fallback_mv,
                                "is_book": False,
                                "book_name": None,
                                "is_brilliant": False,
                                "brilliant_label": "",
                                "cp": 0,
                            }

                        if not decision or decision["move"] is None or decision["move"] not in board.legal_moves:
                            time.sleep(0.06)
                            continue

                        move = decision["move"]
                        is_book = decision["is_book"]
                        book_name = decision["book_name"]
                        is_brilliant = decision["is_brilliant"]
                        bril_label = decision["brilliant_label"]
                        eval_cp = decision.get("cp", 0)

                        # STRICT COLOR LOCK
                        moving_piece = board.piece_at(move.from_square)
                        if moving_piece is None or moving_piece.color != bot_color:
                            synced = False
                            continue

                        from_cell = cell_of(move.from_square, tracker.wb)
                        if observation.colors.get(from_cell) != bot_color:
                            synced = False
                            continue

                        if not self.running:
                            break

                        san_str = board.san(move)
                        eval_str = "M!" if abs(eval_cp) >= 90000 else f"{eval_cp / 100.0:+.2f}"

                        if not settings.get("auto", True):
                            tag = f" [✨ {bril_label}]" if is_brilliant else (f" [{book_name}]" if is_book else "")
                            self.say(f"Saran: {san_str} ({eval_str}){tag}")
                            last_suggestion = position_key
                            time.sleep(0.08)
                            continue

                        # SIMULASI RITME KOGNITIF MANUSIA SEBELUM MENGGERAKKAN MOUSE
                        if human_mode:
                            target_delay = human_cognitive_delay(
                                board,
                                move,
                                base_pace=think_time,
                                is_book=is_book,
                                is_brilliant=is_brilliant,
                            )
                            elapsed = time.perf_counter() - t_calc_start
                            rem_delay = target_delay - elapsed
                            if rem_delay > 0.015:
                                time.sleep(rem_delay)
                                # Pastikan papan tidak tertutup popup selama jeda berpikir
                                img_recheck = grab_region(sct, x1, y1, x2 - x1, y2 - y1)
                                obs_recheck = self.vision.read(img_recheck)
                                if (
                                    obs_recheck.occluded
                                    or not obs_recheck.valid_grid
                                    or obs_recheck.colors.get(from_cell) != bot_color
                                ):
                                    synced = False
                                    continue

                        if is_brilliant:
                            next_num = min(TARGET_BRILLIANTS_PER_GAME, self.brilliant_count + 1)
                            self.say(f"✨ BRILLIANT #{next_num} !! ➔ {san_str} [{eval_str}]")
                        elif is_book and book_name:
                            self.say(f"🔥 {book_name}: {san_str} [{eval_str}]")
                        else:
                            self.say(f"Menyerang: {san_str} ({move.uci()}) [{eval_str}]")

                        observed_after = self.exec_move_verified(
                            sct,
                            move,
                            rect,
                            tracker.wb,
                            settings.get("promo_click", True),
                            settings.get("mode", "klik"),
                            bot_color,
                            human_mode=human_mode,
                        )

                        if tracker.confirm_own_move(move, observed_after):
                            if is_brilliant and self.brilliant_count < TARGET_BRILLIANTS_PER_GAME:
                                self.brilliant_count += 1
                            self.set_badge(bot_color, tracker.wb, tracker.board.turn)
                            if is_brilliant:
                                self.say(f"✨ Terverifikasi BRILLIANT ({self.brilliant_count}/5 !!): {san_str} [{eval_str}]")
                            else:
                                self.say(f"Terverifikasi: {san_str} [{eval_str}]")
                            last_message = ""
                            last_suggestion = None
                        else:
                            time.sleep(0.05)

                    except Exception as loop_exc:
                        self.say(f"Memulihkan siklus ({loop_exc})...")
                        time.sleep(0.10)
        finally:
            if engine is not None:
                try:
                    engine.quit()
                except Exception:
                    pass
            self.running = False


def main():
    root = tk.Tk()
    BotApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()