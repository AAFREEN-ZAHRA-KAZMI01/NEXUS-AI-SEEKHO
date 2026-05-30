import uuid
from datetime import datetime, timezone
from utils.helpers import now_iso
from utils.rag_store import add_document, collection

SEED_DATA = {
    "logistics": [
        "Karachi port handles 60% of Pakistan's imports. Congestion at Karachi port typically increases inland freight costs by 15-25%.",
        "Fuel prices in Pakistan are revised fortnightly by OGRA. A 10% increase in petrol prices typically increases logistics costs by 6-8%.",
        "The National Highway Authority (NHA) reports that road freight accounts for over 90% of land cargo traffic in Pakistan, with transit times between Karachi and Lahore averaging 48-72 hours.",
        "Axle load limit enforcement by the Ministry of Communications regularly reduces payload capacity of heavy transport vehicles by 20-30%, raising short-term shipping rates.",
        "Interprovincial trade transit taxes and checking checkpoints across Sindh and Punjab borders add 5-10% delays and operational overhead for logistics operators."
    ],
    "finance": [
        "SBP monetary policy decisions directly affect commercial lending rates within 48-72 hours of announcement.",
        "KSE-100 index movements above 2% in a single session typically indicate significant market sentiment shift.",
        "The Federal Board of Revenue (FBR) tax collection targets and audits regularly impact corporate liquidity and cash flow management for Pakistani listed entities.",
        "Foreign exchange reserves at the State Bank of Pakistan directly govern letters of credit (LC) approval rates for industrial raw material imports.",
        "Interbank exchange rate volatility of the Pakistani Rupee (PKR) against the US Dollar (USD) directly impacts currency risk hedging costs for trade financing."
    ],
    "healthcare": [
        "DRAP drug approval process takes 6-18 months. Import permits for essential medicines can be expedited in 2-4 weeks under shortage protocol.",
        "The Drug Pricing Committee of DRAP regulates retail prices of essential medicines, causing supply chain friction when global raw material prices increase.",
        "Public sector healthcare procurement in Punjab is managed by the Primary and Secondary Healthcare Department, which operates under strict annual budgetary cycles.",
        "The National Health Vision of Pakistan targets localized production of API (Active Pharmaceutical Ingredients) to decrease import reliance from 90% to 50%.",
        "Private sector healthcare services in Karachi and Lahore account for over 70% of outpatient treatments, funded primarily via out-of-pocket patient expenditures."
    ],
    "policy": [
        "SECP regulations require listed companies to disclose material information within 24 hours of occurrence.",
        "The Federal Budget of Pakistan, presented annually in June, establishes customs duties and sales tax exemptions that immediately dictate sector profitability.",
        "NEPRA determines power tariffs quarterly based on fuel price adjustments, causing unexpected utility overhead increases for manufacturing units.",
        "Board of Investment (BOI) guidelines provide special economic zone (SEZ) incentives, including 10-year income tax holidays, to boost export-oriented manufacturing.",
        "The Competition Commission of Pakistan (CCP) monitors cartelization and anti-competitive behavior in major sectors such as cement, sugar, and wheat."
    ]
}

def seed_if_needed():
    """
    Check if the collection has fewer than 10 documents, and if so,
    seed it with 20 realistic Pakistan-specific facts.
    """
    count = collection.count()
    if count < 10:
        print(f"ChromaDB has {count} documents. Seeding 20 domain-relevant knowledge snippets...")
        timestamp = now_iso()
        for domain, snippets in SEED_DATA.items():
            for idx, text in enumerate(snippets):
                doc_id = f"seed_{domain}_{idx}"
                metadata = {
                    "domain": domain,
                    "source": "seed_data",
                    "timestamp": timestamp,
                    "session_id": "seed"
                }
                add_document(doc_id, text, metadata)
        print(f"Seeding completed. ChromaDB count now: {collection.count()}")
    else:
        print(f"ChromaDB has {count} documents. Seeding skipped.")

if __name__ == "__main__":
    seed_if_needed()
