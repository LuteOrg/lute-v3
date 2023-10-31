def pytest_addoption(parser):
    parser.addoption("--port", action="store", type=int, help="Specify the port number")
