from {{ project_name }}.main import main


def test_main_execution(capsys):
    """Test the main entry point output."""
    try:
        main()
    except SystemExit:
        pass

    captured = capsys.readouterr()
    assert "Starting" in captured.out
