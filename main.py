from backend import (
    get_llm,
    research_product,
    search_prices_serper,
    summarize_prices_for_prompt,
    build_final_report,
    make_price_rows,
)

def main():
    query = "Nike Pegasus 40 running shoes"
    top_n = 8
    usd_inr = 83.0

    llm = get_llm()
    print("\n==============================")
    print(" STEP 1: Product Research")
    print("==============================")
    research = research_product(llm, query)
    print(research)

    print("\n==============================")
    print(" STEP 2: Price Comparison")
    print("==============================")
    prices = search_prices_serper(f"{query} best price")
    rows = make_price_rows(prices, top_n=top_n, usd_inr=usd_inr)
    for r in rows:
        print(f"- {r['Title']} | {r['Price (INR)']} (orig: {r['Price (Original)']}) | {r['Link']}")

    print("\n==============================")
    print(" STEP 3: Final Report")
    print("==============================")
    price_summary = summarize_prices_for_prompt(prices, top_n=top_n, usd_inr=usd_inr)
    report = build_final_report(llm, research, price_summary)
    print(report)

if __name__ == "__main__":
    main()
