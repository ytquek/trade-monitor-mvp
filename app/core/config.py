DEFAULT_TOPIC_PROFILES = {
    "trade_connectivity": {
        "positive_terms": [
            "single window",
            "customs modernization",
            "trade facilitation",
            "national logistics platform",
            "customs digitalization",
            "border digitization",
            "port community system",
            "transit corridor",
            "electronic bill of lading",
            "e-document",
            "cross-border interoperability",
        ],
        "negative_terms": [
            "tourism",
            "festival",
            "sports",
            "lifestyle",
        ],
        "anchor_texts": [
            "Government launches a customs single window to streamline border clearance and inter-agency approvals.",
            "Port community system deployment improves cargo visibility, customs data exchange, and trade processing.",
            "Trade corridor modernization enables digital customs procedures and multimodal logistics integration.",
        ],
    },
    "maritime_activity": {
        "positive_terms": [
            "port expansion",
            "terminal concession",
            "berth expansion",
            "dredging",
            "transshipment",
            "feeder service",
            "vessel traffic",
            "bunkering",
            "ship registry",
            "port investment",
            "container terminal",
            "maritime logistics",
        ],
        "negative_terms": [
            "cruise vacation",
            "celebration",
            "award dinner",
        ],
        "anchor_texts": [
            "Port authority awards a contract for terminal expansion, dredging, and new berth capacity.",
            "A maritime operator launches new feeder and transshipment services to strengthen regional connectivity.",
            "The government approves port infrastructure upgrades and concession reforms to increase cargo throughput.",
        ],
    },
}

EVENT_KEYWORDS = {
    "launch": ["launch", "launched", "rollout", "implement", "deployment", "go-live"],
    "investment": ["invest", "investment", "funding", "capex", "finance"],
    "concession": ["concession", "award", "awarded", "operator", "terminal operator"],
    "expansion": ["expansion", "expand", "berth", "dredging", "capacity", "terminal"],
    "regulation": ["regulation", "policy", "directive", "customs reform", "mandate"],
    "tender": ["tender", "rfp", "procurement", "bid", "solicitation"],
    "disruption": ["disruption", "closure", "congestion", "delay", "incident"],
}

DEFAULT_COUNTRY_TERMS = [
    "singapore", "indonesia", "malaysia", "thailand", "vietnam", "philippines",
    "india", "bangladesh", "sri lanka", "kenya", "tanzania", "mozambique",
    "namibia", "uae", "saudi arabia", "oman", "egypt", "rwanda",
]
