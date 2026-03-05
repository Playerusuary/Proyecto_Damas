"""
visualizaciones/rival_eval.py

Objetivo (para el reporte)
- Generar metricas adicionales "tipo prototipo" sin modificar el juego:
  - Win-rate: porcentaje de partidas que gana la IA (lado 'ai') contra un rival.
  - Metricas de clasificacion (precision/recall/F1) usando el score del modelo como
    predictor del ganador final en partidas simuladas (evidencia cuantitativa).

Importante
- Este script NO se integra al flujo del producto (web/desktop).
- Solo genera evidencias en:
  - backend/data/rival/           (logs de simulacion)
  - visualizaciones/output/*      (tablas y figuras para pegar al reporte)

Como funciona
- Implementa en Python una version equivalente de las reglas usadas en
  frontend/src/game/rules.js:
  - tablero 8x8 con codigos: 0, 1, 2, -1, -2
  - movimiento diagonal, capturas, promocion a rey, limite de empate sin capturas
  - rey con movimiento diagonal largo y captura con aterrizaje inmediato despues de la pieza rival
  - cadenas de captura con pieza forzada

Politicas (agentes)
- 'ai': elige el movimiento que maximiza el score del modelo
- 'player': por defecto elige el movimiento que minimiza el score del modelo (rival adversarial)
  Esto permite simular "IA vs rival" usando el mismo evaluador (modelo).

Requisitos
- Ejecutar con el Python del venv del backend si TensorFlow no esta global:
  backend\\venv\\Scripts\\python.exe visualizaciones\\rival_eval.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import json
import math
import os
import random
from typing import Any, Dict, List, Literal, Optional, Tuple

import numpy as np
import pandas as pd


Side = Literal["player", "ai"]


# -----------------------------
# Convenciones del tablero
# -----------------------------
EMPTY = 0
PLAYER_MAN = 1
PLAYER_KING = 2
AI_MAN = -1
AI_KING = -2
BOARD_SIZE = 8

# Misma regla que el frontend: declarar empate despues de N "plies" sin captura.
DRAW_NO_CAPTURE_LIMIT = 80


def try_import_tensorflow():
    try:
        import tensorflow as tf  # noqa: F401

        return True, None
    except Exception as exc:  # pragma: no cover
        return False, exc


def is_inside(r: int, c: int) -> bool:
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def is_dark(r: int, c: int) -> bool:
    # En un tablero 8x8, las casillas oscuras (usadas en damas) son (r+c) impar.
    return (r + c) % 2 == 1


def is_king(v: int) -> bool:
    return abs(v) == 2


def is_player_piece(v: int) -> bool:
    return v == PLAYER_MAN or v == PLAYER_KING


def is_ai_piece(v: int) -> bool:
    return v == AI_MAN or v == AI_KING


def is_opponent(piece: int, other: int) -> bool:
    return (is_player_piece(piece) and is_ai_piece(other)) or (is_ai_piece(piece) and is_player_piece(other))


def clone_board(state: List[List[int]]) -> List[List[int]]:
    return [row[:] for row in state]


def create_initial_board() -> List[List[int]]:
    # Misma configuracion inicial que frontend/src/game/rules.js
    return [
        [EMPTY, AI_MAN, EMPTY, AI_MAN, EMPTY, AI_MAN, EMPTY, AI_MAN],
        [AI_MAN, EMPTY, AI_MAN, EMPTY, AI_MAN, EMPTY, AI_MAN, EMPTY],
        [EMPTY, AI_MAN, EMPTY, AI_MAN, EMPTY, AI_MAN, EMPTY, AI_MAN],
        [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
        [PLAYER_MAN, EMPTY, PLAYER_MAN, EMPTY, PLAYER_MAN, EMPTY, PLAYER_MAN, EMPTY],
        [EMPTY, PLAYER_MAN, EMPTY, PLAYER_MAN, EMPTY, PLAYER_MAN, EMPTY, PLAYER_MAN],
        [PLAYER_MAN, EMPTY, PLAYER_MAN, EMPTY, PLAYER_MAN, EMPTY, PLAYER_MAN, EMPTY],
    ]


def get_directions(piece: int) -> List[Tuple[int, int]]:
    if piece in (PLAYER_KING, AI_KING):
        return [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    if piece == PLAYER_MAN:
        return [(-1, -1), (-1, 1)]
    return [(1, -1), (1, 1)]


@dataclass(frozen=True)
class Move:
    from_r: int
    from_c: int
    to_r: int
    to_c: int
    capture: bool
    captured_r: Optional[int] = None
    captured_c: Optional[int] = None


def get_piece_capture_moves(state: List[List[int]], r: int, c: int) -> List[Move]:
    piece = state[r][c]
    if piece == EMPTY:
        return []

    moves: List[Move] = []
    directions = get_directions(piece)

    if is_king(piece):
        # Rey: recorre una diagonal hasta encontrar 1 enemigo. Si lo encuentra,
        # solo puede aterrizar en la casilla inmediata despues (si esta vacia).
        for dr, dc in directions:
            row = r + dr
            col = c + dc
            enemy_found = False
            enemy_r = -1
            enemy_c = -1

            while is_inside(row, col) and is_dark(row, col):
                current = state[row][col]

                if not enemy_found:
                    if current == EMPTY:
                        row += dr
                        col += dc
                        continue
                    if is_opponent(piece, current):
                        enemy_found = True
                        enemy_r = row
                        enemy_c = col
                        row += dr
                        col += dc
                        continue
                    break

                # Ya vimos enemigo: la primera casilla vacia despues define el aterrizaje.
                if current != EMPTY:
                    break
                moves.append(
                    Move(
                        from_r=r,
                        from_c=c,
                        to_r=row,
                        to_c=col,
                        capture=True,
                        captured_r=enemy_r,
                        captured_c=enemy_c,
                    )
                )
                break

        return moves

    # Peon: salto 2 casillas sobre rival.
    for dr, dc in directions:
        mid_r = r + dr
        mid_c = c + dc
        land_r = r + dr * 2
        land_c = c + dc * 2

        if not is_inside(mid_r, mid_c) or not is_inside(land_r, land_c):
            continue
        if not is_dark(land_r, land_c):
            continue
        if state[land_r][land_c] != EMPTY:
            continue

        mid_piece = state[mid_r][mid_c]
        if is_player_piece(piece) and is_ai_piece(mid_piece):
            moves.append(Move(r, c, land_r, land_c, True, mid_r, mid_c))
        if is_ai_piece(piece) and is_player_piece(mid_piece):
            moves.append(Move(r, c, land_r, land_c, True, mid_r, mid_c))

    return moves


def get_piece_simple_moves(state: List[List[int]], r: int, c: int) -> List[Move]:
    piece = state[r][c]
    if piece == EMPTY:
        return []

    moves: List[Move] = []
    directions = get_directions(piece)

    if is_king(piece):
        # Rey: puede moverse multiples casillas diagonales si estan vacias.
        for dr, dc in directions:
            to_r = r + dr
            to_c = c + dc
            while is_inside(to_r, to_c) and is_dark(to_r, to_c) and state[to_r][to_c] == EMPTY:
                moves.append(Move(r, c, to_r, to_c, False))
                to_r += dr
                to_c += dc
        return moves

    # Peon: 1 casilla diagonal hacia adelante.
    for dr, dc in directions:
        to_r = r + dr
        to_c = c + dc
        if not is_inside(to_r, to_c) or not is_dark(to_r, to_c):
            continue
        if state[to_r][to_c] != EMPTY:
            continue
        moves.append(Move(r, c, to_r, to_c, False))

    return moves


def get_all_legal_moves(
    state: List[List[int]],
    side: Side,
    forced_piece: Optional[Tuple[int, int]] = None,
    force_capture_only: bool = False,
) -> List[Move]:
    capture_moves: List[Move] = []
    simple_moves: List[Move] = []

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = state[r][c]
            if side == "player" and not is_player_piece(piece):
                continue
            if side == "ai" and not is_ai_piece(piece):
                continue
            if forced_piece and (forced_piece[0] != r or forced_piece[1] != c):
                continue

            capture_moves.extend(get_piece_capture_moves(state, r, c))
            if not force_capture_only:
                simple_moves.extend(get_piece_simple_moves(state, r, c))

    if capture_moves:
        return capture_moves
    if force_capture_only:
        return []
    return simple_moves


def apply_move(state: List[List[int]], move: Move) -> Dict[str, bool]:
    piece = state[move.from_r][move.from_c]
    state[move.from_r][move.from_c] = EMPTY
    state[move.to_r][move.to_c] = piece

    captured = False
    if move.capture and move.captured_r is not None and move.captured_c is not None:
        state[move.captured_r][move.captured_c] = EMPTY
        captured = True

    promoted = False
    if piece == PLAYER_MAN and move.to_r == 0:
        state[move.to_r][move.to_c] = PLAYER_KING
        promoted = True
    if piece == AI_MAN and move.to_r == BOARD_SIZE - 1:
        state[move.to_r][move.to_c] = AI_KING
        promoted = True

    return {"captured": captured, "promoted": promoted}


def count_pieces(state: List[List[int]]) -> Dict[str, int]:
    player = 0
    ai = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if is_player_piece(state[r][c]):
                player += 1
            if is_ai_piece(state[r][c]):
                ai += 1
    return {"player": player, "ai": ai}


def winner_for_turn(state: List[List[int]], side_to_move: Side, no_capture_count: int) -> Optional[Literal["player", "ai", "draw"]]:
    if no_capture_count >= DRAW_NO_CAPTURE_LIMIT:
        return "draw"

    counts = count_pieces(state)
    if counts["player"] == 0:
        return "ai"
    if counts["ai"] == 0:
        return "player"

    legal = get_all_legal_moves(state, side_to_move)
    if len(legal) == 0:
        return "ai" if side_to_move == "player" else "player"

    return None


@dataclass(frozen=True)
class EvalConfig:
    games: int = 50
    max_plies: int = 240
    epsilon: float = 0.05
    seed: int = 42
    save_states: bool = True
    player_policy: Literal["minimize", "random"] = "minimize"
    out_prefix: str = "rival"


class ScoreProvider:
    def score_ai_perspective(self, board: List[List[int]]) -> float:
        raise NotImplementedError

    def score_many_ai_perspective(self, boards: List[List[List[int]]]) -> List[float]:
        # Default: llama a la version individual (lento, pero correcto).
        return [self.score_ai_perspective(b) for b in boards]


class TfModelScoreProvider(ScoreProvider):
    def __init__(self, model_path: Path):
        ok_tf, exc = try_import_tensorflow()
        if not ok_tf:  # pragma: no cover
            raise RuntimeError(
                "No se pudo importar TensorFlow. Ejecuta con el Python del venv del backend "
                f"(backend/venv/Scripts/python.exe). Detalle: {exc}"
            )

        import tensorflow as tf

        self._model = tf.keras.models.load_model(str(model_path), compile=False)
        # Cache simple para evitar recomputar estados repetidos durante simulacion.
        self._cache: Dict[Tuple[int, ...], float] = {}

    def score_ai_perspective(self, board: List[List[int]]) -> float:
        key = tuple(int(v) for v in np.asarray(board, dtype=np.int8).reshape(64))
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        x = np.asarray(board, dtype=np.float32).reshape(1, 64)
        pred = self._model.predict(x, verbose=0)
        score = float(pred[0][0])
        self._cache[key] = score
        return score

    def score_many_ai_perspective(self, boards: List[List[List[int]]]) -> List[float]:
        # Prediccion en batch (mucho mas rapido) + cache.
        if not boards:
            return []

        keys: List[Tuple[int, ...]] = []
        to_eval: List[List[List[int]]] = []
        positions: List[int] = []

        out: List[Optional[float]] = [None] * len(boards)
        for i, b in enumerate(boards):
            key = tuple(int(v) for v in np.asarray(b, dtype=np.int8).reshape(64))
            keys.append(key)
            cached = self._cache.get(key)
            if cached is not None:
                out[i] = cached
            else:
                to_eval.append(b)
                positions.append(i)

        if to_eval:
            x = np.asarray(to_eval, dtype=np.float32).reshape(len(to_eval), 64)
            pred = self._model.predict(x, verbose=0).reshape(-1)
            for j, score in enumerate(pred.tolist()):
                s = float(score)
                idx = positions[j]
                key = keys[idx]
                self._cache[key] = s
                out[idx] = s

        # mypy: out ya esta completa
        return [float(v) for v in out]  # type: ignore[arg-type]


def choose_move(
    provider: ScoreProvider,
    state: List[List[int]],
    side: Side,
    legal_moves: List[Move],
    rng: random.Random,
    epsilon: float,
    player_policy: Literal["minimize", "random"],
) -> Move:
    # Politica del rival (lado player).
    if side == "player" and player_policy == "random":
        return rng.choice(legal_moves)

    # Exploracion simple para variar partidas y evitar empates repetitivos.
    if epsilon > 0 and rng.random() < epsilon:
        return rng.choice(legal_moves)

    drafts: List[List[List[int]]] = []
    for mv in legal_moves:
        draft = clone_board(state)
        apply_move(draft, mv)
        drafts.append(draft)

    scores = provider.score_many_ai_perspective(drafts)
    scored = list(zip(scores, legal_moves))

    # Convencion: el score es "bueno para la IA".
    # - 'ai' maximiza
    # - 'player' minimiza (rival adversarial)
    if side == "ai":
        best = max(scored, key=lambda t: t[0])[0]
        best_moves = [mv for (s, mv) in scored if s == best]
        return rng.choice(best_moves)

    worst = min(scored, key=lambda t: t[0])[0]
    worst_moves = [mv for (s, mv) in scored if s == worst]
    return rng.choice(worst_moves)


def simulate_one_game(
    provider: ScoreProvider,
    cfg: EvalConfig,
    game_id: int,
    rng: random.Random,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    state = create_initial_board()
    side: Side = "player"  # arranca el jugador, como en UI tipico
    no_capture = 0
    plies = 0
    captures = 0
    promotions = 0

    # Para metricas tipo "precision": guardamos score -> ganador final.
    states_log: List[Dict[str, Any]] = []

    while True:
        winner = winner_for_turn(state, side, no_capture)
        if winner is not None:
            break
        if plies >= cfg.max_plies:
            winner = "draw"
            break

        score_now = provider.score_ai_perspective(state)
        if cfg.save_states:
            states_log.append(
                {
                    "game_id": game_id,
                    "ply": plies,
                    "side_to_move": side,
                    "score_ai": score_now,
                }
            )

        forced_piece: Optional[Tuple[int, int]] = None
        force_capture_only = False

        # Un "turno" puede incluir multiples capturas en cadena.
        while True:
            legal = get_all_legal_moves(state, side, forced_piece, force_capture_only)
            if not legal:
                # Sin movimientos legales: pierde quien esta por jugar.
                winner = "ai" if side == "player" else "player"
                break

            mv = choose_move(provider, state, side, legal, rng, cfg.epsilon, cfg.player_policy)
            result = apply_move(state, mv)
            plies += 1

            if result["captured"]:
                captures += 1
                no_capture = 0
            else:
                no_capture += 1

            if result["promoted"]:
                promotions += 1

            # Si captura y no se promovio, forzamos continuar cadena si hay mas capturas.
            if mv.capture and (not result["promoted"]):
                next_caps = get_piece_capture_moves(state, mv.to_r, mv.to_c)
                if next_caps:
                    forced_piece = (mv.to_r, mv.to_c)
                    force_capture_only = True
                    continue

            break

        if winner is not None:
            break

        # Cambio de lado al terminar el turno (incluyendo cadenas).
        side = "ai" if side == "player" else "player"

    match_row = {
        "game_id": game_id,
        "winner": winner,
        "plies": plies,
        "captures": captures,
        "promotions": promotions,
        "epsilon": cfg.epsilon,
        "max_plies": cfg.max_plies,
        "player_policy": cfg.player_policy,
    }

    # Enriquecemos states_log con el ganador final y prediccion (threshold 0).
    for row in states_log:
        row["winner"] = winner
        row["predicted_winner"] = "ai" if float(row["score_ai"]) > 0 else "player"

    return match_row, states_log


def safe_div(num: float, den: float) -> float:
    return float(num / den) if den else float("nan")


def classification_metrics_from_states(states_df: pd.DataFrame) -> Dict[str, float]:
    # Metricas binarias para "ai" como clase positiva.
    # Excluimos draws porque no pertenecen a la clasificacion binaria.
    df = states_df[states_df["winner"].isin(["ai", "player"])].copy()
    if df.empty:
        return {"accuracy": math.nan, "precision": math.nan, "recall": math.nan, "f1": math.nan}

    y_true = (df["winner"] == "ai").to_numpy()
    y_pred = (df["predicted_winner"] == "ai").to_numpy()

    tp = int(np.logical_and(y_true, y_pred).sum())
    tn = int(np.logical_and(~y_true, ~y_pred).sum())
    fp = int(np.logical_and(~y_true, y_pred).sum())
    fn = int(np.logical_and(y_true, ~y_pred).sum())

    acc = safe_div(tp + tn, tp + tn + fp + fn)
    prec = safe_div(tp, tp + fp)
    rec = safe_div(tp, tp + fn)
    f1 = safe_div(2 * prec * rec, prec + rec) if (not math.isnan(prec) and not math.isnan(rec)) else math.nan

    return {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "tp": float(tp),
        "tn": float(tn),
        "fp": float(fp),
        "fn": float(fn),
        "n_states": float(len(df)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulacion IA vs Rival para generar metricas del prototipo.")
    parser.add_argument("--games", type=int, default=50)
    parser.add_argument("--max-plies", type=int, default=240)
    parser.add_argument("--epsilon", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-save-states", action="store_true")
    parser.add_argument(
        "--player-policy",
        choices=["minimize", "random"],
        default="minimize",
        help="Politica del lado player: minimize (adversarial con modelo) o random (rival aleatorio).",
    )
    parser.add_argument(
        "--out-prefix",
        type=str,
        default="rival",
        help="Prefijo para nombres de archivos (permite correr varios escenarios sin sobreescribir).",
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default="",
        help="Ruta al .keras (por default: backend/models/checkers_model.keras o $DAMAS_MODEL_PATH).",
    )
    args = parser.parse_args()

    cfg = EvalConfig(
        games=int(args.games),
        max_plies=int(args.max_plies),
        epsilon=float(args.epsilon),
        seed=int(args.seed),
        save_states=(not bool(args.no_save_states)),
        player_policy=str(args.player_policy),  # type: ignore[arg-type]
        out_prefix=str(args.out_prefix).strip() or "rival",
    )

    repo_root = Path(__file__).resolve().parent.parent
    default_model = repo_root / "backend" / "models" / "checkers_model.keras"
    model_path = Path(args.model_path) if args.model_path else Path(
        (os.environ.get("DAMAS_MODEL_PATH") or str(default_model))
    )
    if not model_path.is_absolute():
        model_path = (repo_root / model_path).resolve()

    provider = TfModelScoreProvider(model_path)

    # Salida "rival" en backend/data (solo evidencia, no afecta al juego).
    rival_root = repo_root / "backend" / "data" / "rival"
    rival_root.mkdir(parents=True, exist_ok=True)

    # Salida para el reporte en visualizaciones/output.
    out_root = Path(__file__).resolve().parent / "output"
    fig_dir = out_root / "figuras"
    tab_dir = out_root / "tablas"
    fig_dir.mkdir(parents=True, exist_ok=True)
    tab_dir.mkdir(parents=True, exist_ok=True)

    rng = random.Random(cfg.seed)

    matches: List[Dict[str, Any]] = []
    all_states: List[Dict[str, Any]] = []

    for game_id in range(1, cfg.games + 1):
        match_row, states_log = simulate_one_game(provider, cfg, game_id, rng)
        matches.append(match_row)
        if cfg.save_states:
            all_states.extend(states_log)

    matches_df = pd.DataFrame(matches)
    matches_name = f"{cfg.out_prefix}_matches.csv"
    matches_df.to_csv(rival_root / matches_name, index=False)
    matches_df.to_csv(tab_dir / matches_name, index=False)

    states_df = pd.DataFrame(all_states) if all_states else pd.DataFrame()
    if not states_df.empty:
        states_name = f"{cfg.out_prefix}_states.csv"
        states_df.to_csv(rival_root / states_name, index=False)
        states_df.to_csv(tab_dir / states_name, index=False)

    # ---- Metricas agregadas (win-rate) ----
    wins_ai = int((matches_df["winner"] == "ai").sum())
    wins_player = int((matches_df["winner"] == "player").sum())
    draws = int((matches_df["winner"] == "draw").sum())
    n = int(len(matches_df))
    non_draw = max(1, wins_ai + wins_player)

    win_rate_ai = safe_div(wins_ai, non_draw)
    loss_rate_ai = safe_div(wins_player, non_draw)
    draw_rate = safe_div(draws, n) if n else math.nan

    class_metrics: Dict[str, float] = {}
    if not states_df.empty:
        class_metrics = classification_metrics_from_states(states_df)

    metrics = {
        "games": float(cfg.games),
        "wins_ai": float(wins_ai),
        "wins_player": float(wins_player),
        "draws": float(draws),
        "win_rate_ai_no_draw": float(win_rate_ai),
        "loss_rate_ai_no_draw": float(loss_rate_ai),
        "draw_rate_overall": float(draw_rate),
        "avg_plies": float(matches_df["plies"].mean()) if n else math.nan,
        "avg_captures": float(matches_df["captures"].mean()) if n else math.nan,
        "avg_promotions": float(matches_df["promotions"].mean()) if n else math.nan,
        "epsilon": float(cfg.epsilon),
        "max_plies": float(cfg.max_plies),
        "seed": float(cfg.seed),
        **({f"class_{k}": float(v) for k, v in class_metrics.items()} if class_metrics else {}),
    }

    metrics_json = f"{cfg.out_prefix}_metrics.json"
    (rival_root / metrics_json).write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    pd.DataFrame([metrics]).to_csv(tab_dir / f"{cfg.out_prefix}_metrics.csv", index=False)

    # ---- Figuras ----
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set_theme(style="whitegrid", context="talk")

    # Distribucion de resultados (wins/loss/draw).
    plt.figure(figsize=(8, 4))
    counts = matches_df["winner"].value_counts().reindex(["ai", "player", "draw"], fill_value=0)
    counts.plot(kind="bar", color=["#c0392b", "#2980b9", "#7f8c8d"])
    plt.title("Resultados de partidas simuladas (IA vs Rival)")
    plt.xlabel("Resultado final")
    plt.ylabel("Cantidad de partidas")
    plt.tight_layout()
    plt.savefig(fig_dir / f"{cfg.out_prefix}_resultados.png", dpi=180)
    plt.close()

    # Win-rate acumulado (sin draws).
    plt.figure(figsize=(9, 4))
    is_nd = matches_df["winner"].isin(["ai", "player"])
    nd = matches_df[is_nd].copy()
    if not nd.empty:
        nd["ai_win"] = (nd["winner"] == "ai").astype(int)
        nd["cum_win_rate"] = nd["ai_win"].cumsum() / np.arange(1, len(nd) + 1)
        plt.plot(nd["game_id"], nd["cum_win_rate"], color="#c0392b", linewidth=2)
        plt.ylim(0, 1)
    plt.title("Win-rate acumulado de la IA (excluye empates)")
    plt.xlabel("Game ID")
    plt.ylabel("Win-rate")
    plt.tight_layout()
    plt.savefig(fig_dir / f"{cfg.out_prefix}_winrate_acumulado.png", dpi=180)
    plt.close()

    # Confusion matrix (states): prediccion del ganador final vs ganador real.
    if not states_df.empty:
        df_bin = states_df[states_df["winner"].isin(["ai", "player"])].copy()
        if not df_bin.empty:
            y_true = df_bin["winner"]
            y_pred = df_bin["predicted_winner"]
            cm = pd.crosstab(y_true, y_pred).reindex(index=["player", "ai"], columns=["player", "ai"], fill_value=0)
            cm.to_csv(tab_dir / f"{cfg.out_prefix}_confusion_matrix.csv")

            plt.figure(figsize=(5.5, 4.8))
            ax = sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
            ax.set_title("Matriz de confusion (score -> ganador final)")
            ax.set_xlabel("Prediccion")
            ax.set_ylabel("Real")
            plt.tight_layout()
            plt.savefig(fig_dir / f"{cfg.out_prefix}_confusion_matrix.png", dpi=180)
            plt.close()

            # Distribucion del score (para ver si el modelo separa clases en self-play).
            plt.figure(figsize=(8, 4))
            sns.histplot(df_bin, x="score_ai", hue="winner", bins=30, stat="density", common_norm=False)
            plt.title("Distribucion de score del modelo vs ganador final (self-play)")
            plt.xlabel("score_ai (perspectiva IA)")
            plt.ylabel("Densidad")
            plt.tight_layout()
            plt.savefig(fig_dir / f"{cfg.out_prefix}_score_hist.png", dpi=180)
            plt.close()

    # Reporte md resumido para pegar directo.
    report_lines = [
        "# Metricas Rival (IA vs Rival)",
        "",
        f"- Partidas simuladas: **{cfg.games}**",
        f"- IA gana (ai): **{wins_ai}**",
        f"- Rival gana (player): **{wins_player}**",
        f"- Empates: **{draws}**",
        f"- Win-rate IA (sin empates): **{win_rate_ai:.3f}**",
        f"- Draw-rate (global): **{draw_rate:.3f}**",
    ]
    if class_metrics:
        report_lines.extend(
            [
                "",
                "## Metricas de clasificacion (score -> ganador final, sin draws)",
                f"- Accuracy: **{class_metrics.get('accuracy', math.nan):.3f}**",
                f"- Precision (IA): **{class_metrics.get('precision', math.nan):.3f}**",
                f"- Recall (IA): **{class_metrics.get('recall', math.nan):.3f}**",
                f"- F1 (IA): **{class_metrics.get('f1', math.nan):.3f}**",
            ]
        )
    (out_root / f"{cfg.out_prefix}_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print("OK. Resultados guardados en:")
    print(" -", rival_root)
    print(" -", out_root)


if __name__ == "__main__":
    main()
