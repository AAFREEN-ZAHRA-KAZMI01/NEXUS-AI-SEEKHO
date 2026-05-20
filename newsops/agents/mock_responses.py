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
        "actions": [
            {
                "rank": 1,
                "action_type": "update_hedging_position",
                "description": "Trigger immediate USD/PKR forward contracts at current interbank rate to protect export receivables.",
                "api_endpoint": "/api/finance/hedging",
                "api_payload": {
                    "exposure_usd": 200000000,
                    "hedge_ratio_pct": 75,
                    "tenor_days": 90,
                    "target_rate_pkr": 280.50
                },
                "feasibility_score": 8,
                "impact_score": 9,
                "composite_score": 8.4,
                "justification": "Protects PKR 12.0M of export revenue currently at risk from currency devaluation by locking in exchange rates.",
                "success_metric": "Hedged USD value protection",
                "time_to_execute": "12 hours"
            },
            {
                "rank": 2,
                "action_type": "set_fx_alert",
                "description": "Configure real-time volatility thresholds on SBP daily FX rates with notifications.",
                "api_endpoint": "/api/finance/alerts",
                "api_payload": {
                    "currency_pair": "USD/PKR",
                    "threshold_pct": 1.5,
                    "frequency": "hourly"
                },
                "feasibility_score": 10,
                "impact_score": 6,
                "composite_score": 7.6,
                "justification": "Ensures treasury team has immediate visibility of intraday rate spikes for capital deployment.",
                "success_metric": "Alert response latency",
                "time_to_execute": "1 hour"
            }
        ]
    },
    "policy": {
        "agent": "decision",
        "domain": "policy",
        "actions": [
            {
                "rank": 1,
                "action_type": "update_compliance_checklist",
                "description": "Re-audit transport contracts to enforce fuel-indexed pricing adjustment triggers.",
                "api_endpoint": "/api/policy/compliance",
                "api_payload": {
                    "regulatory_ref": "OGRA-PET-2024-847",
                    "effective_date": "2026-05-18",
                    "compliance_category": "Logistics Surcharges",
                    "audit_scope_pct": 100
                },
                "feasibility_score": 9,
                "impact_score": 8,
                "composite_score": 8.4,
                "justification": "Enables immediate capture of contract fuel clauses, ensuring fuel hikes are legally billed to customers.",
                "success_metric": "Contracts updated and audited",
                "time_to_execute": "24 hours"
            },
            {
                "rank": 2,
                "action_type": "trigger_compliance_audit",
                "description": "Initiate comprehensive regional compliance checks across all oil distribution depots.",
                "api_endpoint": "/api/policy/audits",
                "api_payload": {
                    "audit_type": "depot price enforcement",
                    "priority": "high",
                    "regions": ["Punjab", "Sindh"]
                },
                "feasibility_score": 8,
                "impact_score": 7,
                "composite_score": 7.4,
                "justification": "Ensures logistics depots don't price-gouge beyond the legal OGRA PKR 12.74 limit.",
                "success_metric": "Audits completed",
                "time_to_execute": "48 hours"
            }
        ]
    },
    "logistics": {
        "agent": "decision",
        "domain": "logistics",
        "actions": [
            {
                "rank": 1,
                "action_type": "update_pricing",
                "description": "Re-calculate shipping pricing matrices per-route to counter the 18% freight cost surge.",
                "api_endpoint": "/api/logistics/pricing",
                "api_payload": {
                    "base_increase_pct": 12.5,
                    "target_domains": ["logistics", "business"],
                    "surcharge_pkr_per_kg": 0.45
                },
                "feasibility_score": 9,
                "impact_score": 9,
                "composite_score": 9.0,
                "justification": "Directly offsets the cargo price increase by billing cargo surcharges, protecting company margins.",
                "success_metric": "Delivery cost recovery",
                "time_to_execute": "6 hours"
            },
            {
                "rank": 2,
                "action_type": "reroute_fleet",
                "description": "Redirect incoming heavy CKD container shipments from KPT to Gwadar dry-dock.",
                "api_endpoint": "/api/logistics/reroute",
                "api_payload": {
                    "vessels_diverted": 5,
                    "alternative_port": "Gwadar Port",
                    "carrier": "NLC Fleet"
                },
                "feasibility_score": 6,
                "impact_score": 8,
                "composite_score": 7.2,
                "justification": "Bypasses KPTs 11.2 day dwell backlog to supply auto production lines in north zones.",
                "success_metric": "Vessel delay reduction",
                "time_to_execute": "48 hours"
            }
        ]
    },
    "healthcare": {
        "agent": "decision",
        "domain": "healthcare",
        "actions": [
            {
                "rank": 1,
                "action_type": "trigger_emergency_procurement",
                "description": "Directly execute emergency international tenders for Insulin Glargine imports via WHO coordination.",
                "api_endpoint": "/api/healthcare/procurement",
                "api_payload": {
                    "item_name": "Insulin Glargine 100IU/ml",
                    "quantity_vials": 50000,
                    "priority": "critical",
                    "source_country": "Turkey",
                    "funding_source": "Punjab Emergency Fund"
                },
                "feasibility_score": 8,
                "impact_score": 10,
                "composite_score": 9.2,
                "justification": "Bypasses standard drug import delays to rescue 12,000 insulin-dependent diabetic patients in Lahore clinics.",
                "success_metric": "Vials cleared and delivered",
                "time_to_execute": "5 days"
            },
            {
                "rank": 2,
                "action_type": "update_clinical_protocols",
                "description": "Distribute clinical guidance to Lahore hospitals for insulin rationing and formulary substitution.",
                "api_endpoint": "/api/healthcare/protocols",
                "api_payload": {
                    "guideline_id": "INSULIN-RAT-2024",
                    "substitute_drug": "Insulin NPH",
                    "target_clinics": ["Lahore General", "Mayo Hospital"]
                },
                "feasibility_score": 10,
                "impact_score": 7,
                "composite_score": 8.2,
                "justification": "Minimizes mortality risk by utilizing accessible alternative drugs during active glargine safety shortfalls.",
                "success_metric": "Hospital adherence rate",
                "time_to_execute": "12 hours"
            }
        ]
    },
    "urban": {
        "agent": "decision",
        "domain": "urban",
        "actions": [
            {
                "rank": 1,
                "action_type": "dispatch_crews",
                "description": "Mobilize emergency grid repair crews and heavy replacement switchgear to Kot Lakhpat sub-station.",
                "api_endpoint": "/api/urban/maintenance",
                "api_payload": {
                    "target_substation": "132kV Kot Lakhpat",
                    "crew_size": 24,
                    "specialist_teams": ["Breaker Repair", "Grid Stability"],
                    "work_order_id": "LESCO-WO-8472"
                },
                "feasibility_score": 9,
                "impact_score": 9,
                "composite_score": 9.0,
                "justification": "Resolves the primary breaker fault directly to restore 18-hour outage for 340,000 Lahore residents.",
                "success_metric": "Breaker restoration speed",
                "time_to_execute": "6 hours"
            },
            {
                "rank": 2,
                "action_type": "publish_advisory",
                "description": "Broadcast emergency LESCO urban power schedule updates and load-management schedules.",
                "api_endpoint": "/api/urban/alerts",
                "api_payload": {
                    "channels": ["SMS", "FM-93", "Twitter"],
                    "advisory_text": "LESCO Emergency Alert: Unplanned substation repair at Kot Lakhpat in progress.",
                    "affected_zones": ["DHA", "Gulberg", "Johar Town"]
                },
                "feasibility_score": 10,
                "impact_score": 6,
                "composite_score": 7.6,
                "justification": "Mitigates citizen complaints by providing precise restoral ETAs and contingency zone warnings.",
                "success_metric": "Complaint index drop",
                "time_to_execute": "30 minutes"
            }
        ]
    },
    "business": {
        "agent": "decision",
        "domain": "business",
        "actions": [
            {
                "rank": 1,
                "action_type": "crm_outreach",
                "description": "Trigger automated high-value buyer loyalty campaigns and discount alerts in Karachi.",
                "api_endpoint": "/api/business/crm/outreach",
                "api_payload": {
                    "target_accounts": 47,
                    "incentive_pct": 15,
                    "target_skus": ["SKU-1042 Premium Basmati", "SKU-2287 Cooking Oil"],
                    "valid_days": 14
                },
                "feasibility_score": 9,
                "impact_score": 8,
                "composite_score": 8.4,
                "justification": "Recovers PKR 2.63M in Karachi sales risk by immediately re-activating the 47 silent merchant buyers.",
                "success_metric": "Account reactivation rate",
                "time_to_execute": "2 hours"
            },
            {
                "rank": 2,
                "action_type": "update_promotional_campaign",
                "description": "Increase digital retail marketing budget in Karachi for fast-moving bulk products.",
                "api_endpoint": "/api/business/campaigns",
                "api_payload": {
                    "campaign_name": "Karachi Bulk Savings",
                    "channel": "Facebook & Retail SMS",
                    "additional_budget_pkr": 150000
                },
                "feasibility_score": 10,
                "impact_score": 6,
                "composite_score": 7.6,
                "justification": "Drives immediate wholesale order placement, clearing warehousing backlog of high-supply detergent SKUs.",
                "success_metric": "Karachi order volume surge",
                "time_to_execute": "12 hours"
            }
        ]
    }
}
