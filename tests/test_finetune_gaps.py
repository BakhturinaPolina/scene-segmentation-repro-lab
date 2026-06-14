"""Unit tests for finetune gap implementations (E4, E7) and label parsing."""

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
from finetune.label_parse import (  # noqa: E402
    diagnose_generation,
    parse_eval_label,
    parse_label_confidence,
    recommended_max_new_tokens,
    summarize_parse_diagnostics,
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


class LabelParseTest(unittest.TestCase):
    def test_valid_trailing_json_after_cot(self) -> None:
        text = (
            "a) no significant change\n"
            "b) same characters\n"
            '{"label": "BORDER", "confidence": 0.9}'
        )
        result = parse_eval_label(text, mode="tolerant")
        self.assertTrue(result.parse_ok)
        self.assertEqual(result.label, "BORDER")
        self.assertEqual(result.parse_method, "json")
        self.assertAlmostEqual(result.confidence or 0, 0.9)

    def test_truncated_json_is_suspect(self) -> None:
        text = '{"label": "NO'
        diag = diagnose_generation(text, 96)
        self.assertTrue(diag["truncation_suspect"])
        result = parse_eval_label(text, mode="tolerant")
        self.assertFalse(result.parse_ok)

    def test_cot_only_border_regex_fallback(self) -> None:
        text = "a) scene continues\nb) same setting\nFinal: BORDER"
        tolerant = parse_eval_label(text, mode="tolerant")
        strict = parse_eval_label(text, mode="strict")
        self.assertEqual(tolerant.label, "BORDER")
        self.assertEqual(tolerant.parse_method, "regex_fallback")
        self.assertFalse(strict.parse_ok)

    def test_noborder_before_border_substring(self) -> None:
        label, _ = parse_label_confidence("The answer is NOBORDER here.")
        self.assertEqual(label, "NOBORDER")

    def test_summarize_parse_diagnostics(self) -> None:
        entries = [
            {"parse_ok": True, "truncation_suspect": False, "output_chars": 100, "raw": "ok"},
            {"parse_ok": False, "truncation_suspect": True, "output_chars": 50, "raw": "bad", "index": 1},
            {"parse_ok": False, "truncation_suspect": True, "output_chars": 60, "raw": "worse", "index": 2},
        ]
        summary = summarize_parse_diagnostics(entries, max_samples=2)
        self.assertEqual(summary["parse_failure_count"], 2)
        self.assertEqual(summary["parse_failure_rate"], 0.6667)
        self.assertEqual(summary["truncation_suspect_count"], 2)
        self.assertEqual(len(summary["sample_parse_failures"]), 2)

    def test_recommended_max_new_tokens_by_format(self) -> None:
        self.assertEqual(recommended_max_new_tokens("cot_list"), 256)
        self.assertEqual(recommended_max_new_tokens("json"), 96)
        self.assertEqual(recommended_max_new_tokens("no_cot"), 128)


if __name__ == "__main__":
    unittest.main()
