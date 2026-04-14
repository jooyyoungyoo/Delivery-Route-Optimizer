import json
import streamlit as st
import pandas as pd

# Local copy of your repo's OSM working bounds
ABINGTON_BOUNDS = {
    "north": 40.145,
    "south": 40.085,
    "east": -75.075,
    "west": -75.175,
}

# Example warehouse and locations for instant use
SAMPLE_WAREHOUSE = {
    "Type": "Warehouse",
    "Name": "Abington Main Warehouse",
    "Latitude": 40.1165,
    "Longitude": -75.1150,
}

SAMPLE_LOCATIONS = [
    {
        "Type": "Delivery",
        "Name": "Customer A",
        "Latitude": 40.1200,
        "Longitude": -75.1100,
        "Priority": 3,
        "Value": 1.0,
        "Notes": "Sample stop",
    },
    {
        "Type": "Delivery",
        "Name": "Customer B",
        "Latitude": 40.1180,
        "Longitude": -75.1200,
        "Priority": 2,
        "Value": 1.0,
        "Notes": "Sample stop",
    },
    {
        "Type": "Delivery",
        "Name": "Customer C",
        "Latitude": 40.1140,
        "Longitude": -75.1050,
        "Priority": 4,
        "Value": 1.0,
        "Notes": "Sample stop",
    },
    {
        "Type": "Pickup",
        "Name": "Supplier D",
        "Latitude": 40.1125,
        "Longitude": -75.1180,
        "Priority": 1,
        "Value": 2.0,
        "Notes": "Sample pickup",
    },
    {
        "Type": "Delivery",
        "Name": "Customer E",
        "Latitude": 40.1175,
        "Longitude": -75.1120,
        "Priority": 5,
        "Value": 1.0,
        "Notes": "Sample stop",
    },
    {
        "Type": "Other",
        "Name": "Checkpoint F",
        "Latitude": 40.1155,
        "Longitude": -75.1085,
        "Priority": 3,
        "Value": 1.0,
        "Notes": "Sample checkpoint",
    },
]


def get_sample_warehouse():
    return SAMPLE_WAREHOUSE.copy()


def get_sample_locations():
    return [location.copy() for location in SAMPLE_LOCATIONS]


def load_sample_data():
    st.session_state.warehouse = get_sample_warehouse()
    st.session_state.locations = get_sample_locations()


def clear_all_data():
    st.session_state.warehouse = None
    st.session_state.locations = []


def in_bounds(lat: float, lon: float) -> bool:
    return (
        ABINGTON_BOUNDS["south"] <= lat <= ABINGTON_BOUNDS["north"]
        and ABINGTON_BOUNDS["west"] <= lon <= ABINGTON_BOUNDS["east"]
    )


def validate_point(lat: float, lon: float, label: str = "Location") -> None:
    if not in_bounds(lat, lon):
        raise ValueError(
            f"{label} ({lat}, {lon}) is outside the Abington working area.\n"
            f"Valid latitude: {ABINGTON_BOUNDS['south']} to {ABINGTON_BOUNDS['north']}\n"
            f"Valid longitude: {ABINGTON_BOUNDS['west']} to {ABINGTON_BOUNDS['east']}"
        )


st.set_page_config(
    page_title="Delivery Route Menu",
    layout="wide",
)

if "warehouse" not in st.session_state:
    st.session_state.warehouse = get_sample_warehouse()

if "locations" not in st.session_state:
    st.session_state.locations = get_sample_locations()


def locations_df() -> pd.DataFrame:
    if not st.session_state.locations:
        return pd.DataFrame(
            columns=["Type", "Name", "Latitude", "Longitude", "Priority", "Value", "Notes"]
        )
    return pd.DataFrame(st.session_state.locations)


st.title("Delivery Route Optimizer")
st.caption("Baseline location-entry menu only — no algorithms connected yet.")

with st.sidebar:
    st.header("Working Area")
    st.write("Accepted coordinate range:")
    st.info(
        f"Latitude: {ABINGTON_BOUNDS['south']} to {ABINGTON_BOUNDS['north']}\n\n"
        f"Longitude: {ABINGTON_BOUNDS['west']} to {ABINGTON_BOUNDS['east']}"
    )

    st.header("Stored Data")
    st.write(f"Warehouse set: {'Yes' if st.session_state.warehouse else 'No'}")
    st.write(f"Saved stops: {len(st.session_state.locations)}")

    st.header("Quick Actions")
    if st.button("Load Example Data", use_container_width=True):
        load_sample_data()
        st.success("Example data loaded.")

    if st.button("Clear All Data", use_container_width=True):
        clear_all_data()
        st.success("All data cleared.")

tab1, tab2, tab3 = st.tabs(["Warehouse", "Stops", "Saved Data"])

with tab1:
    st.subheader("Set Warehouse / Start Location")

    with st.form("warehouse_form"):
        default_wh = st.session_state.warehouse or {
            "Name": "Main Start Point",
            "Latitude": 40.1165,
            "Longitude": -75.1150,
        }

        wh_name = st.text_input("Warehouse Name", value=default_wh["Name"])
        wh_lat = st.number_input(
            "Warehouse Latitude",
            min_value=float(ABINGTON_BOUNDS["south"]),
            max_value=float(ABINGTON_BOUNDS["north"]),
            value=float(default_wh["Latitude"]),
            format="%.6f",
        )
        wh_lon = st.number_input(
            "Warehouse Longitude",
            min_value=float(ABINGTON_BOUNDS["west"]),
            max_value=float(ABINGTON_BOUNDS["east"]),
            value=float(default_wh["Longitude"]),
            format="%.6f",
        )
        save_warehouse = st.form_submit_button("Save Warehouse")

    if save_warehouse:
        try:
            validate_point(wh_lat, wh_lon, "Warehouse")
            st.session_state.warehouse = {
                "Type": "Warehouse",
                "Name": wh_name.strip() or "Main Start Point",
                "Latitude": float(wh_lat),
                "Longitude": float(wh_lon),
            }
            st.success("Warehouse saved.")
        except ValueError as e:
            st.error(str(e))

    if st.session_state.warehouse:
        st.markdown("**Current Warehouse**")
        st.json(st.session_state.warehouse)

with tab2:
    st.subheader("Add Delivery / Pickup Stops")

    with st.form("stop_form"):
        stop_type = st.selectbox("Stop Type", ["Delivery", "Pickup", "Other"])
        stop_name = st.text_input("Location Name", placeholder="Ex: Customer A")
        stop_lat = st.number_input(
            "Latitude",
            min_value=float(ABINGTON_BOUNDS["south"]),
            max_value=float(ABINGTON_BOUNDS["north"]),
            value=40.1200,
            format="%.6f",
        )
        stop_lon = st.number_input(
            "Longitude",
            min_value=float(ABINGTON_BOUNDS["west"]),
            max_value=float(ABINGTON_BOUNDS["east"]),
            value=-75.1100,
            format="%.6f",
        )
        priority = st.selectbox("Priority", [1, 2, 3, 4, 5], index=2)
        value = st.number_input("Value / Weight / Quantity", min_value=0.0, value=1.0, step=1.0)
        notes = st.text_area("Notes", placeholder="Optional notes")
        add_stop = st.form_submit_button("Add Stop")

    if add_stop:
        try:
            validate_point(stop_lat, stop_lon, stop_name or "Stop")
            st.session_state.locations.append(
                {
                    "Type": stop_type,
                    "Name": stop_name.strip() or f"Stop {len(st.session_state.locations) + 1}",
                    "Latitude": float(stop_lat),
                    "Longitude": float(stop_lon),
                    "Priority": int(priority),
                    "Value": float(value),
                    "Notes": notes.strip(),
                }
            )
            st.success("Stop added.")
        except ValueError as e:
            st.error(str(e))

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Remove Last Stop", use_container_width=True):
            if st.session_state.locations:
                st.session_state.locations.pop()
                st.success("Last stop removed.")
            else:
                st.warning("No stops to remove.")

    with col2:
        if st.button("Clear Stops Only", use_container_width=True):
            st.session_state.locations = []
            st.success("All stops cleared.")

with tab3:
    st.subheader("Saved Data")

    if st.session_state.warehouse:
        st.markdown("**Warehouse**")
        st.json(st.session_state.warehouse)
    else:
        st.info("No warehouse saved yet.")

    st.markdown("**Stops**")
    df = locations_df()
    st.dataframe(df, use_container_width=True, hide_index=True)

    export_data = {
        "warehouse": st.session_state.warehouse,
        "locations": st.session_state.locations,
    }

    st.download_button(
        label="Download Saved Data as JSON",
        data=json.dumps(export_data, indent=2),
        file_name="saved_locations.json",
        mime="application/json",
    )
