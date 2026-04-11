from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

import batch_chat_test
import main_progressive_training as pipeline
import preview_training


def test_compute_steps_and_checkpoint_helpers() -> None:
    assert pipeline.compute_max_steps(0) == pipeline.DEFAULT_CONFIG["min_steps"]
    assert pipeline.compute_max_steps(999, override=1234) == 1234
    assert pipeline.compute_save_steps(50) == 100
    assert pipeline.compute_save_steps(2500) == 250


def test_get_period_directories_and_cumulative_texts(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    (data_dir / "east" / "older (BC)").mkdir(parents=True)
    (data_dir / "east" / "older (BC)" / "a.txt").write_text("one", encoding="utf-8")
    (data_dir / "east" / "100").mkdir(parents=True)
    (data_dir / "east" / "100" / "b.txt").write_text("two", encoding="utf-8")

    dirs = pipeline.get_period_directories("east", "100", str(data_dir))
    assert [d.name for d in dirs] == ["older (BC)", "100"]

    texts = pipeline.load_cumulative_texts("east", "100", str(data_dir))
    assert texts == ["one", "two"]


def test_save_training_manifest_round_trips(tmp_path: Path) -> None:
    manifest_path = tmp_path / "training_manifest.json"
    pipeline.save_training_manifest(
        manifest_path,
        period="100",
        east_checkpoint=tmp_path / "east" / "checkpoint-1",
        west_checkpoint=tmp_path / "west" / "checkpoint-2",
        training_config={"learning_rate": 1e-4},
    )

    saved = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert saved["100"]["east_checkpoint"].endswith("checkpoint-1")
    assert saved["100"]["training_config"]["learning_rate"] == 1e-4


def test_batch_chat_run_writes_expected_json(tmp_path: Path, monkeypatch) -> None:
    checkpoint = tmp_path / "checkpoint"
    checkpoint.mkdir()
    output_path = tmp_path / "results.json"

    class DummyModel:
        pass

    class DummyEncoding:
        pass

    monkeypatch.setattr(batch_chat_test, "load_model", lambda path, device: DummyModel())
    monkeypatch.setattr(batch_chat_test, "get_tokenizer", lambda: DummyEncoding())
    monkeypatch.setattr(
        batch_chat_test,
        "generate_with_history",
        lambda model, encoding, prompt, history, max_new_tokens, temperature, device: (
            f"reply:{prompt}",
            history + prompt,
        ),
    )

    results = batch_chat_test.run_batch_chat_test(
        checkpoint_path=str(checkpoint),
        output_path=str(output_path),
        max_new_tokens=12,
        temperature=0.2,
    )

    saved = json.loads(output_path.read_text(encoding="utf-8"))
    assert len(saved["responses"]) == len(batch_chat_test.PHILOSOPHICAL_PROMPTS)
    assert saved["responses"][0]["response"].startswith("reply:")
    assert results["config"]["temperature"] == 0.2


def test_preview_training_main_validates_and_runs(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        preview_training,
        "get_period_directories",
        lambda region, period, data_dir: [Path(f"/{region}/{period}")],
    )
    monkeypatch.setattr(
        preview_training,
        "load_cumulative_texts",
        lambda region, period, data_dir: [f"{region}:{period}"],
    )
    monkeypatch.setattr(sys, "argv", ["preview_training.py", "--periods", "100", "--regions", "east", "--data-dir", "./data"])

    result = preview_training.main()

    assert result == 0
    assert "PROGRESSIVE TRAINING PIPELINE PREVIEW" in capsys.readouterr().out


def test_progressive_training_main_smoke(tmp_path: Path, monkeypatch) -> None:
    data_dir = tmp_path / "data"
    (data_dir / "east" / "100").mkdir(parents=True)
    (data_dir / "west" / "100").mkdir(parents=True)

    monkeypatch.setattr(
        pipeline,
        "train_period_model",
        lambda region, period, output_base_dir, config, data_base_dir, max_steps_override: tmp_path / f"{region}-{period}" / "checkpoint-1",
    )
    monkeypatch.setattr(
        pipeline,
        "resolve_latest_checkpoint",
        lambda period_dir: period_dir / "checkpoint-1",
    )

    eval_calls: list[tuple] = []
    monkeypatch.setattr(pipeline, "run_evaluate_bias", lambda *args: eval_calls.append(args) or Path(args[3]))
    monkeypatch.setattr(pipeline, "run_batch_chat_test", lambda *args: eval_calls.append(args) or Path(args[3]))
    monkeypatch.setattr(pipeline.sys, "argv", ["main_progressive_training.py", "--periods", "100", "--regions", "east", "west", "--output-dir", str(tmp_path), "--data-dir", str(data_dir), "--skip-evaluation"])

    pipeline.main()

    assert (tmp_path / "training_manifest.json").exists()
    assert eval_calls == []
