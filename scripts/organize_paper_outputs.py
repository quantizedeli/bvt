from pathlib import Path
import shutil


def main():
    out = Path("output")
    paper = out / "paper"
    paper.mkdir(exist_ok=True)
    for d in out.glob("level*"):
        if d.is_dir():
            target = paper / d.name
            target.mkdir(exist_ok=True)
            for p in d.glob("*.png"):
                shutil.copy2(p, target / p.name)
    for p in (out / "html").glob("*.png") if (out / "html").exists() else []:
        target = paper / "html"
        target.mkdir(exist_ok=True)
        shutil.copy2(p, target / p.name)
    print(paper)


if __name__ == "__main__":
    main()
