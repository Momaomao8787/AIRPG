import importlib.metadata

def check_package(package_name):
    try:
        version = importlib.metadata.version(package_name)
        print(f"{package_name}: {version}")
    except importlib.metadata.PackageNotFoundError:
        print(f"{package_name}: NOT FOUND")

check_package("chromadb")
check_package("pydantic")
check_package("langchain-chroma")
