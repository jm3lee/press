from pie import check_post_build


def make_cfg(path):
    path.write_text("- static/indextree.json\n")
    return path


def test_main_reports_missing(tmp_path):
    build = tmp_path / "build"
    build.mkdir()
    cfg = make_cfg(tmp_path / "cfg.yml")
    rc = check_post_build.main([str(build), "-c", str(cfg), "-l", str(tmp_path / "log.txt")])
    assert rc == 1


def test_main_passes_and_logs(tmp_path):
    build = tmp_path / "build" / "static"
    build.mkdir(parents=True)
    (build / "indextree.json").write_text("{}", encoding="utf-8")
    cfg = make_cfg(tmp_path / "cfg.yml")
    log = tmp_path / "log.txt"
    rc = check_post_build.main([str(tmp_path / "build"), "-c", str(cfg), "-l", str(log)])
    assert rc == 0
    assert log.exists()


def test_parse_args_defaults():
    args = check_post_build.parse_args([])
    assert args.directory == "build"
    assert args.config == "cfg/check-post-build.yml"
    assert args.log == "log/check-post-build.txt"
