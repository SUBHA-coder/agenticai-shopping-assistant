# import os
# import pandas as pd
# import streamlit as st
# from dotenv import load_dotenv

# from backend import (
#     get_llm,
#     research_product,
#     search_prices_serper,
#     summarize_prices_for_prompt,
#     make_price_rows,
#     build_final_report,
# )

# load_dotenv()

# st.set_page_config(page_title="Shopping Assistant (INR)", page_icon="🛍️", layout="wide")

# # ---- Aesthetic Header ----
# st.markdown(
#     """
#     <style>
#     .big-title {font-size: 34px; font-weight: 700; margin-bottom: 4px;}
#     .subtle {color: #6b7280;}
#     .card {background: #0f172a0d; padding: 16px 18px; border-radius: 16px; border: 1px solid #e5e7eb;}
#     .pill {display:inline-block; padding:4px 10px; border-radius:999px; border:1px solid #e5e7eb; font-size:12px; color:#374151; background:#fff;}
#     a {text-decoration: none;}
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# st.markdown('<div class="big-title">🛍️ Shopping Assistant</div>', unsafe_allow_html=True)
# st.markdown('<div class="subtle">Research products, compare prices, and get a clean recommendation for Indian buyers.</div>', unsafe_allow_html=True)
# st.markdown("")

# # ---- Inputs ----
# col1, col2, col3 = st.columns([4, 1.4, 1.8])
# with col1:
#     query = st.text_input(
#         "Product query",
#         value="Nike Pegasus 40 running shoes",
#         placeholder="e.g., Apple AirPods Pro 2, Adidas Adizero Boston 12 ..."
#     )
# with col2:
#     top_n = st.number_input("Top N prices", min_value=3, max_value=20, value=8, step=1)
# with col3:
#     usd_inr = st.number_input("USD→INR rate", min_value=50.0, max_value=200.0, value=83.0, step=0.5)

# run = st.button("🔎 Run Search", use_container_width=True)

# # ---- Results ----
# if run:
#     try:
#         llm = get_llm()

#         with st.spinner("Researching product details..."):
#             research = research_product(llm, query)

#         with st.spinner("Fetching prices..."):
#             prices_json = search_prices_serper(f"{query} best price")

#         # Build table rows
#         rows = make_price_rows(prices_json, top_n=int(top_n), usd_inr=float(usd_inr))
#         df = pd.DataFrame(rows)

#         # Summarize for LLM
#         price_summary_text = summarize_prices_for_prompt(prices_json, top_n=int(top_n), usd_inr=float(usd_inr))

#         with st.spinner("Generating final report..."):
#             report = build_final_report(llm, research, price_summary_text)

#         st.markdown("## 🔍 Research")
#         st.markdown(f'<div class="card">{research}</div>', unsafe_allow_html=True)

#         st.markdown("## 💸 Price Comparison (converted to INR)")
#         if not df.empty:
#             st.dataframe(df, use_container_width=True, hide_index=True)
#         else:
#             st.info("No shopping results found.")

#         st.markdown("## ✅ Final Recommendation")
#         st.markdown(f'<div class="card">{report}</div>', unsafe_allow_html=True)

#     except Exception as e:
#         st.error(f"Something went wrong: {e}")
# else:
#     st.markdown('<span class="pill">Tip</span> Enter a product name and click “Run Search”.', unsafe_allow_html=True)
import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from backend import (
    get_llm,
    research_product,
    search_prices_serper,
    summarize_prices_for_prompt,
    make_price_rows,
    build_final_report,
)

# ---- Load environment ----
load_dotenv()
st.set_page_config(page_title="Shopping Assistant (INR)", page_icon="🛍️", layout="wide")

# ---- CSS for aesthetics and animation ----
st.markdown(
    """
    <style>
    .big-title {font-size: 36px; font-weight: 700; margin-bottom: 4px; color: #1f2937;}
    .subtle {color: #6b7280; font-size:14px; margin-bottom:12px;}
    .card {background: #ffffff; padding: 16px 18px; border-radius: 16px; border: 1px solid #e5e7eb; box-shadow: 0 2px 10px rgba(0,0,0,0.08); transition: transform 0.2s;}
    .card:hover {transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.15);}
    .product-img {width: 100%; height: 200px; object-fit: contain; border-radius: 12px;}
    .pill {display:inline-block; padding:4px 10px; border-radius:999px; border:1px solid #e5e7eb; font-size:12px; color:#374151; background:#f3f4f6;}
    a {text-decoration: none; color: #1a73e8;}
    </style>
    """,
    unsafe_allow_html=True
)

# ---- Header ----
st.markdown('<div class="big-title">🛍️ Shopping Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtle">Research products, compare prices, and get a clean recommendation for Indian buyers.</div>', unsafe_allow_html=True)
st.markdown("")

# ---- Inputs ----
col1, col2, col3 = st.columns([4, 1.4, 1.8])
with col1:
    query = st.text_input(
        "Product query",
        value="Nike Pegasus 40 running shoes",
        placeholder="e.g., Apple AirPods Pro 2, Adidas Adizero Boston 12 ..."
    )
with col2:
    top_n = st.number_input("Top N prices", min_value=3, max_value=20, value=8, step=1)
with col3:
    usd_inr = st.number_input("USD→INR rate", min_value=50.0, max_value=200.0, value=83.0, step=0.5)

run = st.button("🔎 Run Search", use_container_width=True)

# ---- Results Section ----
if run:
    try:
        llm = get_llm()

        # Step 1: Research product
        with st.spinner("Researching product details..."):
            research = research_product(llm, query)

        # Step 2: Fetch prices
        with st.spinner("Fetching prices..."):
            prices_json = search_prices_serper(f"{query} best price")

        # Step 3: Build table rows
        rows = make_price_rows(prices_json, top_n=int(top_n), usd_inr=float(usd_inr))
        df = pd.DataFrame(rows)

        # Step 4: Summarize prices for final report
        price_summary_text = summarize_prices_for_prompt(prices_json, top_n=int(top_n), usd_inr=float(usd_inr))

        # Step 5: Generate final report
        with st.spinner("Generating final recommendation..."):
            report = build_final_report(llm, research, price_summary_text)

        # ---- Display Research ----
        st.markdown("## 🔍 Product Research")
        st.markdown(f'<div class="card">{research}</div>', unsafe_allow_html=True)

        # ---- Display Prices as Animated Cards ----
        st.markdown("## 💸 Price Comparison (INR)")
        if not df.empty:
            col_count = 3
            cols = st.columns(col_count)
            for idx, row in df.iterrows():
                col = cols[idx % col_count]
                with col:
                    st.markdown(
                        f"""
                        <div class="card">
                            <img class="product-img" src="{row.get('image','https://via.placeholder.com/250')}" alt="product">
                            <h4>{row.get('title','No title')}</h4>
                            <p><strong>Price:</strong> ₹{row.get('price_inr','N/A')}</p>
                            <p><strong>Vendor:</strong> {row.get('vendor','N/A')}</p>
                            <a href="{row.get('link','#')}" target="_blank">Buy Now</a>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        else:
            st.info("No shopping results found.")

        # ---- Display Final Recommendation ----
        st.markdown("## ✅ Final Recommendation")
        st.markdown(f'<div class="card">{report}</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Something went wrong: {e}")
else:
    st.markdown('<span class="pill">Tip</span> Enter a product name and click “Run Search”.', unsafe_allow_html=True)
