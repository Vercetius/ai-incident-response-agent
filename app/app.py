import sys
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


from src.log_ingestion import load_and_normalize
from src.pipeline import IncidentResponsePipeline


st.set_page_config(
    page_title="AI Incident Response Agent",
    page_icon="🚨",
    layout="wide",
)


@st.cache_resource
def load_pipeline():
    return IncidentResponsePipeline()


@st.cache_data
def load_demo_incidents():
    return load_and_normalize(
        "data/generated/incidents.json"
    )


pipeline = load_pipeline()
incidents = load_demo_incidents()


st.title("🚨 AI Incident Response Agent")

st.write(
    "AI-assisted incident triage, anomaly detection, "
    "runbook retrieval, root-cause analysis and "
    "human-approved response planning."
)


with st.sidebar:
    st.header("Incident")

    incident_labels = {
        (
            f"{incident.incident_id} — "
            f"{incident.title}"
        ): incident
        for incident in incidents
    }

    selected_label = st.selectbox(
        "Select a synthetic incident",
        list(incident_labels.keys()),
    )

    selected_incident = incident_labels[
        selected_label
    ]

    analyze = st.button(
        "Analyze Incident",
        type="primary",
        use_container_width=True,
    )

    st.divider()

    st.caption(
        "Synthetic incident-response environment "
        "for portfolio demonstration."
    )


if analyze:
    with st.spinner(
        "Analyzing incident..."
    ):
        result = pipeline.analyze(
            selected_incident
        )

    triage = result["triage"]
    root_cause = result["root_cause"]
    risk = result["operational_risk"]

    st.subheader(
        f"{selected_incident.incident_id} — "
        f"{selected_incident.title}"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Severity",
            triage["severity"].upper(),
        )

    with col2:
        st.metric(
            "Priority",
            triage["priority"],
        )

    with col3:
        st.metric(
            "Confidence",
            f'{result["confidence"]:.1%}',
        )

    with col4:
        st.metric(
            "Operational Risk",
            f'{risk["risk_score"]}/100',
        )

    if result["human_approval_required"]:
        st.error(
            "Human approval required before "
            "operational changes."
        )
    else:
        st.success(
            "No mandatory human approval triggered."
        )

    if result["escalation_required"]:
        st.warning(
            "Escalation required."
        )

        for reason in result[
            "escalation_reasons"
        ]:
            st.write(
                f"- {reason}"
            )

    st.divider()

    st.subheader("Root Cause Analysis")

    st.write(
        "**Hypothesis:**",
        root_cause["hypothesis"],
    )

    st.write(
        "**Root-cause confidence:**",
        f'{root_cause["confidence"]:.1%}',
    )

    st.write(
        "**Analysis method:**",
        root_cause["method"],
    )

    st.write(
        "**Reasoning:**",
        root_cause["reasoning"],
    )

    st.divider()

    st.subheader("Detected Anomalies")

    anomalies = result[
        "anomalies"
    ]["anomalies"]

    if anomalies:
        for anomaly in anomalies:
            severity = anomaly[
                "severity"
            ].upper()

            message = anomaly[
                "message"
            ]

            st.write(
                f"**{severity}** — {message}"
            )

            if (
                "metric"
                in anomaly
            ):
                st.caption(
                    f'Metric: {anomaly["metric"]} | '
                    f'Value: {anomaly["value"]} | '
                    f'Threshold: {anomaly["threshold"]}'
                )

            if (
                "evidence"
                in anomaly
            ):
                st.caption(
                    f'Evidence: {anomaly["evidence"]}'
                )
    else:
        st.info(
            "No predefined anomalies detected."
        )

    st.divider()

    st.subheader("Recommended Action Plan")

    action_plan = result[
        "action_plan"
    ]

    sections = [
        (
            "Immediate Actions",
            "immediate_actions",
        ),
        (
            "Investigation",
            "investigation_actions",
        ),
        (
            "Recovery",
            "recovery_actions",
        ),
        (
            "Verification",
            "verification_actions",
        ),
    ]

    for title, key in sections:
        st.markdown(
            f"### {title}"
        )

        actions = action_plan.get(
            key,
            []
        )

        if actions:
            for action in actions:
                st.write(
                    f"- {action}"
                )
        else:
            st.write(
                "No action proposed."
            )

    st.caption(
        f'Planning method: '
        f'{action_plan["method"]}'
    )

    st.divider()

    st.subheader(
        "Relevant Runbooks"
    )

    for item in result[
        "retrieval"
    ]["runbooks"]:
        with st.expander(
            (
                f'{item["name"]} '
                f'— similarity '
                f'{item["score"]:.3f}'
            )
        ):
            st.markdown(
                item["content"]
            )

    st.divider()

    st.subheader(
        "Similar Historical Incidents"
    )

    for item in result[
        "retrieval"
    ]["historical_incidents"]:
        with st.expander(
            (
                f'{item["incident_id"]} — '
                f'{item["title"]} '
                f'({item["score"]:.3f})'
            )
        ):
            st.write(
                "**Severity:**",
                item["severity"],
            )

            st.write(
                "**Root Cause:**",
                item["root_cause"],
            )

            st.write(
                "**Resolution:**",
                item["resolution"],
            )

    st.divider()

    st.subheader("Raw Incident Evidence")

    for log in selected_incident.logs:
        st.code(
            (
                f"{log.timestamp} "
                f"[{log.level}] "
                f"{log.service}: "
                f"{log.message}"
            ),
            language=None,
        )

else:
    st.info(
        "Select an incident and click "
        "'Analyze Incident'."
    )
