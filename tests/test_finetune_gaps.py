"""Unit tests for finetune gap implementations (E4, E7)."""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from finetune.build_sft_dataset import (  # noqa: E402
    Example,
    recommended_max_seq_len,
    select_train_examples,
)
from postprocess.postprocess import apply_cluster_merge  # noqa: E402


def _ex(source: str, index: int, label: str) -> Example:
    return Example(
        source=source,
        index=index,
        label=label,
        target_text=f"sent-{index}",
        left_context=[],
        right_context=[],
        reasons=[],
    )


class HardNearBorderTest(unittest.TestCase):
    def test_keeps_all_near_border_then_topup(self) -> None:
        examples = [
            _ex("doc", 0, "NOBORDER"),
            _ex("doc", 1, "BORDER"),
            _ex("doc", 2, "NOBORDER"),
            _ex("doc", 3, "NOBORDER"),
            _ex("doc", 10, "NOBORDER"),
            _ex("doc", 20, "NOBORDER"),
        ]
        selected = select_train_examples(
            examples,
            mode="hard",
            ratio=3,
            negative_pct=0.5,
            seed=1337,
            hard_window=3,
            fp_sentences=set(),
        )
        labels = {(e.index, e.label) for e in selected}
        self.assertIn((1, "BORDER"), labels)
        self.assertIn((0, "NOBORDER"), labels)
        self.assertIn((2, "NOBORDER"), labels)
        self.assertIn((3, "NOBORDER"), labels)
        noborders = [e for e in selected if e.label == "NOBORDER"]
        self.assertGreaterEqual(len(noborders), 3)


class ClusterMergeTest(unittest.TestCase):
    def test_keeps_highest_confidence_in_cluster(self) -> None:
        labels = ["NOBORDER", "BORDER", "NOBORDER", "BORDER", "NOBORDER", "BORDER"]
        confs = [None, 0.7, None, 0.95, None, 0.8]
        out = apply_cluster_merge(labels, confs, radius=3)
        self.assertEqual(out[1], "NOBORDER")
        self.assertEqual(out[3], "BORDER")
        self.assertEqual(out[5], "NOBORDER")


class MaxSeqLenTest(unittest.TestCase):
    def test_recommended_coupling(self) -> None:
        self.assertEqual(recommended_max_seq_len(512), 1280)
        self.assertEqual(recommended_max_seq_len(2048), 2816)


if __name__ == "__main__":
    unittest.main()
