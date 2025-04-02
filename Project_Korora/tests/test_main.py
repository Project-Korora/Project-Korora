from Project_Korora.src.main import main

def test_main_output(capsys):
    main()
    captured = capsys.readouterr()
    assert "Project Kororā" in captured.out
