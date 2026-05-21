# newsops/agents/mock_responses.py
import copy

def get_mock_ingestion(domain: str) -> dict:
    resp = MOCK_INGESTIONS.get(domain, MOCK_INGESTIONS["business"])
    return copy.deepcopy(resp)

def get_mock_research(domain: str) -> dict:
    resp = MOCK_RESEARCHES.get(domain, MOCK_RESEARCHES["business"])
    return copy.deepcopy(resp)

def get_mock_analysis(domain: str) -> dict:
    resp = MOCK_ANALYSES.get(domain, MOCK_ANALYSES["business"])
    return copy.deepcopy(resp)

def get_mock_decision(domain: str) -> dict:
    resp = MOCK_DECISIONS.get(domain, MOCK_DECISIONS["business"])
    return copy.deepcopy(resp)


MOCK_INGESTIONS = {
    "finance": {
        "agent": "ingestion",
        "input_type": "text",
        "domain": "finance",
        "source": "direct_text",
        "timestamp": "2026-05-18T00:00:00Z",
        "facts": [
            {
                "text": "KSE-100 index dropped 847 points today",
                "subject": "KSE-100 index",
                "direction": "decrease",
                "value": 847,
                "unit": "points",
                "date_reference": "today"
            },
            {
                "text": "Foreign investors pulled $200M out of Pakistani equities",
                "subject": "foreign investment",
                "direction": "decrease",
                "value": 200,
                "unit": "USD millions",
                "date_reference": "today"
            },
            {
                "text": "IMF loan uncertainty caused market pressure",
                "subject": "IMF negotiations",
                "direction": "neutral",
                "value": None,
                "unit": None,
                "date_reference": "today"
            }
        ],
        "entities": {
            "organizations": ["KSE", "SECP", "IMF"],
            "locations": ["Pakistan", "Karachi"],
            "people": [],
            "regulations": [],
            "products": [],
            "currencies": ["USD", "PKR"]
        },
        "raw_numbers": [
            { "value": "847", "unit": "points", "context": "dropped 847 points" },
            { "value": "200M", "unit": "USD", "context": "pulled $200M" }
        ],
        "document_meta": {
            "title": "KSE Market Crash Signal",
            "source_domain": None,
            "total_rows": None,
            "pages": None
        },
        "confidence": "high"
    },
    "policy": {
        "agent": "ingestion",
        "input_type": "text",
        "domain": "policy",
        "source": "direct_text",
        "timestamp": "2026-05-18T00:00:00Z",
        "facts": [
            {
                "text": "OGRA has notified a PKR 12.74 per litre increase in petrol prices",
                "subject": "petrol price",
                "direction": "increase",
                "value": 12.74,
                "unit": "PKR per litre",
                "date_reference": "midnight tonight"
            },
            {
                "text": "HSD diesel price rises by PKR 9.50 per litre",
                "subject": "diesel price",
                "direction": "increase",
                "value": 9.50,
                "unit": "PKR per litre",
                "date_reference": "midnight tonight"
            },
            {
                "text": "Notification cites global crude oil movement and PKR depreciation",
                "subject": "oil pricing drivers",
                "direction": "neutral",
                "value": None,
                "unit": None,
                "date_reference": "current"
            }
        ],
        "entities": {
            "organizations": ["OGRA", "Federal Government"],
            "locations": ["Islamabad", "Pakistan"],
            "people": [],
            "regulations": ["Petroleum Act 1934"],
            "products": ["Petrol", "High Speed Diesel"],
            "currencies": ["PKR"]
        },
        "raw_numbers": [
            { "value": "12.74", "unit": "PKR/litre", "context": "increase in petrol prices" },
            { "value": "9.50", "unit": "PKR/litre", "context": "rises by PKR 9.50" }
        ],
        "document_meta": {
            "title": "OGRA Pricing Notification",
            "source_domain": None,
            "total_rows": None,
            "pages": None
        },
        "confidence": "high"
    },
    "logistics": {
        "agent": "ingestion",
        "input_type": "text",
        "domain": "logistics",
        "source": "direct_text",
        "timestamp": "2026-05-18T00:00:00Z",
        "facts": [
            {
                "text": "Karachi Port Trust reports 47 vessels awaiting berth",
                "subject": "vessel berth queue",
                "direction": "increase",
                "value": 47,
                "unit": "vessels",
                "date_reference": "this week"
            },
            {
                "text": "Average container dwell time reaches 11.2 days",
                "subject": "dwell time",
                "direction": "increase",
                "value": 11.2,
                "unit": "days",
                "date_reference": "current"
            },
            {
                "text": "Freight costs have risen 18% since last month",
                "subject": "freight costs",
                "direction": "increase",
                "value": 18,
                "unit": "percent",
                "date_reference": "since last month"
            }
        ],
        "entities": {
            "organizations": ["Karachi Port Trust", "KPT", "National Logistics Cell", "NLC"],
            "locations": ["Karachi", "Gwadar"],
            "people": [],
            "regulations": [],
            "products": ["Containers", "CKD Kits"],
            "currencies": ["PKR"]
        },
        "raw_numbers": [
            { "value": "47", "unit": "vessels", "context": "47 vessels awaiting berth" },
            { "value": "11.2", "unit": "days", "context": "dwell time is 11.2 days" },
            { "value": "18", "unit": "percent", "context": "risen 18%" }
        ],
        "document_meta": {
            "title": "KPT Congestion Signal",
            "source_domain": None,
            "total_rows": None,
            "pages": None
        },
        "confidence": "high"
    },
    "healthcare": {
        "agent": "ingestion",
        "input_type": "text",
        "domain": "healthcare",
        "source": "direct_text",
        "timestamp": "2026-05-18T00:00:00Z",
        "facts": [
            {
                "text": "DRAP confirmed a critical shortage of Insulin Glargine 100IU/ml",
                "subject": "drug shortage",
                "direction": "decrease",
                "value": 100,
                "unit": "IU/ml",
                "date_reference": "current"
            },
            {
                "text": "Diabetic patients affected in Lahore and Rawalpindi public hospitals",
                "subject": "affected patients",
                "direction": "increase",
                "value": 12000,
                "unit": "patients",
                "date_reference": "current"
            },
            {
                "text": "Three manufacturers suspended production due to raw material import limits",
                "subject": "manufacturer suspension",
                "direction": "decrease",
                "value": 3,
                "unit": "manufacturers",
                "date_reference": "current"
            }
        ],
        "entities": {
            "organizations": ["DRAP", "Getz Pharma", "Searle", "Highnoon", "WHO"],
            "locations": ["Lahore", "Rawalpindi", "Punjab"],
            "people": [],
            "regulations": [],
            "products": ["Insulin Glargine", "API raw material"],
            "currencies": []
        },
        "raw_numbers": [
            { "value": "12000", "unit": "patients", "context": "12,000 diabetic patients" },
            { "value": "3", "unit": "manufacturers", "context": "Three manufacturers suspended" }
        ],
        "document_meta": {
            "title": "DRAP Insulin Advisory",
            "source_domain": None,
            "total_rows": None,
            "pages": None
        },
        "confidence": "high"
    },
    "urban": {
        "agent": "ingestion",
        "input_type": "text",
        "domain": "urban",
        "source": "direct_text",
        "timestamp": "2026-05-18T00:00:00Z",
        "facts": [
            {
                "text": "LESCO reports an 18-hour unplanned power outage in Lahore",
                "subject": "power outage",
                "direction": "increase",
                "value": 18,
                "unit": "hours",
                "date_reference": "today"
            },
            {
                "text": "Outage affects 340,000 households and 4,200 businesses",
                "subject": "affected units",
                "direction": "increase",
                "value": 340000,
                "unit": "households",
                "date_reference": "current"
            },
            {
                "text": "Grid fault at 132kV Kot Lakhpat substation",
                "subject": "substation failure",
                "direction": "neutral",
                "value": 132,
                "unit": "kV",
                "date_reference": "today"
            }
        ],
        "entities": {
            "organizations": ["LESCO"],
            "locations": ["Lahore", "Gulberg", "DHA", "Model Town", "Kot Lakhpat"],
            "people": [],
            "regulations": [],
            "products": ["Electricity", "Generators"],
            "currencies": ["PKR"]
        },
        "raw_numbers": [
            { "value": "18", "unit": "hours", "context": "18-hour unplanned power outage" },
            { "value": "340000", "unit": "households", "context": "340,000 households affected" }
        ],
        "document_meta": {
            "title": "LESCO Substation Outage Alert",
            "source_domain": None,
            "total_rows": None,
            "pages": None
        },
        "confidence": "high"
    },
    "business": {
        "agent": "ingestion",
        "input_type": "text",
        "domain": "business",
        "source": "direct_text",
        "timestamp": "2026-05-18T00:00:00Z",
        "facts": [
            {
                "text": "Q3 Karachi revenue down 31% versus Q2",
                "subject": "regional revenue",
                "direction": "decrease",
                "value": 31,
                "unit": "percent",
                "date_reference": "Q3 vs Q2"
            },
            {
                "text": "Monthly order volume fell from 1,240 to 856 orders",
                "subject": "order volume",
                "direction": "decrease",
                "value": 856,
                "unit": "orders",
                "date_reference": "monthly"
            },
            {
                "text": "Customer churn rate spiked to 18.4%",
                "subject": "customer churn",
                "direction": "increase",
                "value": 18.4,
                "unit": "percent",
                "date_reference": "current"
            }
        ],
        "entities": {
            "organizations": ["Karachi Division"],
            "locations": ["Karachi"],
            "people": [],
            "regulations": [],
            "products": ["SKU-1042 Basmati Rice", "SKU-2287 Cooking Oil", "SKU-3391 Detergent"],
            "currencies": ["PKR"]
        },
        "raw_numbers": [
            { "value": "31", "unit": "percent", "context": "Karachi revenue down 31%" },
            { "value": "856", "unit": "orders", "context": "fell to 856 orders" }
        ],
        "document_meta": {
            "title": "Karachi Division Sales Contraction",
            "source_domain": None,
            "total_rows": None,
            "pages": None
        },
        "confidence": "high"
    }
}

MOCK_RESEARCHES = {
    "finance": {
        "agent": "research",
        "domain": "finance",
        "claims_assessed": [
            {
                "claim": "KSE-100 dropped 847 points",
                "veracity": "confirmed",
                "evidence": "Daily stock summaries on PSX and Business Recorder confirm market closed 1.18% down."
            }
        ],
        "corroboration": "confirmed",
        "corroboration_evidence": [
            "SECP emergency coordination board meeting declared for liquidity relief steps."
        ],
        "additional_context": "The Pakistan Stock Exchange (PSX) index fluctuates directly based on IMF loan updates. A PKR 200M capital outflow is significant but typical during delays in international currency releases.",
        "contradictions": [],
        "recommended_sources": ["psx.com.pk", "sbp.org.pk", "brecorder.com"]
    },
    "policy": {
        "agent": "research",
        "domain": "policy",
        "claims_assessed": [
            {
                "claim": "OGRA petrol price increase of PKR 12.74",
                "veracity": "confirmed",
                "evidence": "Official gazette notification published on OGRA site matches petrol price rise of 12.74 PKR/litre."
            }
        ],
        "corroboration": "confirmed",
        "corroboration_evidence": [
            "Ministry of Energy confirmed deregulation updates under Petroleum Act 1934."
        ],
        "additional_context": "OGRA notifications are legally binding. Fuel updates trigger automatic freight revisions across standard logistics contracts under regional commerce guidelines.",
        "contradictions": [],
        "recommended_sources": ["ogra.org.pk", "finance.gov.pk"]
    },
    "logistics": {
        "agent": "research",
        "domain": "logistics",
        "claims_assessed": [
            {
                "claim": "KPT container dwell time reaches 11.2 days",
                "veracity": "confirmed",
                "evidence": "Karachi Port Trust operational logs indicate customs clearance backlogs leading to a 3x standard delay."
            }
        ],
        "corroboration": "confirmed",
        "corroboration_evidence": [
            "National Logistics Cell (NLC) reports heavy vehicle queues on KPT port access routes."
        ],
        "additional_context": "Congestion at KPT is caused by clearing limits. Logistics suppliers are active in moving containers to dry ports and the Gwadar corridor.",
        "contradictions": [],
        "recommended_sources": ["kpt.gov.pk", "nlc.com.pk"]
    },
    "healthcare": {
        "agent": "research",
        "domain": "healthcare",
        "claims_assessed": [
            {
                "claim": "Critical shortage of Insulin Glargine",
                "veracity": "confirmed",
                "evidence": "Punjab Health Department hospital audit reports diabetic patients experiencing insulin shortages."
            }
        ],
        "corroboration": "confirmed",
        "corroboration_evidence": [
            "DRAP shortage portal shows manufacturing import approvals delayed."
        ],
        "additional_context": "Insulin Glargine requires cold chain logistics. API shortages are related to regional letter of credit limits for pharmaceutical imports.",
        "contradictions": [],
        "recommended_sources": ["drap.gov.pk", "who.int/pakistan"]
    },
    "urban": {
        "agent": "research",
        "domain": "urban",
        "claims_assessed": [
            {
                "claim": "18-hour outage DHA Lahore",
                "veracity": "confirmed",
                "evidence": "LESCO official outage board indicates a physical transformer fault at Kot Lakhpat sub-station."
            }
        ],
        "corroboration": "confirmed",
        "corroboration_evidence": [
            "Lahore Cantonment urban management reports local back-up gensets reaching run-time maximums."
        ],
        "additional_context": "Kot Lakhpat sub-station supplies primary industrial feed to Lahores east zones. Unplanned downtime has huge costs for local manufacture.",
        "contradictions": [],
        "recommended_sources": ["lesco.gov.pk", "wasa.lahore.gov.pk"]
    },
    "business": {
        "agent": "research",
        "domain": "business",
        "claims_assessed": [
            {
                "claim": "Karachi Q3 revenue down 31%",
                "veracity": "confirmed",
                "evidence": "Karachi branch financial sheets confirm revenue decline from 8.5M PKR to 5.87M PKR."
            }
        ],
        "corroboration": "confirmed",
        "corroboration_evidence": [
            "CRM churn trackers indicate loss of 47 major consumer accounts."
        ],
        "additional_context": "Revenue issues are related to competitor pricing pressure and local retail inflation impacting consumer sales of premium SKUs.",
        "contradictions": [],
        "recommended_sources": ["secp.gov.pk", "pbs.gov.pk"]
    }
}

MOCK_ANALYSES = {
    "finance": {
        "agent": "analysis",
        "domain": "finance",
        "severity": 9,
        "severity_label": "Critical",
        "severity_reasoning": "Capital outflow of USD 200M triggers severe macro currency pressure, pushing USD/PKR up by 2.3% and impacting export revenue risk. Fits severity 9 rubric.",
        "time_horizon": "immediate",
        "kpis_affected": [
            {
                "kpi": "usd_pkr_rate",
                "current_value": 278.50,
                "current_unit": "PKR/USD",
                "projected_value": 285.00,
                "delta": 6.5,
                "delta_pct": 2.33,
                "direction": "increase"
            },
            {
                "kpi": "export_revenue_at_risk_pkr",
                "current_value": 12000000.0,
                "current_unit": "PKR",
                "projected_value": 14500000.0,
                "delta": 2500000.0,
                "delta_pct": 20.83,
                "direction": "increase"
            }
        ],
        "total_impact": {
            "financial_pkr": 57600000.0,
            "operational": "Severe forex hedging risk on short-term contracts.",
            "human": "Decreased purchasing power due to currency deval.",
            "reputational": "high"
        },
        "affected_parties": ["Export Sales Division", "Treasury Team", "Board of Directors"],
        "second_order_effects": [
            "Forex reserve drawdown causing interbank liquidity crunches.",
            "Increased import costs for manufacturing raw inputs."
        ],
        "reasoning_chain": [
            "IMF loan uncertainty -> capital flight",
            "Outflow of USD 200M -> PKR depreciation pressure",
            "USD/PKR climbs from 278.5 to 285",
            "Unhedged export contract values decline in real USD terms"
        ],
        "data_gaps": []
    },
    "policy": {
        "agent": "analysis",
        "domain": "policy",
        "severity": 8,
        "severity_label": "High",
        "severity_reasoning": "OGRA fuel notification leads to a direct fuel price rise of ~5% in petrol and ~4% in diesel, severely impacting contract margins and transportation costs.",
        "time_horizon": "immediate",
        "kpis_affected": [
            {
                "kpi": "compliance_tasks_open",
                "current_value": 0.0,
                "current_unit": "tasks",
                "projected_value": 5.0,
                "delta": 5.0,
                "delta_pct": 100.0,
                "direction": "increase"
            },
            {
                "kpi": "affected_categories",
                "current_value": 0.0,
                "current_unit": "contract categories",
                "projected_value": 3.0,
                "delta": 3.0,
                "delta_pct": 100.0,
                "direction": "increase"
            }
        ],
        "total_impact": {
            "financial_pkr": 2400000.0,
            "operational": "Required immediate adjustment to all freight and delivery surcharge rates.",
            "human": "High fuel costs impact logistics drivers' independent earnings.",
            "reputational": "medium"
        },
        "affected_parties": ["Logistics Ops", "Contract Compliance Team", "Finance Division"],
        "second_order_effects": [
            "Surcharge increases passed down to consumer delivery products.",
            "Independent carrier union strikes protesting diesel hikes."
        ],
        "reasoning_chain": [
            "OGRA announces PKR 12.74/L hike",
            "Logistics fuel costs spike immediately by ~4.5%",
            "Existing shipping contracts become unprofitable without fuel adjustments",
            "Emergency audits triggered for standard commercial transport logs"
        ],
        "data_gaps": []
    },
    "logistics": {
        "agent": "analysis",
        "domain": "logistics",
        "severity": 8,
        "severity_label": "High",
        "severity_reasoning": "Port dwell time spike to 11.2 days leads to critical production line risks, with 18% freight cost surge causing significant weekly margins loss.",
        "time_horizon": "immediate",
        "kpis_affected": [
            {
                "kpi": "delivery_price_per_kg",
                "current_value": 2.40,
                "current_unit": "PKR/kg",
                "projected_value": 2.83,
                "delta": 0.43,
                "delta_pct": 17.92,
                "direction": "increase"
            },
            {
                "kpi": "on_time_delivery_pct",
                "current_value": 87.50,
                "current_unit": "percent",
                "projected_value": 68.20,
                "delta": -19.30,
                "delta_pct": -22.06,
                "direction": "decrease"
            }
        ],
        "total_impact": {
            "financial_pkr": 4850000.0,
            "operational": "Severe port dwell times disrupt inventory replenishment cycles.",
            "human": "Warehouse workers experience extreme overtime demands.",
            "reputational": "high"
        },
        "affected_parties": ["Warehouse Ops", "Procurement Division", "Key Account Managers"],
        "second_order_effects": [
            "Shortage of auto manufacturing components.",
            "Retail inventory out-of-stocks for winter product ranges."
        ],
        "reasoning_chain": [
            "KPT port congestion peaks at 47 vessels",
            "Average dwell time rises to 11.2 days",
            "Freight prices surge 18% due to carrier shortage",
            "Customer SLA violations trigger auto penalties"
        ],
        "data_gaps": []
    },
    "healthcare": {
        "agent": "analysis",
        "domain": "healthcare",
        "severity": 10,
        "severity_label": "Critical",
        "severity_reasoning": "Critical shortage of Insulin Glargine impacts over 12,000 patients in Lahore and Punjab public clinics, triggering severe clinical risks and WHO level notifications.",
        "time_horizon": "immediate",
        "kpis_affected": [
            {
                "kpi": "drug_availability_pct",
                "current_value": 94.00,
                "current_unit": "percent",
                "projected_value": 68.00,
                "delta": -26.00,
                "delta_pct": -27.66,
                "direction": "decrease"
            },
            {
                "kpi": "patients_at_risk",
                "current_value": 0.00,
                "current_unit": "patients",
                "projected_value": 12000.00,
                "delta": 12000.00,
                "delta_pct": 100.00,
                "direction": "increase"
            }
        ],
        "total_impact": {
            "financial_pkr": 15000000.0,
            "operational": "Emergency cold chain transport required for active drug re-routing.",
            "human": "12,000 diabetic patients facing life-threatening insulin access failure.",
            "reputational": "high"
        },
        "affected_parties": ["Public Health Directorate", "Hospital Emergency Units", "Procurement Division"],
        "second_order_effects": [
            "Spike in diabetic ketoacidosis emergency admissions.",
            "Retail black market pricing of insulin glargine rising 300%."
        ],
        "reasoning_chain": [
            "API raw material import limits applied",
            "Searle and Highnoon suspend local manufacturing",
            "Hospital stocks of Insulin Glargine deplete below safety threshold",
            "12,000 diabetic patients lose clinical prescription coverage"
        ],
        "data_gaps": []
    },
    "urban": {
        "agent": "analysis",
        "domain": "urban",
        "severity": 9,
        "severity_label": "Critical",
        "severity_reasoning": "LESCO 18-hour outage affects 340k households and 4.2k commercial units, causing huge losses to local businesses and massive backup generator fuel demand.",
        "time_horizon": "immediate",
        "kpis_affected": [
            {
                "kpi": "active_faults",
                "current_value": 0.00,
                "current_unit": "grid faults",
                "projected_value": 1.00,
                "delta": 1.00,
                "delta_pct": 100.00,
                "direction": "increase"
            },
            {
                "kpi": "population_affected",
                "current_value": 0.00,
                "current_unit": "people",
                "projected_value": 340000.00,
                "delta": 340000.00,
                "delta_pct": 100.00,
                "direction": "increase"
            }
        ],
        "total_impact": {
            "financial_pkr": 18500000.0,
            "operational": "Complete grid shutdown in DHA, Gulberg, and Johar Town segments.",
            "human": "340,000 citizens experiencing high heat index without power.",
            "reputational": "high"
        },
        "affected_parties": ["Grid Maintenance Division", "Local Businesses", "Residential Management"],
        "second_order_effects": [
            "Severe backup diesel generator failures due to continuous runs.",
            "Traffic signal outages causing heavy gridlock in Lahore east zones."
        ],
        "reasoning_chain": [
            "Kot Lakhpat substation substation breaker fails",
            "LESCO grid segment experiences total outage",
            "Commercial activities stop, causing PKR 45M hourly regional loss",
            "Citizen complaints spike to absolute maximums"
        ],
        "data_gaps": []
    },
    "business": {
        "agent": "analysis",
        "domain": "business",
        "severity": 8,
        "severity_label": "High",
        "severity_reasoning": "Karachi Q3 revenue contraction of 31% is a major sales failure, driven by 30% drop in order volumes and critical SKU level account churn.",
        "time_horizon": "medium_term",
        "kpis_affected": [
            {
                "kpi": "regional_revenue_pkr",
                "current_value": 8500000.0,
                "current_unit": "PKR",
                "projected_value": 5870000.0,
                "delta": -2630000.0,
                "delta_pct": -30.94,
                "direction": "decrease"
            },
            {
                "kpi": "order_volume_monthly",
                "current_value": 1240.0,
                "current_unit": "orders",
                "projected_value": 856.0,
                "delta": -384.0,
                "delta_pct": -30.97,
                "direction": "decrease"
            }
        ],
        "total_impact": {
            "financial_pkr": 2630000.0,
            "operational": "High inventory pileup of premium food and laundry SKUs.",
            "human": "Karachi sales team commissions drop by 45%.",
            "reputational": "medium"
        },
        "affected_parties": ["Karachi Sales Team", "Inventory Controllers", "Regional Sales Director"],
        "second_order_effects": [
            "Warehouse holding costs increase due to slow SKU turnover.",
            "Competitor brands capturing retail shelf space in Karachi."
        ],
        "reasoning_chain": [
            "Inflation impacts consumer purchase of Premium Basmati SKUs",
            " Karachis 47 high-volume B2B retail buyers halt replenishment orders",
            "Monthly order volumes collapse from 1,240 to 856",
            "Karachi division sales revenues contract by PKR 2.63M"
        ],
        "data_gaps": []
    }
}

MOCK_DECISIONS = {
    "finance": {
        "agent": "decision",
        "domain": "finance",
        "candidates_evaluated": 5,
        "actions": [
            {
                "rank": 1,
                "action_id": "A1",
                "action_type": "book_hedging_contract",
                "description": "Book USD/PKR forward contracts at current interbank rate to protect export receivables from devaluation.",
                "api_endpoint": "POST /api/finance/hedging/book",
                "api_payload": {
                    "currency_pair": "USD/PKR",
                    "amount_usd": 12000000,
                    "duration_days": 90,
                    "rate": 285.00
                },
                "quantified_delta": "Locks in PKR 3.42B of exposure at 285 PKR/USD for 90 days",
                "feasibility_score": 8,
                "impact_score": 9,
                "composite_score": 8.6,
                "justification": "Capital flight of USD 200M drives PKR depreciation. Hedging USD 12M at 285 prevents further revenue erosion on unhedged export contracts. Expected to protect PKR 2.5M in at-risk export revenue.",
                "success_metric": "hedged_amount_usd in state increases by 12000000",
                "time_to_execute": "< 4 hours"
            },
            {
                "rank": 2,
                "action_id": "A2",
                "action_type": "update_export_pricing",
                "description": "Update export contract pricing to reflect new 2.33% USD/PKR rate increase.",
                "api_endpoint": "POST /api/finance/pricing/export_update",
                "api_payload": {
                    "currency_pair": "USD/PKR",
                    "rate_delta_pct": 2.33,
                    "affected_contracts": ["CONTRACT-001", "CONTRACT-002", "CONTRACT-003"],
                    "effective_date": "2026-05-21T00:00:00Z"
                },
                "quantified_delta": "3 contracts repriced to reflect PKR 285 exchange rate",
                "feasibility_score": 9,
                "impact_score": 7,
                "composite_score": 7.8,
                "justification": "Contracts priced at old 278.5 rate become unprofitable. Repricing immediately closes the 2.33% gap and restores margin on active export deals.",
                "success_metric": "contracts_repriced increases to 3 in state",
                "time_to_execute": "< 2 hours"
            }
        ],
        "recommended_execution_sequence": [1, 2],
        "auto_execute_rank_1": True,
        "reasoning_summary": "Hedging is prioritized because it locks in rate before further depreciation. Export repricing follows to close revenue gap on existing contracts."
    },
    "policy": {
        "agent": "decision",
        "domain": "policy",
        "candidates_evaluated": 5,
        "actions": [
            {
                "rank": 1,
                "action_id": "A1",
                "action_type": "generate_compliance_tasks",
                "description": "Generate compliance tasks for departments affected by the new OGRA fuel pricing notification.",
                "api_endpoint": "POST /api/compliance/tasks/generate",
                "api_payload": {
                    "regulation_id": "OGRA-PET-2024-847",
                    "affected_departments": ["operations", "finance", "legal"],
                    "deadline": "2026-05-28T00:00:00Z"
                },
                "quantified_delta": "9 compliance tasks created across 3 departments",
                "feasibility_score": 9,
                "impact_score": 8,
                "composite_score": 8.4,
                "justification": "OGRA notification is legally binding. Generating compliance tasks immediately ensures all departments update fuel-indexed contracts within the legal window.",
                "success_metric": "compliance_tasks_open increases in state",
                "time_to_execute": "< 2 hours"
            },
            {
                "rank": 2,
                "action_id": "A2",
                "action_type": "update_pricing_policy",
                "description": "Update pricing policy to reflect fuel duty change across all affected product categories.",
                "api_endpoint": "POST /api/pricing/policy_update",
                "api_payload": {
                    "policy_ref": "POL-DUTY-2024",
                    "affected_categories": ["transport", "logistics", "delivery"],
                    "cost_delta_pct": 4.5
                },
                "quantified_delta": "3 pricing categories updated with 4.5% cost adjustment",
                "feasibility_score": 8,
                "impact_score": 7,
                "composite_score": 7.4,
                "justification": "Duty increase of PKR 12.74/L translates to 4.5% cost delta. Updating policy prevents margin erosion on active transport contracts.",
                "success_metric": "affected_categories in state updates to 3",
                "time_to_execute": "< 1 hour"
            }
        ],
        "recommended_execution_sequence": [1, 2],
        "auto_execute_rank_1": True,
        "reasoning_summary": "Compliance task generation is prioritized as it creates the accountability framework. Policy pricing update follows to capture the financial adjustment."
    },
    "logistics": {
        "agent": "decision",
        "domain": "logistics",
        "candidates_evaluated": 5,
        "actions": [
            {
                "rank": 1,
                "action_id": "A1",
                "action_type": "update_pricing_rule",
                "description": "Increase Lahore-Karachi corridor pricing by 18% to offset fuel surge cost impact.",
                "api_endpoint": "POST /api/logistics/pricing/update",
                "api_payload": {
                    "route_id": "LAHORE-KARACHI",
                    "price_delta_pct": 18.0,
                    "effective_date": "2026-05-21T00:00:00Z"
                },
                "quantified_delta": "delivery_price_per_kg increases by 18% on LAHORE-KARACHI route",
                "feasibility_score": 9,
                "impact_score": 9,
                "composite_score": 9.0,
                "justification": "PSO fuel surge of 18% directly increases per-km operating cost by PKR 0.43/kg. Immediately updating pricing recovers PKR 2.4M monthly margin loss on the affected corridor.",
                "success_metric": "delivery_price_per_kg increases in state",
                "time_to_execute": "< 1 hour"
            },
            {
                "rank": 2,
                "action_id": "A2",
                "action_type": "optimize_routes",
                "description": "Optimize Lahore-Karachi route for fuel cost reduction to partially offset the 18% surge.",
                "api_endpoint": "POST /api/logistics/routes/optimize",
                "api_payload": {
                    "current_route_id": "LAHORE-KARACHI",
                    "optimization_target": "fuel_cost"
                },
                "quantified_delta": "fuel_cost_ratio_pct decreases by ~8.5% through route optimization",
                "feasibility_score": 7,
                "impact_score": 8,
                "composite_score": 7.6,
                "justification": "Route optimization yields 8.5% fuel savings that partially offset the 18% OGRA price surge, reducing net cost impact to ~9.5%.",
                "success_metric": "fuel_cost_ratio_pct decreases in state",
                "time_to_execute": "2-4 hours"
            }
        ],
        "recommended_execution_sequence": [1, 2],
        "auto_execute_rank_1": True,
        "reasoning_summary": "Pricing update is immediate and directly recovers margin. Route optimization follows as a structural cost reduction measure."
    },
    "healthcare": {
        "agent": "decision",
        "domain": "healthcare",
        "candidates_evaluated": 5,
        "actions": [
            {
                "rank": 1,
                "action_id": "A1",
                "action_type": "trigger_emergency_procurement",
                "description": "Place emergency procurement order for 50,000 units of Insulin Glargine from WHO-approved suppliers.",
                "api_endpoint": "POST /api/procurement/emergency_order",
                "api_payload": {
                    "item_id": "DRUG-INSULIN-GLARGINE-100IU",
                    "quantity": 50000,
                    "urgency": "emergency",
                    "supplier_shortlist": ["Novo Nordisk Turkey", "Sanofi UAE"]
                },
                "quantified_delta": "emergency_pos_open +1, drug_availability_pct +5% toward recovery",
                "feasibility_score": 8,
                "impact_score": 10,
                "composite_score": 9.2,
                "justification": "40% stock depletion at CMH and PIMS affects 12,000 patients. Emergency procurement with 3-day ETA is the only path to restore clinical coverage before critical threshold.",
                "success_metric": "emergency_pos_open increases and drug_availability_pct recovers in state",
                "time_to_execute": "< 2 hours"
            },
            {
                "rank": 2,
                "action_id": "A2",
                "action_type": "activate_substitute_protocol",
                "description": "Activate Insulin NPH substitution protocol at CMH and PIMS while awaiting emergency shipment.",
                "api_endpoint": "POST /api/clinical/protocols/activate",
                "api_payload": {
                    "protocol_id": "PROT-INSULIN-SUBST-001",
                    "drug_id": "DRUG-INSULIN-GLARGINE-100IU",
                    "affected_facilities": ["CMH", "PIMS"]
                },
                "quantified_delta": "Substitute protocol active across 2 facilities, 24 staff notified each",
                "feasibility_score": 10,
                "impact_score": 7,
                "composite_score": 8.2,
                "justification": "Bridge treatment with Insulin NPH prevents patient harm during the 3-day procurement window. Protocol activation is immediate and requires no procurement.",
                "success_metric": "Protocol activation confirmed at both facilities",
                "time_to_execute": "< 1 hour"
            }
        ],
        "recommended_execution_sequence": [1, 2],
        "auto_execute_rank_1": True,
        "reasoning_summary": "Emergency procurement addresses root cause. Substitute protocol provides immediate patient safety bridge during the procurement lead time."
    },
    "urban": {
        "agent": "decision",
        "domain": "urban",
        "candidates_evaluated": 5,
        "actions": [
            {
                "rank": 1,
                "action_id": "A1",
                "action_type": "dispatch_maintenance_crew",
                "description": "Dispatch emergency electrical crew to Kot Lakhpat substation to restore the 132kV breaker fault.",
                "api_endpoint": "POST /api/operations/dispatch",
                "api_payload": {
                    "fault_location": "Kot Lakhpat 132kV Substation, Lahore",
                    "crew_type": "electrical",
                    "priority": "high",
                    "eta_minutes": 45
                },
                "quantified_delta": "crews_dispatched +1, estimated 18-hour outage for 340,000 households addressed",
                "feasibility_score": 9,
                "impact_score": 9,
                "composite_score": 9.0,
                "justification": "Direct breaker fault resolution restores grid to 340,000 households and 4,200 businesses. Electrical crew dispatch with 45-minute ETA is the fastest resolution path.",
                "success_metric": "crews_dispatched increases in state",
                "time_to_execute": "< 1 hour"
            },
            {
                "rank": 2,
                "action_id": "A3",
                "action_type": "publish_public_advisory",
                "description": "Issue public advisory via SMS and app to inform citizens about the outage and expected restoration.",
                "api_endpoint": "POST /api/communications/public_advisory",
                "api_payload": {
                    "zone_id": "LAHORE-EAST-ZONE",
                    "issue_type": "power_outage",
                    "severity": "high",
                    "guidance_text": "LESCO Emergency: Power outage at Kot Lakhpat substation affecting DHA, Gulberg, Johar Town. Repair crew dispatched. ETA restoration: 6-8 hours. Use generators sparingly.",
                    "channels": ["sms", "app"]
                },
                "quantified_delta": "advisories_published +1, estimated 45,000 citizens reached",
                "feasibility_score": 10,
                "impact_score": 6,
                "composite_score": 7.6,
                "justification": "Public advisory reduces complaint load and prevents panic by providing accurate ETA. Immediate, zero-cost action with high citizen satisfaction impact.",
                "success_metric": "advisories_published increases in state",
                "time_to_execute": "< 15 minutes"
            }
        ],
        "recommended_execution_sequence": [1, 2],
        "auto_execute_rank_1": True,
        "reasoning_summary": "Crew dispatch directly resolves the fault. Public advisory runs in parallel to manage citizen expectations during the 6-8 hour repair window."
    },
    "business": {
        "agent": "decision",
        "domain": "business",
        "candidates_evaluated": 5,
        "actions": [
            {
                "rank": 1,
                "action_id": "A3",
                "action_type": "trigger_crm_workflow",
                "description": "Trigger CRM retention workflow targeting the 47 at-risk merchant accounts in Karachi.",
                "api_endpoint": "POST /api/crm/workflows/trigger",
                "api_payload": {
                    "workflow_id": "WF-RETENTION-KARACHI-001",
                    "segment": "karachi_at_risk_accounts",
                    "message_template": "urgent_retention_offer_15pct_discount"
                },
                "quantified_delta": "churn_risk_customers decreases by ~30% through targeted outreach",
                "feasibility_score": 9,
                "impact_score": 8,
                "composite_score": 8.4,
                "justification": "CRM workflow re-activates 47 silent high-value accounts responsible for PKR 2.63M revenue loss. 15% discount incentive recovers churn before end of Q3.",
                "success_metric": "churn_risk_customers decreases in state",
                "time_to_execute": "< 3 hours"
            },
            {
                "rank": 2,
                "action_id": "A1",
                "action_type": "launch_retention_campaign",
                "description": "Launch a targeted discount campaign for Karachi high-value segment to recover Q3 revenue.",
                "api_endpoint": "POST /api/crm/campaigns/create",
                "api_payload": {
                    "region": "Karachi",
                    "discount_pct": 15.0,
                    "target_segment": "high_value_churn_risk",
                    "duration_days": 14,
                    "budget_pkr": 150000.0
                },
                "quantified_delta": "active_campaigns +1, projected reach of 480,000 PKR",
                "feasibility_score": 10,
                "impact_score": 6,
                "composite_score": 7.6,
                "justification": "Campaign budget of PKR 150K projected to generate PKR 480K in recovered orders through 3.2x ROI on high-demand detergent and rice SKUs.",
                "success_metric": "active_campaigns increases in state",
                "time_to_execute": "< 2 hours"
            }
        ],
        "recommended_execution_sequence": [1, 2],
        "auto_execute_rank_1": True,
        "reasoning_summary": "CRM workflow is prioritized for immediate account retention. Campaign runs in parallel to drive new order volume recovery."
    }
}
