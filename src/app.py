from pipeline import run_topic_pipeline
import argparse, json

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True)
    ap.add_argument("--subtopics", nargs="*")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    result = run_topic_pipeline(args.topic, args.subtopics)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
